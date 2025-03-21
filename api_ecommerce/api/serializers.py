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


class CartaoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['id', 'numero', 'dt_expiracao', 'cvv', 'saldo', "FK_usuario"]

class CartaoReadSerializer(serializers.ModelSerializer):
        class Meta:
            model = CartaoCredito
            fields = ['id', 'numero', 'dt_expiracao', 'cvv', 'saldo']


class UsuarioReadSerializer (serializers.ModelSerializer):
    cartoes = CartaoReadSerializer(many=True, read_only=True)
    enderecos = EnderecoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']

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