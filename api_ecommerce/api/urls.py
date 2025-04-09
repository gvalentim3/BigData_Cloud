from django.urls import path
from .views import (UsuarioReadUpdateDeleteView, UsuarioCreateListView, CartaoCreateListView, 
                       CartaoUpdateDeleteView, EnderecoCreateListView, EnderecoUpdateDeleteView,
                       AuthorizeTransacaoView, ProdutoReadUpdateDeleteView, ProdutoCreateListView)#, PedidoView)

urlpatterns = [
    path('usuarios/', UsuarioCreateListView.as_view(), name='cria&lista-usuarios'), #URL para criação e listagem de usuários.
    path('usuarios/<int:id_usuario>/', UsuarioReadUpdateDeleteView.as_view(), name='detalhes&atualizacoes&delete-usuario'), #URL para detalhamento, atualizações e remoção de usuários.
    
    path('usuarios/<int:id_usuario>/enderecos/', EnderecoCreateListView.as_view(), name='lista-enderecos-por-usuario'),
    path('usuarios/<int:id_usuario>/enderecos/<int:id_endereco>/', EnderecoUpdateDeleteView.as_view(), name='detalhes-endereco-por-usuario'),
    
    path('usuarios/<int:id_usuario>/cartoes/', CartaoCreateListView.as_view(), name='cria&lista-cartoes-por-usuario'), 
    path('usuarios/<int:id_usuario>/cartoes/<int:id_cartao>/', CartaoUpdateDeleteView.as_view(), name='atualiza&delete-cartao-por-usuario'),

    path('authorize/<int:id_usuario>/', AuthorizeTransacaoView.as_view(), name='autoriza-transacao'),
   
    path('produtos/', ProdutoCreateListView.as_view(), name='cria&lista-prdutos'), #URL para criação e listagem de produtos.
    path('produtos/<int:id_produto>/', ProdutoReadUpdateDeleteView.as_view(), name='detalhes&atualizacoes&delete-produto'), #URL para detalhamento, atualizações e remoção de produtos.
   


    #path('produtos/', ProdutoView.as_view(), name='produto-lista'),
    #path('produtos/<int:id_produto>/', ProdutoView.as_view(), name='produto-detail'),

    #path('pedidos/', PedidoView.as_view(), name='pedido-lista'),
    #path('pedidos/<int:id_pedido>/', PedidoView.as_view(), name='pedido-detail'),

]

