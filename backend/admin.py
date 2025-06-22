from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Product, ProductImage, Order, OrderItem, 
    ContactMessage, CateringInquiry, BusinessSettings, NoupiaTransaction
)

# Custom admin site configuration
admin.site.site_header = "BueaDelights Administration"
admin.site.site_title = "BueaDelights Admin"
admin.site.index_title = "Welcome to BueaDelights Admin Portal"

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price', 'stock_quantity', 
        'is_available', 'is_featured', 'created_at'
    )
    list_filter = ('category', 'is_available', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing and Inventory', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['make_available', 'make_unavailable', 'make_featured', 'remove_featured']
    
    def make_available(self, request, queryset):
        queryset.update(is_available=True)
    make_available.short_description = "Mark selected products as available"
    
    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    make_unavailable.short_description = "Mark selected products as unavailable"
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark selected products as featured"
    
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
    remove_featured.short_description = "Remove featured status from selected products"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'customer_name', 'customer_phone', 
        'total_with_delivery', 'payment_method', 'payment_status', 
        'order_status', 'created_at'
    )
    list_filter = (
        'payment_method', 'payment_status', 'order_status', 
        'created_at'
    )
    search_fields = (
        'order_id', 'customer_name', 'customer_phone', 
        'customer_email'
    )
    readonly_fields = (
        'order_id', 'qr_code_display', 'created_at', 
        'total_with_delivery'
    )
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'created_at', 'order_status')
        }),
        ('Customer Information', {
            'fields': (
                'customer_name', 'customer_phone', 
                'customer_email', 'customer_location'
            )
        }),
        ('Payment Information', {
            'fields': (
                'total_amount', 'delivery_fee', 'total_with_delivery',
                'payment_method', 'payment_status', 'noupia_transaction_id'
            )
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'receipt_generated'),
            'classes': ('collapse',)
        }),
        ('QR Code', {
            'fields': ('qr_code_display',),
            'classes': ('collapse',)
        })
    )
    
    def total_with_delivery(self, obj):
        return f"{obj.get_total_with_delivery():,.0f} FCFA"
    total_with_delivery.short_description = 'Total (with delivery)'
    
    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="150" height="150" />',
                obj.qr_code.url
            )
        return "No QR Code"
    qr_code_display.short_description = 'QR Code'
    
    actions = ['mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_delivered']
    
    def mark_confirmed(self, request, queryset):
        queryset.update(order_status='confirmed')
    mark_confirmed.short_description = "Mark orders as confirmed"
    
    def mark_preparing(self, request, queryset):
        queryset.update(order_status='preparing')
    mark_preparing.short_description = "Mark orders as preparing"
    
    def mark_ready(self, request, queryset):
        queryset.update(order_status='ready')
    mark_ready.short_description = "Mark orders as ready"
    
    def mark_delivered(self, request, queryset):
        queryset.update(order_status='delivered')
    mark_delivered.short_description = "Mark orders as delivered"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'phone', 'subject', 
        'is_read', 'created_at'
    )
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject')
    readonly_fields = ('created_at', 'responded_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Admin Response', {
            'fields': ('is_read', 'admin_response', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"

@admin.register(CateringInquiry)
class CateringInquiryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'event_type', 'guest_count', 
        'preferred_date', 'status', 'created_at'
    )
    list_filter = ('event_type', 'status', 'preferred_date', 'created_at')
    search_fields = ('name', 'phone', 'email', 'location')
    readonly_fields = ('created_at',)
    date_hierarchy = 'preferred_date'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Event Details', {
            'fields': (
                'event_type', 'guest_count', 'preferred_date', 
                'preferred_time', 'location'
            )
        }),
        ('Requirements', {
            'fields': ('special_requirements',)
        }),
        ('Admin Management', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_contacted', 'mark_quoted', 'mark_confirmed']
    
    def mark_contacted(self, request, queryset):
        queryset.update(status='contacted')
    mark_contacted.short_description = "Mark inquiries as contacted"
    
    def mark_quoted(self, request, queryset):
        queryset.update(status='quoted')
    mark_quoted.short_description = "Mark inquiries as quoted"
    
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Mark inquiries as confirmed"

@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'phone', 'email', 'is_accepting_orders')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('business_name', 'business_description')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Operating Information', {
            'fields': ('operating_hours', 'delivery_areas', 'is_accepting_orders')
        }),
        ('Pricing', {
            'fields': ('delivery_fee',)
        })
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not BusinessSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of business settings
        return False

@admin.register(NoupiaTransaction)
class NoupiaTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id', 'order', 'amount', 
        'customer_phone', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'order__order_id', 'customer_phone')
    readonly_fields = (
        'transaction_id', 'order', 'amount', 'customer_phone',
        'noupia_reference', 'response_data', 'created_at', 'updated_at'
    )
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'transaction_id', 'order', 'amount', 
                'customer_phone', 'status'
            )
        }),
        ('Noupia Details', {
            'fields': ('noupia_reference', 'response_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False  # Transactions should only be created programmatically
    
    def has_delete_permission(self, request, obj=None):
        return False  # Don't allow deletion of transaction records





from django.contrib import admin

# Register your models here when they're ready
try:
    from .models import Category, Product, BusinessSettings
    
    @admin.register(Category)
    class CategoryAdmin(admin.ModelAdmin):
        list_display = ['name', 'is_active', 'created_at']
        prepopulated_fields = {'slug': ('name',)}
        list_filter = ['is_active', 'created_at']
        search_fields = ['name', 'description']

    @admin.register(Product)
    class ProductAdmin(admin.ModelAdmin):
        list_display = ['name', 'category', 'price', 'is_available', 'is_featured', 'stock_quantity']
        prepopulated_fields = {'slug': ('name',)}
        list_filter = ['category', 'is_available', 'is_featured', 'created_at']
        search_fields = ['name', 'description']

    @admin.register(BusinessSettings)
    class BusinessSettingsAdmin(admin.ModelAdmin):
        list_display = ['business_name', 'phone', 'email', 'is_accepting_orders']
        
except ImportError:
    # Models not available yet, skip admin registration
    pass