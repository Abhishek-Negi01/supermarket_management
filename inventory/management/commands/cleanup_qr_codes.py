import os
from django.core.management.base import BaseCommand
from django.conf import settings
from inventory.models import Product

class Command(BaseCommand):
    help = 'Clean up orphaned QR code files'

    def handle(self, *args, **options):
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr')
        
        if not os.path.exists(qr_dir):
            self.stdout.write('QR directory does not exist')
            return
        
        # Get all QR files in directory
        qr_files = [f for f in os.listdir(qr_dir) if f.endswith('.png')]
        
        # Get all valid QR code paths from database
        valid_qr_files = set()
        for product in Product.objects.exclude(qr_code=''):
            if product.qr_code:
                filename = os.path.basename(product.qr_code.name)
                valid_qr_files.add(filename)
        
        # Delete orphaned files
        deleted_count = 0
        for qr_file in qr_files:
            if qr_file not in valid_qr_files:
                file_path = os.path.join(qr_dir, qr_file)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    self.stdout.write(f'Deleted: {qr_file}')
                except Exception as e:
                    self.stdout.write(f'Error deleting {qr_file}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleanup completed. Deleted {deleted_count} orphaned QR files')
        )