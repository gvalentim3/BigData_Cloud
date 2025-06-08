from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.core import UserState
from botbuilder.schema import HeroCard, CardAction, ActionTypes
from botbuilder.core import CardFactory
from api.pedido_api import PedidoAPI

class ConsultarPedidoDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ConsultarPedidoDialog, self).__init__("ConsultarPedidoDialog")

        self.user_state = user_state

        self.add_dialog(TextPrompt(TextPrompt.__name__, self.pedido_id_validator))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

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
    
    def criar_card_pedido(self, pedido):
        produtos_text = "\n".join(
            f"- {p['nome_produto']} (Qtd: {p['quantidade']}, Preço unit.: R$ {p['preco_unitario']:.2f})"
            for p in pedido.get("produtos", [])
        )

        card = CardFactory.hero_card(
            HeroCard(
                title=f"Pedido #{pedido['id']}",
                subtitle=f"Status: {pedido.get('status', 'Desconhecido')} | Data: {pedido.get('data_pedido', 'Desconhecida')}",
                text=f"🧾 Valor Total: R$ {pedido.get('valor_total', 0.0):.2f}\n\n📦 Produtos:\n{produtos_text}"
            )
        )
        return MessageFactory.attachment(card)

    async def consultar_pedido_step(self, step_context: WaterfallStepContext):
        pedido_id = step_context.result

        pedido_api = PedidoAPI()
        response = pedido_api.search_pedido(pedido_id)

        if "error" in response:
            await step_context.context.send_activity(f"⚠️ {response['error']}")
        else:
            await step_context.context.send_activity(self.criar_card_pedido(response))

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("📋 O que você gostaria de fazer agora?"),
                choices=[
                    Choice("Consultar outro pedido"),
                    Choice("Voltar ao menu principal"),
                ],
            ),
        )

    async def next_action_step(self, step_context: WaterfallStepContext):
        option = step_context.result.value

        if option == "Consultar outro pedido":
            await step_context.context.send_activity("🔄 Ok! Vamos consultar outro pedido.")
            return await step_context.replace_dialog(self.initial_dialog_id)

        elif option == "Voltar ao menu principal":
            await step_context.context.send_activity("🏠 Voltando ao menu principal...")
            return await step_context.replace_dialog("MainDialog")

        # Fallback para entrada inesperada
        await step_context.context.send_activity("🤔 Não entendi sua escolha. Voltando ao menu principal.")
        return await step_context.replace_dialog("MainDialog")


