from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (UsuarioReadSerializer, UsuarioWriteSerializer, CartaoReadSerializer, 
                             CartaoWriteSerializer, EnderecoReadSerializer, EnderecoWriteSerializer, 
                             TipoEnderecoSerializer, TransacaoRequestSerializer, TransacaoResponseSerializer, ProdutoSerializer) #, PedidoSerializer)
from .apps import cosmos_db
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Usuario, Endereco, CartaoCredito, TipoEndereco, Produto #, Pedido
from rest_framework import status
import requests
from django.utils import timezone
import uuid
from django.conf import settings
from azure.cosmos import exceptions as cosmos_exceptions


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
        print(request)
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
                    f'https://projeto-ibmec-cloud-9016-2025-f8hhfgetc3g3a2fg.centralus-01.azurewebsites.net/api/usuarios/{usuario_id}/cartoes/',
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
            serializer = CartaoReadSerializer(cartoes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
class CartaoUpdateDeleteView(APIView):
    @swagger_auto_schema(
        request_body=CartaoWriteSerializer,
        responses={200: CartaoWriteSerializer, 400: "Erro de validação", 404: "Cartão não encontrado"},
        operation_description="Atualiza parcialmente um cartão pelo ID.",
    )
    def patch(self, request, id_usuario, id_cartao):
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
    @swagger_auto_schema(
        request_body=TransacaoRequestSerializer,
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
            202: TransacaoResponseSerializer,
            400: "Erro de validação",
            404: "Usuário ou cartão não encontrado"
        },
        operation_description="Autoriza transação de compra com cartão de crédito."
    )    
    
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
        
        data = serializer.validated_data
        
        cartao_compra = usuario.cartoes.filter(
            numero=data['numero'],
            cvv=data['cvv']
        ).first()

        if not cartao_compra:
            return self._error_response("Cartão não encontrado para o usuário")
        
        if data['dt_expiracao'] < timezone.now().date():
            return self._error_response("Cartão expirado")
            
        if cartao_compra.saldo < data['valor']:
            return self._error_response("Saldo insuficiente")
        
        cartao_compra.saldo -= data['valor']
        cartao_compra.save()
        
        return self._success_response()

    def _error_response(self, message):
        response_data = {
            "status": "NOT_AUTHORIZED",
            "codigo_autorizacao": uuid.uuid4(),
            "dt_transacao": timezone.now(),
            "mensagem": message
        }
        serializer = TransacaoResponseSerializer(data=response_data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def _success_response(self):
        response_data = {
            "status": "AUTHORIZED",
            "codigo_autorizacao": uuid.uuid4(),
            "dt_transacao": timezone.now(),
            "mensagem": "Compra autorizada com sucesso"
        }
        serializer = TransacaoResponseSerializer(data=response_data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class ProdutoCreateListView(APIView):
    partition_key = "categoria"
    @swagger_auto_schema(
        operation_description="Cria um novo produto",
        request_body=ProdutoSerializer,
        responses={201: ProdutoSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        serializer = ProdutoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        produto = serializer.create(serializer.validated_data)
        try:
            created_item = cosmos_db.containers["produtos"].create_item(
                body=produto.to_dict(),
                enable_automatic_id_generation=True
            )
            return Response(created_item, status=status.HTTP_201_CREATED)
        except cosmos_exceptions.CosmosHttpResponseError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Lista todos os Produtos",
        responses={
            200: ProdutoSerializer(many=True),
            404: "Not Found",
            400: "Bad Request"
        }
    )
    def get(self, request):
        container = cosmos_db.containers["produtos"]
        try:
            products = list(container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ))
            produtos = [Produto.from_dict(p) for p in products]
            serializer = ProdutoSerializer(produtos, many=True)
            return Response(serializer.data)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )  

class ProdutoReadUpdateDeleteView(APIView):
    partition_key = "/categoria"
    @swagger_auto_schema(
        operation_description="Retorna um Produto específico",
        manual_parameters=[
            openapi.Parameter(
                'id_produto',
                openapi.IN_PATH,
                description="Product ID",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ProdutoSerializer(many=True),
            404: "Not Found",
            400: "Bad Request"
        }
    )
    def get(self, request, id_produto):
        container = cosmos_db.containers["produtos"]
        try:
            product_data = container.read_item(id_produto, partition_key=self.partition_key)
            produto = Produto.from_dict(product_data)
            serializer = ProdutoSerializer(produto)
            return Response(serializer.data)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Atualiza um produto pelo ID",
        request_body=ProdutoSerializer,
        manual_parameters=[
            openapi.Parameter(
                'id_produto',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: ProdutoSerializer,
            404: "Not Found",
            400: "Bad Request"
        }
    )
    def patch(self, request, id_produto):
        container = cosmos_db.containers["produtos"]
        try:
            existing_item = container.read_item(id_produto, partition_key=self.partition_key)
            serializer = ProdutoSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            updated_data = {**existing_item, **serializer.validated_data}
            updated_item = container.replace_item(id, updated_data)
            return Response(updated_item)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Deleta um produto pelo ID.",
        manual_parameters=[
            openapi.Parameter(
                'id_produto',
                openapi.IN_PATH,
                description="id do produto",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Produto deletado com sucesso",
            404: "Produto não encontrado",
            400: "Erro de validação"
        }
    )
    def delete(self, request, id_produto):
        container = cosmos_db.containers["produtos"]
        try:
            container.delete_item(id_produto, partition_key=self.partition_key)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
"""
class ProdutoView(APIView):
    @swagger_auto_schema(
        request_body=ProdutoSerializer,
        responses={
            201: ProdutoSerializer,
            400: "Bad Request"
        },
        operation_description="Create a new product"
    )
    def post(self, request):
        try:
            produto = Produto.from_dict(request.data)

            created_item = cosmos_db.containers["produtos"].create_item(
                body=produto.to_dict(),
                enable_automatic_id_generation=True  # Will be ignored since we provide id
            )
            
            return Response(created_item, status=201)
        
        except cosmos_exceptions.CosmosHttpResponseError as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id_produto',
                openapi.IN_PATH,
                description="ID do produto",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ProdutoSerializer(),
            404: "Product not found"
        },
        operation_description="Pegar todos os produtos ou um specifico pelo ID"
    )
    def get(self, request, id_produto=None):
        if id_produto:
            produto_data = cosmos_db.find_by_id("produtos", id_produto)
            if not produto_data:
                return Response({"error": "Produto não encontrado"}, status=404)
            produto = ProdutoSerializer.deserialize(produto_data)
            return Response(ProdutoSerializer.serialize(produto), status=200)
        else:
            produtos_data = cosmos_db.find_all("produtos")
            produtos = [ProdutoSerializer.deserialize(p) for p in produtos_data]
            return Response([ProdutoSerializer.serialize(p) for p in produtos], safe=False, status=200)

@swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of the product to update",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'produtocategoriaid',
            openapi.IN_QUERY,
            description="Product category ID (partition key)",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    request_body=ProdutoSerializer,
    responses={
        200: ProdutoSerializer,
        400: "Bad Request or Missing partition key",
        404: "Product not found"
    },
    operation_description="Update a product by ID"
)
def put(self, request, id):
    try:
        container = cosmos_db.containers["produtos"]
        
        # 1. Validate partition key
        partition_key = request.query_params.get('produtocategoriaid')
        if not partition_key:
            return Response(
                {"error": "produtocategoriaid query parameter required as partition key"},
                status=400
            )
        
        # 2. Get existing item
        existing_item = container.read_item(
            item=id,
            partition_key=partition_key
        )
        
        # 3. Validate and process update data
        serializer = ProdutoSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        # 4. Prepare updated data (preserve existing fields not in update)
        updated_data = {
            **existing_item,
            **serializer.validated_data,
            "id": id,  # Ensure ID remains the same
            "produtocategoriaid": partition_key  # Ensure partition key remains the same
        }
        
        # 5. Update item in Cosmos DB
        updated_item = container.replace_item(
            item=id,
            body=updated_data
        )
        
        # 6. Return the updated product
        produto = Produto.from_dict(updated_item)
        return Response(ProdutoSerializer(produto).data, status=200)
        
    except cosmos_exceptions.CosmosResourceNotFoundError:
        return Response({"error": "Product not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id_produto',
                openapi.IN_PATH,
                description="ID of the product to delete",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: "Product deleted successfully",
            404: "Product not found"
        },
        operation_description="Delete a product by ID"
    )
    def delete(self, request, id_produto):
        produto_data = cosmos_db.find_by_id("produtos", id_produto)
        if not produto_data:
            return Response({"error": "Produto não encontrado"}, status=404)
        cosmos_db.delete("produtos", id_produto)
        return Response({"Produto deletado com sucesso!"}, status=204)
    
class PedidoView(APIView):
    @swagger_auto_schema(
        request_body=Pedido,
        responses={
            201: "DEu certo",
            400: "Bad Request"
        },
        operation_description="Create a new order"
    )
    def post(self, request):
        try:
            pedido = Pedido.from_dict(request.data)
            
            created_item = cosmos_db.containers["pedidos"].create_item(
                body=pedido.to_dict(),
                enable_automatic_id_generation=True
            )
            
            return Response(created_item, status=201)
            
        except cosmos_exceptions.CosmosHttpResponseError as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id_pedido',
                openapi.IN_PATH,
                description="ID of the order to retrieve",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'nome_cliente',
                openapi.IN_QUERY,
                description="Client name (required when getting a single order)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: "Deu certo",
            400: "Missing partition key",
            404: "Order not found"
        },
        operation_description="Get all orders or a specific order by ID"
    )
    def get(self, request, id_pedido=None):
        try:
            container = cosmos_db.containers["pedidos"]
            
            if id_pedido:
                
                partition_key = request.query_params.get('nome_cliente')
                if not partition_key:
                    return Response(
                        {"error": "nome_cliente query parameter required as partition key"},
                        status=400
                    )
                
                pedido_data = container.read_item(
                    item=id_pedido,
                    partition_key=partition_key
                )
                pedido = Pedido.from_dict(pedido_data)
                pedidodict = Pedido.to_dict(pedido)
                return Response(pedidodict)
            else:
                # List all products (cross-partition query)
                pedidos = list(container.query_items(
                    query="SELECT * FROM c",
                    enable_cross_partition_query=True
                ))
                pedidos = [Pedido.from_dict(p) for p in pedidos]
                pedidosdict = Pedido.to_dict(pedidos)
                return Response(pedidosdict)
                
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response({"error": "Product not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the order to update",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'nome_cliente',
                openapi.IN_QUERY,
                description="Pedido category ID (partition key)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=Pedido,
        responses={
            200: "Deu Certo",
            400: "Bad Request or Missing partition key",
            404: "Pedido not found"
        },
        operation_description="Update a Pedido by ID"
    )
    def put(self, request, id):
        try:
            container = cosmos_db.containers["pedidos"]
            
            partition_key = request.query_params.get('nome_cliente')
            if not partition_key:
                return Response(
                    {"error": "nome_cliente query parameter required as partition key"},
                    status=400
                )
            
            existing_item = container.read_item(
                item=id,
                partition_key=partition_key
            )

            updated_data = {**existing_item, **request.data}
            
            updated_item = container.replace_item(
                item=id,
                body=updated_data
            )
            
            return Response(updated_item)
            
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response({"error": "Product not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the Pedido to delete",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'nome_cliente',
                openapi.IN_QUERY,
                description="Product category ID (partition key)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: "Pedido deleted successfully",
            400: "Missing partition key",
            404: "Pedido not found"
        },
        operation_description="Delete a pedido by ID"
    )
    def delete(self, request, id):
        try:
            container = cosmos_db.containers["pedidos"]
            
            partition_key = request.query_params.get('nome_cliente')
            if not partition_key:
                return Response(
                    {"error": "nome_cliente query parameter required as partition key"},
                    status=400
                )
            
            container.delete_item(
                item=id,
                partition_key=partition_key
            )
            return Response(status=204)
            
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response({"error": "Pedido not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
"""