import csv
import pandas as pd
from django.db import transaction
from .models import Product, Category

class BulkImporter:
    
    @staticmethod
    def import_from_csv(file_path):
        results = {'success': 0, 'errors': [], 'created_products': []}
        
        try:
            df = pd.read_csv(file_path)
            required_columns = ['name', 'price', 'quantity_in_stock']
            
            # Validate columns
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                results['errors'].append(f"Missing columns: {missing_cols}")
                return results
            
            products_to_create = []
            
            for index, row in df.iterrows():
                try:
                    # Get or create category
                    category = None
                    if 'category' in df.columns and pd.notna(row['category']):
                        category, _ = Category.objects.get_or_create(name=row['category'])
                    
                    # Create product object
                    product = Product(
                        name=row['name'],
                        price=float(row['price']),
                        quantity_in_stock=int(row['quantity_in_stock']),
                        description=row.get('description', ''),
                        category=category,
                        expiry_date=pd.to_datetime(row['expiry_date']).date() if 'expiry_date' in df.columns and pd.notna(row['expiry_date']) else None
                    )
                    products_to_create.append(product)
                    
                except Exception as e:
                    results['errors'].append(f"Row {index + 2}: {str(e)}")
            
            # Bulk create products
            if products_to_create:
                with transaction.atomic():
                    created_products = Product.objects.bulk_create(products_to_create)
                    results['success'] = len(created_products)
                    results['created_products'] = created_products
            
        except Exception as e:
            results['errors'].append(f"File processing error: {str(e)}")
        
        return results