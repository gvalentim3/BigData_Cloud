from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import UsuarioSerializer, EnderecoSerializer
# Criar requisições
from .models import Usuario, Endereco, CartaoCredito
from rest_framework import status


class UsuarioView(APIView):
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            cpf = serializer.validated_data.get('cpf')

            if Usuario.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Este email já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if Usuario.objects.filter(cpf=cpf).exists():
                return Response(
                    {'error': 'Este CPF já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        if pk:
            try:
                # Se na requisição é enviado um ID de usuário, programa verifica se existe na base de dados e caso exista, retorna os dados do usuário junto dos de cartão e endereço.
                usuario = Usuario.objects.prefetch_related('cartoes', 'enderecos').get(pk=pk)
                serializer = UsuarioSerializer(usuario)
                return Response(serializer.data)
            except Usuario.DoesNotExist:
                return Response(
                    {'error': 'Usuário não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        usuarios = Usuario.objects.prefetch_related('cartoes', 'enderecos').all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            if Usuario.objects.filter(email=email).exclude(pk=pk).exists():
                return Response(
                    {'error': 'Este email já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EnderecoView(APIView):
    def post(self, request):
        serializer = EnderecoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        if pk:
            try:
                # Se na requisição é enviado um ID de endereço, programa verifica se existe na base de dados e caso exista, retorna os dados.
                endereco = Endereco.objects.get(pk=pk)
                serializer = EnderecoSerializer(endereco)
                return Response(serializer.data)
            except Endereco.DoesNotExist:
                return Response(
                    {'error': 'Endereço não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        enderecos = Endereco.objects.all()
        serializer = EnderecoSerializer(enderecos, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            endereco = Endereco.objects.get(pk=pk)
        except Endereco.DoesNotExist:
            return Response(
                {'error': 'Endereço não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = EnderecoSerializer(endereco, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            endereco = Endereco.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Endereço não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        endereco.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


