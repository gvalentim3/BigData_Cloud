from rest_framework import serializers
from api.models import Usuario,Endereco,Produto,Pedido

class UsuarioSerializer (serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        
class EnderecoSerializer (serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'