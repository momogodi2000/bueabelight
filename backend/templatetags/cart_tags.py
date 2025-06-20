from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def cart_item_count(cart):
    """Return the total number of items in cart."""
    if not cart:
        return 0
    return sum(item['quantity'] for item in cart.values())

@register.filter
def cart_total(cart):
    """Return the total price of items in cart."""
    if not cart:
        return 0
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return total

@register.simple_tag
def whatsapp_message(order_details):
    """Generate WhatsApp message for order."""
    message = f"Hello! I'd like to place an order:\n\n"
    message += f"Order Details:\n{order_details}\n\n"
    message += "Please confirm my order. Thank you!"
    return message




from django.template import Library
from ..utils import WhatsAppHelper

register = Library()

@register.simple_tag
def whatsapp_url(message=""):
    """Generate WhatsApp URL."""
    return WhatsAppHelper.get_business_whatsapp_url(message)

@register.simple_tag
def whatsapp_order_url(order):
    """Generate WhatsApp URL for order."""
    message = WhatsAppHelper.create_order_message(order)
    return WhatsAppHelper.get_business_whatsapp_url(message)