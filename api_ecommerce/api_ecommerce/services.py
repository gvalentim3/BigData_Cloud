from api_ecommerce.repositories import ProdutoRepository, PedidoRepository
from api_ecommerce.settings import MONGO_DB

class ProdutoService:
    @staticmethod
    def listar_produtos():
        return ProdutoRepository.listar_produtos()

    @staticmethod
    def buscar_produto(produto_id):
        return ProdutoRepository.buscar_por_id(produto_id)

class PedidoService:
    @staticmethod
    def criar_pedido():
        pedido = PedidoRepository.criar_pedido()
        MONGO_DB.logs.insert_one({"mensagem": f"Pedido {pedido.id} criado!"})
        return pedido