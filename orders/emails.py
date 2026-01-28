from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation(order):
    """
    Send order confirmation email to customer.
    """
    try:
        subject = f'Order Confirmation - ZLATO Order #{order.order_number}'

        context = {
            'order': order,
            'admin_email': getattr(settings, 'ADMIN_EMAIL', 'orders@zlato.bg')
        }

        # Render HTML and text versions
        html_content = render_to_string('orders/emails/order_confirmation.html', context)
        text_content = render_to_string('orders/emails/order_confirmation.txt', context)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer_email]
        )
        email.attach_alternative(html_content, "text/html")

        # Send
        email.send(fail_silently=False)
        logger.info(f'Order confirmation email sent to {order.customer_email} for order {order.order_number}')

        return True
    except Exception as e:
        logger.error(f'Failed to send order confirmation email for order {order.order_number}: {str(e)}')
        return False


def send_shipping_notification(order):
    """
    Send shipping notification email to customer.
    """
    try:
        subject = f'Your ZLATO Order Has Shipped! #{order.order_number}'

        context = {
            'order': order,
            'admin_email': getattr(settings, 'ADMIN_EMAIL', 'orders@zlato.bg')
        }

        # Render HTML and text versions
        html_content = render_to_string('orders/emails/shipping_notification.html', context)
        text_content = render_to_string('orders/emails/shipping_notification.txt', context)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer_email]
        )
        email.attach_alternative(html_content, "text/html")

        # Send
        email.send(fail_silently=False)
        logger.info(f'Shipping notification email sent to {order.customer_email} for order {order.order_number}')

        return True
    except Exception as e:
        logger.error(f'Failed to send shipping notification email for order {order.order_number}: {str(e)}')
        return False


def send_admin_notification(order):
    """
    Send new order notification to admin.
    """
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'orders@zlato.bg')
        subject = f'New ZLATO Order #{order.order_number} - {order.total} BGN'

        # Build admin URL for the order
        admin_url = f'{settings.SITE_URL}/admin/orders/order/{order.id}/change/' if hasattr(settings, 'SITE_URL') else '#'

        context = {
            'order': order,
            'admin_url': admin_url
        }

        # Render HTML and text versions
        html_content = render_to_string('orders/emails/admin_notification.html', context)
        text_content = render_to_string('orders/emails/admin_notification.txt', context)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email]
        )
        email.attach_alternative(html_content, "text/html")

        # Send
        email.send(fail_silently=False)
        logger.info(f'Admin notification email sent for order {order.order_number}')

        return True
    except Exception as e:
        logger.error(f'Failed to send admin notification email for order {order.order_number}: {str(e)}')
        return False
