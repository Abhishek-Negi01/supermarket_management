from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Product, InventoryAlert, SystemNotification

class EmailNotificationService:
    
    @staticmethod
    def send_low_stock_alert(product):
        subject = f'Low Stock Alert: {product.name}'
        message = f'{product.name} is running low with only {product.quantity_in_stock} units remaining.'
        
        html_message = render_to_string('inventory/emails/low_stock_alert.html', {
            'product': product,
            'stock_level': product.quantity_in_stock
        })
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    @staticmethod
    def send_out_of_stock_alert(product):
        subject = f'URGENT: Out of Stock - {product.name}'
        message = f'{product.name} is completely out of stock!'
        
        html_message = render_to_string('inventory/emails/out_of_stock_alert.html', {
            'product': product
        })
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    @staticmethod
    def send_daily_summary():
        low_stock_products = Product.objects.filter(quantity_in_stock__lt=10)
        active_alerts = InventoryAlert.objects.filter(is_active=True)
        
        if low_stock_products.exists() or active_alerts.exists():
            subject = 'Daily Inventory Summary'
            html_message = render_to_string('inventory/emails/daily_summary.html', {
                'low_stock_products': low_stock_products,
                'active_alerts': active_alerts,
                'total_alerts': active_alerts.count()
            })
            
            try:
                send_mail(
                    subject=subject,
                    message='Daily inventory summary attached.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    html_message=html_message,
                    fail_silently=False,
                )
                return True
            except Exception as e:
                print(f"Daily summary email failed: {e}")
                return False
        return False