#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies (if you have them)
if [ -f "package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    
    # Build CSS if you have npm scripts
    if npm run --silent >/dev/null 2>&1; then
        echo "🎨 Building CSS..."
        npm run build-css-prod || echo "⚠️  CSS build failed, continuing..."
    fi
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗃️  Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@bueadelights.com', 'BueaDelights2024!')
    print('✅ Admin user created')
else:
    print('✅ Admin user already exists')
"

# Create business settings if they don't exist
echo "⚙️  Setting up business configuration..."
python manage.py shell -c "
try:
    from backend.models import BusinessSettings
    if not BusinessSettings.objects.exists():
        BusinessSettings.objects.create()
        print('✅ Business settings created')
    else:
        print('✅ Business settings already exist')
except ImportError:
    print('⚠️  BusinessSettings model not found, skipping...')
"

echo "✅ Build process completed successfully!"