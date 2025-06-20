#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting BueaDelights build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies and build CSS
echo "🎨 Installing Node.js dependencies and building CSS..."
npm install
npm run build-css-prod

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --no-input --settings=bueadelights.settings_prod

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate --settings=bueadelights.settings_prod

# Create super admin users
echo "👤 Creating super admin users..."
python manage.py create_superadmins --settings=bueadelights.settings_prod

# Create business settings if not exists
echo "🏪 Setting up business configuration..."
python manage.py shell --settings=bueadelights.settings_prod << EOF
from backend.models import BusinessSettings
if not BusinessSettings.objects.exists():
    BusinessSettings.objects.create(
        business_name='BueaDelights',
        business_description='Local Flavors at Your Fingertips',
        phone='+237699808260',
        email='info@bueadelights.com',
        address='Buea, Southwest Region, Cameroon',
        operating_hours='Monday - Sunday: 8:00 AM - 10:00 PM',
        delivery_fee=1500,
        delivery_areas='Buea, Limbe, Tiko, Douala',
        is_accepting_orders=True
    )
    print("✅ Business settings created")
else:
    print("✅ Business settings already exist")
EOF

# Create sample data for demonstration (optional)
echo "🥘 Creating sample data..."
python manage.py shell --settings=bueadelights.settings_prod << EOF
from backend.models import Category, Product
from decimal import Decimal

# Create categories if they don't exist
categories_data = [
    {
        'name': 'Traditional Dishes',
        'description': 'Authentic Cameroonian traditional meals'
    },
    {
        'name': 'Local Snacks',
        'description': 'Popular local snacks and appetizers'
    },
    {
        'name': 'Beverages',
        'description': 'Fresh local drinks and beverages'
    },
    {
        'name': 'Pastries',
        'description': 'Fresh baked goods and pastries'
    }
]

for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"✅ Created category: {category.name}")

# Create sample products if they don't exist
traditional_cat = Category.objects.get(name='Traditional Dishes')
snacks_cat = Category.objects.get(name='Local Snacks')
beverages_cat = Category.objects.get(name='Beverages')

products_data = [
    {
        'name': 'Ndolé with Plantain',
        'description': 'Traditional Cameroonian dish with groundnuts, vegetables, and meat served with ripe plantain',
        'price': Decimal('3500'),
        'category': traditional_cat,
        'is_featured': True,
        'stock_quantity': 20
    },
    {
        'name': 'Achu with Yellow Soup',
        'description': 'Traditional pounded cocoyam served with delicious yellow soup',
        'price': Decimal('3000'),
        'category': traditional_cat,
        'is_featured': True,
        'stock_quantity': 15
    },
    {
        'name': 'Chin-chin',
        'description': 'Crispy fried snack, perfect for any time of the day',
        'price': Decimal('1000'),
        'category': snacks_cat,
        'stock_quantity': 50
    },
    {
        'name': 'Puff-puff',
        'description': 'Sweet fried dough balls, a favorite local snack',
        'price': Decimal('500'),
        'category': snacks_cat,
        'stock_quantity': 30
    },
    {
        'name': 'Bissap Juice',
        'description': 'Refreshing hibiscus flower drink',
        'price': Decimal('800'),
        'category': beverages_cat,
        'stock_quantity': 25
    }
]

for prod_data in products_data:
    product, created = Product.objects.get_or_create(
        name=prod_data['name'],
        defaults=prod_data
    )
    if created:
        print(f"✅ Created product: {product.name}")

print("🎉 Sample data setup complete!")
EOF

# Optimize database
echo "🔧 Optimizing database..."
python manage.py shell --settings=bueadelights.settings_prod << EOF
from django.db import connection
cursor = connection.cursor()
cursor.execute("VACUUM;")
print("✅ Database optimized")
EOF

echo "✅ Build process completed successfully!"
echo "🎉 BueaDelights is ready for deployment!"
echo ""
echo "📋 Deployment Summary:"
echo "- Python dependencies installed"
echo "- CSS built and optimized"
echo "- Static files collected"
echo "- Database migrations applied"
echo "- Super admin users created"
echo "- Business settings configured"
echo "- Sample data created"
echo ""
echo "🔑 Admin Access:"
echo "- URL: /admin/"
echo "- Users: folefack_caroline, momo_godi_yvan, momo_marlyse"
echo "- Default passwords set (change immediately!)"
echo ""
echo "🌐 Application URLs:"
echo "- Homepage: /"
echo "- Menu: /menu/"
echo "- Cart: /cart/"
echo "- Contact: /contact/"
echo "- Catering: /catering/"