from django.urls import path
from . import views
from . import views_csv
from . import views_billing

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alt'),
    
    # Products & Inventory
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    
    # Purchases
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
    
    # Stock Adjustments
    path('adjustments/', views.stock_adjustment_list, name='stock_adjustment_list'),
    path('adjustments/add/', views.add_stock_adjustment, name='add_stock_adjustment'),
    
    # QR Code Features
    path('qr/', views.qr_dashboard, name='qr_dashboard'),
    path('qr/generate/', views.generate_qr_labels, name='generate_qr_labels'),
    path('qr/scan/', views.scan_qr_code_page, name='scan_qr_code_page'),
    path('qr/history/', views.scan_event_list, name='scan_event_list'),
    path('products/<int:pk>/label/', views.print_qr_label, name='print_qr_label'),
    
    # API endpoints
    path('api/scan_product/', views.api_scan_product, name='api_scan_product'),
    path('api/add_to_cart/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/verify_stock/', views.api_verify_stock, name='api_verify_stock'),
    path('api/cart_status/', views.api_cart_status, name='api_cart_status'),
    
    # Cart & Orders
    path('cart/', views.cart_summary, name='cart_summary'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/stock/', views.stock_report, name='stock_report'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),
    
    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('settings/', views.system_settings, name='system_settings'),
    path('api-testing/', views.api_testing, name='api_testing'),
    
    # Phase 3: Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/product/<int:pk>/', views.product_analytics, name='product_analytics'),
    path('notifications/', views.notifications_center, name='notifications_center'),
    path('alerts/', views.alert_management, name='alert_management'),
    path('api/analytics/', views.api_analytics_data, name='api_analytics_data'),
    path('api/mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/dismiss-alert/<int:alert_id>/', views.dismiss_alert, name='dismiss_alert'),
    path('api/trigger-alert-check/', views.trigger_alert_check, name='trigger_alert_check'),
    
    # Export endpoints
    path('export/stock-csv/', views.export_stock_csv, name='export_stock_csv'),
    path('export/analytics-pdf/', views.export_analytics_pdf, name='export_analytics_pdf'),
    
    # Bulk import
    path('bulk-import/', views.bulk_import_products, name='bulk_import_products'),
    
    # CSV Import/Export
    path('csv-import/', views_csv.csv_import_page, name='csv_import'),
    path('csv-export/<str:export_type>/', views_csv.csv_export, name='csv_export'),
    path('csv-template/<str:template_type>/', views_csv.download_template, name='download_template'),
    
    # Billing System
    path('billing/', views_billing.billing_page, name='billing_page'),
    path('bills/', views_billing.bills_list, name='bills_list'),
    path('bill/<int:bill_id>/print/', views_billing.print_bill, name='print_bill'),
    path('bill/<int:bill_id>/pdf/', views_billing.download_bill_pdf, name='download_bill_pdf'),
    path('api/add-to-bill/', views_billing.add_to_current_bill, name='add_to_bill'),
    path('api/get-bill/', views_billing.get_current_bill, name='get_current_bill'),
    path('api/complete-bill/', views_billing.complete_bill, name='complete_bill'),
    path('api/remove-from-bill/', views_billing.remove_from_bill, name='remove_from_bill'),
]