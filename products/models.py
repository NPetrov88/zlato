from django.db import models


class Product(models.Model):
    """
    Represents a product in the ZLATO store.
    High-quality Greek olive oil in squeezable bottles for the Bulgarian market.
    Supports bilingual content (English + Bulgarian).
    """
    PRODUCT_TYPE_CHOICES = [
        ('finishing', 'Finishing Oil'),
        ('cooking', 'Cooking Oil'),
        ('bundle', 'Gift Box'),
    ]

    # Basic Information (English)
    name = models.CharField(max_length=200, help_text="Product name in English (e.g., 'ZLATO Finishing')")
    name_bg = models.CharField(max_length=200, help_text="Product name in Bulgarian", blank=True)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the name")

    # Product Type
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='finishing',
        help_text="Type of product"
    )

    # Descriptions (Bilingual)
    short_description = models.CharField(max_length=255, help_text="Short tagline in English", blank=True)
    short_description_bg = models.CharField(max_length=255, help_text="Short tagline in Bulgarian", blank=True)
    description = models.TextField(help_text="Full product description in English")
    description_bg = models.TextField(help_text="Full product description in Bulgarian", blank=True)

    # Pricing & Inventory
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in BGN (Bulgarian Lev)")
    inventory = models.IntegerField(default=0, help_text="Stock quantity")

    # Main Image
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Main product image")

    # Display Options
    is_active = models.BooleanField(default=True, help_text="Show this product on the website?")
    featured = models.BooleanField(default=False, help_text="Show on homepage?")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', 'name']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        """Check if product is in stock"""
        return self.inventory > 0


class ProductImage(models.Model):
    """
    Additional images for products.
    Allows multiple photos per product for galleries.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/', help_text="Additional product image")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for SEO")
    order = models.IntegerField(default=0, help_text="Display order (0 = first)")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"
