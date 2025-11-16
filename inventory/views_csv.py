from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import csv
from .csv_import import CSVImporter, CSVExporter
from .models import Product, Supplier, Category

@login_required
def csv_import_page(request):
    """CSV import interface"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        import_type = request.POST.get('import_type')
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file')
            return redirect('csv_import')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV')
            return redirect('csv_import')
        
        try:
            import io
            decoded_file = io.StringIO(csv_file.read().decode('utf-8'))
            
            result = None
            if import_type == 'products':
                result = CSVImporter.import_products(decoded_file)
            elif import_type == 'categories':
                result = CSVImporter.import_categories(decoded_file)
            elif import_type == 'suppliers':
                result = CSVImporter.import_suppliers(decoded_file)
            elif import_type == 'employees':
                result = CSVImporter.import_employees(decoded_file)
            elif import_type == 'purchases':
                result = CSVImporter.import_purchases(decoded_file, request.user)
            elif import_type == 'stock_adjustments':
                result = CSVImporter.import_stock_adjustments(decoded_file, request.user)
            
            if result:
                if result.get('errors'):
                    messages.warning(request, f"Import completed with errors. Created: {result.get('created', 0)}, Updated: {result.get('updated', 0)}, Errors: {len(result['errors'])}")
                    for error in result['errors'][:5]:  # Show first 5 errors
                        messages.error(request, error)
                else:
                    messages.success(request, f"Successfully imported! Created: {result.get('created', 0)}, Updated: {result.get('updated', 0)}")
            
        except Exception as e:
            messages.error(request, f'Error processing CSV: {str(e)}')
        
        return redirect('csv_import')
    
    return render(request, 'inventory/csv_import.html')

@login_required
def csv_export(request, export_type):
    """Export data to CSV"""
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'products':
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.DictWriter(response, fieldnames=['name', 'description', 'price', 'quantity_in_stock', 'category_name', 'expiry_date'])
        writer.writeheader()
        writer.writerows(CSVExporter.export_products())
    
    elif export_type == 'suppliers':
        response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'
        writer = csv.DictWriter(response, fieldnames=['name', 'contact_person', 'phone', 'email', 'address'])
        writer.writeheader()
        writer.writerows(CSVExporter.export_suppliers())
    
    elif export_type == 'categories':
        response['Content-Disposition'] = 'attachment; filename="categories.csv"'
        writer = csv.DictWriter(response, fieldnames=['name', 'description'])
        writer.writeheader()
        writer.writerows(CSVExporter.export_categories())
    
    return response

@login_required
def download_template(request, template_type):
    """Download CSV template"""
    response = HttpResponse(content_type='text/csv')
    
    templates = {
        'products': ['name', 'description', 'price', 'quantity_in_stock', 'category_name', 'expiry_date'],
        'categories': ['name', 'description'],
        'suppliers': ['name', 'contact_person', 'phone', 'email', 'address'],
        'employees': ['first_name', 'last_name', 'role', 'email', 'phone'],
        'purchases': ['product_name', 'supplier_name', 'quantity', 'purchase_price', 'purchase_date'],
        'stock_adjustments': ['product_name', 'quantity_change', 'reason', 'notes']
    }
    
    if template_type in templates:
        response['Content-Disposition'] = f'attachment; filename="{template_type}_template.csv"'
        writer = csv.writer(response)
        writer.writerow(templates[template_type])
    
    return response
