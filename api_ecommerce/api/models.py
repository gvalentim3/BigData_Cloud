from django.db import models

# Models são representações das tabelas da nossa DB

class Usuario (models.Model):
    nome = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    data_nascimento = models.DateField
    cpf = models.CharField(max_length=11)
    telefone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'usuario'
    
class Endereco (models.Model):
    logradouro = models.CharField(max_length=200)
    complemento = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=8)
    id_tp_endereco = models.IntegerField()
    id_usuario = models.IntegerField()

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'endereco'