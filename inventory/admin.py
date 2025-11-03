from django.contrib import admin
from .models import (
    Product, Employee, Purchase, StockAdjustment, Supplier, Category,
    ScanEvent, Order, OrderItem, ProductAnalytics, InventoryAlert, 
    SystemNotification, SystemSettings
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'quantity_in_stock', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'role', 'email', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['product', 'supplier', 'quantity', 'purchase_price', 'purchase_date']
    list_filter = ['purchase_date', 'supplier']
    search_fields = ['product__name']

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_change', 'reason', 'adjustment_date', 'created_by']
    list_filter = ['reason', 'adjustment_date']
    search_fields = ['product__name']

@admin.register(ScanEvent)
class ScanEventAdmin(admin.ModelAdmin):
    list_display = ['product', 'scan_type', 'quantity', 'timestamp', 'user']
    list_filter = ['scan_type', 'timestamp']
    search_fields = ['product__name']
    readonly_fields = ['timestamp']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['product__name', 'order__id']

@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'scan_count', 'revenue', 'velocity_score']
    list_filter = ['date']
    search_fields = ['product__name']

@admin.register(InventoryAlert)
class InventoryAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_type', 'threshold', 'is_active', 'created_at']
    list_filter = ['alert_type', 'is_active', 'created_at']
    search_fields = ['product__name']

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message']

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'currency', 'low_stock_threshold', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


