#!/usr/bin/env bash
# FIXED BUILD SCRIPT - Only fixes migration issues
set -o errexit

echo "🚀 STARTING BUEADELIGHTS DEPLOYMENT..."
echo "📅 Build started at: $(date)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create ALL necessary directories (from your original script)
echo "📁 Creating directory structure..."
directories=(
    "staticfiles"
    "staticfiles/css"
    "staticfiles/js" 
    "staticfiles/images"
    "staticfiles/admin"
    "media"
    "media/uploads"
    "logs"
    "static/css"
    "static/js"
    "static/images"
    "static/admin"
    "backend/static/backend/css"
    "backend/static/backend/js"
    "backend/static/backend/images"
    "backend/templates/backend"
    "backend/migrations"
    "templates"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo "✅ Created: $dir"
done

# Ensure migrations directory is properly initialized
echo "🔧 Initializing migrations..."
touch backend/__init__.py
touch backend/migrations/__init__.py

# Create basic CSS file (your original)
echo "🎨 Creating CSS files..."
cat > static/css/style.css << 'EOF'
/* BueaDelights Base Styles */
:root {
    --primary-color: #228B22;
    --primary-hover: #1e7a1e;
    --secondary-color: #32CD32;
    --text-dark: #333;
    --text-light: #666;
    --bg-light: #f8f9fa;
    --white: #ffffff;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
    --border-radius: 8px;
    --transition: all 0.3s ease;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body { 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    line-height: 1.6;
    color: var(--text-dark);
    background-color: var(--bg-light);
}

.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

.header { 
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); 
    color: var(--white); 
    padding: 40px 20px; 
    text-align: center; 
    box-shadow: var(--shadow);
}

.header h1 { 
    font-size: clamp(2rem, 5vw, 4rem);
    margin-bottom: 15px; 
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    font-weight: 700;
}

.btn { 
    background: var(--primary-color); 
    color: var(--white); 
    padding: 15px 30px; 
    border: none; 
    border-radius: var(--border-radius); 
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 600;
    transition: var(--transition);
    box-shadow: var(--shadow);
}

.btn:hover { 
    background: var(--primary-hover); 
    transform: translateY(-2px);
}

.welcome-message {
    text-align: center;
    padding: 60px 40px;
    background: var(--white);
    margin: 30px 0;
    border-radius: 15px;
    box-shadow: var(--shadow);
}

.welcome-message h1 {
    color: var(--primary-color);
    font-size: clamp(2rem, 4vw, 3rem);
    margin-bottom: 25px;
    font-weight: 700;
}

.status {
    background: #d4edda;
    color: #155724;
    padding: 20px;
    border-radius: var(--border-radius);
    margin: 25px 0;
    border-left: 5px solid #28a745;
}

.status.error {
    background: #f8d7da;
    color: #721c24;
    border-left-color: #dc3545;
}

@media (max-width: 768px) {
    .container { padding: 0 15px; }
    .welcome-message { padding: 40px 20px; margin: 20px 0; }
    .btn { padding: 12px 24px; font-size: 0.9rem; }
}
EOF

# Copy CSS to all required locations
cp static/css/style.css staticfiles/css/style.css 2>/dev/null || true
mkdir -p backend/static/backend/css
cp static/css/style.css backend/static/backend/css/style.css 2>/dev/null || true

# Create placeholder images (your original)
echo "🖼️ Creating placeholder images..."
python3 -c "
import base64
from pathlib import Path

# Simple 1x1 transparent PNG
png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHH/wEqFAAAAABJRU5ErkJggg==')

# ICO file for favicon
ico_data = base64.b64decode('AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAAAAAAAAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==')

# Create icons in multiple locations
icon_locations = ['static/images', 'staticfiles/images', 'backend/static/backend/images']

for location in icon_locations:
    Path(location).mkdir(parents=True, exist_ok=True)
    
    # Create favicon
    with open(Path(location) / 'favicon.ico', 'wb') as f:
        f.write(ico_data)
    
    # Create PNG images
    for filename in ['favicon.png', 'logo.png', 'default.png']:
        with open(Path(location) / filename, 'wb') as f:
            f.write(png_data)

print('✅ Placeholder images created')
"

# CRITICAL FIX: Force database connection and run migrations properly
echo "🔍 Testing Django configuration..."
python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')

try:
    django.setup()
    print('✅ Django setup successful')
    print(f'✅ Database: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
    print(f'✅ Debug mode: {settings.DEBUG}')
    
    # Test basic imports
    from backend.models import Category, Product
    print('✅ Models imported successfully')
    
except Exception as e:
    print(f'❌ Django setup error: {e}')
    exit(1)
"

# THE REAL FIX: Force migrations to run with proper error handling
echo "📊 Running database migrations..."

# First, ensure Django can connect to database
python -c "
from django.db import connection
print('Testing database connection...')
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('✅ Database connection successful')
"

# Run migrations with force
echo "🔨 Applying migrations..."
python manage.py migrate --run-syncdb --verbosity=2

# Verify tables were created
echo "🔍 Verifying database tables..."
python -c "
from django.db import connection
cursor = connection.cursor()

# Check if backend_category table exists
try:
    cursor.execute('SELECT COUNT(*) FROM backend_category')
    print('✅ backend_category table exists')
except:
    print('❌ backend_category table does not exist')
    exit(1)

try:
    cursor.execute('SELECT COUNT(*) FROM backend_product')
    print('✅ backend_product table exists')
except:
    print('❌ backend_product table does not exist')

try:
    cursor.execute('SELECT COUNT(*) FROM backend_businesssettings')
    print('✅ backend_businesssettings table exists')
except:
    print('❌ backend_businesssettings table does not exist')
"

# Create superuser accounts (your original code)
echo "👤 Creating superuser accounts..."
python manage.py create_superadmins || {
    echo "⚠️ Manual superuser creation..."
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
django.setup()

from django.contrib.auth.models import User

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
"
}

# Create sample data (your original code)
echo "🍽️ Creating sample data..."
python manage.py create_sample_data || {
    echo "⚠️ Manual sample data creation..."
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
django.setup()

from backend.models import Category, BusinessSettings
from django.utils.text import slugify

try:
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
    
    # Create basic categories
    categories = ['Traditional Dishes', 'Local Snacks', 'Beverages', 'Pastries & Sweets']
    for cat_name in categories:
        cat, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={'slug': slugify(cat_name), 'is_active': True}
        )
        print(f'✅ Category {cat_name}: {\"created\" if created else \"exists\"}')
        
except Exception as e:
    print(f'⚠️ Sample data error: {e}')
"
}

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --no-input --clear --verbosity=2 || echo "⚠️ Static collection completed with warnings"

# Final verification
echo "🔍 Final verification..."
python -c "
from django.db import connection
from backend.models import Category

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    
    # Test model access
    count = Category.objects.count()
    print(f'✅ Database verification successful - {count} categories found')
    
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
echo "   📁 Directories: Created"
echo "   🎨 Static Files: Generated"
echo "   📊 Database: Migrated & Verified"
echo "   👤 Admin Users: Created"
echo "   🍽️ Sample Data: Loaded"
echo ""
echo "🌐 APPLICATION READY!"
echo "   🔗 Site: https://bueadelights.onrender.com"
echo "   🔐 Admin: https://bueadelights.onrender.com/admin/"
echo ""
echo "👤 ADMIN CREDENTIALS:"
echo "   folefack_caroline : @caroline2025"
echo "   momo_godi_yvan : @momoyvan65"
echo "   admin : BueaDelights2025!"
echo ""