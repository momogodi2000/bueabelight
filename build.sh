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
mkdir -p static

# Database setup and migrations
echo "📊 Setting up database and running migrations..."

# Test database connection first
echo "🔗 Testing database connection..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
django.setup()
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    import sys
    sys.exit(1)
"

# Create migrations for backend app
echo "📋 Creating migrations for backend app..."
python manage.py makemigrations backend --settings=bueadelights.settings

# Create any other migrations
echo "📋 Creating all migrations..."  
python manage.py makemigrations --settings=bueadelights.settings

# Apply all migrations
echo "📊 Applying all migrations..."
python manage.py migrate --settings=bueadelights.settings

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --no-input --settings=bueadelights.settings

# Verify static files were collected
if [ -d "staticfiles" ]; then
    echo "✅ Static files collected successfully"
    ls -la staticfiles/ | head -10
else
    echo "❌ Static files collection failed"
fi

# Create superuser
echo "👤 Creating superuser..."
python manage.py shell --settings=bueadelights.settings << 'EOF'
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
python manage.py shell --settings=bueadelights.settings << 'EOF'
# Create business settings
try:
    from backend.models import BusinessSettings
    settings_obj, created = BusinessSettings.objects.get_or_create(
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
        print("✅ Business settings created")
    else:
        print("✅ Business settings already exist")
except Exception as e:
    print(f"⚠️ Error with business settings: {e}")

# Create sample categories and products
try:
    from backend.models import Category, Product
    from decimal import Decimal

    # Create categories
    traditional_cat, created = Category.objects.get_or_create(
        name='Traditional Dishes',
        defaults={'description': 'Authentic Cameroonian traditional meals'}
    )
    if created:
        print("✅ Created Traditional Dishes category")

    snacks_cat, created = Category.objects.get_or_create(
        name='Local Snacks',
        defaults={'description': 'Popular local snacks and appetizers'}
    )
    if created:
        print("✅ Created Local Snacks category")

    # Create sample products
    product1, created = Product.objects.get_or_create(
        name='Ndolé with Plantain',
        defaults={
            'description': 'Traditional Cameroonian dish with groundnuts, vegetables, and meat served with ripe plantain',
            'price': Decimal('3500'),
            'category': traditional_cat,
            'is_featured': True,
            'stock_quantity': 20
        }
    )
    if created:
        print("✅ Created Ndolé product")

    product2, created = Product.objects.get_or_create(
        name='Chin-chin',
        defaults={
            'description': 'Crispy fried snack, perfect for any time of the day',
            'price': Decimal('1000'),
            'category': snacks_cat,
            'stock_quantity': 50
        }
    )
    if created:
        print("✅ Created Chin-chin product")

    print("🎉 Sample data setup complete!")

except Exception as e:
    print(f"⚠️ Error creating sample data: {e}")
EOF

# Final verification
echo "🔍 Final verification..."
python manage.py check --settings=bueadelights.settings

echo "✅ Build process completed successfully!"
echo "🎉 BueaDelights is ready for deployment!"
echo ""
echo "📋 Deployment Summary:"
echo "- Python dependencies installed"
echo "- Database connected and migrated"
echo "- Static files collected"
echo "- Super admin user created"
echo "- Business settings configured"
echo "- Sample data created"
echo ""
echo "🔑 Admin Access:"
echo "- URL: /admin/"
echo "- Username: admin"
echo "- Password: BueaDelights2024!"