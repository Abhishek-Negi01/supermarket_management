from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Purchase, StockAdjustment, ScanEvent, Order, OrderItem, Category, Supplier, Employee, ProductAnalytics, InventoryAlert, SystemNotification
from .forms import ProductForm, PurchaseForm, StockAdjustmentForm
from .cart_utils import get_cart, clear_cart

def staff_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated_view_func


def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@staff_required
def add_product(request):
    if request.method ==  'POST':
        form = ProductForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('product_list')
        
    else:
        form = ProductForm()
    
    return render(request,'inventory/add_product.html',{'form':form})

@staff_required
def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()
            # Update product stock
            purchase.product.quantity_in_stock += purchase.quantity
            purchase.product.save()
            return redirect('purchase_list')
    else:
        form = PurchaseForm()
    return render(request, 'inventory/add_purchase.html', {'form': form})



def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-purchase_date')
    
    # Calculate purchase statistics
    total_value = sum(p.purchase_price * p.quantity for p in purchases)
    average_purchase = total_value / len(purchases) if purchases else 0
    
    # Monthly purchases
    from datetime import datetime
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_purchases = purchases.filter(
        purchase_date__month=current_month,
        purchase_date__year=current_year
    ).count()
    
    context = {
        'purchases': purchases,
        'total_value': total_value,
        'average_purchase': average_purchase,
        'monthly_purchases': monthly_purchases
    }
    return render(request, 'inventory/purchase_list.html', context)


@staff_required
def add_stock_adjustment(request):
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.created_by = request.user
            adjustment.save()
            
            # Update product stock
            product = adjustment.product
            new_stock = product.quantity_in_stock + adjustment.quantity_change
            
            # Prevent negative stock
            if new_stock < 0:
                messages.error(request, f'Cannot reduce stock below 0. Current stock: {product.quantity_in_stock}')
                return render(request, 'inventory/add_stock_adjustment.html', {'form': form})
            
            product.quantity_in_stock = new_stock
            product.save()
            
            messages.success(request, f'Stock adjusted successfully. New stock: {product.quantity_in_stock} units')
            return redirect('stock_adjustment_list')
    else:
        form = StockAdjustmentForm()
    return render(request, 'inventory/add_stock_adjustment.html', {'form': form})



def stock_adjustment_list(request):
    adjustments = StockAdjustment.objects.all().order_by('-adjustment_date')
    return render(request, 'inventory/stock_adjustment_list.html', {'adjustments': adjustments})



def home(request):
    from django.db.models import Sum, F, Count
    from datetime import datetime
    
    products = Product.objects.all()
    low_stock = products.filter(quantity_in_stock__lt=10).count()
    total_products = products.count()
    
    # Calculate total inventory value
    total_value = products.aggregate(
        value=Sum(F('price') * F('quantity_in_stock'))
    )['value'] or 0
    
    # Get this month's purchases
    current_month = datetime.now().month
    current_year = datetime.now().year
    recent_purchases = Purchase.objects.filter(
        purchase_date__month=current_month,
        purchase_date__year=current_year
    ).count()
    
    context = {
        'total_products': total_products,
        'low_stock': low_stock,
        'total_value': total_value,
        'recent_purchases': recent_purchases,
        'products': products[:8]
    }
    return render(request, 'inventory/index.html', context)




def print_qr_label(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'inventory/qr_label.html', {'product': product})

def scan_qr_code_page(request):
    return render(request, 'inventory/scan_billing.html')

@csrf_exempt
def api_scan_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        scan_type = request.POST.get('scan_type', 'BILL')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Check stock availability for billing
            if scan_type == 'BILL' and product.quantity_in_stock < quantity:
                return JsonResponse({
                    'success': False, 
                    'error': f'Insufficient stock. Available: {product.quantity_in_stock}'
                })
            
            # Log scan event
            scan_event = ScanEvent.objects.create(
                product=product,
                scan_type=scan_type,
                quantity=quantity,
                remarks=f'Scanned for {scan_type.lower()}',
                user=request.user if request.user.is_authenticated else None
            )
            
            # Automatic stock update for billing
            if scan_type == 'BILL':
                product.quantity_in_stock -= quantity
                product.save()
                
            return JsonResponse({
                'success': True, 
                'product_name': product.name,
                'price': float(product.price),
                'remaining_stock': product.quantity_in_stock,
                'scan_id': scan_event.id
            })
            
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def cart_summary(request):
    cart = get_cart(request.session)
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total_price = 0

    for product in products:
        quantity = cart.get(str(product.id), 0)
        total = product.price * quantity
        total_price += total
        cart_items.append({'product': product, 'quantity': quantity, 'total': total})

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'inventory/cart_summary.html', context)


@login_required
def checkout(request):
    cart = get_cart(request.session)
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_summary')

    total_price = 0
    order = Order.objects.create(user=request.user, total_price=0, status='PENDING')

    try:
        for product_id, quantity in cart.items():
            product = Product.objects.get(pk=product_id)
            
            # Check stock availability
            if product.quantity_in_stock < quantity:
                order.delete()  # Remove incomplete order
                messages.error(request, f'Insufficient stock for {product.name}. Available: {product.quantity_in_stock}')
                return redirect('cart_summary')
            
            item_total = product.price * quantity
            total_price += item_total
            
            OrderItem.objects.create(
                order=order, 
                product=product, 
                quantity=quantity, 
                price=product.price
            )
            
            # Update stock
            product.quantity_in_stock -= quantity
            product.save()

        order.total_price = total_price
        order.status = 'COMPLETED'
        order.save()

        clear_cart(request.session)
        messages.success(request, f'Order #{order.id} completed successfully! Total: ₹{total_price}')
        return redirect('order_list')
        
    except Exception as e:
        order.delete()  # Clean up on error
        messages.error(request, f'Order failed: {str(e)}')
        return redirect('cart_summary')


def scan_event_list(request):
    events = ScanEvent.objects.select_related('product').order_by('-timestamp')[:100]
    return render(request, 'inventory/scan_event_list.html', {'events': events})

# Missing view functions for new URLs
@staff_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/add_product.html', {'form': form, 'product': product})

@staff_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()  # This will automatically delete QR file
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('product_list')
    return redirect('product_list')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

@staff_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        Category.objects.create(name=name, description=description)
        messages.success(request, 'Category added successfully!')
        return redirect('category_list')
    return render(request, 'inventory/add_category.html')

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@staff_required
def add_supplier(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        Supplier.objects.create(
            name=name, contact_person=contact_person, 
            phone=phone, email=email, address=address
        )
        messages.success(request, 'Supplier added successfully!')
        return redirect('supplier_list')
    return render(request, 'inventory/add_supplier.html')

def qr_dashboard(request):
    recent_scans = ScanEvent.objects.select_related('product').order_by('-timestamp')[:10]
    scan_stats = ScanEvent.objects.values('scan_type').annotate(count=Count('id'))
    return render(request, 'inventory/qr_dashboard.html', {
        'recent_scans': recent_scans,
        'scan_stats': scan_stats
    })

@staff_required
def generate_qr_labels(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('products')
        products = Product.objects.filter(id__in=product_ids)
        
        generated_count = 0
        already_exist_count = 0
        
        for product in products:
            if product.qr_code:
                already_exist_count += 1
            else:
                product.generate_qr_code()
                generated_count += 1
        
        if generated_count > 0:
            messages.success(request, f'Generated QR codes for {generated_count} products!')
        if already_exist_count > 0:
            messages.info(request, f'{already_exist_count} products already have QR codes!')
            
        return render(request, 'inventory/qr_labels_bulk.html', {'products': products})
    
    products = Product.objects.all()
    return render(request, 'inventory/generate_qr_labels.html', {'products': products})

@csrf_exempt
def api_add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
            if product.quantity_in_stock >= quantity:
                # Add to session cart
                cart = get_cart(request.session)
                cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
                request.session['cart'] = cart
                request.session.modified = True
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Added to cart',
                    'product_name': product.name,
                    'cart_quantity': cart[str(product_id)],
                    'total_items': sum(cart.values())
                })
            else:
                return JsonResponse({'success': False, 'error': 'Insufficient stock'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at') if request.user.is_authenticated else []
    return render(request, 'inventory/order_list.html', {'orders': orders})

@staff_required
def reports_dashboard(request):
    return render(request, 'inventory/reports_dashboard.html')

@staff_required
def stock_report(request):
    from django.db.models import Sum, F
    
    products = Product.objects.all()
    low_stock = products.filter(quantity_in_stock__lt=10)
    
    # Calculate total inventory value (current stock × selling price)
    total_value = products.aggregate(
        value=Sum(F('price') * F('quantity_in_stock'))
    )['value'] or 0
    
    return render(request, 'inventory/stock_report.html', {
        'products': products,
        'low_stock': low_stock,
        'total_value': total_value
    })

@staff_required
def sales_report(request):
    # Get sales from both completed orders and QR scan events
    orders = Order.objects.filter(status='COMPLETED').order_by('-created_at')[:50]
    
    # Get QR scan sales (billing events) with calculated totals
    qr_sales = ScanEvent.objects.filter(scan_type='BILL').select_related('product').order_by('-timestamp')[:50]
    
    # Add total calculation to each scan event
    for scan in qr_sales:
        scan.total = scan.quantity * scan.product.price
    
    # Calculate totals
    order_total = sum(order.total_price for order in orders)
    qr_total = sum(event.quantity * event.product.price for event in qr_sales)
    
    context = {
        'orders': orders,
        'qr_sales': qr_sales,
        'order_total': order_total,
        'qr_total': qr_total,
        'grand_total': order_total + qr_total
    }
    return render(request, 'inventory/sales_report.html', context)

@staff_required
def low_stock_report(request):
    low_stock_products = Product.objects.filter(quantity_in_stock__lt=10)
    return render(request, 'inventory/low_stock_report.html', {
        'products': low_stock_products
    })

@staff_required
def admin_dashboard(request):
    from django.contrib.auth.models import User
    stats = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'recent_activities': ScanEvent.objects.order_by('-timestamp')[:10]
    }
    return render(request, 'inventory/admin_dashboard.html', stats)

@staff_required
def user_management(request):
    from django.contrib.auth.models import User
    users = User.objects.all()
    return render(request, 'inventory/user_management.html', {'users': users})

@staff_required
def system_settings(request):
    from .models import SystemSettings
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        # Update settings
        settings.low_stock_threshold = int(request.POST.get('low_stock_threshold', 10))
        settings.currency = request.POST.get('currency', 'INR')
        settings.company_name = request.POST.get('company_name', 'SuperMarket Pro')
        settings.auto_generate_qr = request.POST.get('auto_generate_qr') == 'on'
        settings.qr_format = request.POST.get('qr_format', 'ID,Name,Price')
        settings.enable_email_alerts = request.POST.get('enable_email_alerts') == 'on'
        settings.alert_check_interval = int(request.POST.get('alert_check_interval', 60))
        settings.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('system_settings')
    
    return render(request, 'inventory/system_settings.html', {'settings': settings})

def api_verify_stock(request):
    """API endpoint to verify current stock levels after scanning"""
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            return JsonResponse({
                'success': True,
                'product_name': product.name,
                'current_stock': product.quantity_in_stock,
                'price': float(product.price),
                'low_stock_warning': product.quantity_in_stock < 10
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@staff_required
def api_testing(request):
    """API testing dashboard with UI forms"""
    products = Product.objects.all()[:20]  # Show first 20 products
    return render(request, 'inventory/api_testing.html', {'products': products})

# Phase 3: Analytics Views
@staff_required
def analytics_dashboard(request):
    """Main analytics dashboard"""
    from .analytics import InventoryAnalytics
    
    # Get key metrics
    fast_moving = InventoryAnalytics.get_fast_moving_products(5)
    low_stock = InventoryAnalytics.get_low_stock_products()
    sales_trends = InventoryAnalytics.get_sales_trends(30)
    
    # Get recent notifications
    notifications = SystemNotification.objects.filter(is_read=False)[:5]
    
    context = {
        'fast_moving_products': fast_moving,
        'low_stock_products': low_stock,
        'sales_trends': sales_trends,
        'notifications': notifications,
        'total_products': Product.objects.count(),
        'total_alerts': InventoryAlert.objects.filter(is_active=True).count(),
    }
    return render(request, 'inventory/analytics_dashboard.html', context)

@staff_required
def product_analytics(request, pk):
    """Individual product analytics"""
    from .analytics import InventoryAnalytics
    
    product = get_object_or_404(Product, pk=pk)
    velocity = InventoryAnalytics.calculate_product_velocity(product)
    reorder_point = InventoryAnalytics.calculate_reorder_point(product)
    
    # Get product's scan history
    recent_scans = ScanEvent.objects.filter(product=product).order_by('-timestamp')[:20]
    
    # Get analytics data for charts
    analytics_data = ProductAnalytics.objects.filter(product=product).order_by('-date')[:30]
    
    context = {
        'product': product,
        'velocity': velocity,
        'reorder_point': reorder_point,
        'recent_scans': recent_scans,
        'analytics_data': analytics_data,
    }
    return render(request, 'inventory/product_analytics.html', context)

@staff_required
def notifications_center(request):
    """Notifications management center"""
    notifications = SystemNotification.objects.all().order_by('-created_at')
    
    # Mark as read if requested
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            SystemNotification.objects.filter(id=notification_id).update(is_read=True)
            return redirect('notifications_center')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'inventory/notifications_center.html', context)

def api_analytics_data(request):
    """API endpoint for analytics data"""
    from .analytics import InventoryAnalytics
    
    data_type = request.GET.get('type', 'sales_trends')
    
    if data_type == 'sales_trends':
        days = int(request.GET.get('days', 30))
        data = InventoryAnalytics.get_sales_trends(days)
    elif data_type == 'fast_moving':
        limit = int(request.GET.get('limit', 10))
        products = InventoryAnalytics.get_fast_moving_products(limit)
        data = [{
            'name': p['product'].name,
            'velocity': p['velocity'],
            'stock': p['current_stock']
        } for p in products]
    else:
        data = []
    
    return JsonResponse({'success': True, 'data': data})

@csrf_exempt
def api_cart_status(request):
    """Get current cart status"""
    if request.method == 'GET':
        cart = get_cart(request.session)
        products = Product.objects.filter(id__in=cart.keys())
        cart_items = []
        total_price = 0
        
        for product in products:
            quantity = cart.get(str(product.id), 0)
            total = float(product.price) * quantity
            total_price += total
            cart_items.append({
                'product_id': product.id,
                'product_name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'total': total
            })
        
        return JsonResponse({
            'success': True,
            'cart_items': cart_items,
            'total_items': sum(cart.values()),
            'total_price': total_price
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        try:
            notification = SystemNotification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except SystemNotification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def dismiss_alert(request, alert_id):
    if request.method == 'POST':
        try:
            alert = InventoryAlert.objects.get(id=alert_id)
            alert.is_active = False
            alert.save()
            return JsonResponse({'success': True})
        except InventoryAlert.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Alert not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def trigger_alert_check(request):
    if request.method == 'POST':
        try:
            from .analytics import InventoryAnalytics
            alerts_created = InventoryAnalytics.check_inventory_alerts()
            return JsonResponse({
                'success': True, 
                'alerts_created': alerts_created,
                'message': f'Created {alerts_created} new alerts'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@staff_required
def alert_management(request):
    """Alert management dashboard"""
    active_alerts = InventoryAlert.objects.filter(is_active=True).select_related('product')
    dismissed_alerts = InventoryAlert.objects.filter(is_active=False).select_related('product')[:20]
    
    context = {
        'active_alerts': active_alerts,
        'dismissed_alerts': dismissed_alerts,
        'alert_counts': {
            'low_stock': active_alerts.filter(alert_type='LOW_STOCK').count(),
            'out_of_stock': active_alerts.filter(alert_type='OUT_OF_STOCK').count(),
            'fast_moving': active_alerts.filter(alert_type='FAST_MOVING').count(),
        }
    }
    return render(request, 'inventory/alert_management.html', context)

@staff_required
def bulk_import_products(request):
    import_results = None
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            from .bulk_import import BulkImporter
            import tempfile
            import os
            
            # Save uploaded file temporarily
            csv_file = request.FILES['csv_file']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                for chunk in csv_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            # Process import
            import_results = BulkImporter.import_from_csv(tmp_file_path)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            if import_results['success'] > 0:
                messages.success(request, f'Successfully imported {import_results["success"]} products!')
            if import_results['errors']:
                messages.warning(request, f'{len(import_results["errors"])} errors occurred during import.')
                
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
    
    return render(request, 'inventory/bulk_import.html', {'import_results': import_results})

@staff_required
def export_stock_csv(request):
    from .exports import ReportExporter
    return ReportExporter.export_stock_report_csv()

@staff_required
def export_analytics_pdf(request):
    from .exports import ReportExporter
    response = ReportExporter.export_analytics_pdf()
    if response:
        return response
    return JsonResponse({'error': 'PDF generation failed'}, status=500)