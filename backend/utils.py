import urllib.parse
import requests
import qrcode
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailHelper:
    """Helper class for email notifications"""
    
    WHOLESALER_EMAIL = "Folefacvivianekokibe@gmail.com"
    
    @staticmethod
    def send_order_notification(order):
        """Send order notification email to wholesaler"""
        try:
            # Email subject
            subject = f"🍽️ New Order #{order.order_id} - {order.customer_name}"
            
            # Create the email context
            context = {
                'order': order,
                'business_name': settings.BUSINESS_NAME,
                'items': order.items.all(),
                'total_amount': order.total_amount,
                'delivery_fee': order.delivery_fee,
                'grand_total': order.get_total_with_delivery(),
            }
            
            # Create HTML email content
            html_content = EmailHelper._create_order_html_email(context)
            
            # Create plain text version
            text_content = EmailHelper._create_order_text_email(context)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[EmailHelper.WHOLESALER_EMAIL],
                reply_to=[order.customer_email] if order.customer_email else None
            )
            
            # Attach HTML content
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Order notification email sent successfully for order {order.order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order notification email for order {order.order_id}: {str(e)}")
            return False
    
    @staticmethod
    def _create_order_html_email(context):
        """Create HTML email content for order notification"""
        order = context['order']
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Order Notification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #228B22, #32CD32); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .order-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .order-info h2 {{ margin-top: 0; color: #228B22; border-bottom: 2px solid #228B22; padding-bottom: 10px; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0; }}
                .info-item {{ background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #228B22; }}
                .info-label {{ font-weight: bold; color: #666; font-size: 12px; text-transform: uppercase; }}
                .info-value {{ font-size: 16px; color: #333; margin-top: 5px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .items-table th {{ background: #228B22; color: white; padding: 12px; text-align: left; }}
                .items-table td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
                .items-table tr:nth-child(even) {{ background: #f8f9fa; }}
                .total-section {{ background: #228B22; color: white; padding: 20px; border-radius: 8px; margin-top: 20px; }}
                .total-row {{ display: flex; justify-content: space-between; margin: 5px 0; }}
                .total-row.grand {{ font-size: 18px; font-weight: bold; border-top: 2px solid white; padding-top: 10px; margin-top: 10px; }}
                .payment-method {{ display: inline-block; background: #FFD700; color: #333; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
                .urgency {{ background: #DC143C; color: white; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
                @media (max-width: 600px) {{
                    .info-grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍽️ New Order Received!</h1>
                    <p>Order #{order.order_id}</p>
                </div>
                
                <div class="urgency">
                    ⚡ <strong>Action Required:</strong> New order needs confirmation and processing
                </div>
                
                <div class="order-info">
                    <h2>📋 Order Details</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Order ID</div>
                            <div class="info-value">{order.order_id}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Order Date</div>
                            <div class="info-value">{order.created_at.strftime('%B %d, %Y at %I:%M %p')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Payment Method</div>
                            <div class="info-value">
                                <span class="payment-method">{order.get_payment_method_display()}</span>
                            </div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Payment Status</div>
                            <div class="info-value">{order.get_payment_status_display()}</div>
                        </div>
                    </div>
                </div>
                
                <div class="order-info">
                    <h2>👤 Customer Information</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Customer Name</div>
                            <div class="info-value">{order.customer_name}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Phone Number</div>
                            <div class="info-value">
                                <a href="https://wa.me/{order.customer_phone.replace('+', '').replace(' ', '')}" 
                                   style="color: #25D366; text-decoration: none;">
                                    📱 {order.customer_phone}
                                </a>
                            </div>
                        </div>
                        {f'''
                        <div class="info-item">
                            <div class="info-label">Email</div>
                            <div class="info-value">
                                <a href="mailto:{order.customer_email}" style="color: #228B22;">
                                    ✉️ {order.customer_email}
                                </a>
                            </div>
                        </div>
                        ''' if order.customer_email else ''}
                        <div class="info-item" style="grid-column: 1 / -1;">
                            <div class="info-label">Delivery Location</div>
                            <div class="info-value">📍 {order.customer_location}</div>
                        </div>
                    </div>
                </div>
                
                <div class="order-info">
                    <h2>🛒 Ordered Items</h2>
                    <table class="items-table">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Add order items
        for item in context['items']:
            html_content += f"""
                            <tr>
                                <td><strong>{item.product.name}</strong></td>
                                <td>{item.quantity}</td>
                                <td>{item.unit_price:,.0f} FCFA</td>
                                <td><strong>{item.total_price:,.0f} FCFA</strong></td>
                            </tr>
            """
        
        html_content += f"""
                        </tbody>
                    </table>
                </div>
                
                <div class="total-section">
                    <div class="total-row">
                        <span>Subtotal:</span>
                        <span>{context['total_amount']:,.0f} FCFA</span>
                    </div>
                    <div class="total-row">
                        <span>Delivery Fee:</span>
                        <span>{context['delivery_fee']:,.0f} FCFA</span>
                    </div>
                    <div class="total-row grand">
                        <span>TOTAL AMOUNT:</span>
                        <span>{context['grand_total']:,.0f} FCFA</span>
                    </div>
                </div>
        """
        
        if order.special_instructions:
            html_content += f"""
                <div class="order-info">
                    <h2>📝 Special Instructions</h2>
                    <p style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #FFD700;">
                        {order.special_instructions}
                    </p>
                </div>
            """
        
        html_content += f"""
                <div class="urgency">
                    <strong>⏰ Next Steps:</strong><br>
                    1. Confirm order availability<br>
                    2. Contact customer for delivery time<br>
                    3. Update order status in admin panel
                </div>
                
                <div class="footer">
                    <p>This email was automatically generated by {context['business_name']} order system.</p>
                    <p>Please login to the admin panel to manage this order.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    @staticmethod
    def _create_order_text_email(context):
        """Create plain text email content for order notification"""
        order = context['order']
        
        text_content = f"""
🍽️ NEW ORDER NOTIFICATION - {context['business_name']}
{'='*50}

⚡ URGENT: New order requires immediate attention!

ORDER DETAILS:
Order ID: {order.order_id}
Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}
Payment Method: {order.get_payment_method_display()}
Payment Status: {order.get_payment_status_display()}

CUSTOMER INFORMATION:
Name: {order.customer_name}
Phone: {order.customer_phone}
{'Email: ' + order.customer_email if order.customer_email else 'Email: Not provided'}
Location: {order.customer_location}

ORDERED ITEMS:
{'-'*30}
"""
        
        for item in context['items']:
            text_content += f"{item.quantity}x {item.product.name} - {item.total_price:,.0f} FCFA\n"
        
        text_content += f"""
{'-'*30}

PAYMENT SUMMARY:
Subtotal: {context['total_amount']:,.0f} FCFA
Delivery Fee: {context['delivery_fee']:,.0f} FCFA
TOTAL: {context['grand_total']:,.0f} FCFA
"""
        
        if order.special_instructions:
            text_content += f"""
SPECIAL INSTRUCTIONS:
{order.special_instructions}
"""
        
        text_content += f"""
NEXT STEPS:
1. Confirm order availability
2. Contact customer for delivery time
3. Update order status in admin panel

WhatsApp Customer: https://wa.me/{order.customer_phone.replace('+', '').replace(' ', '')}

This email was automatically generated by {context['business_name']} order system.
Please login to the admin panel to manage this order.
        """
        
        return text_content

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
    """Helper class for Noupia payment processing"""
    
    @staticmethod
    def process_payment(amount, phone, transaction_id):
        """Process payment with Noupia API"""
        try:
            # This is a placeholder for actual Noupia API integration
            # Replace with actual Noupia API calls when available
            
            api_url = "https://api.noupia.com/v1/payments"  # Placeholder URL
            
            payload = {
                "merchant_id": settings.NOUPIA_MERCHANT_ID,
                "api_key": settings.NOUPIA_API_KEY,
                "amount": amount,
                "phone": phone,
                "transaction_id": transaction_id,
                "currency": "XAF",
                "description": f"BueaDelights Order Payment - {transaction_id}"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.NOUPIA_API_KEY}"
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "reference": response.json().get("reference"),
                    "message": "Payment initiated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Payment failed: {response.json().get('message', 'Unknown error')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing payment: {str(e)}"
            }

class ReceiptGenerator:
    """Helper class for generating PDF receipts"""
    
    @staticmethod
    def generate_pdf_receipt(order, buffer):
        """Generate PDF receipt for order"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Header
            title_style = styles['Title']
            title_style.alignment = TA_CENTER
            story.append(Paragraph(f"{settings.BUSINESS_NAME}", title_style))
            story.append(Paragraph("ORDER RECEIPT", title_style))
            story.append(Spacer(1, 20))
            
            # Order information
            order_info = [
                ['Order ID:', order.order_id],
                ['Date:', order.created_at.strftime('%B %d, %Y at %I:%M %p')],
                ['Customer:', order.customer_name],
                ['Phone:', order.customer_phone],
                ['Location:', order.customer_location],
                ['Payment Method:', order.get_payment_method_display()],
            ]
            
            order_table = Table(order_info, colWidths=[2*inch, 4*inch])
            order_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(order_table)
            story.append(Spacer(1, 20))
            
            # Order items
            items_data = [['Item', 'Qty', 'Unit Price', 'Total']]
            for item in order.items.all():
                items_data.append([
                    item.product.name,
                    str(item.quantity),
                    f"{item.unit_price:,.0f} FCFA",
                    f"{item.total_price:,.0f} FCFA"
                ])
            
            items_table = Table(items_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 20))
            
            # Totals
            totals_data = [
                ['Subtotal:', f"{order.total_amount:,.0f} FCFA"],
                ['Delivery Fee:', f"{order.delivery_fee:,.0f} FCFA"],
                ['TOTAL:', f"{order.get_total_with_delivery():,.0f} FCFA"]
            ]
            
            totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ]))
            
            story.append(totals_table)
            
            if order.special_instructions:
                story.append(Spacer(1, 20))
                story.append(Paragraph("Special Instructions:", styles['Heading3']))
                story.append(Paragraph(order.special_instructions, styles['Normal']))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = styles['Normal']
            footer_style.alignment = TA_CENTER
            story.append(Paragraph(f"Thank you for choosing {settings.BUSINESS_NAME}!", footer_style))
            
            # Build PDF
            doc.build(story)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF receipt for order {order.order_id}: {str(e)}")
            raise e