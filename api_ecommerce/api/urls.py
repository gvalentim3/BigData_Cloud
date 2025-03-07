from django.urls import path
from .views import product_list  # Import the view from views.py

urlpatterns = [
    path('products/', product_list, name='product-list'),
]
