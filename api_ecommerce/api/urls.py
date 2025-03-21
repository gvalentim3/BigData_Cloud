from django.urls import path
from api.views import UsuarioReadUpdateDeleteView, UsuarioCreateListView, EnderecoView, CartaoView

urlpatterns = [
    path('usuarios/', UsuarioCreateListView.as_view(), name='cria&lista-usuarios'), #URL para criação e listagem de usuários.
    path('usuarios/<int:id_usuario>/', UsuarioReadUpdateDeleteView.as_view(), name='detalhes&atualizacoes&delete-usuario'), #URL para detalhamento, atualizações e remoção de usuários.
    
    path('usuarios/<int:id_usuario>/enderecos/', EnderecoView.as_view(), name='lista-enderecos-por-usuario'),
    path('usuarios/<int:id_usuario>/enderecos/<int:id_endereco>/', EnderecoView.as_view(), name='detalhes-endereco-por-usuario'),
    
    path('usuarios/<int:id_usuario>/cartoes/', CartaoView.as_view(), name='lista-cartoes-por-usuario'), 
    path('usuarios/<int:id_usuario>/cartoes/<int:id_endereco>/', CartaoView.as_view(), name='detalhes-cartao-por-usuario')    
]

