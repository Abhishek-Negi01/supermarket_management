from django.contrib import admin
from .models import Product,Employee,Purchase,StockAdjustment,Supplier

admin.site.register(Product)
admin.site.register(Employee)
admin.site.register(Purchase)
admin.site.register(StockAdjustment)
admin.site.register(Supplier)


