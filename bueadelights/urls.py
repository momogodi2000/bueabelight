# bueadelights/urls.py - FIXED Main URL Configuration

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Health check view for Render.com
def health_check(request):
    """Health check endpoint for deployment monitoring"""
    try:
        from django.db import connection
        from backend.models import Category
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        
        # Test model access
        category_count = Category.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'categories': category_count,
            'timestamp': str(timezone.now())
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': str(timezone.now())
        }, status=500)

# Simple test view for debugging
def test_view(request):
    """Simple test view to verify Django is working"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BueaDelights - Django Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #228B22; }
            .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
            a { color: #228B22; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 BueaDelights Django is Working!</h1>
            <div class="status">
                ✅ Django application is running successfully
            </div>
            <p><strong>Available endpoints:</strong></p>
            <ul>
                <li><a href="/admin/">Admin Panel</a></li>
                <li><a href="/">Homepage</a></li>
                <li><a href="/health/">Health Check</a></li>
                <li><a href="/debug/">Debug Info</a></li>
            </ul>
            <p><em>Local Flavors at Your Fingertips</em></p>
        </div>
    </body>
    </html>
    """)

# Debug view for troubleshooting
def debug_view(request):
    """Debug information view"""
    try:
        from django.db import connection
        from backend.models import Category, Product, BusinessSettings
        from django.contrib.auth.models import User
        
        debug_info = {
            'django_version': getattr(settings, 'VERSION', 'Unknown'),
            'debug_mode': settings.DEBUG,
            'database_engine': settings.DATABASES['default']['ENGINE'],
            'static_url': settings.STATIC_URL,
            'media_url': settings.MEDIA_URL,
            'allowed_hosts': settings.ALLOWED_HOSTS,
        }
        
        # Test database
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            debug_info['database_status'] = 'Connected'
            
            # Count objects
            debug_info['categories'] = Category.objects.count()
            debug_info['products'] = Product.objects.count()
            debug_info['users'] = User.objects.count()
            debug_info['business_settings'] = BusinessSettings.objects.count()
            
        except Exception as e:
            debug_info['database_status'] = f'Error: {str(e)}'
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health and debugging endpoints
    path('health/', health_check, name='health_check'),
    path('test/', test_view, name='test'),
    path('debug/', debug_view, name='debug'),
    
    # Main application URLs
    path('', include('backend.urls')),
]

# Serve media files in both development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # In production, still serve media files through Django (WhiteNoise handles static)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Import timezone at the top after the initial imports
from django.utils import timezone