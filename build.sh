#!/usr/bin/env bash
# SIMPLE, ROBUST BUILD SCRIPT FOR BUEADELIGHTS
set -o errexit

echo "🚀 STARTING BUEADELIGHTS DEPLOYMENT..."
echo "📅 Build started at: $(date)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p staticfiles
mkdir -p media
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Create basic CSS
echo "🎨 Creating basic CSS..."
cat > static/css/style.css << 'EOF'
/* BueaDelights Base Styles */
:root {
    --primary-color: #228B22;
    --secondary-color: #32CD32;
    --text-dark: #333;
    --bg-light: #f8f9fa;
    --white: #ffffff;
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
}

.welcome-message {
    text-align: center;
    padding: 60px 40px;
    background: var(--white);
    margin: 30px 0;
    border-radius: 15px;
}

.btn { 
    background: var(--primary-color); 
    color: var(--white); 
    padding: 15px 30px; 
    border: none; 
    border-radius: 8px; 
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 600;
}

.btn:hover { 
    background: #1e7a1e; 
    transform: translateY(-2px);
}
EOF

# Test Django configuration
echo "🔍 Testing Django configuration..."
python -c "
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')

try:
    django.setup()
    print('✅ Django setup successful')
    
    from django.conf import settings
    print(f'✅ Database: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
    
    from backend.models import Category
    print('✅ Models imported successfully')
    
except Exception as e:
    print(f'❌ Django setup error: {e}')
    exit(1)
"

# Make sure backend app migrations directory exists
echo "📁 Ensuring migrations directory..."
mkdir -p backend/migrations
touch backend/__init__.py
touch backend/migrations/__init__.py

# CRITICAL: Make and run migrations in correct order
echo "🔨 Creating migrations..."
python manage.py makemigrations backend --verbosity=2

echo "📊 Running all migrations..."
python manage.py migrate --verbosity=2

# Create sample data
echo "🍽️ Creating sample data..."
python manage.py shell << 'EOF'
import os
import django
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
print(f'✅ Business settings: {"created" if created else "exists"}')

# Create basic categories
categories = ['Traditional Dishes', 'Local Snacks', 'Beverages', 'Pastries & Sweets']
for cat_name in categories:
    cat, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': slugify(cat_name), 'is_active': True}
    )
    print(f'✅ Category {cat_name}: {"created" if created else "exists"}')

# Create superuser accounts
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
EOF

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --noinput --verbosity=2

# Final system check
echo "🔍 Final system check..."
python manage.py check

echo ""
echo "🎉 BUILD COMPLETED SUCCESSFULLY!"
echo "============================================="
echo "📅 Completed at: $(date)"
echo ""
echo "✅ DEPLOYMENT SUMMARY:"
echo "   📦 Dependencies: Installed"
echo "   📁 Directories: Created"
echo "   🎨 Static Files: Generated"
echo "   📊 Database: Migrated"
echo "   👤 Admin Users: Created"
echo "   🍽️ Sample Data: Loaded"
echo ""
echo "🌐 APPLICATION READY!"