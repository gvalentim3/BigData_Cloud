from api.models import Produto, Pedido, ItemPedido

class ProdutoRepository:
    @staticmethod
    def listar_produtos():
        return Produto.objects.all()

    @staticmethod
    def buscar_por_id(produto_id):
        return Produto.objects.filter(id=produto_id).first()

class PedidoRepository:
    @staticmethod
    def criar_pedido():
        return Pedido.objects.create()