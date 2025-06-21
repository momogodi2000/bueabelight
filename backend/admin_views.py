from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json

from .models import (
    Product, Category, Order, OrderItem, ContactMessage, 
    CateringInquiry, BusinessSettings
)
from .forms import ForgotPasswordForm, ResetPasswordForm
from .utils import EmailHelper

# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Password Reset Views
class ForgotPasswordView(PasswordResetView):
    template_name = 'backend/auth/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('backend:admin_login')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email, is_superuser=True)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = self.request.build_absolute_uri(
                reverse_lazy('backend:reset_password', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )
            
            # Send email
            if EmailHelper.send_password_reset_email(user, reset_link):
                messages.success(self.request, 'Password reset email sent successfully!')
            else:
                messages.error(self.request, 'Error sending password reset email')
                
        except User.DoesNotExist:
            messages.error(self.request, 'No admin account found with this email address')
        
        return redirect(self.success_url)

class ResetPasswordView(PasswordResetConfirmView):
    template_name = 'backend/auth/reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('backend:admin_login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset successfully! You can now login.')
        return super().form_valid(form)

# Admin Product Management Views
class AdminProductListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = 'admin/products_list.html'
    context_object_name = 'products'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category').order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Availability filter
        availability = self.request.GET.get('availability')
        if availability == 'available':
            queryset = queryset.filter(is_available=True)
        elif availability == 'unavailable':
            queryset = queryset.filter(is_available=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_products'] = Product.objects.count()
        context['available_products'] = Product.objects.filter(is_available=True).count()
        context['featured_products'] = Product.objects.filter(is_featured=True).count()
        return context

class AdminProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    template_name = 'admin/form.html'
    fields = ['name', 'description', 'price', 'category', 'image', 'is_available', 'is_featured', 'stock_quantity']
    success_url = reverse_lazy('backend:admin_products')
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)

class AdminProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'admin/form.html'
    fields = ['name', 'description', 'price', 'category', 'image', 'is_available', 'is_featured', 'stock_quantity']
    success_url = reverse_lazy('backend:admin_products')
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)

class AdminProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'admin/delete.html'
    success_url = reverse_lazy('backend:admin_products')
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Admin Order Management Views
class AdminOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'admin/orders/list.html'
    context_object_name = 'orders'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = Order.objects.select_related().order_by('-created_at')
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(order_status=status)
        
        # Payment status filter
        payment_status = self.request.GET.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Search by customer name or order ID
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(order_id__icontains=search) |
                Q(customer_phone__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_statuses'] = Order.ORDER_STATUS_CHOICES
        context['payment_statuses'] = Order.PAYMENT_STATUS_CHOICES
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(order_status='pending').count()
        context['completed_orders'] = Order.objects.filter(order_status='delivered').count()
        return context

class AdminOrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'admin/orders/detail.html'
    context_object_name = 'order'
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser

@login_required
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
    template_name = 'admin/categories/list.html'
    context_object_name = 'categories'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser

class AdminCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    template_name = 'admin/categories/form.html'
    fields = ['name', 'description', 'image', 'is_active']
    success_url = reverse_lazy('backend:admin_categories')
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

# Admin Message Management Views
class AdminMessageListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ContactMessage
    template_name = 'admin/messages/list.html'
    context_object_name = 'messages'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = ContactMessage.objects.order_by('-created_at')
        
        # Filter by read status
        is_read = self.request.GET.get('is_read')
        if is_read == 'true':
            queryset = queryset.filter(is_read=True)
        elif is_read == 'false':
            queryset = queryset.filter(is_read=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = ContactMessage.objects.filter(is_read=False).count()
        context['total_messages'] = ContactMessage.objects.count()
        return context

# Admin Catering Management Views
class AdminCateringListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CateringInquiry
    template_name = 'admin/catering/list.html'
    context_object_name = 'inquiries'
    paginate_by = 20
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = CateringInquiry.objects.order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by event type
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = CateringInquiry.STATUS_CHOICES
        context['event_types'] = CateringInquiry.EVENT_TYPE_CHOICES
        context['new_inquiries'] = CateringInquiry.objects.filter(status='new').count()
        context['total_inquiries'] = CateringInquiry.objects.count()
        return context

# Admin Analytics View
# views.py or admin_views.py
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
from .models import Order, OrderItem, Product, Category

class AdminAnalyticsView(TemplateView):
    template_name = 'admin/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query parameters (default to 30 days)
        date_range = int(self.request.GET.get('range', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=date_range)
        
        # Filter orders by date range
        orders = Order.objects.filter(created_at__range=[start_date, end_date])
        
        # Calculate metrics
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = orders.count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Revenue data by day
        revenue_data = orders.values('created_at__date').annotate(
            revenue=Sum('total_amount')
        ).order_by('created_at__date')
        
        # Orders data by day
        orders_data = orders.values('created_at__date').annotate(
            orders=Count('id')
        ).order_by('created_at__date')
        
        # Product performance
        product_performance = OrderItem.objects.filter(
            order__in=orders
        ).values(
            'product__name'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_revenue')[:10]
        
        # Customer insights
        customer_insights = orders.values(
            'customer_phone'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_amount')
        ).order_by('-total_spent')[:10]
        
        # Category performance
        category_performance = OrderItem.objects.filter(
            order__in=orders
        ).values(
            'product__category__name'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_revenue')
        
        # Add all data to context
        context.update({
            'date_range': date_range,
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'revenue_data': list(revenue_data),
            'orders_data': list(orders_data),
            'product_performance': product_performance,
            'customer_insights': customer_insights,
            'category_performance': category_performance,
        })
        
        return context

# Admin Settings View
class AdminSettingsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BusinessSettings
    template_name = 'admin/settings.html'
    fields = [
        'business_name', 'business_description', 'phone', 'email', 
        'address', 'operating_hours', 'delivery_fee', 'delivery_areas',
        'is_accepting_orders'
    ]
    success_url = reverse_lazy('backend:admin_settings')
    login_url = 'backend:admin_login'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_object(self):
        settings, created = BusinessSettings.objects.get_or_create(pk=1)
        return settings
    
    def form_valid(self, form):
        messages.success(self.request, 'Business settings updated successfully!')
        return super().form_valid(form)



