class PedidoModel:
    def __init__(self, usuario_id, produtos, id_cartao, cvv, id_endereco):
        """
        Args:
            usuario_id (int): ID do usuário
            produtos (list): lista de dicts com:
                - id_produto (str)
                - categoria_produto (str)
                - quantidade (int)
            id_cartao (int): ID do cartão
            cvv (str): CVV do cartão
            id_endereco (int): ID do endereço
        """
        self.usuario = usuario_id
        self.produtos = produtos
        self.id_cartao = id_cartao
        self.cvv = cvv
        self.id_endereco = id_endereco

    def to_dict(self):
        return {
            "usuario": self.usuario,
            "produtos": self.produtos,
            "id_cartao": self.id_cartao,
            "cvv": self.cvv,
            "id_endereco": self.id_endereco
        }
