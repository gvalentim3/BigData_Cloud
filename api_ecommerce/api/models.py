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