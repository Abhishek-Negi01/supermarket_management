from django.core.management.base import BaseCommand
from django.conf import settings
import os
import glob
from inventory.models import Product

class Command(BaseCommand):
    help = 'Clean up orphaned QR code files'

    def handle(self, *args, **options):
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr')
        if not os.path.exists(qr_dir):
            self.stdout.write('No QR directory found')
            return

        # Get all QR files
        qr_files = glob.glob(os.path.join(qr_dir, '*.png'))
        
        # Get all product IDs that should have QR files
        valid_product_ids = set(Product.objects.values_list('id', flat=True))
        
        deleted_count = 0
        for qr_file in qr_files:
            filename = os.path.basename(qr_file)
            if filename.startswith('product_') and filename.endswith('_qr.png'):
                try:
                    # Extract product ID from filename
                    product_id = int(filename.replace('product_', '').replace('_qr.png', ''))
                    
                    # Delete if product doesn't exist
                    if product_id not in valid_product_ids:
                        os.remove(qr_file)
                        deleted_count += 1
                        self.stdout.write(f'Deleted orphaned QR file: {filename}')
                except (ValueError, OSError):
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleanup complete. Deleted {deleted_count} orphaned QR files.')
        )