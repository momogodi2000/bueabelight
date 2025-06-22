#!/usr/bin/env bash
# FINAL BUILD SCRIPT FIX - Forces PostgreSQL migrations
set -o errexit

echo "🚀 STARTING BUEADELIGHTS DEPLOYMENT..."
echo "📅 Build started at: $(date)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p staticfiles media static/css static/js static/images backend/migrations

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
EOF

# Copy CSS to staticfiles
cp static/css/style.css staticfiles/ 2>/dev/null || true

# DEBUG: Check database configuration
echo "🔍 Checking database configuration..."
python -c "
import os
from decouple import config
print(f'DATABASE_URL exists: {bool(config(\"DATABASE_URL\", default=None))}')
print(f'RENDER env var: {bool(os.environ.get(\"RENDER\"))}')
print(f'DATABASE_URL preview: {config(\"DATABASE_URL\", default=\"Not set\")[:50]}...')
"

# CRITICAL: Test Django setup and database connection
echo "🔧 Testing Django setup..."
python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
django.setup()

print(f'✅ Django settings loaded')
print(f'✅ Database engine: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'✅ Database name: {settings.DATABASES[\"default\"].get(\"NAME\", \"N/A\")}')

# Test database connection
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        result = cursor.fetchone()
        print(f'✅ Database connected: {result[0][:50]}...')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    raise
"

# FORCE migrations to run
echo "📊 Running database migrations (FORCED)..."
python manage.py makemigrations backend --verbosity=2
python manage.py migrate --verbosity=2

# Verify tables were created in PostgreSQL
echo "🔍 Verifying PostgreSQL tables..."
python -c "
from django.db import connection
cursor = connection.cursor()

# List all tables
cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\")
tables = cursor.fetchall()
print(f'✅ Found {len(tables)} tables in PostgreSQL')

# Check specific tables
required_tables = ['backend_category', 'backend_product', 'backend_businesssettings']
for table in required_tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'✅ {table}: {count} records')
    except Exception as e:
        print(f'❌ {table}: ERROR - {e}')
        exit(1)
"

# Create sample data
echo "🍽️ Creating sample data..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
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

# Final verification that everything works
echo "🔍 Final verification..."
python -c "
from django.db import connection
from backend.models import Category, BusinessSettings

# Test database and models
try:
    cat_count = Category.objects.count()
    bs_count = BusinessSettings.objects.count()
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()[0]
    
    print(f'✅ Final verification successful:')
    print(f'   - Database: PostgreSQL ({db_version[:30]}...)')
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
echo "   🔗 Site: https://bueadelights.onrender.com"
echo "   🔐 Admin: https://bueadelights.onrender.com/admin/"
echo ""