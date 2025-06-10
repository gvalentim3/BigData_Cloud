import requests
from config import DefaultConfig

class PedidoAPI:
    def __init__(self):
        self.config = DefaultConfig()
        self.base_url = f"{self.config.URL_PREFIX}/api/pedidos/"

    def post_pedidos(self, pedido_data):
        """
        Cria um novo pedido com a estrutura especificada
        Args:
            pedido_data: {
                "usuario": int,
                "produtos": [
                    {
                        "id_produto": str,
                        "categoria_produto": str,
                        "quantidade": int
                    }
                ],
                "id_cartao": int,
                "cvv": str,
                "id_endereco": int
            }
        Returns:
            dict: Resposta da API ou mensagem de erro
        """
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.base_url,
                json=pedido_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"[POST_PEDIDOS] HTTP Error: {http_err}")
            return {"mensagem": f"{response.json().get('mensagem', http_err)}"}
        except Exception as e:
            print(f"[POST_PEDIDOS] API Error: {e}")
            return {"error": "Falha ao criar pedido"}

    def search_pedido(self, pedido_id):
        """
        Busca um pedido específico pelo ID
        Args:
            pedido_id: ID do pedido a ser buscado
        Returns:
            dict: Estrutura do pedido no formato:
                {
                    "id": str,
                    "usuario": int,
                    "produtos": [
                        {
                            "id_produto": str,
                            "categoria_produto": str,
                            "quantidade": int,
                            "preco_unitario": float,
                            "nome_produto": str
                        }
                    ],
                    "data_pedido": str,
                    "status": str,
                    "valor_total": float
                }
        """
        try:
            url = f"{self.base_url}{pedido_id}"
            response = requests.get(url)
            response.raise_for_status()
            
            # Padroniza a resposta para incluir todos campos esperados
            pedido_data = response.json()
                
            return pedido_data
            
        except requests.exceptions.HTTPError as http_err:
            print(f"[SEARCH_PEDIDO] HTTP Error: {http_err}")
            return {"error": f"Pedido não encontrado: {http_err}"}
        except Exception as e:
            print(f"[SEARCH_PEDIDO] API Error: {e}")
            return {"error": "Falha ao buscar pedido"}