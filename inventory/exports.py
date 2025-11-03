import csv
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from .models import Product, ScanEvent, InventoryAlert
from .analytics import InventoryAnalytics

class ReportExporter:
    
    @staticmethod
    def export_stock_report_csv():
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Product Name', 'Current Stock', 'Price', 'Category', 'Status'])
        
        for product in Product.objects.all():
            status = 'Low Stock' if product.quantity_in_stock < 10 else 'Normal'
            writer.writerow([
                product.name,
                product.quantity_in_stock,
                product.price,
                product.category.name if product.category else 'N/A',
                status
            ])
        
        return response
    
    @staticmethod
    def export_analytics_pdf():
        template = get_template('inventory/reports/analytics_pdf.html')
        
        # Get analytics data
        fast_moving = InventoryAnalytics.get_fast_moving_products(10)
        low_stock = InventoryAnalytics.get_low_stock_products()
        active_alerts = InventoryAlert.objects.filter(is_active=True)
        
        context = {
            'fast_moving_products': fast_moving,
            'low_stock_products': low_stock,
            'active_alerts': active_alerts,
            'total_products': Product.objects.count(),
        }
        
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="analytics_report.pdf"'
            return response
        
        return None