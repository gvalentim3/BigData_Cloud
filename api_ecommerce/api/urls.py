from django.urls import path
from api.views import UsuarioReadUpdateDeleteView, UsuarioCreateListView, CartaoCreateListView, CartaoUpdateDeleteView

urlpatterns = [
    path('usuarios/', UsuarioCreateListView.as_view(), name='cria&lista-usuarios'), #URL para criação e listagem de usuários.
    path('usuarios/<int:id_usuario>/', UsuarioReadUpdateDeleteView.as_view(), name='detalhes&atualizacoes&delete-usuario'), #URL para detalhamento, atualizações e remoção de usuários.
    
    #path('usuarios/<int:id_usuario>/enderecos/', EnderecoView.as_view(), name='lista-enderecos-por-usuario'),
    #path('usuarios/<int:id_usuario>/enderecos/<int:id_endereco>/', EnderecoView.as_view(), name='detalhes-endereco-por-usuario'),
    
    path('usuarios/<int:id_usuario>/cartoes/', CartaoCreateListView.as_view(), name='cria&lista-cartoes-por-usuario'), 
    path('usuarios/<int:id_usuario>/cartoes/<int:id_endereco>/', CartaoUpdateDeleteView.as_view(), name='atualiza&delete-cartao-por-usuario')    
]

