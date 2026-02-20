from django.db import migrations


def seed_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')

    products = [
        {
            'id': 1,
            'name': 'ZLATO Finishing',
            'name_bg': 'ЗЛАТО Финиш',
            'slug': 'zlato-finishing',
            'product_type': 'finishing',
            'short_description': 'Premium extra virgin olive oil for drizzling',
            'short_description_bg': 'Премиум екстра върджин зехтин за поливане',
            'description': (
                "The star of your kitchen. ZLATO Finishing is a premium extra virgin olive oil\n"
                "sourced from the finest groves in Greece. Its robust flavor and silky texture make it perfect for\n"
                "finishing dishes, drizzling over salads, or dipping with fresh bread.\n\n"
                "Our squeezable bottle gives you complete control - from a delicate drizzle to a generous pour.\n"
                "No more awkward bottle tilting or oil spills. Just precision and perfection, every time.\n\n"
                "Cold-pressed, unfiltered, and packed with flavor. This is olive oil, reimagined."
            ),
            'description_bg': (
                "Звездата на вашата кухня. ЗЛАТО Финиш е премиум екстра върджин зехтин,\n"
                "добит от най-добрите маслинови горички в Гърция. Неговият богат вкус и копринена текстура го правят\n"
                "перфектен за завършване на ястия, поливане на салати или потапяне със свеж хляб.\n\n"
                "Нашата стискаща се бутилка ви дава пълен контрол - от деликатно поливане до щедро наливане.\n"
                "Няма повече неудобно накланяне на бутилки или разливане на зехтин. Само прецизност и съвършенство, всеки път.\n\n"
                "Студено пресован, нефилтриран и пълен с вкус. Това е зехтин, преосмислен."
            ),
            'price': '28.00',
            'inventory': 50,
            'image': 'products/zlato-finishing-purple.png',
            'is_active': True,
            'featured': True,
        },
        {
            'id': 2,
            'name': 'ZLATO Cooking',
            'name_bg': 'ЗЛАТО Готвене',
            'slug': 'zlato-cooking',
            'product_type': 'cooking',
            'short_description': 'Premium extra virgin olive oil for high-heat cooking',
            'short_description_bg': 'Премиум екстра върджин зехтин за готвене на високи температури',
            'description': (
                "Your everyday cooking hero. ZLATO Cooking is the same premium Greek extra virgin olive oil,\n"
                "optimized for high-heat cooking. Sauté, roast, fry - this oil can handle it all while adding incredible flavor.\n\n"
                "The squeezable bottle makes cooking effortless. Need a quick splash for the pan? Done. Want to coat vegetables\n"
                "before roasting? Easy. ZLATO Cooking brings restaurant-quality results to your home kitchen.\n\n"
                "High smoke point, exceptional flavor, and the control you need. Cook like a pro, squeeze like a boss."
            ),
            'description_bg': (
                "Вашият ежедневен герой в кухнята. ЗЛАТО Готвене е същият премиум гръцки екстра върджин зехтин,\n"
                "оптимизиран за готвене на високи температури. Задушавайте, печете, пържете - това масло може да се справи с всичко,\n"
                "като добавя невероятен вкус.\n\n"
                "Стискащата се бутилка прави готвенето лесно. Нуждаете се от бърз плисък за тигана? Готово. Искате да покриете\n"
                "зеленчуци преди печене? Лесно. ЗЛАТО Готвене носи ресторантско качество в домашната ви кухня.\n\n"
                "Висока точка на димене, изключителен вкус и контролът, от който се нуждаете. Гответе като професионалист."
            ),
            'price': '26.00',
            'inventory': 50,
            'image': 'products/zlato-bottle-mockup.png',
            'is_active': True,
            'featured': True,
        },
        {
            'id': 3,
            'name': 'ZLATO Complete Set',
            'name_bg': 'ZLATO Комплект',
            'slug': 'zlato-complete-set',
            'product_type': 'bundle',
            'short_description': 'Premium extra virgin olive oil gift set with salt & pepper',
            'short_description_bg': 'Подаръчен комплект с екстра върджин зехтин, сол и пипер',
            'description': (
                "The ultimate ZLATO experience. This luxury gift set includes two bottles of our premium extra virgin "
                "olive oil, plus artisanal salt and pepper grinders. Perfect for gifting or treating yourself."
            ),
            'description_bg': (
                "Най-добрият ZLATO опит. Този луксозен подаръчен комплект включва две бутилки наше премиум екстра върджин "
                "зехтин, плюс артизански мелнички за сол и пипер. Перфектен за подарък или за вас."
            ),
            'price': '68.00',
            'inventory': 50,
            'image': 'products/zlato-complete-set.png',
            'is_active': True,
            'featured': False,
        },
    ]

    for product_data in products:
        Product.objects.update_or_create(
            slug=product_data.pop('slug'),
            defaults=product_data,
        )


def reverse_seed(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.filter(slug__in=[
        'zlato-finishing', 'zlato-cooking', 'zlato-complete-set'
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_product_options_product_description_bg_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_products, reverse_seed),
    ]
