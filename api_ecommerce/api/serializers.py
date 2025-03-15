from rest_framework import serializers
from api.models import CartaoCredito,Usuario,Endereco, TipoEndereco

class EnderecoSerializer (serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep']

class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['numero', 'validade', 'cvv', 'saldo']

class UsuarioSerializer (serializers.ModelSerializer):
    #cartoes = CartaoSerializer(many=True, read_only=True)
    #enderecos = EnderecoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        #fields = ['nome', 'email', 'data_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone']

"""        
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'
"""