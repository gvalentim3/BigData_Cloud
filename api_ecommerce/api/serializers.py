from rest_framework import serializers
from models import Usuario
from models import Endereco

class UsuarioSerializer (serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        
class EnderecoSerializer (serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'