from django.urls import path
from . import views

urlpatterns = [
    path('',views.welcome,name='welcome'),
    path('home/',views.home,name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/add',views.add_product,name='add_product'),
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
    path('adjustments/', views.stock_adjustment_list, name='stock_adjustment_list'),
    path('adjustments/add/', views.add_stock_adjustment, name='add_stock_adjustment'),
    
]
