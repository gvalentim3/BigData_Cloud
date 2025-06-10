from django.utils import timezone
import uuid
from rest_framework import status
from rest_framework.response import Response
from .models import Usuario, CartaoCredito, Endereco
from .serializers import CartaoWriteSerializer, EnderecoWriteSerializer, ProdutoSerializer
from azure.cosmos import exceptions as cosmos_exceptions

class CartaoService():
    def cria_cartao(usuario_id, cartao_data):
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return None, {"error": "Usuário não encontrado"}

        serializer = CartaoWriteSerializer(data={**cartao_data})

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
        
        serializer = EnderecoWriteSerializer(data={**endereco_data})

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

    def busca_por_cpf(cpf):
        try:
            usuario = Usuario.objects.get(cpf=cpf)
            return usuario, None
        except Usuario.DoesNotExist:
            return None, {"error": "Usuário não encontrado"}

class ProdutoService():
    def __init__(self, container):
        self.container = container

    def retira_quantidade_produto(self, id_produto, quantidade, categoria):
        try:
            current_item = self.container.read_item(id_produto, partition_key=categoria)

            if quantidade > current_item['quantidade']: 
                return Response(
                    {"error": "Quantidade indisponível"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            current_item['quantidade'] -= quantidade

            self.container.replace_item(
                item=current_item['id'],
                body=current_item
            )

        except cosmos_exceptions.CosmosResourceNotFoundError:
            return Response(
                {"error": "Produto não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )



class PedidoService():
    def __init__ (self, container):
        self.container = container

    def set_numero_pedido(self):
        query = "SELECT TOP 1 VALUE c.numero " \
        "FROM c " \
        "ORDER BY c.numero DESC"
        
        items = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        return items[0] + 1 if items else 1000
    
    def busca_cartao_pelo_numero(numero_cartao, usuario):
        cartao = CartaoCredito.objects.filter(
            usuario_id=usuario,
            numero=numero_cartao,
        ).first()
        
        return cartao 

class TransacaoService:
    def autoriza_transacao(self, cartao: CartaoCredito, valor, cvv_request):
        if not cartao.cvv == cvv_request:
            return self.error_response("CVV informado incorreto")
        
        if cartao.dt_expiracao < timezone.now().date():
            return self.error_response("Cartão expirado")
            
        if cartao.saldo < valor:
            return self.error_response("Saldo insuficiente")
        
        cartao.saldo -= valor
        cartao.save()

        return self.success_response()

    def error_response(self, message):
        response_data = {
            "status": "NOT_AUTHORIZED",
            "codigo_autorizacao": uuid.uuid4(),
            "dt_transacao": timezone.now(),
            "mensagem": message
        }

        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def success_response(self):
        response_data = {
            "status": "AUTHORIZED",
            "codigo_autorizacao": uuid.uuid4(),
            "dt_transacao": timezone.now(),
            "mensagem": "Compra autorizada com sucesso"
        }

        return Response(response_data, status=status.HTTP_202_ACCEPTED)