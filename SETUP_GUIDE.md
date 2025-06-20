# 🍽️ BueaDelights Complete Setup Guide

Welcome to BueaDelights! This guide will walk you through the complete setup process for your Django-based Cameroonian food delivery application.

## 📋 Quick Setup (Recommended)

### 1. Clone and Initialize

```bash
# Clone the repository (if from git)
git clone <your-repo-url>
cd bueadelights

# Or if you have the files locally, navigate to the project directory
cd bueadelights-project
```

### 2. Run Automated Setup

```bash
# Make scripts executable
python make_executable.py

# Run complete setup
python setup.py
```

### 3. Start Development Server

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start development server with hot reload
python dev_server.py
```

### 4. Access Your Application

- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

## 🔑 Default Admin Credentials

```
Username: folefack_caroline
Password: BueaDelights2025!Caroline

Username: momo_godi_yvan  
Password: BueaDelights2025!Yvan

Username: momo_marlyse
Password: BueaDelights2025!Marlyse
```

**⚠️ IMPORTANT**: Change these passwords immediately after first login!

## 🛠️ Manual Setup (Advanced)

If you prefer to set up manually or the automated setup fails:

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Node.js Dependencies

```bash
# Install Node.js dependencies
npm install

# Build CSS for development
npm run build-css
```

### Step 3: Environment Configuration

Create `.env` file:

```env
# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Business Configuration
WHATSAPP_NUMBER=+237699808260
BUSINESS_NAME=BueaDelights
BUSINESS_EMAIL=info@bueadelights.com
DELIVERY_FEE=1500

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Configuration (Optional)
NOUPIA_API_KEY=your-noupia-api-key
NOUPIA_MERCHANT_ID=your-merchant-id
```

### Step 4: Django Setup

```bash
# Run database migrations
python manage.py migrate

# Create super admin users
python manage.py create_superadmins

# Create sample data (optional)
python manage.py create_sample_data

# Collect static files
python manage.py collectstatic --noinput
```

### Step 5: Start Development Server

```bash
# Option 1: Use development script
python dev_server.py

# Option 2: Manual start
# Terminal 1: Start Tailwind CSS watcher
npm run build-css

# Terminal 2: Start Django server
python manage.py runserver
```

## 🔧 Configuration

### Email Configuration

1. **Gmail Setup**:
   - Enable 2-factor authentication
   - Generate app password
   - Update `.env` file with credentials

2. **Test Email**:
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Hello!', 'from@example.com', ['to@example.com'])
   ```

### WhatsApp Configuration

1. **Business Account**:
   - Set up WhatsApp Business account
   - Update `WHATSAPP_NUMBER` in `.env`

2. **Test Integration**:
   - Visit frontend and test "Contact via WhatsApp" links
   - Verify order messages generate correctly

### Payment Configuration (Noupia)

1. **Account Setup**:
   - Register with Noupia
   - Get API credentials
   - Configure webhook endpoints

2. **Test Payment**:
   - Add products to cart
   - Test mobile money payment flow
   - Verify transactions in admin panel

## 📊 Features Overview

### Customer Features
- ✅ Product catalog with categories
- ✅ Shopping cart with persistence
- ✅ Multiple payment options
- ✅ WhatsApp integration
- ✅ Order tracking
- ✅ Catering service requests
- ✅ Mobile-optimized design

### Admin Features
- ✅ Comprehensive dashboard
- ✅ Product management
- ✅ Order processing
- ✅ Customer communication
- ✅ Analytics and reporting
- ✅ Business settings
- ✅ Receipt generation

### Technical Features
- ✅ Django 4.2 LTS
- ✅ Tailwind CSS styling
- ✅ Auto-reload development
- ✅ PostgreSQL ready
- ✅ Security features
- ✅ API endpoints
- ✅ Test coverage

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test backend

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🚀 Production Deployment

### Render.com Deployment

1. **Push to Git**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Render**:
   - Link GitHub repository
   - Configure environment variables
   - Deploy using `build.sh`

3. **Environment Variables**:
   ```
   DJANGO_SETTINGS_MODULE=bueadelights.settings_prod
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-domain.onrender.com
   DATABASE_URL=postgresql://...
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   NOUPIA_API_KEY=your-noupia-api-key
   NOUPIA_MERCHANT_ID=your-merchant-id
   ```

### Manual Production Setup

```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=bueadelights.settings_prod

# Install dependencies
pip install -r requirements.txt

# Build production assets
npm run build-css-prod

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin users
python manage.py create_superadmins

# Start with Gunicorn
gunicorn bueadelights.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

## 🛠️ Development Commands

### Django Commands

```bash
# Create new app
python manage.py startapp newapp

# Make migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell

# Database shell
python manage.py dbshell
```

### Custom Commands

```bash
# Create super admin users
python manage.py create_superadmins

# Create sample data
python manage.py create_sample_data

# Create sample data (force recreate)
python manage.py create_sample_data --force
```

### CSS Commands

```bash
# Build CSS for development (watch mode)
npm run build-css

# Build CSS for production (minified)
npm run build-css-prod

# Start development server with CSS watching
npm run dev
```

## 🔍 Troubleshooting

### Common Issues

1. **CSS Not Loading**:
   ```bash
   npm run build-css-prod
   python manage.py collectstatic --noinput
   ```

2. **Database Errors**:
   ```bash
   python manage.py migrate
   python manage.py migrate --run-syncdb
   ```

3. **Template Not Found**:
   - Check `TEMPLATES` setting in `settings.py`
   - Verify template files exist
   - Run `python manage.py collectstatic`

4. **Import Errors**:
   - Activate virtual environment
   - Install requirements: `pip install -r requirements.txt`

5. **Permission Errors**:
   ```bash
   python make_executable.py
   chmod +x *.py
   chmod +x *.sh
   ```

### Getting Help

- **Documentation**: Check README.md
- **Issues**: Create GitHub issue
- **Email**: info@bueadelights.com
- **WhatsApp**: +237 6 99 80 82 60

## 📚 Project Structure

```
bueadelights/
├── 📁 backend/              # Main Django app
│   ├── 📄 models.py         # Database models
│   ├── 📄 views.py          # Public views
│   ├── 📄 admin_views.py    # Admin views
│   ├── 📄 forms.py          # Django forms
│   ├── 📄 urls.py           # URL routing
│   ├── 📄 admin.py          # Admin config
│   ├── 📄 utils.py          # Utilities
│   ├── 📄 signals.py        # Django signals
│   ├── 📁 management/       # Custom commands
│   └── 📁 templates/        # HTML templates
├── 📁 bueadelights/         # Project settings
├── 📁 static/               # Static files
├── 📁 media/                # User uploads
├── 📁 templates/            # Global templates
├── 📄 requirements.txt      # Python deps
├── 📄 package.json          # Node.js deps
├── 📄 tailwind.config.js    # Tailwind config
├── 📄 .env                  # Environment vars
├── 📄 setup.py              # Setup script
├── 📄 dev_server.py         # Dev server
└── 📄 README.md             # Documentation
```

## 🎯 Next Steps

After successful setup:

1. **Customize Business Settings**:
   - Update business information in admin panel
   - Configure delivery areas and fees
   - Set operating hours

2. **Add Real Products**:
   - Replace sample data with real products
   - Upload high-quality product images
   - Write compelling descriptions

3. **Configure Payments**:
   - Set up Noupia account for mobile money
   - Test payment workflows
   - Configure webhook endpoints

4. **Email Setup**:
   - Configure SMTP settings
   - Test order confirmations
   - Set up marketing emails

5. **Go Live**:
   - Deploy to production
   - Configure domain name
   - Set up monitoring

## 🎉 Congratulations!

You now have a fully functional Cameroonian food delivery platform! 

**BueaDelights** is ready to serve authentic local flavors to your customers with modern convenience.

---

*"Local Flavors at Your Fingertips" - BueaDelights Team*