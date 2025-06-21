# bueadelights/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Simple test view
def test_view(request):
    return HttpResponse("✅ Django is working! <a href='/admin/'>Admin</a> | <a href='/debug/'>Debug</a>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test_view, name='test'),
    path('', include('backend.urls')),
]

# Serve media files in development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Also serve static files in production with WhiteNoise fallback
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)