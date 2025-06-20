import urllib.parse
import requests
import qrcode
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.mail import send_mail
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json
from datetime import datetime

class WhatsAppHelper:
    """Helper class for WhatsApp integration"""
    
    @staticmethod
    def create_order_message(order):
        """Create WhatsApp message for order."""
        message = f"🍽️ *New Order from {settings.BUSINESS_NAME}*\n\n"
        message += f"📋 Order ID: {order.order_id}\n"
        message += f"👤 Customer: {order.customer_name}\n"
        message += f"📱 Phone: {order.customer_phone}\n"
        message += f"📍 Location: {order.customer_location}\n\n"
        
        message += "🛒 *Order Items:*\n"
        for item in order.items.all():
            message += f"• {item.quantity}x {item.product.name} - {item.total_price:,.0f} FCFA\n"
        
        message += f"\n💰 *Subtotal: {order.total_amount:,.0f} FCFA*\n"
        message += f"🚚 *Delivery Fee: {order.delivery_fee:,.0f} FCFA*\n"
        message += f"💳 *Total: {order.get_total_with_delivery():,.0f} FCFA*\n"
        message += f"💳 *Payment: {order.get_payment_method_display()}*\n"
        
        if order.special_instructions:
            message += f"\n📝 *Special Instructions:*\n{order.special_instructions}\n"
        
        message += f"\n⏰ *Order placed:* {order.created_at.strftime('%d/%m/%Y at %H:%M')}\n"
        message += f"\n✅ Please confirm this order and provide delivery time estimate."
        
        return message
    
    @staticmethod
    def create_whatsapp_url(phone_number, message):
        """Create WhatsApp URL with message."""
        # Clean phone number
        phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded_message}"
    
    @staticmethod
    def create_order_whatsapp_url(order):
        """Get WhatsApp URL for order."""
        message = WhatsAppHelper.create_order_message(order)
        return WhatsAppHelper.create_whatsapp_url(settings.WHATSAPP_NUMBER, message)
    
    @staticmethod
    def get_business_whatsapp_url(message=""):
        """Get business WhatsApp URL."""
        default_message = f"Hello {settings.BUSINESS_NAME}! I'm interested in your services."
        final_message = message if message else default_message
        return WhatsAppHelper.create_whatsapp_url(settings.WHATSAPP_NUMBER, final_message)

class NoupiaPaymentHelper:
    """Helper class for Noupia mobile money integration"""
    
    BASE_URL = "https://api.noupia.com"  # Replace with actual Noupia API URL
    
    @staticmethod
    def process_payment(amount, phone, transaction_id, description="BueaDelights Order"):
        """Process mobile money payment via Noupia"""
        try:
            # Clean phone number
            clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            payload = {
                'merchant_id': settings.NOUPIA_MERCHANT_ID,
                'api_key': settings.NOUPIA_API_KEY,
                'transaction_id': transaction_id,
                'amount': float(amount),
                'phone': clean_phone,
                'description': description,
                'callback_url': f"{settings.ALLOWED_HOSTS[0]}/payment/callback/",
                'return_url': f"{settings.ALLOWED_HOSTS[0]}/order-confirmation/"
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.NOUPIA_API_KEY}'
            }
            
            response = requests.post(
                f"{NoupiaPaymentHelper.BASE_URL}/payments/initiate",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'reference': data.get('reference'),
                    'message': 'Payment initiated successfully',
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'message': f'Payment failed: {response.text}',
                    'status_code': response.status_code
                }
        
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Payment error: {str(e)}'
            }
    
    @staticmethod
    def verify_payment(transaction_id):
        """Verify payment status"""
        try:
            headers = {
                'Authorization': f'Bearer {settings.NOUPIA_API_KEY}'
            }
            
            response = requests.get(
                f"{NoupiaPaymentHelper.BASE_URL}/payments/verify/{transaction_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data.get('status'),
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'message': 'Verification failed'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

class ReceiptGenerator:
    """Generate PDF receipts for orders"""
    
    @staticmethod
    def generate_pdf_receipt(order, buffer):
        """Generate PDF receipt for order"""
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = styles['Title']
        title_style.alignment = TA_CENTER
        
        heading_style = styles['Heading2']
        heading_style.alignment = TA_LEFT
        
        normal_style = styles['Normal']
        
        # Header
        story.append(Paragraph(f"<b>{settings.BUSINESS_NAME}</b>", title_style))
        story.append(Paragraph("Local Flavors at Your Fingertips", normal_style))
        story.append(Spacer(1, 20))
        
        # Receipt title
        story.append(Paragraph(f"<b>RECEIPT - Order #{order.order_id}</b>", heading_style))
        story.append(Spacer(1, 20))
        
        # Customer information
        customer_data = [
            ['Customer Name:', order.customer_name],
            ['Phone:', order.customer_phone],
            ['Email:', order.customer_email or 'N/A'],
            ['Location:', order.customer_location],
            ['Order Date:', order.created_at.strftime('%d/%m/%Y %H:%M')],
            ['Payment Method:', order.get_payment_method_display()],
            ['Payment Status:', order.get_payment_status_display()],
        ]
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        
        story.append(customer_table)
        story.append(Spacer(1, 20))
        
        # Order items
        story.append(Paragraph("<b>Order Items:</b>", heading_style))
        story.append(Spacer(1, 10))
        
        items_data = [['Item', 'Quantity', 'Unit Price', 'Total']]
        
        for item in order.items.all():
            items_data.append([
                item.product.name,
                str(item.quantity),
                f"{item.unit_price:,.0f} FCFA",
                f"{item.total_price:,.0f} FCFA"
            ])
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Item names left-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Totals
        totals_data = [
            ['Subtotal:', f"{order.total_amount:,.0f} FCFA"],
            ['Delivery Fee:', f"{order.delivery_fee:,.0f} FCFA"],
            ['<b>Total Amount:</b>', f"<b>{order.get_total_with_delivery():,.0f} FCFA</b>"],
        ]
        
        totals_table = Table(totals_data, colWidths=[2*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 30))
        
        # Special instructions
        if order.special_instructions:
            story.append(Paragraph("<b>Special Instructions:</b>", heading_style))
            story.append(Paragraph(order.special_instructions, normal_style))
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Thank you for choosing BueaDelights!", normal_style))
        story.append(Paragraph(f"Contact us: {settings.WHATSAPP_NUMBER}", normal_style))
        story.append(Paragraph("Follow us on social media for updates!", normal_style))
        
        # Build PDF
        doc.build(story)
        return buffer

class EmailHelper:
    """Helper class for email functionality"""
    
    @staticmethod
    def send_order_confirmation(order):
        """Send order confirmation email"""
        if not order.customer_email:
            return False
        
        subject = f"Order Confirmation - {order.order_id}"
        message = f"""
        Dear {order.customer_name},
        
        Thank you for your order from BueaDelights!
        
        Order Details:
        Order ID: {order.order_id}
        Total Amount: {order.get_total_with_delivery():,.0f} FCFA
        Payment Method: {order.get_payment_method_display()}
        
        We will contact you shortly to confirm your order and provide delivery details.
        
        Best regards,
        BueaDelights Team
        Phone: {settings.WHATSAPP_NUMBER}
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [order.customer_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, reset_link):
        """Send password reset email"""
        subject = "Password Reset - BueaDelights Admin"
        message = f"""
        Hello {user.username},
        
        You requested a password reset for your BueaDelights admin account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 24 hours.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        BueaDelights System
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Password reset email failed: {e}")
            return False

class QRCodeGenerator:
    """Generate QR codes for orders"""
    
    @staticmethod
    def generate_order_qr(order):
        """Generate QR code for order"""
        qr_content = f"""
Order ID: {order.order_id}
Customer: {order.customer_name}
Phone: {order.customer_phone}
Total: {order.get_total_with_delivery():,.0f} FCFA
Date: {order.created_at.strftime('%d/%m/%Y %H:%M')}
        """.strip()
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img