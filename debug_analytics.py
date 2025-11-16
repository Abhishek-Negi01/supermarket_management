from inventory.models import ScanEvent, Product, ProductAnalytics
from django.utils import timezone
from datetime import timedelta

print("Current date:", timezone.now().date())
print("\nRecent scan events:")
scans = ScanEvent.objects.filter(scan_type='BILL').order_by('-timestamp')[:10]
for s in scans:
    print(f"  {s.product.name} - {s.timestamp.date()} - qty: {s.quantity}")

print("\nBanana scans (last 7 days):")
banana = Product.objects.filter(name='Banana').first()
if banana:
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    print(f"  Date range: {start_date} to {end_date}")
    banana_scans = ScanEvent.objects.filter(
        product=banana,
        timestamp__date__range=[start_date, end_date],
        scan_type='BILL'
    )
    print(f"  Total scans: {banana_scans.count()}")
    total_qty = sum(s.quantity for s in banana_scans)
    print(f"  Total quantity: {total_qty}")
    print(f"  Velocity: {total_qty / 7:.2f} per day")

print("\nProductAnalytics for today:")
today_analytics = ProductAnalytics.objects.filter(date=timezone.now().date())
for a in today_analytics:
    print(f"  {a.product.name}: scans={a.scan_count}, velocity={a.velocity_score:.2f}")
