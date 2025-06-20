from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from backend.models import Category, Product, BusinessSettings
from decimal import Decimal
from PIL import Image
import io

class Command(BaseCommand):
    help = 'Create sample data for BueaDelights application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if data exists',
        )

    def handle(self, *args, **options):
        self.stdout.write('🥘 Creating sample data for BueaDelights...')
        
        # Create or update business settings
        self.create_business_settings()
        
        # Create categories
        self.create_categories(options['force'])
        
        # Create sample products
        self.create_products(options['force'])
        
        self.stdout.write(
            self.style.SUCCESS('✅ Sample data created successfully!')
        )

    def create_business_settings(self):
        """Create or update business settings"""
        settings, created = BusinessSettings.objects.get_or_create(
            pk=1,
            defaults={
                'business_name': 'BueaDelights',
                'business_description': 'Local Flavors at Your Fingertips',
                'phone': '+237699808260',
                'email': 'info@bueadelights.com',
                'address': 'Buea, Southwest Region, Cameroon',
                'operating_hours': 'Monday - Sunday: 8:00 AM - 10:00 PM',
                'delivery_fee': 1500,
                'delivery_areas': 'Buea, Limbe, Tiko, Douala',
                'is_accepting_orders': True
            }
        )
        
        if created:
            self.stdout.write('✅ Business settings created')
        else:
            self.stdout.write('✅ Business settings already exist')

    def create_categories(self, force=False):
        """Create product categories"""
        categories_data = [
            {
                'name': 'Traditional Dishes',
                'description': 'Authentic Cameroonian traditional meals prepared with local ingredients and time-honored recipes.',
            },
            {
                'name': 'Local Snacks',
                'description': 'Popular Cameroonian snacks and appetizers perfect for any time of the day.',
            },
            {
                'name': 'Beverages',
                'description': 'Fresh natural drinks and traditional beverages made from local fruits and herbs.',
            },
            {
                'name': 'Pastries & Sweets',
                'description': 'Fresh baked goods, cakes, and traditional Cameroonian sweets.',
            },
            {
                'name': 'Seasonings & Spices',
                'description': 'Traditional Cameroonian spices and seasoning blends for authentic flavors.',
            }
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            
            if created or force:
                created_count += 1
                self.stdout.write(f'✅ Created category: {category.name}')

        self.stdout.write(f'📁 {created_count} categories processed')

    def create_products(self, force=False):
        """Create sample products"""
        # Get categories
        traditional = Category.objects.get(name='Traditional Dishes')
        snacks = Category.objects.get(name='Local Snacks')
        beverages = Category.objects.get(name='Beverages')
        pastries = Category.objects.get(name='Pastries & Sweets')
        seasonings = Category.objects.get(name='Seasonings & Spices')

        products_data = [
            # Traditional Dishes
            {
                'name': 'Ndolé with Plantain',
                'description': 'Traditional Cameroonian dish with groundnuts, vegetables, beef/fish, and aromatic spices served with sweet ripe plantain. A true taste of Cameroon!',
                'price': Decimal('3500'),
                'category': traditional,
                'is_featured': True,
                'stock_quantity': 20
            },
            {
                'name': 'Achu with Yellow Soup',
                'description': 'Traditional pounded cocoyam served with delicious yellow soup made with palm oil, herbs, and your choice of meat or fish.',
                'price': Decimal('3000'),
                'category': traditional,
                'is_featured': True,
                'stock_quantity': 15
            },
            {
                'name': 'Eru with Fufu',
                'description': 'Traditional Eru leaves cooked with groundnuts, crayfish, and meat, served with fresh fufu. A delicacy from the Southwest region.',
                'price': Decimal('3200'),
                'category': traditional,
                'is_featured': False,
                'stock_quantity': 18
            },
            {
                'name': 'Koki Beans',
                'description': 'Steamed black-eyed beans cake seasoned with traditional spices and palm oil. Wrapped in banana leaves for authentic flavor.',
                'price': Decimal('2000'),
                'category': traditional,
                'is_featured': True,
                'stock_quantity': 25
            },
            {
                'name': 'Pilé with Njamah Njamah',
                'description': 'Traditional pounded yam served with vegetables soup made with huckleberry leaves and groundnuts.',
                'price': Decimal('2800'),
                'category': traditional,
                'is_featured': False,
                'stock_quantity': 12
            },
            
            # Local Snacks
            {
                'name': 'Chin-chin',
                'description': 'Crispy fried snack cubes seasoned with nutmeg and sugar. Perfect for any time of the day. Available in small or large portions.',
                'price': Decimal('1000'),
                'category': snacks,
                'is_featured': False,
                'stock_quantity': 50
            },
            {
                'name': 'Puff-puff',
                'description': 'Sweet fried dough balls, golden and fluffy. A favorite local snack loved by all ages. Served warm and fresh.',
                'price': Decimal('500'),
                'category': snacks,
                'is_featured': True,
                'stock_quantity': 30
            },
            {
                'name': 'Plantain Chips',
                'description': 'Thinly sliced and perfectly fried plantain chips. Crispy, salty, and absolutely addictive. Made fresh daily.',
                'price': Decimal('800'),
                'category': snacks,
                'is_featured': False,
                'stock_quantity': 40
            },
            {
                'name': 'Groundnut Cake (Kulikuli)',
                'description': 'Traditional peanut cake seasoned with local spices. Crunchy and flavorful, perfect for snacking.',
                'price': Decimal('1200'),
                'category': snacks,
                'is_featured': False,
                'stock_quantity': 35
            },
            {
                'name': 'Beignets (Boflot)',
                'description': 'Soft and sweet fried doughnuts, perfect with tea or coffee. Made fresh every morning.',
                'price': Decimal('600'),
                'category': snacks,
                'is_featured': False,
                'stock_quantity': 25
            },
            
            # Beverages
            {
                'name': 'Bissap Juice',
                'description': 'Refreshing hibiscus flower drink, rich in vitamin C and antioxidants. Available with ginger, mint, or plain.',
                'price': Decimal('800'),
                'category': beverages,
                'is_featured': True,
                'stock_quantity': 25
            },
            {
                'name': 'Ginger Beer',
                'description': 'Spicy and refreshing homemade ginger beer. Natural and energizing, perfect for hot days.',
                'price': Decimal('900'),
                'category': beverages,
                'is_featured': False,
                'stock_quantity': 20
            },
            {
                'name': 'Baobab Juice',
                'description': 'Exotic baobab fruit juice, creamy and nutritious. Rich in vitamin C and natural minerals.',
                'price': Decimal('1000'),
                'category': beverages,
                'is_featured': True,
                'stock_quantity': 15
            },
            {
                'name': 'Palm Wine',
                'description': 'Fresh palm wine tapped daily. Sweet and naturally fermented. Available in small or large calabash.',
                'price': Decimal('1500'),
                'category': beverages,
                'is_featured': False,
                'stock_quantity': 10
            },
            {
                'name': 'Soya Milk',
                'description': 'Fresh homemade soya milk, creamy and nutritious. Flavored with vanilla or plain.',
                'price': Decimal('700'),
                'category': beverages,
                'is_featured': False,
                'stock_quantity': 20
            },
            
            # Pastries & Sweets
            {
                'name': 'Meat Pie',
                'description': 'Flaky pastry filled with seasoned minced meat, vegetables, and spices. Baked fresh daily.',
                'price': Decimal('1500'),
                'category': pastries,
                'is_featured': True,
                'stock_quantity': 15
            },
            {
                'name': 'Sausage Roll',
                'description': 'Golden pastry wrapped around seasoned sausage. Perfect for breakfast or snack.',
                'price': Decimal('1200'),
                'category': pastries,
                'is_featured': False,
                'stock_quantity': 20
            },
            {
                'name': 'Coconut Cake',
                'description': 'Moist coconut cake made with fresh grated coconut and traditional ingredients.',
                'price': Decimal('2500'),
                'category': pastries,
                'is_featured': True,
                'stock_quantity': 8
            },
            {
                'name': 'Banana Bread',
                'description': 'Sweet and moist banana bread made with local bananas and traditional spices.',
                'price': Decimal('2000'),
                'category': pastries,
                'is_featured': False,
                'stock_quantity': 10
            },
            
            # Seasonings & Spices
            {
                'name': 'Traditional Spice Mix',
                'description': 'Authentic Cameroonian spice blend including country onions, white pepper, and traditional herbs.',
                'price': Decimal('2000'),
                'category': seasonings,
                'is_featured': False,
                'stock_quantity': 30
            },
            {
                'name': 'Palm Oil (1 Liter)',
                'description': 'Pure red palm oil extracted traditionally. Essential for authentic Cameroonian cooking.',
                'price': Decimal('3000'),
                'category': seasonings,
                'is_featured': True,
                'stock_quantity': 25
            },
            {
                'name': 'Dried Fish Mix',
                'description': 'Assorted dried fish including stockfish and local varieties. Perfect for traditional soups.',
                'price': Decimal('2500'),
                'category': seasonings,
                'is_featured': False,
                'stock_quantity': 20
            }
        ]

        created_count = 0
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )
            
            if created or force:
                # Create a simple placeholder image
                self.create_placeholder_image(product)
                created_count += 1
                self.stdout.write(f'✅ Created product: {product.name}')

        self.stdout.write(f'🍽️ {created_count} products processed')

    def create_placeholder_image(self, product):
        """Create a simple placeholder image for products"""
        try:
            # Create a simple colored rectangle as placeholder
            img = Image.new('RGB', (400, 300), color='#228B22')
            
            # Save to BytesIO
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # Save to product
            image_file = ContentFile(img_buffer.read())
            product.image.save(
                f'{product.slug}_placeholder.jpg',
                image_file,
                save=True
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not create image for {product.name}: {e}')
            )