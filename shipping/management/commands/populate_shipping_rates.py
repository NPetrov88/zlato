from django.core.management.base import BaseCommand
from shipping.models import ShippingRate


class Command(BaseCommand):
    help = 'Populate default shipping rates for Bulgaria'

    def handle(self, *args, **kwargs):
        # Define shipping rates for major Bulgarian cities
        rates = [
            ('София', 5.00),  # Sofia
            ('Пловдив', 6.00),  # Plovdiv
            ('Варна', 7.00),  # Varna
            ('Бургас', 7.00),  # Burgas
            ('Русе', 7.00),  # Ruse
            ('Стара Загора', 6.50),  # Stara Zagora
            ('Плевен', 6.50),  # Pleven
            ('Добрич', 7.50),  # Dobrich
            ('Default', 8.00),  # Default for other cities
        ]

        created_count = 0
        updated_count = 0

        for region, rate in rates:
            obj, created = ShippingRate.objects.update_or_create(
                region=region,
                defaults={'rate': rate, 'is_active': True}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed shipping rates: {created_count} created, {updated_count} updated'
            )
        )
