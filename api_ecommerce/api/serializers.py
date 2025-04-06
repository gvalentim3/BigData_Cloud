from rest_framework import serializers
from api.models import CartaoCredito,Usuario,Endereco,TipoEndereco #Produto,Pedido

class TipoEnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEndereco
        fields = ['tipo']


class EnderecoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'FK_tp_endereco', 'FK_usuario']

class EnderecoReadSerializer(serializers.ModelSerializer):
    tipo_endereco = TipoEnderecoSerializer(many=False)

    class Meta:
        model = Endereco
        fields = ['id', 'logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'tipo_endereco']


class CartaoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['id', 'numero', 'dt_expiracao', 'cvv', 'saldo', 'FK_usuario']

class CartaoReadSerializer(serializers.ModelSerializer):
        class Meta:
            model = CartaoCredito
            fields = ['id', 'numero', 'dt_expiracao', 'cvv', 'saldo']


class UsuarioReadSerializer (serializers.ModelSerializer):
    cartoes = CartaoReadSerializer(many=True, read_only=True)
    enderecos = EnderecoReadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']

class UsuarioWriteSerializer (serializers.ModelSerializer):    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone']


class TransacaoRequestSerializer (serializers.ModelSerializer):
    numero = serializers.CharField(max_length=16)
    dt_expiracao = serializers.DateField()
    cvv = serializers.CharField(max_length=3)
    valor = serializers.DecimalField(max_digits=10,decimal_places=2)

class TransacaoResponseSerializer (serializers.ModelSerializer):
    status = serializers.CharField()
    codigo_autorizacao = serializers.UUIDField()
    dt_transacao = serializers.DateTimeField()
    mensagem = serializers.CharField()
