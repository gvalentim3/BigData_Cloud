from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (ExtratoRequestSerializer, ExtratoResponseSerializer, UsuarioReadSerializer, UsuarioCreateSerializer, CartaoReadSerializer, 
                             CartaoWriteSerializer, EnderecoReadSerializer, EnderecoWriteSerializer, 
                            ProdutoSerializer, PedidoSerializer)
from .apps import cosmos_db
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Usuario, Endereco, CartaoCredito, Produto
from rest_framework import status
from azure.cosmos import exceptions as cosmos_exceptions
from .services import PedidoService, ProdutoService, TransacaoService, UsuarioService, CartaoService, EnderecoService


class UsuarioCreateListView(APIView):
    @swagger_auto_schema(
        operation_description="Criação um novo usuário. Necessário enviar também pelo menos um cadastro de cartão e um de endereço",
        request_body=UsuarioCreateSerializer,
        responses={
            201: "Usuário criado com sucesso!",
            400: "Erro de validação: Email ou CPF já cadastrados."
        }
    )
    def post(self, request):
        serializer = UsuarioCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario = serializer.save()

        cartoes_data = request.data.get('cartoes', [])
        enderecos_data = request.data.get('enderecos', [])

        UsuarioService.cria_cartoes_enderecos(
            usuario.id,
            cartoes_data,
            enderecos_data
        )

        return Response(
            {"id": usuario.id, "message": "Usuário criado com sucesso"},
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_description="Lista todos os usuários cadastrados.",
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
        request_body=UsuarioCreateSerializer,
        responses={
            200: UsuarioCreateSerializer,
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endereco_serializer = EnderecoWriteSerializer

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
        responses={201: EnderecoReadSerializer, 400: "Erro de validação"},
        operation_description="Cria um novo Endereço vinculado a um usuário.",
    )
    def post(self, request, id_usuario):        
        endereco, errors = EnderecoService.cria_endereco(
            usuario_id=id_usuario, 
            endereco_data=request.data
        )

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST if 'error' not in errors else status.HTTP_404_NOT_FOUND)

        return Response(EnderecoReadSerializer(endereco).data, status=status.HTTP_201_CREATED)
    
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

            enderecos = Endereco.objects.filter(usuario=usuario.id)
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
                endereco = Endereco.objects.get(id=id_endereco, usuario=usuario.id)
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
            endereco = Endereco.objects.get(id=id_endereco, usuario=id_usuario)
        except Endereco.DoesNotExist:
            return Response(
                {"error": "Endereço não encontrado para este usuário."}, status=status.HTTP_404_NOT_FOUND
            )

        endereco.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartaoCreateListView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cartao_serializer = CartaoWriteSerializer

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
        cartao, errors = CartaoService.cria_cartao(
            usuario_id=id_usuario, 
            cartao_data=request.data
        )

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST if 'error' not in errors else status.HTTP_404_NOT_FOUND)

        return Response(CartaoReadSerializer(cartao).data, status=status.HTTP_201_CREATED)
    


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

            cartoes = CartaoCredito.objects.filter(usuario=usuario.id)
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
                cartao = CartaoCredito.objects.get(id=id_cartao, usuario=usuario.id)
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
            cartao = CartaoCredito.objects.get(id=id_cartao, usuario=id_usuario)
        except CartaoCredito.DoesNotExist:
            return Response(
                {"error": "Cartão não encontrado para este usuário."}, status=status.HTTP_404_NOT_FOUND
            )

        cartao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProdutoCreateListView(APIView):
    container = cosmos_db.containers["produtos"]
    
    @swagger_auto_schema(
        operation_description="Cria um novo produto",
        request_body=ProdutoSerializer,
        responses={201: ProdutoSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        serializer = ProdutoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": "Dados inválidos",
                            "details": serializer.errors}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            produto = serializer.create(serializer.validated_data)
            produto_dict = produto.to_dict()

            created_item = self.container.create_item(
                body=produto_dict,
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
        try:
            items = self.container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            )

            serializer = ProdutoSerializer(items, many=True)

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
    container = cosmos_db.containers["produtos"]

    @swagger_auto_schema(
        operation_description="Retorna um Produto específico",
        manual_parameters=[
            openapi.Parameter(
                'id_produto',
                openapi.IN_PATH,
                description="id do produto",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'categoria',  
                openapi.IN_PATH, 
                description="Categoria do produto (string)",
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
    def get(self, request, categoria, id_produto):
        try:
            product_data = self.container.read_item(id_produto, partition_key=categoria)
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
                description="id do produto",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'categoria',  
                openapi.IN_PATH, 
                description="Categoria do produto (string)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ProdutoSerializer,
            404: "Not Found",
            400: "Bad Request"
        }
    )
    def patch(self, request, categoria, id_produto):
        try:
            existing_item = self.container.read_item(id_produto, partition_key=categoria)
            serializer = ProdutoSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            updated_data = {**existing_item, **serializer.validated_data}
            updated_item = self.container.replace_item(id_produto, updated_data)
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
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'categoria',  
                openapi.IN_PATH, 
                description="Categoria do produto (string)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: "Produto deletado com sucesso",
            404: "Produto não encontrado",
            400: "Erro de validação"
        }
    )
    def delete(self, request, categoria, id_produto):
        try:
            self.container.delete_item(id_produto, partition_key=categoria)
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

class ProdutoSearchView(APIView):
    container = cosmos_db.containers["produtos"]

    @swagger_auto_schema(
        operation_description="Retorna um Produto específico",
        manual_parameters=[
            openapi.Parameter(
                'nome',
                openapi.IN_PATH,
                description="Termo de busca para o nome do produto",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ProdutoSerializer(many=True),
            404: "Not Found",
            400: "Bad Request",
            500: "Erro interno do servidor"
        }
    )
    
    def get(self, request, nome):
        try:
            if not nome.strip():
                return Response(
                    {"error": "O termo de busca não pode estar vazio"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            query = "SELECT * FROM c WHERE CONTAINS(LOWER(c.nome), @name)"

            parameters = [
                {"name": "@name", "value": nome.lower()}
            ]

            products = self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            )
            
            serializer = ProdutoSerializer(products, many=True)

            if not serializer.data:
                return Response(
                    {"message": "Nenhum produto encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(serializer.data)
        
        except cosmos_exceptions.CosmosHttpResponseError as e:
            return Response(
                {"error": f"Erro no banco de dados: {str(e)}"},
                status=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class PedidoCreateView(APIView):
    container_pedidos = cosmos_db.containers["pedidos"]
    container_produtos = cosmos_db.containers["produtos"]
    
    @swagger_auto_schema(
        operation_description="Cria um novo produto",
        request_body=PedidoSerializer,
        responses={201: "Pedido #{numero_pedido} criado com sucesso", 400: "Bad Request"}
    )
    def post(self, request):
        """
        {
            usuario = int,
            produtos = [
                {
                    id_produto =
                    preco = 
                    quantidade = 
                }
            ],
            preco_total = 
            id_cartao = 
            id_endereco = 
            data = 
        }
        
        """

        serializer = PedidoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": "Dados inválidos",
                            "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        
        cvv = serializer.cvv  # Acessa o CVV que foi removido
        validated_data = serializer.validated_data  # Dados sem CVV


        try:
            cartao_informado = CartaoCredito.objects.get(id=validated_data['id_cartao'])

            transacao_response = TransacaoService().autoriza_transacao(
                                                cartao=cartao_informado, 
                                                valor=validated_data['preco_total'],
                                                cvv_request=cvv)
            
            if transacao_response.status_code == status.HTTP_400_BAD_REQUEST:
                return transacao_response
            
            produto_service = ProdutoService(container=self.container_produtos)

            for produto in validated_data['produtos']:
                produto_service.retira_quantidade_produto(
                    id_produto=produto['id_produto'],
                    quantidade=produto['quantidade'],
                    categoria=produto['categoria_produto']
                )

            numero_pedido = PedidoService(self.container_pedidos).set_numero_pedido()

            dados_pedido = {**serializer.validated_data, 'numero': numero_pedido}

            self.container_pedidos.create_item(
                body=dados_pedido,
                enable_automatic_id_generation=True
            )

            return Response(
                {"success": f"Pedido #{numero_pedido} criado com sucesso"},
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {"error": "Erro ao processar pedido", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class PedidoSearchView(APIView):
    container_pedidos = cosmos_db.containers["pedidos"]
    def get(self, request, numero):
        try:
            if not numero.strip():
                return Response(
                    {"error": "O termo de busca não pode estar vazio"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            query = "SELECT TOP 1 * FROM c WHERE c.numero = @numero"

            parameters = [
                {"name": "@numero", "value": int(numero.strip())}
            ]

            pedido = next(
                self.container_pedidos.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ),
                None
            )
            
            if not pedido:
                return Response(
                    {"message": "Nenhum pedido encontrado com o numero fornecido."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = PedidoSerializer(pedido)
            return Response(serializer.data)
        
        except cosmos_exceptions.CosmosHttpResponseError as e:
            return Response(
                {"error": f"Erro no banco de dados: {str(e)}"},
                status=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ExtratoCartaoView(APIView):
    container_pedidos = cosmos_db.containers["pedidos"]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('usuario', openapi.IN_PATH, type=openapi.TYPE_INTEGER),
            openapi.Parameter('cartao', openapi.IN_PATH, type=openapi.TYPE_INTEGER),
            openapi.Parameter('ano_mes', openapi.IN_PATH, type=openapi.TYPE_STRING)
        ],
        responses={
            200: ExtratoResponseSerializer(many=True),
            400: "Dados inválidos",
            404: "Usuário/Cartão não encontrado"
        }
    )
    def get(self, request, usuario, cartao, ano_mes):
        try:
            ano, mes = map(int, ano_mes.split('-'))
        except ValueError:
            return Response(
                {"error": "Formato de ano_mes inválido. Use YYYY-MM."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'usuario': usuario,
            'cartao': cartao,
            'ano': ano,
            'mes': mes
        }

        serializer = ExtratoRequestSerializer(data=data)

        if not serializer.is_valid():
            return Response({"errors": "Dados inválidos",
                            "details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data

        query = "SELECT * FROM c WHERE c.id_cartao = @cartao AND STARTSWITH(c.data, @ano_mes)"

        parameters = [
            {"name": "@cartao", "value": validated_data['cartao']},
            {"name": "@ano_mes", "value": validated_data['ano_mes']}
        ]

        pedidos = list(self.container_pedidos.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        if not pedidos:
            return Response({
                "message": "Nenhum pedido encontrado para o cartão no período especificado",
                "cartao": validated_data['cartao'],
                "ano_mes": validated_data['ano_mes']
            }, status=status.HTTP_404_NOT_FOUND)
        
        pedidos_serializados = ExtratoResponseSerializer(pedidos, many=True).data

        response_data = {
            "cartao": validated_data['cartao'],
            "ano_mes": validated_data['ano_mes'],
            "quantidade_pedidos": len(pedidos),
            "pedidos": pedidos_serializados
        }

        return Response(response_data, status=status.HTTP_200_OK)