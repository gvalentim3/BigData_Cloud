from django.urls import path
from api.views import listar_produtos, buscar_produto, criar_pedido # Import the view from views.py

urlpatterns = [
    path('produtos/', listar_produtos, name='listar_produtos'),
    path('produtos/<int:produto_id>/', buscar_produto, name='buscar_produto'),
    path('pedidos/', criar_pedido, name='criar_pedido'),
]
