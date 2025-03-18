from rest_framework.response import Response
from api.serializers import UsuarioSerializer, EnderecoSerializer, CartaoSerializer
# Criar requisições
from .models import Usuario, Endereco, CartaoCredito
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ValidationError

class UsuarioView(APIView):
    def post(self, request):
        user_serializer = UsuarioSerializer(data=request.data)
        if user_serializer.is_valid():
            email = user_serializer.validated_data.get('email')
            cpf = user_serializer.validated_data.get('cpf')

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
            
            validated_data = user_serializer.validated_data.copy()
            data_cartoes = validated_data.pop('cartoes')
            data_enderecos = validated_data.pop('enderecos')            

            try:
                with transaction.atomic():
                    usuario = Usuario.objects.create(**validated_data)
                    
                    if data_enderecos:
                        data_enderecos['id_usuario_endereco'] = usuario.id
                        endereco_serializer = EnderecoSerializer(data=data_enderecos)
                        if endereco_serializer.is_valid():
                            endereco_serializer.save()
                        else:
                            raise ValidationError(endereco_serializer.errors)

                    if data_cartoes:
                        data_cartoes['id_usuario_cartao'] = usuario.id
                        cartao_serializer = CartaoSerializer(data=data_cartoes)
                        if cartao_serializer.is_valid():
                            cartao_serializer.save()
                        else:
                            raise ValidationError(cartao_serializer.errors)
                    
                    return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
            # Handle validation errors
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
            # Handle other exceptions
                return Response({'error': 'Ocorreu um erro ao processar a solicitação.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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


