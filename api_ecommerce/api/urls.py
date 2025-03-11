from django.urls import path  # Import the view from views.py
from . import views

urlpatterns = [
    path('example/', views.example_view, name='example')
]

