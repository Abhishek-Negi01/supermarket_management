from django.contrib.auth.models import User
from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import os

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField()
    expiry_date = models.DateField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        
        # Save first to get ID
        super().save(*args, **kwargs)
        
        # Generate QR code for new products or if forced
        if is_new or not self.qr_code:
            self.generate_qr_code()
    
    def delete(self, *args, **kwargs):
        # Delete QR code file before deleting product
        if self.qr_code:
            try:
                import os
                if os.path.exists(self.qr_code.path):
                    os.remove(self.qr_code.path)
            except:
                pass
        super().delete(*args, **kwargs)
    
    def generate_qr_code(self):
        try:
            import os
            from django.conf import settings
            
            # Delete existing QR file if it exists
            if self.qr_code:
                try:
                    os.remove(self.qr_code.path)
                except:
                    pass
            
            # Generate QR code
            qr_content = f"{self.id},{self.name},{self.price}"
            qr_img = qrcode.make(qr_content)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            
            # Use consistent filename format
            filename = f'product_{self.id}_qr.png'
            
            # Save QR code
            self.qr_code.save(filename, File(buffer), save=False)
            
            # Update the database record
            Product.objects.filter(pk=self.pk).update(qr_code=self.qr_code)
            
        except Exception as e:
            print(f"QR Code generation failed: {e}")

class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, unique=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_supplier_name')
        ]

    def __str__(self):
        return self.name

class Employee(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('CASHIER', 'Cashier'),
        ('STOCK', 'Stock Keeper'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CASHIER')
    email = models.EmailField(blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Purchase {self.product.name} - {self.quantity}'

class StockAdjustment(models.Model):
    REASON_CHOICES = [
        ('DAMAGE', 'Damaged'),
        ('EXPIRED', 'Expired'),
        ('THEFT', 'Theft'),
        ('COUNT', 'Stock Count'),
        ('OTHER', 'Other'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_change = models.IntegerField(help_text="Positive for addition, negative for subtraction")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='OTHER')
    notes = models.TextField(blank=True)
    adjustment_date = models.DateField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Stock Adjustment for {self.product.name} on {self.adjustment_date}'

class ScanEvent(models.Model):
    SCAN_TYPE_CHOICES = [
        ('BILL', 'Billing'),
        ('STOCK', 'Stock Check'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('INVENTORY', 'Inventory Count'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    remarks = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.scan_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order #{self.id} - {self.status}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

# Phase 3: Analytics Models
class ProductAnalytics(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField()
    scan_count = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    velocity_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.product.name} - {self.date}'

class InventoryAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('FAST_MOVING', 'Fast Moving'),
        ('SLOW_MOVING', 'Slow Moving'),
        ('REORDER', 'Reorder Required'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.IntegerField()
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'alert_type']
    
    def __str__(self):
        return f'{self.product.name} - {self.alert_type}'

class SystemNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('ALERT', 'Alert'),
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('SUCCESS', 'Success'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='INFO')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} - {self.created_at.strftime("%Y-%m-%d")}'

# Phase 3: System Settings Model
class SystemSettings(models.Model):
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee (₹)'),
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
    ]
    
    # General Settings
    low_stock_threshold = models.PositiveIntegerField(default=10, help_text="Alert when stock falls below this number")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    company_name = models.CharField(max_length=200, default='SuperMarket Pro')
    
    # QR Settings
    auto_generate_qr = models.BooleanField(default=True, help_text="Auto-generate QR codes for new products")
    qr_format = models.CharField(max_length=100, default='ID,Name,Price', help_text="QR code data format")
    
    # Alert Settings
    enable_email_alerts = models.BooleanField(default=False)
    alert_check_interval = models.PositiveIntegerField(default=60, help_text="Alert check interval in minutes")
    
    # System Info (Read-only)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"System Settings - {self.company_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and SystemSettings.objects.exists():
            raise ValueError("Only one SystemSettings instance is allowed")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

# Signal to automatically delete QR files when products are deleted
@receiver(post_delete, sender=Product)
def delete_qr_file(sender, instance, **kwargs):
    """Delete QR code file when product is deleted"""
    if instance.qr_code:
        try:
            if os.path.exists(instance.qr_code.path):
                os.remove(instance.qr_code.path)
        except:
            pass

# Bill Models for Receipt Generation
class Bill(models.Model):
    bill_number = models.CharField(max_length=20, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bills_created')
    customer_name = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('CASH', 'Cash'), ('CARD', 'Card'), ('UPI', 'UPI')], default='CASH')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Bill #{self.bill_number}'
    
    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate bill number: BILL-YYYYMMDD-XXXX
            from datetime import datetime
            today = datetime.now().strftime('%Y%m%d')
            last_bill = Bill.objects.filter(bill_number__startswith=f'BILL-{today}').order_by('-bill_number').first()
            if last_bill:
                last_num = int(last_bill.bill_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.bill_number = f'BILL-{today}-{new_num:04d}'
        super().save(*args, **kwargs)

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

# Signal to auto-update analytics after scan
@receiver(post_save, sender=ScanEvent)
def update_analytics_on_scan(sender, instance, created, **kwargs):
    """Auto-update analytics when product is scanned for billing"""
    if created and instance.scan_type == 'BILL':
        try:
            from .analytics import InventoryAnalytics
            InventoryAnalytics.update_daily_analytics()
            InventoryAnalytics.check_inventory_alerts()
        except Exception as e:
            print(f"Analytics update failed: {e}")
            import traceback
            traceback.print_exc()