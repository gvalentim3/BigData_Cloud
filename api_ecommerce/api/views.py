from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import (UsuarioReadSerializer, UsuarioWriteSerializer, CartaoReadSerializer, 
                             CartaoWriteSerializer, EnderecoReadSerializer, EnderecoWriteSerializer, 
                             TipoEnderecoSerializer, TransacaoRequestSerializer, TransacaoResponseSerializer)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Usuario, Endereco, CartaoCredito
from rest_framework import status
import requests
from django.utils import timezone
import uuid



class UsuarioCreateListView(APIView):
    @swagger_auto_schema(
        operation_description="Criação um novo usuário. Necessário enviar também pelo menos um cadastro de cartão e um de endereço",
        request_body=UsuarioWriteSerializer,
        responses={
            201: UsuarioWriteSerializer,
            400: "Erro de validação: Email ou CPF já cadastrados."
        }
    )
    def post(self, request):
        raw_data = request.data.copy()
        cartao_raw_data = None
        if 'cartao' in raw_data and raw_data['cartao']:            
            cartao_raw_data = raw_data.pop('cartao')
    
        
        user_serializer = UsuarioWriteSerializer(data=raw_data)
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
            
            usuario = user_serializer.save()
            usuario_id = usuario.id

            if cartao_raw_data: 
                cartao_raw_data["FK_usuario"] = usuario_id

                response = requests.post(
                    f'http://localhost:8000/api/usuarios/{usuario_id}/cartoes/',
                    json=cartao_raw_data
                )
            return Response(user_serializer.errors, status=status.HTTP_200_OK)
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Lista de todos os usuários cadastrados.",
        responses={
            200: UsuarioReadSerializer(many=True),
        }
    )
    def get(self, request):
        lista_usuarios = Usuario.objects.all()
        serializer = UsuarioReadSerializer(lista_usuarios, many=True)
        return Response(serializer.data)
class UsuarioReadUpdateDeleteView(APIView):
    @swagger_auto_schema(
        operation_description="Retorna um usuário específico pelo ID ou lista todos os usuários se nenhum ID for fornecido.",
        id_usuario_parameters=[
            openapi.Parameter(
                'id_usuario',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID do usuário",
                required=True
            )
        ],
        responses={
            200: UsuarioReadSerializer,
            404: "Usuário não encontrado."
        }
    )
    def get(self, request, id_usuario):
        try:
            usuario = Usuario.objects.get(id=id_usuario)
            serializer = UsuarioReadSerializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )


    @swagger_auto_schema(
        operation_description="Atualiza um usuário pelo ID (parcialmente).",
        id_usuario_parameters=[
            openapi.Parameter(
                'id_usuario',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID do usuário",
                required=True
            )
        ],
        request_body=UsuarioWriteSerializer,
        responses={
            200: UsuarioWriteSerializer,
            400: "Erro de validação: Email já cadastrado.",
            404: "Usuário não encontrado."
        }
    )
    def patch(self, request, id_usuario):
        try:
            usuario = Usuario.objects.get(id=id_usuario)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UsuarioReadSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            cpf = serializer.validated_data.get('cpf')
            if Usuario.objects.filter(email=email).exclude(id=id_usuario).exists():
                return Response(
                    {'error': 'Este email já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if usuario.cpf != cpf:
                return Response(
                    {'error': 'Não é possível alterar o CPF do cadastro.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_description="Exclui um usuário pelo ID.",
        responses={
            204: "Usuário excluído com sucesso.",
            404: "Usuário não encontrado."
        }
    )
    def delete(self, request, id_usuario):
        try:
            usuario = Usuario.objects.get(id=id_usuario)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnderecoCreateListView(APIView):
    @swagger_auto_schema(
        request_body=EnderecoWriteSerializer,
        id_usuario_parameters=[
            openapi.Parameter(
                'id_usuario',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID do usuário",
                required=True
            )
        ],
        responses={201: CartaoWriteSerializer, 400: "Erro de validação"},
        operation_description="Cria um novo Endereço vinculado a um usuário.",
    )
    def post(self, request, id_usuario):
        try:
            usuario = Usuario.objects.get(pk=id_usuario)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuário não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        endereco_raw_data = request.data.copy()

        tipo_endereco_id = None
        if 'tipo_endereco' in endereco_raw_data and endereco_raw_data['tipo_endereco']:            
            tipo_endereco_raw_data = endereco_raw_data.pop('tipo_endereco')
            tipo_endereco_serializer = TipoEnderecoSerializer(tipo_endereco_raw_data)
            
            if tipo_endereco_serializer.is_valid():
                tipo_endereco = tipo_endereco_serializer.save()
                tipo_endereco_id = tipo_endereco.id


        endereco_raw_data['FK_tp_endereco'] = tipo_endereco_id
        endereco_raw_data['FK_usuario'] = usuario.id
        serializer = EnderecoWriteSerializer(data=endereco_raw_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Lista todos os endereços de um usuário (através do ID)",
        id_usuario_parameters=[
            openapi.Parameter(
                "id_usuario",
                openapi.IN_PATH,
                description="ID do Cartão",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={200: EnderecoReadSerializer(many=True), 404: "Usuário não encontrado"},
    )
    def get(self, request, id_usuario):
            try:
                usuario = Usuario.objects.get(id=id_usuario)
            except Usuario.DoesNotExist:
                return Response(
                {'error': 'Usuario não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

            enderecos = Endereco.objects.filter(FK_usuario=usuario.id)
            serializer = EnderecoReadSerializer(enderecos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
class EnderecoUpdateDeleteView(APIView):
    @swagger_auto_schema(
        request_body=EnderecoWriteSerializer,
        responses={200: EnderecoWriteSerializer, 400: "Erro de validação", 404: "Endereço não encontrado"},
        operation_description="Atualiza parcialmente um endereço pelo ID.",
    )
    def patch(self, request, id_usuario, id_endereco):
            try:
                usuario = Usuario.objects.get(id=id_usuario)
            except Usuario.DoesNotExist:
                return Response(
                {'error': 'Usuario não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
            try:
                endereco = Endereco.objects.get(id=id_endereco, FK_usuario=usuario.id)
            except Endereco.DoesNotExist:
                return Response(
                    {"error": "Endereço não encontrado."}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = EnderecoWriteSerializer(endereco, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        responses={204: "Endereço deletado", 404: "Endereço não encontrado"},
        operation_description="Deleta um endereço pelo ID.",
    )
    def delete(self, request, id_usuario, id_endereco):
        try:
            endereco = Endereco.objects.get(id=id_endereco, FK_usuario=id_usuario)
        except Endereco.DoesNotExist:
            return Response(
                {"error": "Endereço não encontrado para este usuário."}, status=status.HTTP_404_NOT_FOUND
            )

        endereco.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartaoCreateListView(APIView):
    @swagger_auto_schema(
        request_body=CartaoWriteSerializer,
        id_usuario_parameters=[
            openapi.Parameter(
                'id_usuario',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID do usuário",
                required=True
            )
        ],
        responses={201: CartaoWriteSerializer, 400: "Erro de validação"},
        operation_description="Cria um novo Cartão.",
    )
    def post(self, request, id_usuario):
        try:
            usuario = Usuario.objects.get(pk=id_usuario)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuário não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        data_copy = request.data.copy()
        data_copy['FK_usuario'] = usuario.id
        serializer = CartaoWriteSerializer(data=data_copy)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_description="Lista todos os cartões de um usuário (através do ID)",
        id_usuario_parameters=[
            openapi.Parameter(
                "id_usuario",
                openapi.IN_PATH,
                description="ID do Cartão",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={200: CartaoReadSerializer(many=True), 404: "Usuário não encontrado"},
    )
    def get(self, request, id_usuario):
            try:
                usuario = Usuario.objects.get(id=id_usuario)
            except Usuario.DoesNotExist:
                return Response(
                {'error': 'Usuario não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

            cartoes = CartaoCredito.objects.filter(FK_usuario=usuario.id)
            serializer = CartaoWriteSerializer(cartoes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
class CartaoUpdateDeleteView(APIView):
    @swagger_auto_schema(
        request_body=CartaoWriteSerializer,
        responses={200: CartaoWriteSerializer, 400: "Erro de validação", 404: "Cartão não encontrado"},
        operation_description="Atualiza parcialmente um cartão pelo ID.",
    )
    def put(self, request, id_usuario, id_cartao):
            try:
                usuario = Usuario.objects.get(id=id_usuario)
            except Usuario.DoesNotExist:
                return Response(
                {'error': 'Usuario não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
            try:
                cartao = CartaoCredito.objects.get(id=id_cartao, FK_usuario=usuario.id)
            except CartaoCredito.DoesNotExist:
                return Response(
                    {"error": "Cartão não encontrado neste usuário."}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = CartaoWriteSerializer(cartao, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        responses={204: "Cartão deletado", 404: "Cartão não encontrado"},
        operation_description="Deleta um cartão pelo ID.",
    )
    def delete(self, request, id_usuario, id_cartao):
        try:
            usuario = Usuario.objects.get(id=id_usuario)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            cartao = CartaoCredito.objects.get(id=id_cartao, FK_usuario=id_usuario)
        except CartaoCredito.DoesNotExist:
            return Response(
                {"error": "Cartão não encontrado para este usuário."}, status=status.HTTP_404_NOT_FOUND
            )

        cartao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AuthorizeTransacaoView(APIView):
    def post(self, request, id_usuario):
        try:
            usuario = Usuario.objects.get(pk=id_usuario)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuário não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TransacaoRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        numero_cartao = serializer.validated_data['numero']
        cvv_cartao = serializer.validated_data['cvv']
        dt_expiracao_cartao = serializer.validated_data['dt_expiracao']
        valor_transacao = serializer.validated_data['valor']

        cartao_compra = None
        for cartao in usuario.cartoes.all():
            if cartao.numero == numero_cartao and cartao.cvv == cvv_cartao:
                cartao_compra = cartao
                break
        
        if not cartao_compra:
            transacao_response = {
                "status": "NOT_AUTHORIZED",
                "dt_transacao": timezone.now(),
                "message": "Cartão não encontrado para o usuário"
            }

            response_serializer = TransacaoResponseSerializer(data=transacao_response)            
            return Response(response_serializer, status=status.HTTP_404_NOT_FOUND)
        
        if dt_expiracao_cartao < timezone.now():
            transacao_response = {
                "status": "NOT_AUTHORIZED",
                "dt_transacao": timezone.now(),
                "message": "Cartão expirado"
            }

            response_serializer = TransacaoResponseSerializer(data=transacao_response)            
            return Response(response_serializer, status=status.HTTP_400_BAD_REQUEST)
        
        if cartao_compra.saldo < valor_transacao:
            transacao_response = {
                "status": "NOT_AUTHORIZED",
                "dt_transacao": timezone.now(),
                "message": "Cartão sem saldo suficiente para realizar a compra"
            }

            response_serializer = TransacaoResponseSerializer(data=transacao_response)            
            return Response(response_serializer, status=status.HTTP_400_BAD_REQUEST)
        
        cartao_compra.saldo -= valor_transacao
        cartao_compra.save()
        
        transacao_response = {
            "status": "AUTHORIZED",
            "codigo_autorizacao": uuid.uuid4(),
            "dt_transacao": timezone.now(),
            "mensagem": "Cartão sem saldo suficiente para realizar a compra"
        }