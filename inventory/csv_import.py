import csv
from datetime import datetime
from django.db import transaction
from django.contrib.auth.models import User
from .models import (
    Category, Product, Supplier, Employee, 
    Purchase, StockAdjustment, Order, OrderItem
)

class CSVImporter:
    
    @staticmethod
    @transaction.atomic
    def import_categories(csv_file):
        """Import categories from CSV. Format: name,description"""
        reader = csv.DictReader(csv_file)
        created, updated, errors = 0, 0, []
        
        for row in reader:
            try:
                category, is_created = Category.objects.update_or_create(
                    name=row['name'],
                    defaults={'description': row.get('description', '')}
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
        
        return {'created': created, 'updated': updated, 'errors': errors}
    
    @staticmethod
    @transaction.atomic
    def import_suppliers(csv_file):
        """Import suppliers from CSV. Format: name,contact_person,phone,email,address"""
        reader = csv.DictReader(csv_file)
        created, updated, errors = 0, 0, []
        
        for row in reader:
            try:
                supplier, is_created = Supplier.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'contact_person': row.get('contact_person', ''),
                        'phone': row.get('phone', ''),
                        'email': row.get('email', ''),
                        'address': row.get('address', '')
                    }
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
        
        return {'created': created, 'updated': updated, 'errors': errors}
    
    @staticmethod
    @transaction.atomic
    def import_products(csv_file):
        """Import products from CSV. Format: name,description,price,quantity_in_stock,category_name,expiry_date"""
        reader = csv.DictReader(csv_file)
        created, updated, errors = 0, 0, []
        
        for row in reader:
            try:
                category = None
                if row.get('category_name'):
                    category, _ = Category.objects.get_or_create(name=row['category_name'])
                
                expiry_date = None
                if row.get('expiry_date'):
                    expiry_date = datetime.strptime(row['expiry_date'], '%Y-%m-%d').date()
                
                product, is_created = Product.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'description': row.get('description', ''),
                        'price': float(row['price']),
                        'quantity_in_stock': int(row['quantity_in_stock']),
                        'category': category,
                        'expiry_date': expiry_date
                    }
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
        
        return {'created': created, 'updated': updated, 'errors': errors}
    
    @staticmethod
    @transaction.atomic
    def import_employees(csv_file):
        """Import employees from CSV. Format: first_name,last_name,role,email,phone"""
        reader = csv.DictReader(csv_file)
        created, updated, errors = 0, 0, []
        
        for row in reader:
            try:
                employee, is_created = Employee.objects.update_or_create(
                    email=row['email'],
                    defaults={
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'role': row.get('role', 'CASHIER'),
                        'phone': row.get('phone', '')
                    }
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
        
        return {'created': created, 'updated': updated, 'errors': errors}
    
    @staticmethod
    @transaction.atomic
    def import_purchases(csv_file, user=None):
        """Import purchases from CSV. Format: product_name,supplier_name,quantity,purchase_price,purchase_date"""
        reader = csv.DictReader(csv_file)
        created, errors = 0, []
        
        for row in reader:
            try:
                product = Product.objects.get(name=row['product_name'])
                supplier = Supplier.objects.get(name=row['supplier_name']) if row.get('supplier_name') else None
                
                purchase_date = datetime.strptime(row['purchase_date'], '%Y-%m-%d').date() if row.get('purchase_date') else None
                
                purchase = Purchase.objects.create(
                    product=product,
                    supplier=supplier,
                    quantity=int(row['quantity']),
                    purchase_price=float(row['purchase_price']),
                    created_by=user
                )
                
                # Update product stock
                product.quantity_in_stock += int(row['quantity'])
                product.save()
                
                created += 1
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
        
        return {'created': created, 'errors': errors}
    
    @staticmethod
    @transaction.atomic
    def import_stock_adjustments(csv_file, user=None):
        """Import stock adjustments from CSV. Format: product_name,quantity_change,reason,notes"""
        reader = csv.DictReader(csv_file)
        created, errors = 0, []
        
        for row in reader:
            try:
                product = Product.objects.get(name=row['product_name'])
                
                adjustment = StockAdjustment.objects.create(
                    product=product,
                    quantity_change=int(row['quantity_change']),
                    reason=row.get('reason', 'OTHER'),
                    notes=row.get('notes', ''),
                    created_by=user
                )
                
                # Update product stock
                product.quantity_in_stock += int(row['quantity_change'])
                product.save()
                
                created += 1
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
        
        return {'created': created, 'errors': errors}

class CSVExporter:
    
    @staticmethod
    def export_products():
        """Export all products to CSV format"""
        products = Product.objects.all()
        rows = []
        
        for product in products:
            rows.append({
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'quantity_in_stock': product.quantity_in_stock,
                'category_name': product.category.name if product.category else '',
                'expiry_date': product.expiry_date.strftime('%Y-%m-%d') if product.expiry_date else ''
            })
        
        return rows
    
    @staticmethod
    def export_suppliers():
        """Export all suppliers to CSV format"""
        suppliers = Supplier.objects.all()
        rows = []
        
        for supplier in suppliers:
            rows.append({
                'name': supplier.name,
                'contact_person': supplier.contact_person,
                'phone': supplier.phone,
                'email': supplier.email,
                'address': supplier.address
            })
        
        return rows
    
    @staticmethod
    def export_categories():
        """Export all categories to CSV format"""
        categories = Category.objects.all()
        rows = []
        
        for category in categories:
            rows.append({
                'name': category.name,
                'description': category.description
            })
        
        return rows
