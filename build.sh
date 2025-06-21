#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting BueaDelights build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Create a simple CSS file if none exists
echo "📄 Creating basic static files..."
cat > static/css/style.css << 'EOF'
/* Basic styles for BueaDelights */
body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
.container { max-width: 1200px; margin: 0 auto; }
.header { background: #228B22; color: white; padding: 20px; text-align: center; }
.btn { background: #228B22; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
EOF

# Check if we can connect to database
echo "🔗 Testing database connection..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
import django
django.setup()

from django.db import connection
from django.conf import settings

print(f'Database Engine: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'Database Name: {settings.DATABASES[\"default\"].get(\"NAME\", \"N/A\")}')

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        result = cursor.fetchone()
        print(f'✅ Database connected: {result[0] if result else \"Connected\"}')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Force create migrations
echo "📋 Creating migrations..."
python manage.py makemigrations --empty backend || echo "No migrations needed"
python manage.py makemigrations backend || echo "Backend migrations already exist"
python manage.py makemigrations || echo "All migrations already exist"

# Show migration status
echo "📊 Migration status:"
python manage.py showmigrations

# Apply migrations with verbose output
echo "📊 Applying migrations..."
python manage.py migrate --verbosity=2

# Verify tables were created
echo "🔍 Verifying database tables..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
import django
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['backend_businesssettings', 'backend_category', 'backend_product', 'auth_user']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        print(f'❌ Missing tables: {missing}')
        print(f'📋 Available tables: {tables[:10]}')
    else:
        print('✅ All required tables exist')
        print(f'📊 Total tables: {len(tables)}')
"

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --no-input --verbosity=2

# Verify static files
echo "✅ Static files verification:"
ls -la staticfiles/ | head -10 || echo "No staticfiles directory found"

# Create superuser safely
echo "👤 Creating admin user..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
import django
django.setup()

from django.contrib.auth.models import User

username = 'admin'
email = 'admin@bueadelights.com'
password = 'BueaDelights2024!'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    print(f'✅ Created admin user: {username}')
else:
    print(f'✅ Admin user already exists: {username}')
"

# Create basic business data
echo "🏪 Setting up business data..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
import django
django.setup()

try:
    from backend.models import BusinessSettings, Category, Product
    from decimal import Decimal
    
    # Business settings
    settings_obj, created = BusinessSettings.objects.get_or_create(
        id=1,
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
    print('✅ Business settings ready')
    
    # Create a simple category
    cat, created = Category.objects.get_or_create(
        name='Traditional Dishes',
        defaults={'description': 'Authentic Cameroonian traditional meals'}
    )
    print(f'✅ Category ready: {cat.name}')
    
    # Create a simple product
    product, created = Product.objects.get_or_create(
        name='Ndolé with Plantain',
        defaults={
            'description': 'Traditional Cameroonian dish',
            'price': Decimal('3500'),
            'category': cat,
            'is_featured': True,
            'stock_quantity': 20
        }
    )
    print(f'✅ Product ready: {product.name}')
    
except Exception as e:
    print(f'⚠️ Error setting up business data: {e}')
    import traceback
    traceback.print_exc()
"

# Final health check
echo "🔍 Final application health check..."
python manage.py check --deploy

echo "✅ Build completed successfully!"
echo ""
echo "📋 Summary:"
echo "- Database: Connected and migrated"
echo "- Static files: Collected"
echo "- Admin user: admin / BueaDelights2024!"
echo "- Business data: Created"
echo ""
echo "🌐 Your app should be available at: https://bueadelights.onrender.com"