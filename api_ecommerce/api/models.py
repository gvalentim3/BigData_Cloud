from django.db import models

# Models são representações das tabelas da nossa DB

class Usuario (models.Model):
    nome = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    data_nascimento = models.DateField
    cpf = models.CharField(max_length=11)
    telefone = models.CharField(max_length=11)
    
    def __str__(self):
        return self.title
    
class Endereco (models.Model):
    logradouro = models.CharField(max_length=50)
    complemento = models.CharField(max_length=15)
    bairro = models.CharField(max_length=30)
    cidade = models.CharField(max_length=30)
    estado = models.CharField(max_length=30)
    cep = models.CharField(max_length=8)

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