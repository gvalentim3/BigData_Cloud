from rest_framework import serializers
from api.models import CartaoCredito,Usuario,Endereco, TipoEndereco

class EnderecoSerializer (serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['logradouro', 'complemento', 'bairro', 'cidade', 'estado', 'cep']

class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['numero', 'dt_expiracao', 'cvv', 'saldo']

class UsuarioSerializer (serializers.ModelSerializer):
    cartoes = CartaoSerializer(many=True, read_only=True)
    enderecos = EnderecoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']
        read_only_fields = ['cpf']

"""        
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaoCredito
        fields = ['numero', 'dt_expiracao', 'cvv', 'saldo']

class UsuarioSerializer (serializers.ModelSerializer):
    cartoes = CartaoSerializer(many=True, read_only=True)
    enderecos = EnderecoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'dt_nascimento', 'cpf', 'telefone', 'cartoes', 'enderecos']
        read_only_fields = ['cpf']

    def validate(self, data):
        if 'cartoes' not in data or not data['cartoes']:
            raise serializers.ValidationError("Dados do Cartão são obrigatórios.")
        
        if 'enderecos' not in data or not data['enderecos']:
            raise serializers.ValidationError("Dados do Endereço são obrigatórios.")
        
        cartoes_data = data['cartoes']
        for cartao_data in cartoes_data:
            cartao_serializer = CartaoSerializer(data=cartao_data)
            if not cartao_serializer.is_valid():
                raise serializers.ValidationError(cartao_serializer.errors)
        
        data_enderecos = data['enderecos']
        for data in data_enderecos:
            endereco_serializer = EnderecoSerializer(data=data)
            if not endereco_serializer.is_valid():
                raise serializers.ValidationError(endereco_serializer.errors)
            
        return data