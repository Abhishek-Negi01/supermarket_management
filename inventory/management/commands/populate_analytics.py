from django.core.management.base import BaseCommand
from inventory.analytics import InventoryAnalytics

class Command(BaseCommand):
    help = 'Populate analytics from existing scan data'

    def handle(self, *args, **options):
        self.stdout.write('Updating analytics from existing scans...')
        InventoryAnalytics.update_daily_analytics()
        self.stdout.write('Checking inventory alerts...')
        alerts = InventoryAnalytics.check_inventory_alerts()
        self.stdout.write(self.style.SUCCESS(f'Done! Created {alerts} alerts'))
