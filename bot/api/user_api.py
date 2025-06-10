import requests
from config import DefaultConfig

class UserAPI:
    def __init__(self):
        self.config = DefaultConfig()
        self.base_url = f"{self.config.URL_PREFIX}/api/usuarios"

    def get_usuario_by_cpf(self, cpf):
        try:
            url = f"{self.base_url}/{cpf}"  # Supondo que este seja o endpoint correto
            response = requests.get(url)
            response.raise_for_status()
            usuario_data = response.json()

            # Opcional: log para debug
            print(f"[GET_USUARIO_BY_CPF] Sucesso: {usuario_data}")

            return usuario_data
        except requests.exceptions.RequestException as e:
            print(f"[GET_USUARIO_BY_CPF] API Error: {e}")
            return None

    def get_cartoes_by_cpf(self, cpf):
        usuario = self.get_usuario_by_cpf(cpf)
        if usuario and "cartoes" in usuario:
            return [
                {
                    "id": cartao["id"],
                    "numero": cartao["numero"],
                    "dt_expiracao": cartao["dt_expiracao"],
                    "saldo": cartao["saldo"],
                }
                for cartao in usuario["cartoes"]
            ]
        else:
            print(f"[GET_CARTOES_BY_CPF] Nenhum cartão encontrado para CPF: {cpf}")
            return []

    def get_enderecos_by_cpf(self, cpf):
        usuario = self.get_usuario_by_cpf(cpf)
        if usuario and "enderecos" in usuario:
            return [
                {
                    "id": endereco["id"],
                    "descricao": f"{endereco['logradouro']}, {endereco['bairro']}, {endereco['cidade']} - {endereco['estado']} ({endereco['cep']})"
                }
                for endereco in usuario["enderecos"]
            ]
        else:
            print(f"[GET_ENDERECOS_BY_CPF] Nenhum endereço encontrado para CPF: {cpf}")
            return []
