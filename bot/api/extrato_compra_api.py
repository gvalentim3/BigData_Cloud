import requests
from config import DefaultConfig

class ExtratoCompraAPI:
    def __init__(self):
        self.config = DefaultConfig()
        self.base_url = f"{self.config.URL_PREFIX}/api/extrato"

    def consultar_extrato_por_cpf(self, cpf: str):
        try:
            response = requests.get(f"{self.base_url}", params={"cpf": cpf})
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao consultar extrato: status {response.status_code}")
                return []
        except Exception as e:
            print(f"Erro ao consultar extrato: {e}")
            return []
