from rest_framework import serializers
from .models import CartaoCredito,Usuario,Endereco,TipoEndereco #Produto,Pedido

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
    cartoes = CartaoReadSerializer(many=True, read_only=True, required=False, default=list)
    enderecos = EnderecoReadSerializer(many=True, read_only=True, required=False, default=list)
    
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']

class UsuarioWriteSerializer (serializers.ModelSerializer):    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone']


class TransacaoRequestSerializer(serializers.Serializer):
    numero = serializers.CharField(
        max_length=16,
        min_length=16,
        help_text="Número do cartão (16 dígitos)"
    )
    dt_expiracao = serializers.DateField(
        help_text="Data de expiração do cartão no formato YYYY-MM-DD"
    )
    cvv = serializers.CharField(
        max_length=3,
        min_length=3,
        help_text="Código de segurança do cartão (3 dígitos)"
    )
    valor = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor da transação (ex: 10.00)"
    )

class TransacaoResponseSerializer(serializers.Serializer):
    status = serializers.CharField(
        help_text="Status da autorização (AUTHORIZED/NOT_AUTHORIZED)"
    )
    codigo_autorizacao = serializers.UUIDField(
        help_text="Código único de identificação da transação"
    )
    dt_transacao = serializers.DateTimeField(
        help_text="Data/hora da transação"
    )
    mensagem = serializers.CharField(
        help_text="Mensagem descritiva do status"
    )
