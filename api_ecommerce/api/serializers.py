from rest_framework import serializers
from api.models import CartaoCredito,Usuario,Endereco,TipoEndereco

class TipoEnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEndereco
        fields = ['tipo']

class EnderecoSerializer (serializers.ModelSerializer):
    tipo_endereco = TipoEnderecoSerializer(many=False)
    
    class Meta:
        model = Endereco
        fields = ['logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'tipo_endereco']

class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['numero', 'dt_expiracao', 'cvv', 'saldo']


class UsuarioReadSerializer (serializers.ModelSerializer):
    cartoes = CartaoSerializer(many=True, read_only=True)
    enderecos = EnderecoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']

class UsuarioWriteSerializer (serializers.ModelSerializer):    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone']


"""        
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['numero', 'dt_expiracao', 'cvv', 'saldo']

"""