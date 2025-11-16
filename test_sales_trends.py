from inventory.analytics import InventoryAnalytics
import json

print("Testing sales trends...")
sales_trends = InventoryAnalytics.get_sales_trends(30)
print(f"Found {len(sales_trends)} days of data")

for trend in sales_trends[:5]:
    print(f"  {trend}")

# Test JSON conversion
sales_trends_data = []
for trend in sales_trends:
    sales_trends_data.append({
        'day': str(trend['day']),
        'total_scans': trend['total_scans'],
        'total_revenue': float(trend['total_revenue']) if trend['total_revenue'] else 0
    })

print(f"\nJSON data: {json.dumps(sales_trends_data[:3], indent=2)}")
