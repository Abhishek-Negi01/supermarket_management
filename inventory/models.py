# from django.db import models

# class Product(models.Model):
#     name = models.CharField(max_length = 100)
#     description = models.TextField(blank = True)
#     price = models.DecimalField(max_digits = 10, decimal_places = 2)
#     quantity_in_stock = models.PositiveIntegerField()
#     expiray_date = models.DateField(null = True, blank = True)

#     def __str__(self):
#         return self.name


from django.db import models

class Product(models.Model):
    name = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    quantity_in_stock = models.PositiveIntegerField()
    expiry_date = models.DateField(null = True, blank = True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    supplier = models.ForeignKey("Supplier", on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Purchase {self.product.name} - {self.quantity}'

class StockAdjustment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity_change = models.IntegerField(help_text="Positive for addition, negative for subtraction")
    reason = models.CharField(max_length=255, blank=True)
    adjustment_date = models.DateField(auto_now_add=True)
    employee = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Stock Adjustment for {self.product.name} on {self.adjustment_date}'

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
