from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """
    Allows adding multiple images to a product directly from the product edit page.
    """
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing products.
    Supports bilingual content (English + Bulgarian) and multiple images.
    """
    list_display = ['name', 'product_type', 'price', 'inventory', 'in_stock', 'is_active', 'featured']
    list_filter = ['product_type', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'name_bg', 'description', 'description_bg']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'featured', 'inventory']
    inlines = [ProductImageInline]

    fieldsets = (
        ('Product Type', {
            'fields': ('product_type',)
        }),
        ('English Content', {
            'fields': ('name', 'slug', 'short_description', 'description')
        }),
        ('Bulgarian Content', {
            'fields': ('name_bg', 'short_description_bg', 'description_bg'),
            'classes': ('collapse',)
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'inventory')
        }),
        ('Main Image', {
            'fields': ('image',)
        }),
        ('Display Options', {
            'fields': ('is_active', 'featured')
        }),
    )

    def in_stock(self, obj):
        """Display stock status with color indicator"""
        if obj.in_stock:
            return '✅ In Stock'
        return '❌ Out of Stock'
    in_stock.short_description = 'Stock Status'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Manage product images separately if needed.
    Usually managed via Product admin inline.
    """
    list_display = ['product', 'image', 'order']
    list_filter = ['product']
    search_fields = ['product__name', 'alt_text']
