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

from data_models.user_profile import UserProfile
from api.extrato_compra_api import ExtratoCompraAPI  # supondo que você tenha essa API

class ExtratoCompraDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ExtratoCompraDialog, self).__init__("ExtratoCompraDialog")

        self.user_state = user_state

        # Prompts
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        # Waterfall
        self.add_dialog(
            WaterfallDialog(
                "extratoCompraWaterfallDialog",
                [
                    self.consultar_extrato_step,
                    self.menu_step,
                ],
            )
        )

        self.initial_dialog_id = "extratoCompraWaterfallDialog"

    async def consultar_extrato_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        # Recupera o UserProfile
        user_profile_accessor = self.user_state.create_property("UserProfile")
        user_profile: UserProfile = await user_profile_accessor.get(
            step_context.context, UserProfile
        )

        if not user_profile.cpf:
            await step_context.context.send_activity("❌ CPF não cadastrado.")
            return await step_context.end_dialog()

        # Chama a API de extrato
        extrato_api = ExtratoCompraAPI()
        extratos = extrato_api.consultar_extrato_por_cpf(user_profile.cpf)

        if not extratos:
            await step_context.context.send_activity("Nenhum extrato encontrado para este CPF.")
        else:
            for extrato in extratos:
                await step_context.context.send_activity(
                    f"🧾 Compra #{extrato['id']}:\n"
                    f"Produto: {extrato['product_name']}\n"
                    f"Valor: R$ {extrato['amount']}\n"
                    f"Data: {extrato['purchase_date']}"
                )

        # Avança para menu
        return await step_context.next(None)

    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        # Oferece opções após a consulta
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("O que deseja fazer agora?"),
                choices=[
                    Choice("Consultar outro Extrato"),
                    Choice("Voltar ao menu principal"),
                ],
            ),
        )

    async def process_option_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result.value

        if option == "Consultar outro Extrato":
            return await step_context.replace_dialog(self.initial_dialog_id)
        elif option == "Voltar ao menu principal":
            await step_context.context.send_activity("↩️ Voltando ao menu principal...")
            return await step_context.replace_dialog("MainDialog")

        # fallback
        await step_context.context.send_activity("Opção não reconhecida.")
        return await step_context.replace_dialog(self.initial_dialog_id)
