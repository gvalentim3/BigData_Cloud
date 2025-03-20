from django.urls import path
from api.views import UsuarioView, EnderecoView, CartaoView

urlpatterns = [
    #path('user/<int:user_id>/', user_detail, name='user_detail'),
    #path('user/<int:user_id>/address/', address_detail(), name='address_detail'),
    #path('user/<int:user_id>/credit_card/', credit_card_detail, name='credit_card_detail'),
    path('usuarios/', UsuarioView.as_view(), name='lista-usuarios'),
    path('usuarios/<int:pk>/', UsuarioView.as_view(), name='detalhes-usuario'),
    path('usuarios/<int:pk>/enderecos/', EnderecoView.as_view(), name='lista-enderecos-por-usuario'),
    path('usuarios/<int:pk>/enderecos/<int:pk>/', EnderecoView.as_view(), name='detalhes-endereco-por-usuario'),
    path('usuarios/<int:pk>/cartoes/', CartaoView.as_view(), name='lista-cartoes-por-usuario'), 
    path('usuarios/<int:pk>/cartoes/<int:pk>/', CartaoView.as_view(), name='detalhes-cartao-por-usuario')    
]

