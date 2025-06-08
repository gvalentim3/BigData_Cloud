from rest_framework import serializers
from .models import CartaoCredito,Usuario,Endereco,Produto
from decimal import Decimal
from .apps import cosmos_db
from azure.cosmos import exceptions as cosmos_exceptions
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator

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
            fields = ['id', 'numero', 'dt_expiracao', 'saldo', 'usuario']


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
    
class ProdutoPedidoSerializer(serializers.Serializer):
    container = cosmos_db.containers["produtos"]

    id_produto = serializers.CharField()
    nome_produto = serializers.CharField(read_only=True)
    categoria_produto = serializers.CharField()
    preco_produto = serializers.DecimalField(
        read_only=True,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    quantidade = serializers.IntegerField(
        min_value=1
    )


class PedidoSerializer(serializers.Serializer):
    container_produtos = cosmos_db.containers['produtos']

    id = serializers.CharField(read_only=True)
    numero = serializers.IntegerField(read_only=True)
    usuario = serializers.IntegerField()
    produtos = serializers.ListField(
        child=ProdutoPedidoSerializer(),
        min_length = 1
    )
    preco_total = serializers.DecimalField(
        read_only=True,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal(0.01)
    )
    id_cartao = serializers.IntegerField()
    cvv = serializers.CharField(write_only=True, required=True, min_length=3, max_length=3)
    id_endereco = serializers.IntegerField()
    data = serializers.DateField(read_only=True)

    def validate(self, attrs):
        self._validar_usuario(attrs)
        self._validar_cartao(attrs)
        self._validar_endereco(attrs)
        
        attrs['preco_total'] = self._calcular_preco_total(attrs)
        
        attrs['data'] = datetime.now().isoformat()

        self.cvv = attrs.pop('cvv')
        
        return attrs

    def _validar_usuario(self, attrs):
        try:
            Usuario.objects.get(id=attrs['usuario'])
        except Usuario.DoesNotExist:
            raise serializers.ValidationError(
                {'id_usuario': 'Usuário não encontrado'}
            )

    def _validar_cartao(self, attrs):
        try:
            cartao = CartaoCredito.objects.get(id=attrs['id_cartao'])
            if cartao.usuario.id != attrs['usuario']:
                raise serializers.ValidationError(
                    {'id_cartao': 'Cartão não pertence ao usuário'}
                )
        except CartaoCredito.DoesNotExist:
            raise serializers.ValidationError(
                {'id_cartao': 'Cartão não encontrado'}
            )

    def _validar_endereco(self, attrs):
        try:
            endereco = Endereco.objects.get(id=attrs['id_endereco'])
            if endereco.usuario.id != attrs['usuario']:
                raise serializers.ValidationError(
                    {'id_endereco': 'Endereço não pertence ao usuário'}
                )
        except Endereco.DoesNotExist:
            raise serializers.ValidationError(
                {'id_endereco': 'Endereço não encontrado'}
            )

    def _calcular_preco_total(self, attrs):
        preco_total = 0
        
        for produto_data in attrs['produtos']:
            id_produto = produto_data['id_produto']
            qtd_produto = produto_data['quantidade']
            categoria_produto = produto_data['categoria_produto']

            try:
                produto = self.container_produtos.read_item(
                    id_produto, 
                    partition_key=categoria_produto
                )
                preco_produto = produto['preco']
                produto_data['preco_produto'] = preco_produto

                nome_produto = produto['nome']
                produto_data['nome_produto'] = nome_produto

                preco_total += qtd_produto * preco_produto
            
            except cosmos_exceptions.CosmosResourceNotFoundError:
                raise serializers.ValidationError(
                    {'produtos': f'Produto {id_produto} não encontrado na categoria {categoria_produto}'}
                )
            except Exception as e:
                raise serializers.ValidationError(
                    {'produtos': f'Erro ao validar produto {id_produto}: {str(e)}'}
                )
        
        return preco_total
    
class ExtratoRequestSerializer(serializers.Serializer):
    ano = serializers.IntegerField(
            validators=[
                MinValueValidator(2025, message="O ano não pode ser anterior a 2025"),
                MaxValueValidator(datetime.now().year, message="O ano não pode ser no futuro")
            ]
        )
    mes = serializers.IntegerField(            
        validators=[
                MinValueValidator(1, message="Mês não pode ser menor que 1."),
                MaxValueValidator(12, message="Mês não pode ser maior que 12.")
            ])
    usuario = serializers.IntegerField()
    cartao = serializers.IntegerField()

    def validate(self, attrs):
        try:
            Usuario.objects.get(id=attrs['usuario'])
        except Usuario.DoesNotExist:
            raise serializers.ValidationError(
                {'usuario': 'Usuário não encontrado'}
            )
        
        try:
            cartao = CartaoCredito.objects.get(id=attrs['cartao'])
            if cartao.usuario.id != attrs['usuario']:
                raise serializers.ValidationError(
                    {'cartao': 'Cartão não pertence ao usuário'}
                )
        except CartaoCredito.DoesNotExist:
            raise serializers.ValidationError(
                {'cartao': 'Cartão não encontrado'}
            )
        
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        
        if attrs['ano'] > ano_atual or (attrs['ano'] == ano_atual and attrs['mes'] > mes_atual):
            raise serializers.ValidationError({
                'mes': 'Não é possível consultar extrato de meses futuros'
        })

        return attrs

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        validated_data['ano_mes'] = f"{validated_data['ano']}-{validated_data['mes']:02d}"

        return validated_data

class ExtratoResponseSerializer(serializers.Serializer):
    data = serializers.DateTimeField(format=f'%d-%m-%Y')
    numero = serializers.CharField()
    produtos = ProdutoPedidoSerializer(many=True)
    preco_total = serializers.DecimalField(max_digits=10, decimal_places=2)
