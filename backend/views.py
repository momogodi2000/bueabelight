from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO
import json
import urllib.parse
import requests
import uuid


from .models import (
    Product, Category, Order, OrderItem, ContactMessage, 
    CateringInquiry, BusinessSettings, NoupiaTransaction
)
from .forms import (
    ContactForm, CateringInquiryForm, CheckoutForm, 
    AdminLoginForm, ForgotPasswordForm, ResetPasswordForm
)
from .utils import WhatsAppHelper, NoupiaPaymentHelper, ReceiptGenerator

# Don't forget to import the necessary modules at the top of views.py:
import logging
logger = logging.getLogger(__name__)

# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Public Views
class HomeView(TemplateView):
    template_name = 'backend/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_featured=True, is_available=True)[:6]
        context['categories'] = Category.objects.filter(is_active=True)
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'backend/products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'backend/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Related products from same category
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(pk=self.object.pk)[:4]
        return context

class CategoryProductsView(ListView):
    model = Product
    template_name = 'backend/category_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=self.category, is_available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

# Cart Views
class CartView(TemplateView):
    template_name = 'backend/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        cart_items = []
        total = 0
        
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id, is_available=True)
                item_total = item['price'] * item['quantity']
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'total': item_total
                })
                total += item_total
            except Product.DoesNotExist:
                # Remove invalid items from cart
                del cart[product_id]
                self.request.session['cart'] = cart
                self.request.session.modified = True
        
        context['cart_items'] = cart_items
        context['cart_total'] = total
        context['delivery_fee'] = settings.DELIVERY_FEE
        context['grand_total'] = total + settings.DELIVERY_FEE
        return context

@require_POST
def add_to_cart(request):
    """Add product to cart via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_available=True)
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            cart[product_id]['quantity'] += quantity
        else:
            cart[product_id] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'image': product.image.url if product.image else ''
            }
        
        request.session['cart'] = cart
        request.session.modified = True
        
        cart_count = sum(item['quantity'] for item in cart.values())
        
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart',
            'cart_count': cart_count
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
def remove_from_cart(request):
    """Remove product from cart"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Product removed from cart'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
def update_cart(request):
    """Update cart item quantity"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity'))
        
        cart = request.session.get('cart', {})
        
        if product_id in cart and quantity > 0:
            cart[product_id]['quantity'] = quantity
            request.session['cart'] = cart
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def clear_cart(request):
    """Clear entire cart"""
    request.session['cart'] = {}
    request.session.modified = True
    return JsonResponse({'success': True})

def cart_count(request):
    """Get cart item count"""
    cart = request.session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return JsonResponse({'count': count})

# Checkout and Order Views
# Updated CheckoutView in views.py
class CheckoutView(TemplateView):
    template_name = 'backend/checkout.html'
    
    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, 'Your cart is empty')
            return redirect('backend:cart')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        
        cart_items = []
        total = 0
        
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                item_total = item['price'] * item['quantity']
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'total': item_total
                })
                total += item_total
            except Product.DoesNotExist:
                continue
        
        context['cart_items'] = cart_items
        context['cart_total'] = total
        context['delivery_fee'] = settings.DELIVERY_FEE
        context['grand_total'] = total + settings.DELIVERY_FEE
        context['form'] = CheckoutForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)
        cart = request.session.get('cart', {})
        
        if not cart:
            messages.error(request, 'Your cart is empty')
            return redirect('backend:cart')
        
        if form.is_valid():
            try:
                # Calculate totals
                cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
                
                # Create order
                order = Order.objects.create(
                    customer_name=form.cleaned_data['customer_name'],
                    customer_phone=form.cleaned_data['customer_phone'],
                    customer_email=form.cleaned_data['customer_email'],
                    customer_location=form.cleaned_data['customer_location'],
                    total_amount=cart_total,
                    delivery_fee=settings.DELIVERY_FEE,
                    payment_method=form.cleaned_data['payment_method'],
                    special_instructions=form.cleaned_data['special_instructions']
                )
                
                # Create order items
                for product_id, item in cart.items():
                    try:
                        product = Product.objects.get(id=product_id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item['quantity'],
                            unit_price=item['price'],
                            total_price=item['price'] * item['quantity']
                        )
                    except Product.DoesNotExist:
                        continue
                
                # 🎯 SEND EMAIL NOTIFICATION TO WHOLESALER
                from .utils import EmailHelper
                email_sent = EmailHelper.send_order_notification(order)
                
                if email_sent:
                    logger.info(f"Email notification sent successfully for order {order.order_id}")
                else:
                    logger.warning(f"Failed to send email notification for order {order.order_id}")
                
                # Handle payment method routing
                if order.payment_method == 'whatsapp_contact':
                    # Clear cart before redirecting to WhatsApp
                    request.session['cart'] = {}
                    request.session.modified = True
                    
                    # Redirect to WhatsApp with order ID as parameter
                    whatsapp_url = reverse('backend:whatsapp_order') + f'?order_id={order.order_id}'
                    
                    # Add success message
                    messages.success(request, 
                        f'Order #{order.order_id} created successfully! '
                        f'You will be redirected to WhatsApp to complete your order.'
                    )
                    
                    return redirect(whatsapp_url)
                    
                elif order.payment_method == 'mobile_money':
                    # Process Noupia payment with order ID as parameter
                    noupia_url = reverse('backend:noupia_payment') + f'?order_id={order.order_id}'
                    
                    # Add info message
                    messages.info(request, 
                        f'Order #{order.order_id} created! Redirecting to mobile money payment...'
                    )
                    
                    return redirect(noupia_url)
                    
                else:
                    # Cash on delivery
                    order.payment_status = 'pending'
                    order.save()
                    
                    # Clear cart
                    request.session['cart'] = {}
                    request.session.modified = True
                    
                    # Add success message
                    messages.success(request, 
                        f'Order #{order.order_id} placed successfully! '
                        f'We will contact you to confirm delivery details.'
                    )
                    
                    return redirect('backend:order_confirmation', order_id=order.order_id)
            
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                messages.error(request, 'An error occurred while processing your order. Please try again.')
                
        # If form is invalid or error occurred, return with errors
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

class OrderConfirmationView(DetailView):
    model = Order
    template_name = 'backend/order_confirmation.html'
    context_object_name = 'order'
    slug_field = 'order_id'
    slug_url_kwarg = 'order_id'

def whatsapp_order(request):
    """Generate WhatsApp URL for order"""
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, 'Invalid order')
        return redirect('backend:home')
    
    try:
        order = Order.objects.get(order_id=order_id)
        whatsapp_url = WhatsAppHelper.create_order_whatsapp_url(order)
        
        # Mark order as WhatsApp contacted (optional status update)
        if hasattr(order, 'whatsapp_contacted'):
            order.whatsapp_contacted = True
            order.save()
        
        return redirect(whatsapp_url)
    
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('backend:home')

def noupia_payment(request):
    """Process Noupia mobile money payment"""
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, 'Invalid order')
        return redirect('backend:home')
    
    try:
        order = Order.objects.get(order_id=order_id)
        
        # Create Noupia transaction
        transaction = NoupiaTransaction.objects.create(
            order=order,
            transaction_id=f"TXN{uuid.uuid4().hex[:10].upper()}",
            amount=order.delivery_fee,  # Only delivery fee paid via mobile money
            customer_phone=order.customer_phone
        )
        
        # Process payment with Noupia
        payment_result = NoupiaPaymentHelper.process_payment(
            amount=order.delivery_fee,
            phone=order.customer_phone,
            transaction_id=transaction.transaction_id
        )
        
        if payment_result['success']:
            transaction.status = 'success'
            transaction.noupia_reference = payment_result.get('reference', '')
            transaction.response_data = payment_result
            transaction.save()
            
            order.payment_status = 'completed'
            order.noupia_transaction_id = transaction.transaction_id
            order.save()
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            messages.success(request, 
                f'Payment successful! Order #{order.order_id} has been confirmed. '
                f'We will contact you with delivery details.'
            )
            return redirect('backend:order_confirmation', order_id=order.order_id)
        else:
            transaction.status = 'failed'
            transaction.response_data = payment_result
            transaction.save()
            
            messages.error(request, f"Payment failed: {payment_result.get('message', 'Unknown error')}")
            return redirect('backend:checkout')
    
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('backend:home')

@csrf_exempt
def payment_callback(request):
    """Handle Noupia payment callback"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            status = data.get('status')
            
            transaction = NoupiaTransaction.objects.get(transaction_id=transaction_id)
            transaction.status = status
            transaction.response_data = data
            transaction.save()
            
            if status == 'success':
                order = transaction.order
                order.payment_status = 'completed'
                order.save()
            
            return JsonResponse({'status': 'received'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Receipt Generation
def generate_receipt(request, order_id):
    """Generate and download PDF receipt"""
    try:
        order = Order.objects.get(order_id=order_id)
        
        # Generate PDF receipt
        buffer = BytesIO()
        receipt = ReceiptGenerator.generate_pdf_receipt(order, buffer)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{order.order_id}.pdf"'
        
        # Mark receipt as generated
        order.receipt_generated = True
        order.save()
        
        return response
    
    except Order.DoesNotExist:
        raise Http404("Order not found")

# Other Pages
class AboutView(TemplateView):
    template_name = 'backend/about.html'

class ContactView(TemplateView):
    template_name = 'backend/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('backend:contact')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

# In your views.py, make sure the CateringView looks like this:

class CateringView(TemplateView):
    template_name = 'backend/catering.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CateringInquiryForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CateringInquiryForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Your catering inquiry has been submitted! We will contact you shortly.')
                return redirect('backend:catering')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            # Pass form errors back to template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

# Search
def search_products(request):
    """AJAX product search"""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products_qs = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True
        )[:10]
        
        products = [{
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'image': p.image.url if p.image else '',
            'url': p.get_absolute_url()
        } for p in products_qs]
    
    return JsonResponse({'products': products})

# Admin Authentication Views
class AdminLoginView(LoginView):
    template_name = 'backend/auth/login.html'
    form_class = AdminLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('backend:admin_dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser:
            form.add_error(None, 'You do not have admin privileges.')
            return self.form_invalid(form)
        return super().form_valid(form)

def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('backend:admin_login')

# Admin Dashboard and Management Views
class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/dashboard.html'
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(order_status='pending').count()
        context['total_products'] = Product.objects.count()
        context['total_revenue'] = Order.objects.filter(
            payment_status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Recent orders
        context['recent_orders'] = Order.objects.select_related().order_by('-created_at')[:5]
        
        # Low stock products
        context['low_stock_products'] = Product.objects.filter(stock_quantity__lt=5)
        
        return context

# Additional admin views would go here...
# (AdminProductListView, AdminOrderListView, etc.)

# Import admin views
from .admin_views import (
    ForgotPasswordView, ResetPasswordView,
    AdminProductListView, AdminProductCreateView, AdminProductUpdateView, AdminProductDeleteView,
    AdminOrderListView, AdminOrderDetailView, update_order_status,
    AdminCategoryListView, AdminCategoryCreateView,
    AdminMessageListView, AdminCateringListView,
    AdminAnalyticsView, AdminSettingsView
)