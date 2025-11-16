from django.utils import timezone
import datetime

print("Django timezone.now():", timezone.now())
print("Django timezone.now().date():", timezone.now().date())
print("Python datetime.now():", datetime.datetime.now())
print("Python date.today():", datetime.date.today())

from inventory.models import ScanEvent
latest_scan = ScanEvent.objects.order_by('-timestamp').first()
if latest_scan:
    print(f"\nLatest scan timestamp: {latest_scan.timestamp}")
    print(f"Latest scan date: {latest_scan.timestamp.date()}")
