from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import UserState
from botbuilder.schema import HeroCard, CardAction, ActionTypes
from botbuilder.core import CardFactory
from api.pedido_api import PedidoAPI

class ConsultarPedidoDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ConsultarPedidoDialog, self).__init__("ConsultarPedidoDialog")

        self.user_state = user_state

        self.add_dialog(TextPrompt(TextPrompt.__name__, self.pedido_id_validator))
        self.add_dialog(TextPrompt("ChoicePromptText"))  # substitui o ChoicePrompt pelo TextPrompt

        self.add_dialog(
            WaterfallDialog(
                "consultarPedidoWaterfallDialog",
                [
                    self.prompt_pedido_id_step,
                    self.consultar_pedido_step,
                    self.next_action_step,
                ],
            )
        )

        self.initial_dialog_id = "consultarPedidoWaterfallDialog"

    async def pedido_id_validator(self, prompt_context):
        # Garante que seja um número positivo
        return prompt_context.recognized.succeeded and prompt_context.recognized.value.isdigit()

    async def prompt_pedido_id_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("📦 Por favor, digite o número do pedido que deseja consultar:"),
                retry_prompt=MessageFactory.text("❌ Número inválido. Digite apenas números, por favor."),
            )
        )
    
    def criar_card_pedido(self, pedido: dict):
        produtos_text = "\n".join(
            f"- {p['nome_produto']} (Qtd: {p['quantidade']}, Preço unit.: R$ {float(p['preco_produto']):.2f})"
            for p in pedido.get("produtos", [])
        )
        total = float(pedido.get('preco_total', '0.0'))
        
        card = CardFactory.hero_card(
            HeroCard(
                title=f"Pedido #{pedido['numero']}",
                subtitle=f"Data: {pedido.get('data', 'Desconhecida')}",
                text=f"🧾 Valor Total: R$ {total:.2f}\n\n📦 Produtos:\n{produtos_text}"
            )
        )
        return MessageFactory.attachment(card)

    async def consultar_pedido_step(self, step_context: WaterfallStepContext):
        pedido_id = step_context.result

        pedido_api = PedidoAPI()
        response = pedido_api.search_pedido(pedido_id)
        print(response)

        if "error" in response:
            await step_context.context.send_activity(f"⚠️ Pedido #{pedido_id} não encontrado.")
        else:
            await step_context.context.send_activity(self.criar_card_pedido(response))

        # Substituindo o ChoicePrompt por HeroCard com botões
        card = HeroCard(
            title="📋 O que você gostaria de fazer agora?",
            buttons=[
                CardAction(type=ActionTypes.post_back, title="Consultar outro pedido", value="consultar_outro"),
                CardAction(type=ActionTypes.post_back, title="Voltar ao menu principal", value="voltar_menu"),
            ],
        )
        await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))

        return await step_context.prompt(
            "ChoicePromptText",
            PromptOptions(
                prompt=MessageFactory.text("Clique em uma opção acima ou digite sua escolha:"),
                retry_prompt=MessageFactory.text("❌ Opção inválida. Digite 'consultar_outro' ou 'voltar_menu'."),
            ),
        )

    async def next_action_step(self, step_context: WaterfallStepContext):
        option = step_context.result.lower()

        if option == "consultar_outro":
            await step_context.context.send_activity("🔄 Ok! Vamos consultar outro pedido.")
            return await step_context.replace_dialog(self.initial_dialog_id)

        elif option == "voltar_menu":
            await step_context.context.send_activity("🏠 Voltando ao menu principal...")
            return await step_context.replace_dialog("MainDialog")

        # Fallback para entrada inesperada
        await step_context.context.send_activity("🤔 Não entendi sua escolha. Voltando ao menu principal.")
        return await step_context.replace_dialog("MainDialog")
