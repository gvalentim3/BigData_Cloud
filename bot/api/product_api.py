import requests
from config import DefaultConfig

class ProductAPI:
    def __init__(self):
        self.config = DefaultConfig()
        self.base_url = f"{self.config.URL_PREFIX}/api/produtos"

    def get_products(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[GET_PRODUCTS] API Error: {e}")
            return {"error": "Falha na conexão ou status inválido"}

    def search_product(self, product_name):
        try:
            url = f"{self.base_url}/busca/{product_name}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[SEARCH_PRODUCT] API Error: {e}")
            return {"error": "Falha na conexão ou status inválido"}
