from inventory.analytics import InventoryAnalytics
from inventory.models import ProductAnalytics

print("Updating analytics...")
InventoryAnalytics.update_daily_analytics()
print("Analytics updated successfully")

print("\nChecking fast moving products...")
result = InventoryAnalytics.get_fast_moving_products()
print(f"Found {len(result)} fast moving products")
for item in result:
    print(f'{item["product"].name}: velocity={item["velocity"]:.2f}, stock={item["current_stock"]}')

print("\nChecking ProductAnalytics records...")
analytics = ProductAnalytics.objects.all()[:10]
for a in analytics:
    print(f'{a.product.name} - {a.date}: scans={a.scan_count}, velocity={a.velocity_score:.2f}')
