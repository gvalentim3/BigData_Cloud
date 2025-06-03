from rest_framework import serializers
from .models import CartaoCredito,Usuario,Endereco,TipoEndereco,Produto #,Pedido
from drf_yasg.utils import swagger_auto_schema
from decimal import Decimal

class TipoEnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEndereco
        fields = ['tipo']


class EnderecoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'tipo_endereco', 'usuario']

class EnderecoReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Endereco
        fields = ['id', 'logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep']


class CartaoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['id', 'numero', 'dt_expiracao', 'cvv', 'saldo', 'usuario']

class CartaoReadSerializer(serializers.ModelSerializer):
        class Meta:
            model = CartaoCredito
            fields = ['id', 'numero', 'dt_expiracao', 'cvv', 'saldo']


class UsuarioReadSerializer (serializers.ModelSerializer):
    cartoes = CartaoReadSerializer(many=True, read_only=True, required=False)
    enderecos = EnderecoReadSerializer(many=True, read_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']

class UsuarioWriteSerializer (serializers.ModelSerializer):
    cartoes = CartaoReadSerializer(many=True, read_only=True, required=False, default=[])
    enderecos = EnderecoReadSerializer(many=True, read_only=True, required=False, default=[])
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']


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

class ProdutoSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    categoria = serializers.CharField(
        required=True,
        max_length=50,
        help_text="Partition key (categoria do produto)"
    )
    nome = serializers.CharField(max_length=100)
    preco = serializers.FloatField(
        min_value=float(Decimal('0.01')),  # Explicitly convert to float
        max_value=100000000.0
    )
    descricao = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    imagens = serializers.ListField(
        child=serializers.URLField()
    )
    
    quantidade = serializers.IntegerField(
        min_value=0,
        default=0
    )

    def validate(self, attrs):
        if 'nome' in attrs and attrs['nome']:
            attrs['nome'] = attrs['nome'].lower()
        if 'categoria' in attrs and attrs['categoria']:
            attrs['categoria'] = attrs['categoria'].lower()
        return attrs

    def create(self, validated_data):
        return Produto.from_dict(validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance