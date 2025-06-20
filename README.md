# 🍽️ BueaDelights - "Local Flavors at Your Fingertips"

[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.3-blue.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Django-based e-commerce web application for a local Cameroonian food business in Buea, Southwest Region. The platform serves authentic Cameroonian cuisine with modern web technologies, mobile-first design, and integrated payment solutions.

## 🌟 Features

### 🍴 Customer Features
- **Product Catalog**: Browse categorized Cameroonian dishes with search and filters
- **Shopping Cart**: Real-time cart management with persistent sessions
- **Multiple Payment Options**: 
  - WhatsApp Contact Integration
  - Mobile Money via Noupia API
  - Cash on Delivery
- **Order Tracking**: Real-time order status updates
- **Catering Services**: Request quotes for events and celebrations
- **Mobile-First Design**: Optimized for 3G/4G networks common in Cameroon

### 👨‍💼 Admin Features
- **Dashboard Analytics**: Real-time business intelligence and KPI tracking
- **Order Management**: Complete order processing workflow
- **Product Management**: Full CRUD operations with inventory tracking
- **Customer Communication**: Email and WhatsApp integration
- **Receipt Generation**: Automated PDF receipts with QR codes
- **Business Settings**: Configurable delivery areas, fees, and operating hours

### 🔧 Technical Features
- **Django 4.2 LTS**: Robust backend framework
- **Tailwind CSS**: Modern, responsive UI design
- **Auto-reload Development**: Hot reload for rapid development
- **PostgreSQL**: Production-ready database
- **WhatsApp Business API**: Direct customer communication
- **Email Integration**: Automated notifications via Yagmail
- **QR Code Generation**: Order verification and tracking
- **Security**: SSL/TLS encryption, CSRF protection

## 🎯 Target Market

- **Primary**: Local Buea residents and University of Buea students
- **Secondary**: Expatriates seeking authentic Cameroonian cuisine
- **Tertiary**: Office workers, event organizers, and tourists

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+
- npm or yarn
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/bueadelights.git
cd bueadelights
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

### 4. Environment Configuration

Create `.env` file in the root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
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

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create super admin users
python manage.py create_superadmins

# Create sample data (optional)
python manage.py create_sample_data
```

### 6. Start Development Server

```bash
# Option 1: Use our custom development server (recommended)
python dev_server.py

# Option 2: Manual start
# Terminal 1: Start Tailwind CSS watcher
npm run build-css

# Terminal 2: Start Django server
python manage.py runserver
```

### 7. Access the Application

- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Endpoints**: http://localhost:8000/api/

### 8. Default Admin Credentials

```
Username: folefack_caroline
Password: BueaDelights2025!Caroline

Username: momo_godi_yvan
Password: BueaDelights2025!Yvan

Username: momo_marlyse
Password: BueaDelights2025!Marlyse
```

**⚠️ Important**: Change these passwords immediately after first login!

## 📱 Mobile-First Design

BueaDelights is designed with Cameroon's mobile-first internet usage in mind:

- **Fast Loading**: Optimized for 3G/4G networks
- **Responsive Design**: Works perfectly on all device sizes
- **Touch-Friendly**: Large buttons and easy navigation
- **Offline Capability**: Progressive Web App features

## 💳 Payment Integration

### WhatsApp Integration
Direct customer communication for order coordination and payment arrangement.

### Mobile Money (Noupia)
- **MTN Mobile Money**
- **Orange Money**
- Only delivery fee collected online (1,500 FCFA)
- Remaining payment on delivery

### Cash on Delivery
Traditional payment method for local customers.

## 🏗️ Project Structure

```
bueadelights/
├── backend/                 # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # Views and business logic
│   ├── admin_views.py      # Admin panel views
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin configuration
│   ├── utils.py            # Utility functions
│   ├── signals.py          # Django signals
│   ├── management/         # Custom commands
│   └── templates/          # HTML templates
├── bueadelights/           # Django project settings
│   ├── settings.py         # Development settings
│   ├── settings_prod.py    # Production settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── static/                 # Static files
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Static images
├── templates/              # Global templates
├── media/                  # User uploads
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
├── tailwind.config.js     # Tailwind CSS configuration
├── build.sh               # Production build script
├── render.yaml            # Render.com deployment config
└── dev_server.py          # Development server script
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🌐 Production Deployment

### Render.com Deployment

1. **Fork/Clone** this repository
2. **Connect** to Render.com
3. **Set Environment Variables** in Render dashboard:
   ```
   DJANGO_SETTINGS_MODULE=bueadelights.settings_prod
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   DATABASE_URL=postgresql://...  # Provided by Render
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   NOUPIA_API_KEY=your-noupia-api-key
   NOUPIA_MERCHANT_ID=your-merchant-id
   ```
4. **Deploy** using the provided `build.sh` script

### Manual Production Setup

```bash
# Install production dependencies
pip install -r requirements.txt

# Build CSS for production
npm run build-css-prod

# Set production environment
export DJANGO_SETTINGS_MODULE=bueadelights.settings_prod

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create super admins
python manage.py create_superadmins

# Start with Gunicorn
gunicorn bueadelights.wsgi:application --bind 0.0.0.0:8000
```

## 🔧 Configuration

### Business Settings

Configure your business through the admin panel:
- **Business Information**: Name, description, contact details
- **Operating Hours**: When you accept orders
- **Delivery Areas**: Where you deliver
- **Delivery Fees**: Shipping costs
- **Payment Options**: Available payment methods

### Email Configuration

For email notifications, configure SMTP settings:
1. Create Gmail app password
2. Update `.env` file with credentials
3. Test email functionality

### WhatsApp Integration

1. Get WhatsApp Business account
2. Update `WHATSAPP_NUMBER` in settings
3. Test message generation

### Payment Gateway

For Noupia integration:
1. Register with Noupia
2. Get API credentials
3. Configure webhook endpoints
4. Test payment flow

## 📊 Analytics & Monitoring

### Built-in Analytics
- **Sales Tracking**: Daily, weekly, monthly reports
- **Customer Insights**: Behavior and engagement metrics
- **Inventory Management**: Stock levels and reorder alerts
- **Performance Metrics**: Page load times, conversion rates

### Optional Monitoring
- **Sentry**: Error tracking and performance monitoring
- **Google Analytics**: Website traffic analysis
- **Database Monitoring**: Query performance and optimization

## 🛡️ Security Features

- **CSRF Protection**: Cross-site request forgery prevention
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Input sanitization
- **SSL/TLS Encryption**: Secure data transmission
- **Authentication**: Secure admin access
- **Session Security**: Secure session management

## 🎨 Customization

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Cameroon Colors**: Green, Red, Yellow theme
- **Custom Components**: Reusable UI components
- **Responsive Design**: Mobile-first approach

### Adding Products
1. **Admin Panel**: Use Django admin interface
2. **Categories**: Organize products by type
3. **Images**: Upload high-quality photos
4. **Descriptions**: Write compelling product descriptions
5. **Pricing**: Set competitive prices in FCFA

### Custom Features
- **New Models**: Add database models as needed
- **API Endpoints**: Create REST API endpoints
- **Payment Methods**: Integrate additional payment options
- **Shipping Options**: Add delivery and pickup options

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Document new features
- Use meaningful commit messages

## 📞 Support

- **Email**: info@bueadelights.com
- **WhatsApp**: +237 6 99 80 82 60
- **Issues**: GitHub Issues tracker
- **Documentation**: Wiki pages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

### Phase 1 (Current)
- [x] Core e-commerce functionality
- [x] Payment integration
- [x] Admin panel
- [x] Mobile optimization

### Phase 2 (Upcoming)
- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics
- [ ] Multi-vendor support
- [ ] Inventory management API

### Phase 3 (Future)
- [ ] AI-powered recommendations
- [ ] Multi-language support
- [ ] Franchise management
- [ ] Supply chain integration

## 🌍 About Cameroon

BueaDelights celebrates the rich culinary heritage of Cameroon, particularly the Southwest Region. Our platform showcases traditional dishes that have been passed down through generations, bringing authentic flavors to modern consumers.

### Featured Dishes
- **Ndolé**: National dish with groundnuts and vegetables
- **Achu**: Traditional cocoyam with yellow soup
- **Eru**: Delicacy from the Southwest region
- **Koki**: Steamed beans cake wrapped in banana leaves

---

**Made with ❤️ in Buea, Cameroon**

*"Local Flavors at Your Fingertips"*