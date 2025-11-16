from django.db.models import Count, Sum, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Product, ScanEvent, ProductAnalytics, InventoryAlert, SystemNotification
from django.contrib.auth.models import User

class InventoryAnalytics:
    
    @staticmethod
    def calculate_product_velocity(product, days=30):
        """Calculate product velocity (scans per day)"""
        end_datetime = timezone.now()
        start_datetime = end_datetime - timedelta(days=days)
        
        scan_count = ScanEvent.objects.filter(
            product=product,
            timestamp__gte=start_datetime,
            timestamp__lte=end_datetime,
            scan_type='BILL'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return scan_count / days if days > 0 else 0
    
    @staticmethod
    def get_fast_moving_products(limit=10):
        """Get top fast-moving products"""
        products = Product.objects.all()
        product_velocities = []
        
        for product in products:
            velocity = InventoryAnalytics.calculate_product_velocity(product, 7)
            if velocity > 0:
                product_velocities.append({
                    'product': product,
                    'velocity': velocity,
                    'current_stock': product.quantity_in_stock
                })
        
        return sorted(product_velocities, key=lambda x: x['velocity'], reverse=True)[:limit]
    
    @staticmethod
    def get_low_stock_products(threshold=10):
        """Get products with low stock"""
        return Product.objects.filter(quantity_in_stock__lt=threshold)
    
    @staticmethod
    def calculate_reorder_point(product, lead_time_days=7, safety_stock_days=3):
        """Calculate reorder point for a product"""
        daily_usage = InventoryAnalytics.calculate_product_velocity(product)
        return int((daily_usage * lead_time_days) + (daily_usage * safety_stock_days))
    
    @staticmethod
    def update_daily_analytics():
        """Update daily analytics for all products"""
        today = timezone.now().date()
        
        for product in Product.objects.all():
            # Get today's scan data
            today_scans = ScanEvent.objects.filter(
                product=product,
                timestamp__date=today,
                scan_type='BILL'
            ).aggregate(
                count=Count('id'),
                quantity=Sum('quantity')
            )
            
            scan_count = today_scans['quantity'] or 0
            revenue = scan_count * product.price
            velocity = InventoryAnalytics.calculate_product_velocity(product, 7)  # 7-day velocity
            
            # Update or create analytics record
            ProductAnalytics.objects.update_or_create(
                product=product,
                date=today,
                defaults={
                    'scan_count': scan_count,
                    'revenue': revenue,
                    'velocity_score': velocity
                }
            )
    
    @staticmethod
    def check_inventory_alerts():
        """Check and create inventory alerts"""
        alerts_created = 0
        
        # Check low stock alerts
        for product in Product.objects.all():
            # Low stock alert
            if product.quantity_in_stock < 10:
                alert, created = InventoryAlert.objects.get_or_create(
                    product=product,
                    alert_type='LOW_STOCK',
                    defaults={'threshold': 10}
                )
                if created:
                    InventoryAnalytics.create_notification(
                        title=f'Low Stock Alert: {product.name}',
                        message=f'{product.name} has only {product.quantity_in_stock} units left.',
                        notification_type='WARNING'
                    )
                    alerts_created += 1
            
            # Out of stock alert
            if product.quantity_in_stock == 0:
                alert, created = InventoryAlert.objects.get_or_create(
                    product=product,
                    alert_type='OUT_OF_STOCK',
                    defaults={'threshold': 0}
                )
                if created:
                    InventoryAnalytics.create_notification(
                        title=f'Out of Stock: {product.name}',
                        message=f'{product.name} is completely out of stock!',
                        notification_type='ALERT'
                    )
                    alerts_created += 1
            
            # Fast moving product alert
            velocity = InventoryAnalytics.calculate_product_velocity(product, 7)
            if velocity > 1:  # More than 1 unit per day
                alert, created = InventoryAlert.objects.get_or_create(
                    product=product,
                    alert_type='FAST_MOVING',
                    defaults={'threshold': 5}
                )
                if created:
                    InventoryAnalytics.create_notification(
                        title=f'Fast Moving Product: {product.name}',
                        message=f'{product.name} is selling {velocity:.1f} units per day.',
                        notification_type='INFO'
                    )
                    alerts_created += 1
        
        return alerts_created
    
    @staticmethod
    def create_notification(title, message, notification_type='INFO', user=None):
        """Create system notification"""
        return SystemNotification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
    
    @staticmethod
    def get_sales_trends(days=30):
        """Get sales trends for the last N days"""
        end_datetime = timezone.now()
        start_datetime = end_datetime - timedelta(days=days)
        
        daily_sales = ScanEvent.objects.filter(
            timestamp__gte=start_datetime,
            timestamp__lte=end_datetime,
            scan_type='BILL'
        ).extra(
            select={'day': 'DATE(timestamp)'}
        ).values('day').annotate(
            total_scans=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('product__price'))
        ).order_by('day')
        
        return list(daily_sales)