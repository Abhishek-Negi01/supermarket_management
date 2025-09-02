from django.db import models

class Product(models.Model):
    name = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    quantity_in_stock = models.PositiveIntegerField()
    expiray_date = models.DateField(null = True, blank = True)

    def __str__(self):
        return self.name
