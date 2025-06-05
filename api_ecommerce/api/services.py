from rest_framework import status
from rest_framework.response import Response
from .models import Usuario, CartaoCredito, Endereco
from .serializers import CartaoWriteSerializer, EnderecoWriteSerializer

class CartaoService():
    def cria_cartao(usuario_id, cartao_data):
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return None, {"error": "Usuário não encontrado"}

        serializer = CartaoWriteSerializer(data={**cartao_data, 'usuario': usuario.id})

        if not serializer.is_valid():
            return None, serializer.errors    
        
        cartao = CartaoCredito.objects.create(
            usuario=usuario,
            **serializer.validated_data
        )

        return cartao, None
        
class EnderecoService():
    def cria_endereco(usuario_id, endereco_data):
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return None, {"error": "Usuário não encontrado"}
        
        serializer = EnderecoWriteSerializer(data={**endereco_data, 'usuario': usuario.id})

        if not serializer.is_valid():
            return None, serializer.errors    
        
        endereco = Endereco.objects.create(
            usuario=usuario,
            **serializer.validated_data
        )

        return endereco, None


class UsuarioService():
    def cria_cartoes_enderecos(id_usuario, cartoes_data, enderecos_data):
        for cartao_data in cartoes_data or []:
            try:
                CartaoService.cria_cartao(
                    id_usuario, 
                    cartao_data
                )
            
            except:
                continue

        for endereco_data in enderecos_data or []:
            try:
                EnderecoService.cria_endereco(
                    id_usuario, 
                    endereco_data
                )
            except:
                continue