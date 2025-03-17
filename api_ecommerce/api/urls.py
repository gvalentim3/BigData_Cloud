from django.urls import path
from api.views import UsuarioView, EnderecoView

urlpatterns = [
    #path('user/<int:user_id>/', user_detail, name='user_detail'),
    #path('user/<int:user_id>/address/', address_detail(), name='address_detail'),
    #path('user/<int:user_id>/credit_card/', credit_card_detail, name='credit_card_detail'),
    path('usuarios/', UsuarioView.as_view(), name='lista-usuarios'), # Métodos GET(lista) e POST
    path('usuarios/<int:pk>/', UsuarioView.as_view(), name='detalhes-usuario'), # Métodos GET(detalhado e por id), PUT e DELETE
    path('enderecos/', EnderecoView.as_view(), name='lista-enderecos'), # Métodos GET(lista) e POST
    path('enderecos/<int:pk>/', EnderecoView.as_view(), name='detalhes-endereco') # Métodos GET(detalhado e por id), PUT e DELETE
]

