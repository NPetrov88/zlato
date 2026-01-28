from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem


def get_or_create_cart(request):
    """
    Get or create a cart for the current session.
    Creates session if it doesn't exist.
    """
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    """
    Display the shopping cart.
    """
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart.html', {
        'cart': cart
    })


@require_POST
def add_to_cart(request, product_id):
    """
    Add a product to the cart or increase quantity if already in cart.
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)

    # Get quantity from POST data (default 1)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # Item already in cart, increase quantity
        cart_item.quantity += quantity
        cart_item.save()

    # Return JSON for AJAX requests, redirect for regular requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'message': f'{product.name} added to cart'
        })

    return redirect('cart:view')


@require_POST
def update_cart_item(request, item_id):
    """
    Update quantity of a cart item.
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': float(cart.subtotal)
        })

    return redirect('cart:view')


@require_POST
def remove_from_cart(request, item_id):
    """
    Remove an item from the cart.
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': float(cart.subtotal)
        })

    return redirect('cart:view')
