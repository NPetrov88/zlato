from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Assign bottle mockup image to all products'

    def handle(self, *args, **kwargs):
        # Update all products to use the bottle mockup
        updated = Product.objects.update(image='products/zlato-bottle-mockup.png')

        self.stdout.write(self.style.SUCCESS(f'Successfully assigned bottle image to {updated} products'))
