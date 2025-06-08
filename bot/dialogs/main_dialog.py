from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    TextPrompt,
)
from botbuilder.dialogs.prompts import (
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from dialogs.consultar_produtos_dialog import ConsultarProdutosDialog
from dialogs.consultar_pedido_dialog import ConsultarPedidoDialog
from dialogs.extrato_cartao_dialog import ExtratoCartaoDialog
from dialogs.comprar_produto_dialog import ComprarProdutoDialog
from data_models.user_profile import UserProfile
from api.user_api import UserAPI

class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__("MainDialog")

        self.user_state = user_state

        # Diálogos filhos
        self.add_dialog(ConsultarProdutosDialog(user_state))
        self.add_dialog(ConsultarPedidoDialog(user_state))
        self.add_dialog(ExtratoCartaoDialog(user_state))
        self.add_dialog(ComprarProdutoDialog(user_state))

        # Prompts
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt("CpfPrompt", self.validate_cpf))

        # Waterfall
        self.add_dialog(
            WaterfallDialog(
                "mainWaterfallDialog",
                [
                    self.get_cpf_step,
                    self.prompt_option_step,
                    self.process_option_step,
                ],
            )
        )

        self.initial_dialog_id = "mainWaterfallDialog"

    async def get_cpf_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_profile_accessor = self.user_state.create_property("UserProfile")
        user_profile = await user_profile_accessor.get(step_context.context, UserProfile)

        if user_profile.cpf:
            # Já tem CPF
            return await step_context.next(user_profile.cpf)

        # Não tem CPF, pedir
        return await step_context.prompt(
            "CpfPrompt",
            PromptOptions(
                prompt=MessageFactory.text("🪪 Bem-vindo! Por favor, digite seu CPF (11 dígitos):"),
                retry_prompt=MessageFactory.text("❌ CPF inválido. Digite novamente."),
            )
        )

    async def validate_cpf(self, prompt_context):
        cpf = prompt_context.recognized.value
        return cpf.isdigit() and len(set(cpf)) > 1

    async def prompt_option_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        # Se veio CPF da etapa anterior, validar no banco
        if step_context.result is not None and isinstance(step_context.result, str) and step_context.result.isdigit():
            cpf_informado = step_context.result

            user_api = UserAPI()
            usuario = user_api.get_usuario_by_cpf(cpf_informado)

            if usuario is None:
                # CPF não cadastrado → mostra mensagem e reinicia MainDialog
                await step_context.context.send_activity("❌ CPF não cadastrado. Por favor, tente novamente.")
                return await step_context.replace_dialog(self.initial_dialog_id)

            # CPF válido → salva no UserProfile
            user_profile_accessor = self.user_state.create_property("UserProfile")
            user_profile = await user_profile_accessor.get(step_context.context, UserProfile)
            user_profile.cpf = cpf_informado
            await user_profile_accessor.set(step_context.context, user_profile)
            await self.user_state.save_changes(step_context.context)

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
                await step_context.context.send_activity("🏠 Voltando ao menu principal...")

        # Menu principal
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Escolha a opção desejada:"),
                choices=[
                    Choice("Consultar Produtos"),
                    Choice("Consultar Pedidos"),
                    Choice("Extrato do Cartão"),
                ],
            ),
        )

    async def process_option_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        option = ""

        # Se step_context.result is None → diálogo anterior finalizado → volta pro menu sem erro
        if step_context.result is None:
            return await step_context.replace_dialog(self.initial_dialog_id)

        if hasattr(step_context.result, "value"):
            option = step_context.result.value.lower()
        elif isinstance(step_context.result, str):
            option = step_context.result.lower()
        else:
            await step_context.context.send_activity("Opção inválida. Retornando ao menu principal.")
            return await step_context.replace_dialog(self.initial_dialog_id)

        if option == "consultar produtos":
            return await step_context.begin_dialog("ConsultarProdutosDialog")
        elif option == "consultar pedidos":
            return await step_context.begin_dialog("ConsultarPedidoDialog")
        elif option == "extrato do cartão":
            return await step_context.begin_dialog("ExtratoCartaoDialog")

        await step_context.context.send_activity("Opção não reconhecida. Retornando ao menu principal.")
        return await step_context.replace_dialog(self.initial_dialog_id)
