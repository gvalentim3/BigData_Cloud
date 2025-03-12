from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Usuario, Endereco
from django.views import View
from api_ecommerce.services import ProdutoService, PedidoService
from api.serializers import ProdutoSerializer, PedidoSerializer
# Criar requisições
@api_view(['GET'])
def listar_produtos(request):
    produtos = ProdutoService.listar_produtos()
    serializer = ProdutoSerializer(produtos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def criar_pedido(request):
    pedido = PedidoService.criar_pedido()
    serializer = PedidoSerializer(pedido)
    return Response(serializer.data)

@api_view(['GET'])
def buscar_produto(request, produto_id):
    produto = ProdutoService.buscar_produto(produto_id)
    if not produto:
        return Response({"erro": "Produto não encontrado"}, status=404)
    serializer = ProdutoSerializer(produto)
    return Response(serializer.data)