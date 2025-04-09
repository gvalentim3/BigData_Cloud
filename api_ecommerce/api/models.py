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
    saldo = models.DecimalField(max_digits=10 ,decimal_places=2, null=False, blank=False)
    FK_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="cartoes")

    class Meta:
        db_table = 'cartao_credito'

class Produto:  
    def __init__(self, categoria, nome, preco, descricao=None, imagem=None, quantidade=0, id=None):
        self.id = id or str(uuid4())
        self.categoria = categoria  # Partition key
        self.nome = nome
        self.preco = float(preco)
        self.descricao = descricao or ""
        self.imagem = imagem or ""
        self.quantidade = int(quantidade)

    def to_dict(self):
        return {
            "id": self.id,
            "categoria": self.categoria,
            "nome": self.nome,
            "preco": self.preco,
            "descricao": self.descricao,
            "imagem": self.imagem,
            "quantidade": self.quantidade
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            categoria=data["categoria"],
            nome=data["nome"],
            preco=data["preco"],
            descricao=data.get("descricao"),
            imagem=data.get("imagem"),
            quantidade=data.get("quantidade", 0)
        )