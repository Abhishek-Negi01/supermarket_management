from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib import messages
from .models import Product, Bill, BillItem, ScanEvent
from .permissions import cashier_required
from decimal import Decimal

@cashier_required
def billing_page(request):
    """Main billing interface for cashiers"""
    products = Product.objects.filter(quantity_in_stock__gt=0).select_related('category')
    return render(request, 'inventory/billing.html', {'products': products})

@csrf_exempt
@login_required
def add_to_current_bill(request):
    """Add product to current bill session"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
            
            if product.quantity_in_stock < quantity:
                return JsonResponse({'success': False, 'error': f'Only {product.quantity_in_stock} units available'})
            
            # Get or create current bill in session
            current_bill = request.session.get('current_bill', {})
            
            if str(product_id) in current_bill:
                current_bill[str(product_id)]['quantity'] += quantity
            else:
                current_bill[str(product_id)] = {
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity
                }
            
            request.session['current_bill'] = current_bill
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'product_name': product.name,
                'total_items': sum(item['quantity'] for item in current_bill.values())
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@login_required
def get_current_bill(request):
    """Get current bill details"""
    current_bill = request.session.get('current_bill', {})
    items = []
    total = 0
    
    for product_id, item in current_bill.items():
        item_total = item['price'] * item['quantity']
        total += item_total
        items.append({
            'product_id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total
        })
    
    return JsonResponse({
        'success': True,
        'items': items,
        'total': total,
        'item_count': len(items)
    })

@csrf_exempt
@login_required
def complete_bill(request):
    """Complete billing and generate receipt"""
    if request.method == 'POST':
        current_bill = request.session.get('current_bill', {})
        
        if not current_bill:
            return JsonResponse({'success': False, 'error': 'No items in bill'})
        
        payment_method = request.POST.get('payment_method', 'CASH')
        customer_name = request.POST.get('customer_name', '')
        
        try:
            with transaction.atomic():
                # Calculate total
                total_amount = Decimal('0')
                bill_items_data = []
                
                for product_id, item in current_bill.items():
                    product = Product.objects.select_for_update().get(id=product_id)
                    
                    # Check stock
                    if product.quantity_in_stock < item['quantity']:
                        return JsonResponse({
                            'success': False,
                            'error': f'{product.name}: Only {product.quantity_in_stock} units available'
                        })
                    
                    item_total = Decimal(str(item['price'])) * item['quantity']
                    total_amount += item_total
                    
                    bill_items_data.append({
                        'product': product,
                        'quantity': item['quantity'],
                        'unit_price': Decimal(str(item['price'])),
                        'total_price': item_total
                    })
                
                # Create bill
                bill = Bill.objects.create(
                    cashier=request.user,
                    customer_name=customer_name,
                    total_amount=total_amount,
                    payment_method=payment_method
                )
                
                # Create bill items and update stock
                for item_data in bill_items_data:
                    BillItem.objects.create(
                        bill=bill,
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price'],
                        total_price=item_data['total_price']
                    )
                    
                    # Update stock
                    item_data['product'].quantity_in_stock -= item_data['quantity']
                    item_data['product'].save()
                    
                    # Log scan event
                    ScanEvent.objects.create(
                        product=item_data['product'],
                        scan_type='BILL',
                        quantity=item_data['quantity'],
                        user=request.user
                    )
                
                # Clear current bill
                request.session['current_bill'] = {}
                request.session.modified = True
                
                return JsonResponse({
                    'success': True,
                    'bill_number': bill.bill_number,
                    'bill_id': bill.id,
                    'total_amount': float(total_amount)
                })
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def print_bill(request, bill_id):
    """Generate printable bill/receipt"""
    bill = Bill.objects.prefetch_related('items__product').get(id=bill_id)
    return render(request, 'inventory/print_bill.html', {'bill': bill})

@login_required
def download_bill_pdf(request, bill_id):
    """Generate PDF bill/receipt"""
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    from io import BytesIO
    
    bill = Bill.objects.prefetch_related('items__product').get(id=bill_id)
    
    # Render HTML
    html = render_to_string('inventory/bill_pdf.html', {'bill': bill})
    
    # Create PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{bill.bill_number}.pdf"'
        return response
    
    return HttpResponse('Error generating PDF', status=500)

@csrf_exempt
@login_required
def remove_from_bill(request):
    """Remove item from current bill"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        current_bill = request.session.get('current_bill', {})
        
        if str(product_id) in current_bill:
            del current_bill[str(product_id)]
            request.session['current_bill'] = current_bill
            request.session.modified = True
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Item not in bill'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def bills_list(request):
    """List all bills with search and filter"""
    from .permissions import get_user_role
    
    user_role = get_user_role(request.user)
    
    # Cashiers see only their bills, others see all
    if user_role == 'CASHIER':
        bills = Bill.objects.filter(cashier=request.user).prefetch_related('items').order_by('-created_at')
    else:
        bills = Bill.objects.all().prefetch_related('items').order_by('-created_at')
    
    return render(request, 'inventory/bills_list.html', {'bills': bills})
