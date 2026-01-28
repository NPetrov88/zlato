from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from cart.views import get_or_create_cart
from shipping.models import ShippingRate
from .models import Order, OrderItem, DiscountCode
from .emails import send_order_confirmation, send_admin_notification
from decimal import Decimal
import stripe
import logging

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
logger = logging.getLogger(__name__)


def checkout(request):
    """
    Checkout page - collect shipping info and create order.
    """
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        return redirect('cart:view')

    # Calculate totals
    subtotal = cart.subtotal
    shipping_cost = Decimal('5.00')  # Default
    discount_amount = Decimal('0.00')
    discount_code = None

    # Get discount code from session if applied
    discount_code_id = request.session.get('discount_code_id')
    if discount_code_id:
        try:
            discount_code = DiscountCode.objects.get(id=discount_code_id)
            is_valid, message = discount_code.is_valid()
            if is_valid:
                discount_amount = subtotal * (discount_code.discount_percentage / Decimal('100'))
            else:
                # Clear invalid code from session
                del request.session['discount_code_id']
                discount_code = None
        except DiscountCode.DoesNotExist:
            discount_code = None

    total = subtotal + shipping_cost - discount_amount

    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount_amount': discount_amount,
        'discount_code': discount_code,
        'total': total,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
    }

    return render(request, 'orders/checkout.html', context)


@require_POST
def apply_discount_code(request):
    """
    Validate and apply discount code.
    """
    code = request.POST.get('code', '').strip().upper()

    try:
        discount_code = DiscountCode.objects.get(code=code)
        is_valid, message = discount_code.is_valid()

        if is_valid:
            # Store in session
            request.session['discount_code_id'] = discount_code.id
            return JsonResponse({
                'success': True,
                'message': f'Discount code {code} applied! {discount_code.discount_percentage}% off',
                'discount_percentage': float(discount_code.discount_percentage)
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })
    except DiscountCode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Invalid discount code'
        })


@require_POST
def remove_discount_code(request):
    """
    Remove applied discount code.
    """
    if 'discount_code_id' in request.session:
        del request.session['discount_code_id']

    return JsonResponse({
        'success': True,
        'message': 'Discount code removed'
    })


@require_POST
def create_checkout_session(request):
    """
    Create Stripe checkout session and order.
    """
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    # Get form data
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('customer_email')
    customer_phone = request.POST.get('customer_phone')
    shipping_address = request.POST.get('shipping_address')
    shipping_city = request.POST.get('shipping_city')
    shipping_postal_code = request.POST.get('shipping_postal_code')
    shipping_region = request.POST.get('shipping_region', '')

    # Validate required fields
    if not all([customer_name, customer_email, customer_phone, shipping_address, shipping_city, shipping_postal_code]):
        return JsonResponse({'error': 'All fields are required'}, status=400)

    # Calculate totals
    subtotal = cart.subtotal
    shipping_cost = ShippingRate.get_rate_for_city(shipping_city)
    discount_amount = Decimal('0.00')
    discount_code = None

    # Apply discount code if present
    discount_code_id = request.session.get('discount_code_id')
    if discount_code_id:
        try:
            discount_code = DiscountCode.objects.get(id=discount_code_id)
            is_valid, message = discount_code.is_valid()
            if is_valid:
                discount_amount = subtotal * (discount_code.discount_percentage / Decimal('100'))
        except DiscountCode.DoesNotExist:
            pass

    total = subtotal + Decimal(str(shipping_cost)) - discount_amount

    # Create order
    order = Order.objects.create(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        shipping_address=shipping_address,
        shipping_city=shipping_city,
        shipping_postal_code=shipping_postal_code,
        shipping_region=shipping_region,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        total=total,
        discount_code=discount_code,
        status='pending'
    )

    # Create order items
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_name=cart_item.product.name,
            product_price=cart_item.product.price,
            quantity=cart_item.quantity
        )

    # Increment discount code usage
    if discount_code:
        discount_code.times_used += 1
        discount_code.save()

    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'bgn',
                        'unit_amount': int(total * 100),  # Convert to cents
                        'product_data': {
                            'name': f'ZLATO Order #{order.order_number}',
                            'description': f'Order for {customer_name}',
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(f'/orders/success/{order.order_number}/'),
            cancel_url=request.build_absolute_uri('/payment-failed/'),
            client_reference_id=order.order_number,
            customer_email=customer_email,
        )

        # Save Stripe payment intent ID
        order.stripe_payment_intent_id = checkout_session.payment_intent
        order.save()

        # Clear cart and discount code from session
        cart.delete()
        if 'discount_code_id' in request.session:
            del request.session['discount_code_id']

        return JsonResponse({
            'sessionId': checkout_session.id
        })

    except Exception as e:
        # If Stripe fails, delete the order
        order.delete()
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe webhook endpoint for payment confirmation.
    This is called by Stripe when payment events occur.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    if not webhook_secret:
        logger.error('Stripe webhook secret not configured')
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Invalid payload
        logger.error('Invalid webhook payload')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        logger.error('Invalid webhook signature')
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Get order by client_reference_id (order_number)
        order_number = session.get('client_reference_id')

        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)

                # Update order status to paid
                order.status = 'paid'
                order.paid_at = timezone.now()
                order.stripe_payment_intent_id = session.get('payment_intent', '')
                order.save()

                # Update inventory for each product
                for item in order.items.all():
                    product = item.product
                    if product.inventory >= item.quantity:
                        product.inventory -= item.quantity
                        product.save()
                        logger.info(f'Updated inventory for {product.name}: -{item.quantity}')
                    else:
                        logger.warning(f'Insufficient inventory for {product.name}')

                logger.info(f'Order {order_number} marked as paid via webhook')

                # Send confirmation emails
                send_order_confirmation(order)
                send_admin_notification(order)

            except Order.DoesNotExist:
                logger.error(f'Order {order_number} not found for webhook')
        else:
            logger.error('No client_reference_id in webhook session')

    return HttpResponse(status=200)


def order_success(request, order_number):
    """
    Order confirmation page after successful payment.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Mark order as paid (fallback if webhook hasn't fired yet)
    if order.status == 'pending':
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()

    return render(request, 'orders/success.html', {
        'order': order
    })


def track_order(request):
    """
    Order tracking page - lookup order by order number.
    """
    order = None
    error = None

    if request.method == 'POST':
        order_number = request.POST.get('order_number', '').strip().upper()

        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
            except Order.DoesNotExist:
                error = 'Order not found. Please check your order number and try again.'
        else:
            error = 'Please enter an order number.'

    return render(request, 'orders/track.html', {
        'order': order,
        'error': error
    })
