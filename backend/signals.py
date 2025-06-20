from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, ContactMessage, CateringInquiry, Product
from .utils import EmailHelper, WhatsAppHelper
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    """
    Handle order creation - send confirmations and notifications
    """
    if created:
        try:
            # Send order confirmation email to customer
            if instance.customer_email:
                EmailHelper.send_order_confirmation(instance)
                logger.info(f"Order confirmation email sent for order {instance.order_id}")
            
            # Log order creation
            logger.info(f"New order created: {instance.order_id} by {instance.customer_name}")
            
            # You could add WhatsApp notification to business here
            # WhatsAppHelper.send_business_notification(instance)
            
        except Exception as e:
            logger.error(f"Error in order_created_handler: {e}")

@receiver(post_save, sender=Order)
def order_status_changed_handler(sender, instance, **kwargs):
    """
    Handle order status changes - notify customer
    """
    try:
        if instance.pk:  # Only for existing orders
            # Get previous instance to check if status changed
            try:
                old_instance = Order.objects.get(pk=instance.pk)
                if hasattr(old_instance, '_state') and old_instance.order_status != instance.order_status:
                    # Status changed, send notification
                    if instance.customer_email:
                        send_order_status_email(instance)
                    logger.info(f"Order {instance.order_id} status changed to {instance.order_status}")
            except Order.DoesNotExist:
                pass  # New order, handled by order_created_handler
                
    except Exception as e:
        logger.error(f"Error in order_status_changed_handler: {e}")

@receiver(post_save, sender=ContactMessage)
def contact_message_created_handler(sender, instance, created, **kwargs):
    """
    Handle new contact messages - notify admins
    """
    if created:
        try:
            # Send notification to admins
            admin_emails = [admin[1] for admin in settings.ADMINS]
            if admin_emails:
                subject = f"New Contact Message from {instance.name}"
                message = f"""
                New contact message received:
                
                Name: {instance.name}
                Email: {instance.email}
                Phone: {instance.phone}
                Subject: {instance.subject}
                
                Message:
                {instance.message}
                
                Reply to this message through the admin panel.
                """
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    admin_emails,
                    fail_silently=True
                )
                
            logger.info(f"New contact message from {instance.name}")
            
        except Exception as e:
            logger.error(f"Error in contact_message_created_handler: {e}")

@receiver(post_save, sender=CateringInquiry)
def catering_inquiry_created_handler(sender, instance, created, **kwargs):
    """
    Handle new catering inquiries - notify admins
    """
    if created:
        try:
            # Send notification to admins
            admin_emails = [admin[1] for admin in settings.ADMINS]
            if admin_emails:
                subject = f"New Catering Inquiry from {instance.name}"
                message = f"""
                New catering inquiry received:
                
                Name: {instance.name}
                Email: {instance.email}
                Phone: {instance.phone}
                Event Type: {instance.get_event_type_display()}
                Guest Count: {instance.guest_count}
                Preferred Date: {instance.preferred_date}
                Preferred Time: {instance.preferred_time}
                Location: {instance.location}
                
                Special Requirements:
                {instance.special_requirements}
                
                Respond to this inquiry through the admin panel.
                """
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    admin_emails,
                    fail_silently=True
                )
                
            logger.info(f"New catering inquiry from {instance.name} for {instance.event_type}")
            
        except Exception as e:
            logger.error(f"Error in catering_inquiry_created_handler: {e}")

@receiver(post_save, sender=Product)
def product_stock_alert_handler(sender, instance, **kwargs):
    """
    Handle low stock alerts for products
    """
    try:
        # Check if stock is low (less than 5 items)
        if instance.stock_quantity < 5 and instance.is_available:
            # Send low stock alert to admins
            admin_emails = [admin[1] for admin in settings.ADMINS]
            if admin_emails:
                subject = f"Low Stock Alert: {instance.name}"
                message = f"""
                Low stock alert for product:
                
                Product: {instance.name}
                Current Stock: {instance.stock_quantity}
                Category: {instance.category.name}
                Price: {instance.price} FCFA
                
                Please restock this item to avoid stockouts.
                """
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    admin_emails,
                    fail_silently=True
                )
                
            logger.warning(f"Low stock alert for {instance.name}: {instance.stock_quantity} remaining")
            
    except Exception as e:
        logger.error(f"Error in product_stock_alert_handler: {e}")

@receiver(pre_delete, sender=Product)
def product_delete_handler(sender, instance, **kwargs):
    """
    Handle product deletion - cleanup and logging
    """
    try:
        # Log product deletion
        logger.info(f"Product deleted: {instance.name} (ID: {instance.id})")
        
        # You could add additional cleanup here if needed
        # For example, handling related images, etc.
        
    except Exception as e:
        logger.error(f"Error in product_delete_handler: {e}")

def send_order_status_email(order):
    """
    Send order status update email to customer
    """
    try:
        if not order.customer_email:
            return
            
        status_messages = {
            'pending': 'Your order has been received and is being processed.',
            'confirmed': 'Your order has been confirmed and is being prepared.',
            'preparing': 'Your order is currently being prepared.',
            'ready': 'Your order is ready for pickup/delivery.',
            'delivered': 'Your order has been delivered. Thank you for choosing BueaDelights!',
            'cancelled': 'Your order has been cancelled. If you have any questions, please contact us.'
        }
        
        subject = f"Order Update - {order.order_id}"
        message = f"""
        Dear {order.customer_name},
        
        Your order status has been updated:
        
        Order ID: {order.order_id}
        Status: {order.get_order_status_display()}
        
        {status_messages.get(order.order_status, 'Your order status has been updated.')}
        
        If you have any questions, please contact us at {settings.WHATSAPP_NUMBER}
        
        Best regards,
        BueaDelights Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [order.customer_email],
            fail_silently=True
        )
        
    except Exception as e:
        logger.error(f"Error sending order status email: {e}")

# Additional utility signals

@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    """
    Handle new user creation - particularly for admin users
    """
    if created and instance.is_superuser:
        try:
            logger.info(f"New admin user created: {instance.username}")
            
            # You could send welcome email to new admin users here
            if instance.email:
                subject = "Welcome to BueaDelights Admin"
                message = f"""
                Welcome to BueaDelights Admin Panel!
                
                Username: {instance.username}
                Email: {instance.email}
                
                You can access the admin panel at: /admin/
                
                Best regards,
                BueaDelights System
                """
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [instance.email],
                    fail_silently=True
                )
                
        except Exception as e:
            logger.error(f"Error in user_created_handler: {e}")