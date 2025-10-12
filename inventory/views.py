from django.shortcuts import render
from .models import Product,Purchase,StockAdjustment
from .forms import ProductForm,PurchaseForm,StockAdjustmentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test

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
    return render(request, 'inventory/purchase_list.html', {'purchases': purchases})


@staff_required
def add_stock_adjustment(request):
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save()
            # Update product stock
            adjustment.product.quantity_in_stock += adjustment.quantity_change
            adjustment.product.save()
            return redirect('stock_adjustment_list')
    else:
        form = StockAdjustmentForm()
    return render(request, 'inventory/add_stock_adjustment.html', {'form': form})



def stock_adjustment_list(request):
    adjustments = StockAdjustment.objects.all().order_by('-adjustment_date')
    return render(request, 'inventory/stock_adjustment_list.html', {'adjustments': adjustments})



def home(request):
    products = Product.objects.all()
    low_stock = products.filter(quantity_in_stock__lt=10).count()
    total_products = products.count()
    context = {
        'total_products': total_products,
        'low_stock': low_stock,
        'products': products[:8]  # show 8 recent products
    }
    return render(request, 'inventory/index.html', context)


def welcome(request):
    return render(request,'inventory/welcome.html')