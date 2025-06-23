#!/usr/bin/env bash
# BUILD SCRIPT - Manual PostgreSQL Configuration
set -o errexit

echo "🚀 STARTING BUEADELIGHTS DEPLOYMENT..."
echo "📅 Build started at: $(date)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p staticfiles media static/css backend/migrations

# Ensure migrations directory is properly initialized
touch backend/__init__.py
touch backend/migrations/__init__.py

# Create basic CSS
echo "🎨 Creating CSS..."
cat > static/css/style.css << 'EOF'
/* BueaDelights Styles */
:root { --primary-color: #228B22; --secondary-color: #32CD32; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.btn { background: var(--primary-color); color: white; padding: 15px 30px; border: none; border-radius: 8px; }
.welcome-message { text-align: center; padding: 60px 40px; background: white; margin: 30px 0; border-radius: 15px; }
EOF

# Copy CSS to staticfiles
cp static/css/style.css staticfiles/ 2>/dev/null || true

# Show database configuration being used
echo "🔍 Database Configuration:"
echo "   Host: $DB_HOST"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Port: $DB_PORT"

# Test Django setup with production settings
echo "🔧 Testing Django setup..."
python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings_production')
django.setup()

print(f'✅ Django settings loaded: {settings.SETTINGS_MODULE}')
print(f'✅ Database engine: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'✅ Database host: {settings.DATABASES[\"default\"][\"HOST\"]}')
print(f'✅ Database name: {settings.DATABASES[\"default\"][\"NAME\"]}')
"

# Test database connection
echo "🔌 Testing database connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings_production')
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        result = cursor.fetchone()
        print(f'✅ Database connected successfully!')
        print(f'✅ PostgreSQL version: {result[0][:50]}...')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Run migrations
echo "📊 Running database migrations..."
python manage.py makemigrations backend --verbosity=2
python manage.py migrate --verbosity=2

# Verify tables were created
echo "🔍 Verifying tables..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings_production')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Check if our tables exist
tables_to_check = ['backend_category', 'backend_product', 'backend_businesssettings', 'backend_order']
for table in tables_to_check:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'✅ {table}: exists ({count} records)')
    except Exception as e:
        print(f'❌ {table}: ERROR - {e}')
        exit(1)
"

# Create sample data
echo "🍽️ Creating sample data..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings_production')
django.setup()

from backend.models import Category, BusinessSettings
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create business settings
settings, created = BusinessSettings.objects.get_or_create(
    pk=1,
    defaults={
        'business_name': 'BueaDelights',
        'business_description': 'Local Flavors at Your Fingertips',
        'phone': '+237699808260',
        'email': 'info@bueadelights.com'
    }
)
print(f'✅ Business settings: {\"created\" if created else \"exists\"}')

# Create categories
categories = ['Traditional Dishes', 'Local Snacks', 'Beverages', 'Pastries & Sweets']
for cat_name in categories:
    cat, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': slugify(cat_name), 'is_active': True}
    )
    print(f'✅ Category {cat_name}: {\"created\" if created else \"exists\"}')

# Create admin users
admins = [
    ('folefack_caroline', 'folefacvivianekokoko@gmail.com', '@caroline2025'),
    ('momo_godi_yvan', 'yvangodimomo@gmail.com', '@momoyvan65'),
    ('admin', 'admin@bueadelights.com', 'BueaDelights2025!')
]

for username, email, password in admins:
    try:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f'✅ Created superuser: {username}')
        else:
            print(f'✅ Superuser {username} already exists')
    except Exception as e:
        print(f'⚠️ Error creating {username}: {e}')

print('✅ Sample data creation completed')
"

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --no-input --verbosity=1

# Final verification
echo "🔍 Final verification..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings_production')
django.setup()

from backend.models import Category, BusinessSettings

try:
    cat_count = Category.objects.count()
    bs_count = BusinessSettings.objects.count()
    
    print(f'✅ Final verification successful:')
    print(f'   - Categories: {cat_count}')
    print(f'   - Business Settings: {bs_count}')
    
except Exception as e:
    print(f'❌ Final verification failed: {e}')
    exit(1)
"

echo ""
echo "🎉 BUILD COMPLETED SUCCESSFULLY!"
echo "============================================="
echo "📅 Completed at: $(date)"
echo ""
echo "✅ DEPLOYMENT SUMMARY:"
echo "   📦 Dependencies: Installed"
echo "   🗃️ Database: PostgreSQL Connected & Migrated"
echo "   📊 Tables: Created & Verified"
echo "   👤 Admin Users: Created"
echo "   🍽️ Sample Data: Loaded"
echo "   📄 Static Files: Collected"
echo ""
echo "🌐 APPLICATION READY!"
echo ""