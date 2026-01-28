from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Product
import logging

logger = logging.getLogger(__name__)


def homepage(request):
    """
    Display the homepage with all active products.
    This is what visitors see when they visit your site.
    """
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/homepage.html', {
        'products': products
    })


def shop(request):
    """
    Display dedicated shop page with all active products.
    Shows only the product catalog for browsing and purchasing.
    """
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/shop.html', {
        'products': products
    })


def product_detail(request, slug):
    """
    Display individual product page with full details.
    Shows description, images gallery, pricing, and add to cart.
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Get all additional images for gallery
    gallery_images = product.images.all()

    # Get the current language to show correct description
    language = request.LANGUAGE_CODE

    return render(request, 'products/product_detail.html', {
        'product': product,
        'gallery_images': gallery_images,
        'language': language,
    })


def about(request):
    """
    Display About page with ZLATO brand story.
    """
    return render(request, 'products/about.html')


def contact(request):
    """
    Display Contact page with form.
    Handle contact form submissions and send emails.
    """
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Validate required fields
        if not all([name, email, subject, message_text]):
            messages.error(request, 'All fields are required.')
            return redirect('contact')

        # Basic email validation
        if '@' not in email or '.' not in email:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('contact')

        try:
            # Send email to admin
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'orders@zlato.bg')
            email_subject = f'ZLATO Contact Form: {subject}'

            context = {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message_text,
            }

            # Render email content
            text_content = f"""
New Contact Form Submission from ZLATO Website

From: {name} ({email})
Subject: {subject}

Message:
{message_text}

---
Sent via ZLATO Contact Form
            """

            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #000; }}
        .header {{ background-color: #C797A3; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #fff; }}
        .info {{ background-color: #E8D4D8; padding: 15px; border-radius: 8px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="color: #000; margin: 0;">ZLATO Contact Form</h1>
    </div>
    <div class="content">
        <div class="info">
            <p><strong>From:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject}</p>
        </div>
        <h2>Message:</h2>
        <p style="white-space: pre-line;">{message_text}</p>
    </div>
</body>
</html>
            """

            # Create and send email
            email_message = EmailMultiAlternatives(
                subject=email_subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
                reply_to=[email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send(fail_silently=False)

            logger.info(f'Contact form submitted by {name} ({email})')
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('contact')

        except Exception as e:
            logger.error(f'Failed to send contact form email: {str(e)}')
            messages.error(request, 'Sorry, there was an error sending your message. Please try again or email us directly.')
            return redirect('contact')

    return render(request, 'products/contact.html')


def payment_failed(request):
    """
    Display payment failed error page.
    """
    return render(request, 'products/payment_failed.html')


def out_of_stock(request):
    """
    Display out of stock error page.
    """
    return render(request, 'products/out_of_stock.html')


def shipping_policy(request):
    """
    Display shipping policy page.
    """
    return render(request, 'products/shipping_policy.html')


def returns_policy(request):
    """
    Display returns policy page.
    """
    return render(request, 'products/returns_policy.html')
