from django.urls import path
from api.views import UsuarioView # Import the view from views.py

urlpatterns = [
    #path('user/<int:user_id>/', user_detail, name='user_detail'),
    #path('user/<int:user_id>/address/', address_detail(), name='address_detail'),
    #path('user/<int:user_id>/credit_card/', credit_card_detail, name='credit_card_detail'),
    path('usuarios/', UsuarioView.as_view(), name='lista-usuarios'),
]

