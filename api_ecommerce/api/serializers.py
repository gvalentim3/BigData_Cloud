from rest_framework import serializers
from .models import CartaoCredito,Usuario,Endereco,Produto #,Pedido
from drf_yasg.utils import swagger_auto_schema
from decimal import Decimal


class EnderecoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep']

class EnderecoReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['id', 'logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'usuario']


class CartaoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['numero', 'dt_expiracao', 'cvv', 'saldo']

class CartaoReadSerializer(serializers.ModelSerializer):
        class Meta:
            model = CartaoCredito
            fields = ['id', 'numero', 'dt_expiracao', 'cvv', 'saldo', 'usuario']


class UsuarioReadSerializer (serializers.ModelSerializer):
    cartoes = CartaoReadSerializer(many=True, read_only=True, required=False)
    enderecos = EnderecoReadSerializer(many=True, read_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']

class UsuarioCreateSerializer (serializers.ModelSerializer):    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone']

        def validate_email(self, email):
            if Usuario.objects.filter(email=email).exists():
                raise serializers.ValidationError("Email já cadastrado.")
            return email
        
        def validate_cpf(self, cpf):
            if Usuario.objects.filter(cpf=cpf).exists():
                raise serializers.ValidationError("CPF já cadastrado.")
            return cpf

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
    preco = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
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
        attrs['nome'] = attrs.get('nome', '').lower()
        attrs['categoria'] = attrs.get('categoria', '').lower()

        if attrs.get('preco', 0) <= 0:
            raise serializers.ValidationError(
                {"preco": "O preço deve ser maior que zero."}
            )
        
        for url in attrs.get('imagens', []):
            if not url.startswith(('http://', 'https://')):
                raise serializers.ValidationError(
                    {"imagens": f"URL inválida: {url}"}
                )
            
        return attrs

    def create(self, validated_data):
        return Produto.from_dict(validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance