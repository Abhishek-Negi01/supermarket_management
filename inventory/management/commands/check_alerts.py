from django.core.management.base import BaseCommand
from inventory.analytics import InventoryAnalytics

class Command(BaseCommand):
    help = 'Check and generate inventory alerts'

    def handle(self, *args, **options):
        self.stdout.write('Checking inventory alerts...')
        
        # Update daily analytics
        InventoryAnalytics.update_daily_analytics()
        self.stdout.write('Daily analytics updated')
        
        # Check alerts
        alerts_created = InventoryAnalytics.check_inventory_alerts()
        self.stdout.write(f'Created {alerts_created} new alerts')
        
        self.stdout.write(self.style.SUCCESS('Alert check completed'))