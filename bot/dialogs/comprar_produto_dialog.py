from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from api.pedido_api import PedidoAPI
from data_models.pedido_model import PedidoModel
import re

class ComprarProdutoDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super().__init__("ComprarProdutoDialog")
        self.user_state = user_state

        # Prompts com validações específicas
        self.add_dialog(TextPrompt("cpfPrompt", self.validate_cpf))
        self.add_dialog(TextPrompt("numeroCartaoPrompt", self.validate_card_number))
        self.add_dialog(TextPrompt("expiracaoPrompt", self.validate_expiration_date))
        self.add_dialog(TextPrompt("cvvPrompt", self.validate_cvv))

        self.add_dialog(
            WaterfallDialog(
                "comprarProdutoWaterfall",
                [
                    self.cpf_step,
                    self.cartao_step,
                    self.expiracao_step,
                    self.cvv_step,
                    self.confirmar_pedido_step,
                ]
            )
        )

        self.initial_dialog_id = "comprarProdutoWaterfall"

    # ---------- Validações ----------
    async def validate_cpf(self, prompt_context):
        cpf = prompt_context.recognized.value
        if not (cpf and cpf.isdigit() and len(cpf) == 11 and len(set(cpf)) > 1):
            await prompt_context.context.send_activity("❌ CPF inválido. Digite 11 dígitos numéricos válidos.")
            return False
        return True

    async def validate_card_number(self, prompt_context):
        card = prompt_context.recognized.value
        return card.isdigit() and len(card) in (15, 16)

    async def validate_expiration_date(self, prompt_context):
        date = prompt_context.recognized.value
        match = re.match(r"^(0[1-9]|1[0-2])/(\d{2})$", date)
        if not match:
            await prompt_context.context.send_activity("❌ Data inválida. Use o formato MM/AA.")
            return False
        return True

    async def validate_cvv(self, prompt_context):
        cvv = prompt_context.recognized.value
        return cvv.isdigit() and len(cvv) in (3, 4)

    # ---------- Etapas do Diálogo ----------
    async def cpf_step(self, step_context: WaterfallStepContext):
        product_id = step_context.options.get("productId")
        product_name = step_context.options.get("productName")

        step_context.values["productId"] = product_id
        step_context.values["productName"] = product_name

        return await step_context.prompt(
            "cpfPrompt",
            PromptOptions(
                prompt=MessageFactory.text("🪪 Digite seu CPF (apenas números):"),
                retry_prompt=MessageFactory.text("❌ CPF inválido. Por favor, insira novamente.")
            )
        )

    async def cartao_step(self, step_context: WaterfallStepContext):
        step_context.values["cpf"] = step_context.result
        return await step_context.prompt(
            "numeroCartaoPrompt",
            PromptOptions(
                prompt=MessageFactory.text("💳 Digite o número do cartão de crédito (15 ou 16 dígitos):"),
                retry_prompt=MessageFactory.text("❌ Número do cartão inválido.")
            )
        )

    async def expiracao_step(self, step_context: WaterfallStepContext):
        step_context.values["numero_cartao"] = step_context.result
        return await step_context.prompt(
            "expiracaoPrompt",
            PromptOptions(
                prompt=MessageFactory.text("📆 Digite a data de expiração do cartão (formato MM/AA):"),
                retry_prompt=MessageFactory.text("❌ Data inválida. Use MM/AA.")
            )
        )

    async def cvv_step(self, step_context: WaterfallStepContext):
        step_context.values["data_expiracao"] = step_context.result
        return await step_context.prompt(
            "cvvPrompt",
            PromptOptions(
                prompt=MessageFactory.text("🔐 Digite o CVV (3 ou 4 dígitos):"),
                retry_prompt=MessageFactory.text("❌ CVV inválido.")
            )
        )

    async def confirmar_pedido_step(self, step_context: WaterfallStepContext):
        step_context.values["cvv"] = step_context.result

        # Monta dados para pedido
        pedido_api = PedidoAPI()
        pedido_data = {
            "usuario": 1,  # ID do usuário fictício (substituir conforme necessário)
            "produtos": [{
                "id_produto": step_context.values["productId"],
                "categoria_produto": "geral",  # você pode ajustar isso
                "quantidade": 1
            }],
            "id_cartao": 123,  # simulado
            "cvv": step_context.values["cvv"],
            "id_endereco": 456  # simulado
        }

        response = pedido_api.post_pedidos(pedido_data)

        if "error" in response:
            await step_context.context.send_activity(f"❌ Erro ao criar pedido: {response['error']}")
        else:
            pedido_id = response.get("id", "desconhecido")
            await step_context.context.send_activity(
                f"✅ Pedido criado com sucesso!\n\n"
                f"📦 Produto: {step_context.values['productName']}\n"
                f"📝 Número do pedido: {pedido_id}\n"
                f"💳 Cartão final: {step_context.values['numero_cartao'][-4:]}"
            )

        return await step_context.end_dialog()
