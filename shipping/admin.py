from django.contrib import admin
from .models import ShippingRate


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    """
    Admin interface for managing shipping rates.
    """
    list_display = ['region', 'rate', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['region']
    list_editable = ['rate', 'is_active']

    fieldsets = (
        ('Shipping Details', {
            'fields': ('region', 'rate', 'is_active')
        }),
    )
