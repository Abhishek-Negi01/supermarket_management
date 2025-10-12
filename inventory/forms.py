from django import forms
from .models import Product,Purchase,StockAdjustment

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','description','price','quantity_in_stock','expiry_date']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product', 'supplier', 'quantity', 'purchase_price'] # 'purchase_date' will automatically added (today)

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['product', 'quantity_change', 'reason',  'employee'] # 'adjustment_date' will automatically added (today)