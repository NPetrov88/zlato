from django.db import models
from django.utils import timezone
from products.models import Product
from decimal import Decimal


class DiscountCode(models.Model):
    """
    Discount codes for influencer marketing campaigns.
    Example: MARIA10 gives 10% off
    """
    code = models.CharField(max_length=50, unique=True, help_text="Discount code (e.g., MARIA10)")
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage discount (e.g., 10.00 for 10%)"
    )
    active = models.BooleanField(default=True, help_text="Is this code currently active?")
    valid_from = models.DateTimeField(help_text="Code valid from this date")
    valid_to = models.DateTimeField(help_text="Code valid until this date")
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum uses (leave blank for unlimited)"
    )
    times_used = models.IntegerField(default=0, help_text="Number of times code has been used")
    created_by = models.CharField(max_length=100, blank=True, help_text="Influencer name or campaign")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Discount Code"
        verbose_name_plural = "Discount Codes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% off)"

    def is_valid(self):
        """Check if code is currently valid"""
        now = timezone.now()
        if not self.active:
            return False, "Code is inactive"
        if now < self.valid_from:
            return False, "Code not yet valid"
        if now > self.valid_to:
            return False, "Code has expired"
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "Code usage limit reached"
        return True, "Valid"

    def apply_discount(self, amount):
        """Calculate discounted amount"""
        discount = amount * (self.discount_percentage / Decimal('100'))
        return amount - discount


class Order(models.Model):
    """
    Customer order with guest checkout support.
    Stores customer info and shipping address directly.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # Order identification
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Customer information (guest checkout)
    customer_name = models.CharField(max_length=200, help_text="Full name")
    customer_email = models.EmailField(help_text="Email for order confirmation")
    customer_phone = models.CharField(max_length=20, help_text="Phone number")

    # Shipping address (Bulgaria only)
    shipping_address = models.TextField(help_text="Street address")
    shipping_city = models.CharField(max_length=100, help_text="City")
    shipping_postal_code = models.CharField(max_length=20, help_text="Postal code")
    shipping_region = models.CharField(max_length=100, help_text="Region/Oblast", blank=True)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Before shipping and discount")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Final amount paid")

    # Discount code tracking
    discount_code = models.ForeignKey(
        DiscountCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Discount code used for this order"
    )

    # Payment
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Fulfillment
    shipped_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import uuid
            self.order_number = str(uuid.uuid4().hex[:12].upper())
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Individual product in an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200, help_text="Product name at time of order")
    product_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of order")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def total_price(self):
        """Total price for this line item"""
        return self.product_price * self.quantity
