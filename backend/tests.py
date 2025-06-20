from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import json
import tempfile
from PIL import Image
from io import BytesIO

from .models import (
    Category, Product, Order, OrderItem, ContactMessage, 
    CateringInquiry, BusinessSettings
)

class BaseTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_superuser(
            username='testadmin',
            email='test@bueadelights.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description',
            is_active=True
        )
        
        # Create test image
        image = Image.new('RGB', (100, 100), color='red')
        temp_file = BytesIO()
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=temp_file.read(),
            content_type='image/jpeg'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            price=2500.00,
            category=self.category,
            image=self.test_image,
            is_available=True,
            is_featured=True,
            stock_quantity=10
        )
        
        # Create business settings
        self.business_settings = BusinessSettings.objects.create(
            business_name='BueaDelights Test',
            business_description='Test description',
            phone='+237699808260',
            email='test@bueadelights.com'
        )

class HomeViewTest(BaseTestCase):
    def test_home_page_loads(self):
        """Test that home page loads successfully"""
        response = self.client.get(reverse('backend:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BueaDelights')
    
    def test_home_page_context(self):
        """Test home page context data"""
        response = self.client.get(reverse('backend:home'))
        self.assertIn('featured_products', response.context)
        self.assertIn('categories', response.context)

class ProductViewTest(BaseTestCase):
    def test_product_list_view(self):
        """Test product list page"""
        response = self.client.get(reverse('backend:products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
    
    def test_product_detail_view(self):
        """Test product detail page"""
        response = self.client.get(
            reverse('backend:product_detail', kwargs={'slug': self.product.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
    
    def test_category_products_view(self):
        """Test category products page"""
        response = self.client.get(
            reverse('backend:category_products', kwargs={'slug': self.category.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.name)
        self.assertContains(response, self.product.name)
    
    def test_product_search(self):
        """Test product search functionality"""
        response = self.client.get(reverse('backend:api/search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('products', data)
        self.assertTrue(len(data['products']) > 0)

class CartViewTest(BaseTestCase):
    def test_cart_view(self):
        """Test cart page"""
        response = self.client.get(reverse('backend:cart'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_cart(self):
        """Test adding product to cart"""
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(
            reverse('backend:add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
    
    def test_remove_from_cart(self):
        """Test removing product from cart"""
        # First add to cart
        self.client.post(
            reverse('backend:add_to_cart'),
            data=json.dumps({'product_id': self.product.id, 'quantity': 1}),
            content_type='application/json'
        )
        
        # Then remove
        response = self.client.post(
            reverse('backend:remove_from_cart'),
            data=json.dumps({'product_id': self.product.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
    
    def test_cart_count(self):
        """Test cart count endpoint"""
        response = self.client.get(reverse('backend:cart_count'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('count', data)

class CheckoutViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Add product to session cart
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'name': self.product.name,
                'price': float(self.product.price),
                'quantity': 2,
                'image': self.product.image.url if self.product.image else ''
            }
        }
        session.save()
    
    def test_checkout_view_get(self):
        """Test checkout page loads"""
        response = self.client.get(reverse('backend:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'checkout')
    
    def test_checkout_view_post_cash_delivery(self):
        """Test checkout with cash on delivery"""
        data = {
            'customer_name': 'Test Customer',
            'customer_phone': '+237699808260',
            'customer_email': 'test@example.com',
            'customer_location': 'Test Location',
            'payment_method': 'cash_on_delivery',
            'special_instructions': 'Test instructions'
        }
        response = self.client.post(reverse('backend:checkout'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful order
    
    def test_checkout_empty_cart(self):
        """Test checkout with empty cart"""
        # Clear session cart
        session = self.client.session
        session['cart'] = {}
        session.save()
        
        response = self.client.get(reverse('backend:checkout'))
        self.assertEqual(response.status_code, 302)  # Redirect to cart

class OrderModelTest(BaseTestCase):
    def test_order_creation(self):
        """Test order creation"""
        order = Order.objects.create(
            customer_name='Test Customer',
            customer_phone='+237699808260',
            customer_email='test@example.com',
            customer_location='Test Location',
            total_amount=5000,
            payment_method='cash_on_delivery'
        )
        
        self.assertTrue(order.order_id.startswith('BD'))
        self.assertEqual(order.customer_name, 'Test Customer')
        self.assertIsNotNone(order.qr_code)
    
    def test_order_item_creation(self):
        """Test order item creation"""
        order = Order.objects.create(
            customer_name='Test Customer',
            customer_phone='+237699808260',
            total_amount=5000,
            payment_method='cash_on_delivery'
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            unit_price=self.product.price
        )
        
        self.assertEqual(order_item.total_price, self.product.price * 2)

class ContactViewTest(BaseTestCase):
    def test_contact_view_get(self):
        """Test contact page loads"""
        response = self.client.get(reverse('backend:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'contact')
    
    def test_contact_form_submission(self):
        """Test contact form submission"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+237699808260',
            'subject': 'Test Subject',
            'message': 'Test message content'
        }
        response = self.client.post(reverse('backend:contact'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if message was created
        self.assertTrue(ContactMessage.objects.filter(email='test@example.com').exists())

class CateringViewTest(BaseTestCase):
    def test_catering_view_get(self):
        """Test catering page loads"""
        response = self.client.get(reverse('backend:catering'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'catering')
    
    def test_catering_inquiry_submission(self):
        """Test catering inquiry submission"""
        data = {
            'name': 'Test User',
            'phone': '+237699808260',
            'email': 'test@example.com',
            'event_type': 'wedding',
            'guest_count': 100,
            'preferred_date': '2025-07-01',
            'preferred_time': '18:00',
            'location': 'Test Location',
            'special_requirements': 'Vegetarian options needed'
        }
        response = self.client.post(reverse('backend:catering'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if inquiry was created
        self.assertTrue(CateringInquiry.objects.filter(email='test@example.com').exists())

class AdminViewTest(BaseTestCase):
    def test_admin_login_view(self):
        """Test admin login page"""
        response = self.client.get(reverse('backend:admin_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        data = {
            'username': 'testadmin',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('backend:admin_login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_admin_dashboard_requires_login(self):
        """Test admin dashboard requires authentication"""
        response = self.client.get(reverse('backend:admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_with_login(self):
        """Test admin dashboard with authenticated user"""
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('backend:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dashboard')

class AboutViewTest(BaseTestCase):
    def test_about_view(self):
        """Test about page"""
        response = self.client.get(reverse('backend:about'))
        self.assertEqual(response.status_code, 200)

class URLPatternsTest(BaseTestCase):
    """Test all URL patterns resolve correctly"""
    
    def test_homepage_url(self):
        """Test homepage URL"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_products_url(self):
        """Test products URL"""
        response = self.client.get('/menu/')
        self.assertEqual(response.status_code, 200)
    
    def test_cart_url(self):
        """Test cart URL"""
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
    
    def test_checkout_url(self):
        """Test checkout URL"""
        response = self.client.get('/checkout/')
        # Should redirect if cart is empty
        self.assertIn(response.status_code, [200, 302])
    
    def test_contact_url(self):
        """Test contact URL"""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
    
    def test_catering_url(self):
        """Test catering URL"""
        response = self.client.get('/catering/')
        self.assertEqual(response.status_code, 200)
    
    def test_about_url(self):
        """Test about URL"""
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_login_url(self):
        """Test admin login URL"""
        response = self.client.get('/admin-login/')
        self.assertEqual(response.status_code, 200)

class ModelStringRepresentationTest(BaseTestCase):
    """Test model string representations"""
    
    def test_category_str(self):
        """Test Category __str__ method"""
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_product_str(self):
        """Test Product __str__ method"""
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_business_settings_str(self):
        """Test BusinessSettings __str__ method"""
        self.assertEqual(str(self.business_settings), 'BueaDelights Test')

class FormValidationTest(BaseTestCase):
    """Test form validations"""
    
    def test_contact_form_invalid_email(self):
        """Test contact form with invalid email"""
        data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'subject': 'Test',
            'message': 'Test message'
        }
        response = self.client.post(reverse('backend:contact'), data)
        # Should return form with errors, not redirect
        self.assertEqual(response.status_code, 200)
    
    def test_checkout_form_missing_fields(self):
        """Test checkout form with missing required fields"""
        # Add product to cart first
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'name': self.product.name,
                'price': float(self.product.price),
                'quantity': 1
            }
        }
        session.save()
        
        data = {
            'customer_name': '',  # Missing required field
            'payment_method': 'cash_on_delivery'
        }
        response = self.client.post(reverse('backend:checkout'), data)
        # Should return form with errors
        self.assertEqual(response.status_code, 200)

class UtilsTest(TestCase):
    """Test utility functions"""
    
    def test_whatsapp_helper_url_creation(self):
        """Test WhatsApp URL creation"""
        from .utils import WhatsAppHelper
        
        phone = '+237699808260'
        message = 'Hello BueaDelights!'
        url = WhatsAppHelper.create_whatsapp_url(phone, message)
        
        self.assertIn('wa.me', url)
        self.assertIn('237699808260', url)
        self.assertIn('Hello%20BueaDelights', url)

# Custom test runner command
class CommandTest(TestCase):
    """Test management commands"""
    
    def test_create_superadmins_command(self):
        """Test create superadmins command"""
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('create_superadmins', stdout=out)
        
        # Check if super admins were created
        self.assertTrue(User.objects.filter(username='folefack_caroline').exists())
        self.assertTrue(User.objects.filter(username='momo_godi_yvan').exists())
        self.assertTrue(User.objects.filter(username='momo_marlyse').exists())
        
        # Check if they are superusers
        caroline = User.objects.get(username='folefack_caroline')
        self.assertTrue(caroline.is_superuser)
        self.assertTrue(caroline.is_staff)