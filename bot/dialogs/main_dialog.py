from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from dialogs.consultar_produtos_dialog import ConsultarProdutosDialog
from dialogs.consultar_pedido_dialog import ConsultarPedidoDialog
from dialogs.extrato_compra_dialog import ExtratoCompraDialog
from dialogs.comprar_produto_dialog import ComprarProdutoDialog


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__("MainDialog")

        self.user_state = user_state

        # Diálogos filhos
        self.add_dialog(ConsultarProdutosDialog(user_state))
        self.add_dialog(ConsultarPedidoDialog(user_state))
        self.add_dialog(ExtratoCompraDialog(user_state))
        self.add_dialog(ComprarProdutoDialog(user_state))

        # Prompts
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        # Waterfall
        self.add_dialog(
            WaterfallDialog(
                "mainWaterfallDialog",
                [
                    self.prompt_option_step,
                    self.process_option_step,
                ],
            )
        )

        self.initial_dialog_id = "mainWaterfallDialog"

    async def prompt_option_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        # Se o diálogo foi iniciado com dados da compra, redireciona diretamente
        if isinstance(step_context.options, dict):
            acao = step_context.options.get("acao")
            if acao == "comprar":
                return await step_context.begin_dialog(
                    "ComprarProdutoDialog",
                    {
                        "productId": step_context.options["productId"],
                        "productName": step_context.options["productName"],
                    },
                )
            elif acao == "voltar_menu":
                # Apenas cai no menu sem fazer nada
                await step_context.context.send_activity("🏠 Voltando ao menu principal...")

        # Caso contrário, mostra o menu principal
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Escolha a opção desejada:"),
                choices=[
                    Choice("Consultar Produtos"),
                    Choice("Consultar Pedidos"),
                    Choice("Extrato de Compras"),
                ],
            ),
        )

    async def process_option_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        option = ""

        # Proteção contra None
        if step_context.result is not None:
            if hasattr(step_context.result, "value"):
                option = step_context.result.value.lower()
            elif isinstance(step_context.result, str):
                option = step_context.result.lower()
        else:
            await step_context.context.send_activity("Opção inválida. Retornando ao menu principal.")
            return await step_context.replace_dialog(self.initial_dialog_id)

        # Navegação
        if option == "consultar produtos":
            return await step_context.begin_dialog("ConsultarProdutosDialog")
        elif option == "consultar pedidos":
            return await step_context.begin_dialog("ConsultarPedidoDialog")
        elif option == "extrato de compras":
            return await step_context.begin_dialog("ExtratoCompraDialog")

        # fallback — não deveria acontecer
        await step_context.context.send_activity("Opção não reconhecida. Retornando ao menu principal.")
        return await step_context.replace_dialog(self.initial_dialog_id)
