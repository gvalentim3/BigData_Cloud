from django.urls import path, include
from .views import (ProdutoSearchView, UsuarioReadUpdateDeleteView, UsuarioCreateListView, 
                    CartaoCreateListView, CartaoUpdateDeleteView, EnderecoCreateListView, 
                    EnderecoUpdateDeleteView, ProdutoReadUpdateDeleteView, ProdutoCreateListView,
                    PedidoCreateView)


urlpatterns = [
    path('usuarios/', include([
        path('', UsuarioCreateListView.as_view(), name='users-list-create'),
        path('<int:id_usuario>/', UsuarioReadUpdateDeleteView.as_view(), name='users-detail'),
        
        path('<int:id_usuario>/enderecos/', include([
            path('', EnderecoCreateListView.as_view(), name='user-addresses-list'),
            path('<int:id_endereco>/', EnderecoUpdateDeleteView.as_view(), name='user-addresses-detail'),
        ])),
            
        path('<int:id_usuario>/cartoes/', include([
            path('', CartaoCreateListView.as_view(), name='user-cards-list'),
            path('<int:id_cartao>/', CartaoUpdateDeleteView.as_view(), name='user-cards-detail'),
        ])),
    ])),
        
    path('produtos/', include([
        path('', ProdutoCreateListView.as_view(), name='products-list-create'),
        path('busca/<str:nome>', ProdutoSearchView.as_view(), name='products-search'),
        path('<str:categoria>/<str:id_produto>/', ProdutoReadUpdateDeleteView.as_view(), name='products-detail'),
    ])),

    path('pedidos/', PedidoCreateView.as_view(), name='pedido-create')
]