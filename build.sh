#!/usr/bin/env bash
# ULTIMATE BUILD SCRIPT - Bulletproof Django deployment
set -o errexit

echo "🚀 ULTIMATE BUILD: Starting BueaDelights deployment..."
echo "📅 Build started at: $(date)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create ALL necessary directories
echo "📁 Creating complete directory structure..."
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
    "static/backend/css"
    "static/backend/js"
    "static/backend/images"
    "backend/templates"
    "backend/templates/backend"
    "backend/static"
    "backend/static/backend"
    "backend/static/backend/css"
    "backend/static/backend/js"
    "backend/static/backend/images"
    "templates"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo "✅ Created: $dir"
done

# Run database migrations
echo "📊 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (non-interactive)
echo "👤 Creating superuser..."
python manage.py create_superadmins

# Collect static files
echo "📄 Collecting static files..."
python manage.py collectstatic --no-input --clear

# Create sample data
echo "🥘 Creating sample data..."
python manage.py create_sample_data

echo "🎉 Build completed successfully!"