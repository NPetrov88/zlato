from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderItem, DiscountCode
from .emails import send_shipping_notification


class OrderItemInline(admin.TabularInline):
    """
    Display order items within order admin page.
    """
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'total_price']
    can_delete = False

    def total_price(self, obj):
        return f"{obj.total_price} BGN"
    total_price.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for managing orders.
    """
    list_display = [
        'order_number',
        'customer_name',
        'customer_email',
        'status_badge',
        'total',
        'discount_code',
        'created_at'
    ]
    list_filter = ['status', 'created_at', 'paid_at', 'shipped_at', 'discount_code']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = [
        'order_number',
        'subtotal',
        'discount_amount',
        'total',
        'stripe_payment_intent_id',
        'created_at',
        'updated_at'
    ]
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_region')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'discount_amount', 'total', 'discount_code')
        }),
        ('Payment', {
            'fields': ('stripe_payment_intent_id', 'paid_at')
        }),
        ('Fulfillment', {
            'fields': ('shipped_at', 'tracking_number', 'notes')
        }),
    )

    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#6c757d',  # Gray
            'paid': '#28a745',     # Green
            'processing': '#007bff', # Blue
            'shipped': '#17a2b8',   # Cyan
            'delivered': '#28a745', # Green
            'cancelled': '#dc3545', # Red
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing"""
        count = queryset.filter(status='paid').update(status='processing')
        self.message_user(request, f'{count} order(s) marked as processing')
    mark_as_processing.short_description = 'Mark as Processing'

    def mark_as_shipped(self, request, queryset):
        """Mark selected orders as shipped"""
        now = timezone.now()
        updated = 0
        for order in queryset.filter(status__in=['paid', 'processing']):
            order.status = 'shipped'
            order.shipped_at = now
            order.save()
            # Send shipping notification email
            send_shipping_notification(order)
            updated += 1
        self.message_user(request, f'{updated} order(s) marked as shipped and customers notified')
    mark_as_shipped.short_description = 'Mark as Shipped (Send Email)'

    def has_add_permission(self, request):
        """Prevent manual order creation"""
        return False


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    """
    Admin interface for managing discount codes.
    """
    list_display = [
        'code',
        'discount_percentage',
        'active',
        'times_used',
        'usage_limit',
        'valid_from',
        'valid_to',
        'created_by'
    ]
    list_filter = ['active', 'created_at']
    search_fields = ['code', 'created_by']
    list_editable = ['active']

    fieldsets = (
        ('Code Details', {
            'fields': ('code', 'discount_percentage', 'active')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Usage', {
            'fields': ('usage_limit', 'times_used', 'created_by')
        }),
    )

    readonly_fields = ['times_used']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    View order items (read-only).
    """
    list_display = ['order', 'product_name', 'quantity', 'product_price', 'get_total']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'product_name']

    def get_total(self, obj):
        return f"{obj.total_price} BGN"
    get_total.short_description = 'Total'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
