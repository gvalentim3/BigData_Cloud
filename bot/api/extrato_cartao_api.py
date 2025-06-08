import requests
from config import DefaultConfig

class ExtratoCartaoAPI:
    def __init__(self):
        self.config = DefaultConfig()
        self.base_url = f"{self.config.URL_PREFIX}/api/extrato"

    def get_extrato(self, usuario_id, cartao_id, ano_mes):
        """
        Consulta o extrato do cartão.

        Args:
            usuario_id (int): ID do usuário.
            cartao_id (int): ID do cartão.
            ano_mes (str): Período no formato YYYY-MM.

        Returns:
            dict: Resposta da API de extrato (ou erro).
        """
        url = f"{self.base_url}/{usuario_id}/{cartao_id}/{ano_mes}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[GET_EXTRATO] API Error: {e}")
            return {"error": str(e)}
