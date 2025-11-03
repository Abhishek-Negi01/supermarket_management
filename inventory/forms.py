from django import forms
from .models import Product, Purchase, StockAdjustment, Category, Supplier, Employee

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'quantity_in_stock', 'expiry_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500', 'step': '0.01'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'expiry_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'type': 'date'
            }),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product', 'supplier', 'quantity', 'purchase_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'supplier': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500', 'step': '0.01'}),
        }

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['product', 'quantity_change', 'reason', 'notes', 'employee']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'quantity_change': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'reason': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500', 'rows': 3}),
            'employee': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-xl text-white focus:ring-2 focus:ring-primary-500'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }