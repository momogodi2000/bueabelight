from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Products
    path('menu/', views.ProductListView.as_view(), name='products'),
    path('menu/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', views.CategoryProductsView.as_view(), name='category_products'),
    
    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/count/', views.cart_count, name='cart_count'),
    
    # Orders and Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order-confirmation/<str:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('receipt/<str:order_id>/', views.generate_receipt, name='generate_receipt'),
    path('whatsapp-order/', views.whatsapp_order, name='whatsapp_order'),
    
    # Payment
    path('payment/noupia/', views.noupia_payment, name='noupia_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    
    # Pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('catering/', views.CateringView.as_view(), name='catering'),
    
    # AJAX endpoints
    path('api/search/', views.search_products, name='search_products'),
    
    # Admin Authentication
    path('admin-login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    # Admin Management
    path('admin-panel/products/', views.AdminProductListView.as_view(), name='admin_products'),
    path('admin-panel/products/add/', views.AdminProductCreateView.as_view(), name='admin_product_add'),
    path('admin-panel/products/<int:pk>/edit/', views.AdminProductUpdateView.as_view(), name='admin_product_edit'),
    path('admin-panel/products/<int:pk>/delete/', views.AdminProductDeleteView.as_view(), name='admin_product_delete'),
    
    path('admin-panel/orders/', views.AdminOrderListView.as_view(), name='admin_orders'),
    path('admin-panel/orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin-panel/orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    
    path('admin-panel/categories/', views.AdminCategoryListView.as_view(), name='admin_categories'),
    path('admin-panel/categories/add/', views.AdminCategoryCreateView.as_view(), name='admin_category_add'),
    
    path('admin-panel/messages/', views.AdminMessageListView.as_view(), name='admin_messages'),
    path('admin-panel/catering/', views.AdminCateringListView.as_view(), name='admin_catering'),
    
    path('admin-panel/analytics/', views.AdminAnalyticsView.as_view(), name='admin_analytics'),
    path('admin-panel/settings/', views.AdminSettingsView.as_view(), name='admin_settings'),



    #path('admin/api/csrf-token/', views.csrf_token_view, name='csrf_token'),
    #path('admin/offline/', views.offline_view, name='admin_offline')
]