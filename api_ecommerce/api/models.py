from django.db import models
from uuid import uuid4

# Models são representações das tabelas da nossa DB

class Usuario (models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    email = models.CharField(max_length=150, null=False, blank=False, unique=True)
    dt_nascimento = models.DateField(null=False, blank=False)
    cpf = models.CharField(max_length=11, null=False, blank=False, unique=True)
    telefone = models.CharField(max_length=20, null=False, blank=False)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        db_table = 'usuario'
    
class TipoEndereco(models.Model):
    tipo = models.CharField(max_length=45)

    class Meta:
        db_table = 'tipo_endereco'

class Endereco (models.Model):
    logradouro = models.CharField(max_length=200, null=False, blank=False)
    complemento = models.CharField(max_length=200, null=False, blank=True, default="")
    bairro = models.CharField(max_length=100, null=False, blank=False)
    cidade = models.CharField(max_length=100, null=False, blank=False)
    estado = models.CharField(max_length=100, null=False, blank=False)
    cep = models.CharField(max_length=8, null=False, blank=False)
    FK_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="enderecos")
    FK_tp_endereco = models.ForeignKey(TipoEndereco, on_delete=models.CASCADE, related_name="enderecos")

    class Meta:
        db_table = 'endereco'

class CartaoCredito (models.Model):
    numero = models.CharField(max_length=45, null=False, blank=False)
    dt_expiracao = models.DateField(null=False, blank=False)
    cvv = models.CharField(max_length=3, null=False, blank=False)
    saldo = models.DecimalField(decimal_places=2, null=False, blank=False)
    FK_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="cartoes")

    class Meta:
        db_table = 'cartao_credito'


class Produto:
    def __init__(self, produtocategoria, nome , preco, descricao, imagem, id=None):
        self.id = id or str(uuid4())  # gera um UUID se nao for informado
        self.produtocategoria = produtocategoria
        self.nome = nome
        self.preco = preco
        self.descricao = descricao
        self.imagem = imagem

    def to_dict(self):
        return {
            "id": self.id,
            "produtocategoria": self.produtocategoria,
            "nome": self.nome,
            "preco": self.preco,
            "descricao": self.descricao,
            "imagem": self.imagem,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            produtocategoria=data.get("produtocategoria"),
            nome=data.get("nome"),
            preco=data.get("preco"),
            descricao=data.get("descricao"),
            imagem=data.get("imagem"),
        )

class Pedido:
    def __init__(self, produto_id, quantidade, nome_cliente, id=None):
        self.id = id or str(uuid4())  # Generate a UUID if not provided
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.nome_cliente = nome_cliente

    def to_dict(self):
        return {
            "id": self.id,
            "produto_id": self.produto_id,
            "quantidade": self.quantidade,
            "nome_cliente": self.nome_cliente,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            produto_id=data.get("produto_id"),
            quantidade=data.get("quantidade"),
            nome_cliente=data.get("nome_cliente"),
        )
"""
class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome




class Pedido(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Processando', 'Processando'),
        ('Concluído', 'Concluído'),
        ('Cancelado', 'Cancelado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
"""