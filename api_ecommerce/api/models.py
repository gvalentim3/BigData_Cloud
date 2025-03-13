from django.db import models

# Models são representações das tabelas da nossa DB

class Usuario (models.Model):
    nome = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    data_nascimento = models.DateField
    cpf = models.CharField(max_length=11)
    telefone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        db_table = 'usuario'
    
class Endereco (models.Model):
    logradouro = models.CharField(max_length=200)
    complemento = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=8)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

class Cartao (models.Model):
    numero = models.CharField(max_length=16)
    validade = models.DateField
    cvv = models.CharField(max_length=3)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

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