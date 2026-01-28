from django.db import models


class ShippingRate(models.Model):
    """
    Shipping rates for different regions in Bulgaria.
    """
    region = models.CharField(
        max_length=100,
        unique=True,
        help_text="Region name in Bulgarian (e.g., София, Пловдив)"
    )
    rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Shipping cost in BGN"
    )
    is_active = models.BooleanField(default=True, help_text="Is this rate currently active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shipping Rate"
        verbose_name_plural = "Shipping Rates"
        ordering = ['region']

    def __str__(self):
        return f"{self.region} - {self.rate} BGN"

    @staticmethod
    def get_rate_for_city(city):
        """
        Get shipping rate for a given city.
        Returns default rate if city not found.
        """
        try:
            rate = ShippingRate.objects.get(region__iexact=city, is_active=True)
            return rate.rate
        except ShippingRate.DoesNotExist:
            # Return default rate if city not found
            try:
                default = ShippingRate.objects.get(region="Default", is_active=True)
                return default.rate
            except ShippingRate.DoesNotExist:
                # Fallback to 5 BGN if no rates configured
                return 5.00
