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
            
            # Handle payment method
            if order.payment_method == 'whatsapp_contact':
                # Redirect to WhatsApp
                return redirect('backend:whatsapp_order') + f'?order_id={order.order_id}'
            elif order.payment_method == 'mobile_money':
                # Process Noupia payment
                return redirect('backend:noupia_payment') + f'?order_id={order.order_id}'
            else:
                # Cash on delivery
                order.payment_status = 'pending'
                order.save()
                
                # Clear cart
                request.session['cart'] = {}
                request.session.modified = True
                
                return redirect('backend:order_confirmation', order_id=order.order_id)
        
        # If form is invalid, return with errors
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
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        return redirect(whatsapp_url)
    
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('backend:home')

# Payment Views
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
            
            messages.success(request, 'Payment successful! Your order has been confirmed.')
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

class CateringView(TemplateView):
    template_name = 'backend/catering.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CateringInquiryForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CateringInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your catering inquiry has been submitted!')
            return redirect('backend:catering')
        
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
    template_name = 'backend/admin/login.html'
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
    template_name = 'backend/admin/dashboard.html'
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

# The rest of the admin views will be implemented based on the same patterns
# Add these missing views to your existing views.py file

# Password Reset Views
class ForgotPasswordView(TemplateView):
    template_name = 'backend/admin/forgot_password.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ForgotPasswordForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email, is_superuser=True)
                
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset URL
                reset_url = request.build_absolute_uri(
                    reverse('backend:reset_password', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Send email
                subject = 'Password Reset - BueaDelights Admin'
                message = f'Click the link to reset your password: {reset_url}'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                
                messages.success(request, 'Password reset link sent to your email.')
                return redirect('backend:admin_login')
            
            except User.DoesNotExist:
                form.add_error('email', 'No admin account found with this email.')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

class ResetPasswordView(TemplateView):
    template_name = 'backend/admin/reset_password.html'
    
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid, is_superuser=True)
            
            if default_token_generator.check_token(user, token):
                context = {
                    'form': ResetPasswordForm(),
                    'uidb64': uidb64,
                    'token': token
                }
                return render(request, self.template_name, context)
            else:
                messages.error(request, 'Invalid or expired reset link.')
                return redirect('backend:admin_login')
        
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Invalid reset link.')
            return redirect('backend:admin_login')
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid, is_superuser=True)
            
            if default_token_generator.check_token(user, token):
                form = ResetPasswordForm(request.POST)
                if form.is_valid():
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    messages.success(request, 'Password reset successfully. You can now login.')
                    return redirect('backend:admin_login')
                
                context = {
                    'form': form,
                    'uidb64': uidb64,
                    'token': token
                }
                return render(request, self.template_name, context)
            else:
                messages.error(request, 'Invalid or expired reset link.')
                return redirect('backend:admin_login')
        
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Invalid reset link.')
            return redirect('backend:admin_login')

# Admin Product Management Views
class AdminProductListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = 'backend/admin/products.html'
    context_object_name = 'products'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by availability
        availability = self.request.GET.get('availability')
        if availability == 'available':
            queryset = queryset.filter(is_available=True)
        elif availability == 'unavailable':
            queryset = queryset.filter(is_available=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_availability'] = self.request.GET.get('availability', '')
        return context

class AdminProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    template_name = 'backend/admin/product_form.html'
    fields = [
        'name', 'description', 'price', 'category', 'image', 
        'is_available', 'is_featured', 'stock_quantity'
    ]
    login_url = 'backend:admin_login'
    success_url = reverse_lazy('backend:admin_products')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)

class AdminProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'backend/admin/product_form.html'
    fields = [
        'name', 'description', 'price', 'category', 'image', 
        'is_available', 'is_featured', 'stock_quantity'
    ]
    login_url = 'backend:admin_login'
    success_url = reverse_lazy('backend:admin_products')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)

class AdminProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'backend/admin/product_confirm_delete.html'
    login_url = 'backend:admin_login'
    success_url = reverse_lazy('backend:admin_products')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Admin Order Management Views
class AdminOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'backend/admin/orders.html'
    context_object_name = 'orders'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items__product')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(order_status=status)
        
        # Filter by payment status
        payment_status = self.request.GET.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Search by order ID or customer name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_id__icontains=search) | 
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_statuses'] = Order.ORDER_STATUS_CHOICES
        context['payment_statuses'] = Order.PAYMENT_STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_payment_status'] = self.request.GET.get('payment_status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class AdminOrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'backend/admin/order_detail.html'
    context_object_name = 'order'
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.select_related('product')
        return context

@login_required(login_url='backend:admin_login')
@user_passes_test(is_admin)
@require_POST
def update_order_status(request, pk):
    """Update order status via AJAX"""
    try:
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.ORDER_STATUS_CHOICES):
            order.order_status = new_status
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {order.get_order_status_display()}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

# Admin Category Management Views
class AdminCategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'backend/admin/categories.html'
    context_object_name = 'categories'
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count('products')
        ).order_by('name')

class AdminCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    template_name = 'backend/admin/category_form.html'
    fields = ['name', 'description', 'image', 'is_active']
    login_url = 'backend:admin_login'
    success_url = reverse_lazy('backend:admin_categories')
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

# Admin Messages and Catering Views
class AdminMessageListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ContactMessage
    template_name = 'backend/admin/messages.html'
    context_object_name = 'messages'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        
        # Filter by read status
        is_read = self.request.GET.get('is_read')
        if is_read == 'true':
            queryset = queryset.filter(is_read=True)
        elif is_read == 'false':
            queryset = queryset.filter(is_read=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = ContactMessage.objects.filter(is_read=False).count()
        context['selected_filter'] = self.request.GET.get('is_read', '')
        return context

class AdminCateringListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CateringInquiry
    template_name = 'backend/admin/catering_inquiries.html'
    context_object_name = 'inquiries'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = CateringInquiry.objects.all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by event type
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = CateringInquiry.STATUS_CHOICES
        context['event_types'] = CateringInquiry.EVENT_TYPE_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_event_type'] = self.request.GET.get('event_type', '')
        return context

# Admin Analytics View
class AdminAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'backend/admin/analytics.html'
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic statistics
        context['total_orders'] = Order.objects.count()
        context['total_customers'] = Order.objects.values('customer_phone').distinct().count()
        context['total_products'] = Product.objects.count()
        context['active_products'] = Product.objects.filter(is_available=True).count()
        
        # Revenue statistics
        completed_orders = Order.objects.filter(payment_status='completed')
        context['total_revenue'] = completed_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        context['total_delivery_revenue'] = completed_orders.aggregate(
            total=Sum('delivery_fee')
        )['total'] or 0
        
        # Order status breakdown
        context['order_status_stats'] = {}
        for status, label in Order.ORDER_STATUS_CHOICES:
            context['order_status_stats'][label] = Order.objects.filter(
                order_status=status
            ).count()
        
        # Popular products
        from django.db.models import Sum as ModelSum
        context['popular_products'] = Product.objects.annotate(
            total_ordered=ModelSum('orderitem__quantity')
        ).filter(total_ordered__isnull=False).order_by('-total_ordered')[:10]
        
        # Monthly sales data (last 12 months)
        from datetime import datetime, timedelta
        from django.db.models import TruncMonth
        
        twelve_months_ago = timezone.now() - timedelta(days=365)
        monthly_sales = Order.objects.filter(
            created_at__gte=twelve_months_ago,
            payment_status='completed'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('month')
        
        context['monthly_sales'] = list(monthly_sales)
        
        # Recent activity
        context['recent_orders'] = Order.objects.select_related().order_by('-created_at')[:10]
        context['recent_messages'] = ContactMessage.objects.order_by('-created_at')[:5]
        context['recent_catering'] = CateringInquiry.objects.order_by('-created_at')[:5]
        
        return context

# Admin Settings View
class AdminSettingsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'backend/admin/settings.html'
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['business_settings'] = BusinessSettings.objects.first()
        except BusinessSettings.DoesNotExist:
            context['business_settings'] = BusinessSettings.objects.create()
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            settings_obj = BusinessSettings.objects.first()
            if not settings_obj:
                settings_obj = BusinessSettings.objects.create()
            
            # Update settings from POST data
            settings_obj.business_name = request.POST.get('business_name', settings_obj.business_name)
            settings_obj.business_description = request.POST.get('business_description', settings_obj.business_description)
            settings_obj.phone = request.POST.get('phone', settings_obj.phone)
            settings_obj.email = request.POST.get('email', settings_obj.email)
            settings_obj.address = request.POST.get('address', settings_obj.address)
            settings_obj.operating_hours = request.POST.get('operating_hours', settings_obj.operating_hours)
            settings_obj.delivery_areas = request.POST.get('delivery_areas', settings_obj.delivery_areas)
            settings_obj.delivery_fee = request.POST.get('delivery_fee', settings_obj.delivery_fee)
            settings_obj.is_accepting_orders = request.POST.get('is_accepting_orders') == 'on'
            
            settings_obj.save()
            messages.success(request, 'Settings updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
        
        return redirect('backend:admin_settings')