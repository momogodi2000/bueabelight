from .models import BusinessSettings, Category

def business_context(request):
    """Add business settings and common data to all templates."""
    try:
        business = BusinessSettings.objects.first()
    except BusinessSettings.DoesNotExist:
        business = None
    
    categories = Category.objects.filter(is_active=True)
    
    # Cart context
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values()) if cart else 0
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values()) if cart else 0
    
    return {
        'business': business,
        'categories': categories,
        'cart': cart,
        'cart_count': cart_count,
        'cart_total': cart_total,
    }