from rest_framework import status
from rest_framework.response import Response
from .models import Usuario
from .serializers import CartaoWriteSerializer, EnderecoWriteSerializer

def criar_cartao(usuario_id, cartao_data, request=None):
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        error_data = {"error": "Usuário não encontrado"}
        if request:
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)
        return error_data, status.HTTP_404_NOT_FOUND

    data_copy = cartao_data.copy()
    data_copy['usuario'] = usuario.id
    serializer = CartaoWriteSerializer(data=data_copy)

    if serializer.is_valid():
        serializer.save()
        if request:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return serializer.data, status.HTTP_201_CREATED
    
    if request:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return serializer.errors, status.HTTP_400_BAD_REQUEST

def criar_endereco(usuario_id, endereco_data, request=None):
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        error_data = {"error": "Usuário não encontrado"}
        if request:
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)
        return error_data, status.HTTP_404_NOT_FOUND
    
    data_copy = endereco_data.copy()
    data_copy['usuario'] = usuario.id
    serializer = EnderecoWriteSerializer(data=data_copy)

    if serializer.is_valid():
        serializer.save()
        if request:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return serializer.data, status.HTTP_201_CREATED
    
    if request:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return serializer.errors, status.HTTP_400_BAD_REQUEST