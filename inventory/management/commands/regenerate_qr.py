from django.core.management.base import BaseCommand
from inventory.models import Product

class Command(BaseCommand):
    help = 'Regenerate QR codes for all products with consistent naming'

    def handle(self, *args, **options):
        products = Product.objects.all()
        count = 0
        
        for product in products:
            # Clear existing QR code
            product.qr_code = None
            product.save()  # This will trigger QR generation with new format
            count += 1
            self.stdout.write(f'Generated QR for: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully regenerated {count} QR codes')
        )