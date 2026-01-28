from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Populate database with ZLATO products'

    def handle(self, *args, **kwargs):
        # Delete existing products
        Product.objects.all().delete()

        # ZLATO Finishing Oil
        finishing = Product.objects.create(
            name="ZLATO Finishing",
            name_bg="ЗЛАТО Финиш",
            slug="zlato-finishing",
            product_type="finishing",
            short_description="Premium extra virgin olive oil for drizzling",
            short_description_bg="Премиум екстра върджин зехтин за поливане",
            description="""The star of your kitchen. ZLATO Finishing is a premium extra virgin olive oil
sourced from the finest groves in Greece. Its robust flavor and silky texture make it perfect for
finishing dishes, drizzling over salads, or dipping with fresh bread.

Our squeezable bottle gives you complete control - from a delicate drizzle to a generous pour.
No more awkward bottle tilting or oil spills. Just precision and perfection, every time.

Cold-pressed, unfiltered, and packed with flavor. This is olive oil, reimagined.""",
            description_bg="""Звездата на вашата кухня. ЗЛАТО Финиш е премиум екстра върджин зехтин,
добит от най-добрите маслинови горички в Гърция. Неговият богат вкус и копринена текстура го правят
перфектен за завършване на ястия, поливане на салати или потапяне със свеж хляб.

Нашата стискаща се бутилка ви дава пълен контрол - от деликатно поливане до щедро наливане.
Няма повече неудобно накланяне на бутилки или разливане на зехтин. Само прецизност и съвършенство, всеки път.

Студено пресован, нефилтриран и пълен с вкус. Това е зехтин, преосмислен.""",
            price=28.00,
            inventory=50,
            is_active=True,
            featured=True
        )

        # ZLATO Cooking Oil
        cooking = Product.objects.create(
            name="ZLATO Cooking",
            name_bg="ЗЛАТО Готвене",
            slug="zlato-cooking",
            product_type="cooking",
            short_description="Premium extra virgin olive oil for high-heat cooking",
            short_description_bg="Премиум екстра върджин зехтин за готвене на високи температури",
            description="""Your everyday cooking hero. ZLATO Cooking is the same premium Greek extra virgin olive oil,
optimized for high-heat cooking. Sauté, roast, fry - this oil can handle it all while adding incredible flavor.

The squeezable bottle makes cooking effortless. Need a quick splash for the pan? Done. Want to coat vegetables
before roasting? Easy. ZLATO Cooking brings restaurant-quality results to your home kitchen.

High smoke point, exceptional flavor, and the control you need. Cook like a pro, squeeze like a boss.""",
            description_bg="""Вашият ежедневен герой в кухнята. ЗЛАТО Готвене е същият премиум гръцки екстра върджин зехтин,
оптимизиран за готвене на високи температури. Задушавайте, печете, пържете - това масло може да се справи с всичко,
като добавя невероятен вкус.

Стискащата се бутилка прави готвенето лесно. Нуждаете се от бърз плисък за тигана? Готово. Искате да покриете
зеленчуци преди печене? Лесно. ЗЛАТО Готвене носи ресторантско качество в домашната ви кухня.

Висока точка на димене, изключителен вкус и контролът, от който се нуждаете. Гответе като професионалист.""",
            price=26.00,
            inventory=50,
            is_active=True,
            featured=True
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {Product.objects.count()} products'))
        self.stdout.write(f'- {finishing.name}: {finishing.price} BGN')
        self.stdout.write(f'- {cooking.name}: {cooking.price} BGN')
