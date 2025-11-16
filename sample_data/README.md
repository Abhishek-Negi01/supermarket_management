# Sample CSV Data Files

This folder contains sample CSV files for testing the import functionality.

## Files Included

1. **categories_sample.csv** - Sample product categories
2. **products_sample.csv** - Sample products with pricing and stock
3. **suppliers_sample.csv** - Sample supplier information

## How to Use

1. Start the Django server: `python manage.py runserver`
2. Login to the system
3. Navigate to **Inventory → CSV Import/Export**
4. Import files in this order:
   - First: `categories_sample.csv`
   - Second: `suppliers_sample.csv`
   - Third: `products_sample.csv`

## Testing Duplicate Prevention

After importing once, try importing the same files again:
- Records will be **updated**, not duplicated
- Modify values in CSV and re-import to see updates

## Modifying Sample Data

Feel free to edit these files to test:
- Adding new records
- Updating existing records
- Testing error handling (invalid data)
