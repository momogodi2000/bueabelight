#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting BueaDelights build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies and build CSS (if package.json exists)
if [ -f "package.json" ]; then
    echo "🎨 Installing Node.js dependencies and building CSS..."
    npm install
    npm run build-css-prod || echo "⚠️ CSS build failed, continuing..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()

# Create admin users
admin_users = [
    {
        'username': 'admin',
        'email': 'admin@bueadelights.com',
        'password': 'BueaDelights2024!',
        'first_name': 'Admin',
        'last_name': 'User'
    },
    {
        'username': 'folefack_caroline',
        'email': 'caroline@bueadelights.com', 
        'password': 'Caroline2024!',
        'first_name': 'Caroline',
        'last_name': 'Folefack'
    },
    {
        'username': 'momo_godi_yvan',
        'email': 'yvan@bueadelights.com',
        'password': 'Yvan2024!', 
        'first_name': 'Yvan',
        'last_name': 'Momo Godi'
    },
    {
        'username': 'momo_marlyse',
        'email': 'marlyse@bueadelights.com',
        'password': 'Marlyse2024!',
        'first_name': 'Marlyse', 
        'last_name': 'Momo'
    }
]

for user_data in admin_users:
    if not User.objects.filter(username=user_data['username']).exists():
        user = User.objects.create_superuser(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        print(f"✅ Created superuser: {user.username}")
    else:
        print(f"✅ Superuser {user_data['username']} already exists")
EOF

# Create business settings and sample data
echo "🏪 Setting up business configuration and sample data..."
python manage.py shell << 'EOF'
# Create business settings
try:
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
except ImportError:
    print("⚠️ BusinessSettings model not found, skipping...")
except Exception as e:
    print(f"⚠️ Error creating business settings: {e}")

# Create sample categories and products
try:
    from backend.models import Category, Product
    from decimal import Decimal

    # Create categories
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

    # Create sample products
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

except ImportError:
    print("⚠️ Product models not found, skipping sample data...")
except Exception as e:
    print(f"⚠️ Error creating sample data: {e}")
EOF

echo "✅ Build process completed successfully!"
echo "🎉 BueaDelights is ready for deployment!"
echo ""
echo "📋 Deployment Summary:"
echo "- Python dependencies installed"
echo "- Static files collected"
echo "- Database migrations applied"
echo "- Super admin users created"
echo "- Business settings configured"
echo "- Sample data created"
echo ""
echo "🔑 Admin Access:"
echo "- URL: /admin/"
echo "- Users: admin, folefack_caroline, momo_godi_yvan, momo_marlyse"
echo "- Check logs for passwords or change them immediately!"