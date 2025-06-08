from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import HeroCard, CardAction, ActionTypes
from botbuilder.core import CardFactory
from data_models.user_profile import UserProfile
from api.user_api import UserAPI
from api.extrato_cartao_api import ExtratoCartaoAPI
import re

class ExtratoCartaoDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super().__init__("ExtratoCartaoDialog")
        self.user_state = user_state

        self.add_dialog(TextPrompt("CartaoIdPrompt"))
        self.add_dialog(TextPrompt("AnoMesPrompt", self.validate_ano_mes))
        self.add_dialog(TextPrompt("ChoiceExtrato"))

        self.add_dialog(
            WaterfallDialog(
                "extratoCartaoWaterfall",
                [
                    self.get_usuario_id_step,
                    self.escolher_cartao_step,
                    self.consultar_extrato_step,
                    self.next_action_step,
                ]
            )
        )

        self.initial_dialog_id = "extratoCartaoWaterfall"

    async def validate_ano_mes(self, prompt_context):
        ano_mes = prompt_context.recognized.value
        return bool(re.match(r"^\d{2}-\d{4}$", ano_mes))

    async def get_usuario_id_step(self, step_context: WaterfallStepContext):
        user_profile_accessor = self.user_state.create_property("UserProfile")
        user_profile = await user_profile_accessor.get(step_context.context, UserProfile)

        if not user_profile.cpf:
            await step_context.context.send_activity("❌ CPF não encontrado. Volte ao menu principal.")
            return await step_context.end_dialog()

        user_api = UserAPI()
        usuario_info = user_api.get_usuario_by_cpf(user_profile.cpf)

        if usuario_info is None:
            await step_context.context.send_activity("❌ Não foi possível localizar o usuário. CPF inválido.")
            return await step_context.end_dialog()

        step_context.values["usuario_id"] = usuario_info["id"]

        cartoes = user_api.get_cartoes_by_cpf(user_profile.cpf)

        if not cartoes:
            await step_context.context.send_activity("❌ Nenhum cartão encontrado para este usuário.")
            return await step_context.end_dialog()

        buttons = [
            CardAction(
                type=ActionTypes.post_back,
                title=f"Cartão: {cartao['numero']}",
                value=str(cartao["id"]),
            ) for cartao in cartoes
        ]

        card = HeroCard(
            title="💳 Selecione um cartão para consultar o extrato:",
            buttons=buttons
        )

        await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))

        return await step_context.prompt(
            "CartaoIdPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Clique no cartão selecionado:"),
                retry_prompt=MessageFactory.text("❌ ID inválido."),
            )
        )

    async def escolher_cartao_step(self, step_context: WaterfallStepContext):
        step_context.values["id_cartao"] = int(step_context.result)

        return await step_context.prompt(
            "AnoMesPrompt",
            PromptOptions(
                prompt=MessageFactory.text("📅 Digite o período no formato MM-AAAA para consultar o extrato:"),
                retry_prompt=MessageFactory.text("❌ Formato inválido. Use MM-AAAA (ex: 06-2025)."),
            )
        )

    async def consultar_extrato_step(self, step_context: WaterfallStepContext):
        usuario_id = step_context.values["usuario_id"]
        id_cartao = step_context.values["id_cartao"]

        mm_aaaa = step_context.result
        mes, ano = mm_aaaa.split('-')
        ano_mes_api = f"{ano}-{mes}"

        extrato_api = ExtratoCartaoAPI()
        data = extrato_api.get_extrato(usuario_id, id_cartao, ano_mes_api)

        if "error" in data or not data.get("pedidos"):
            await step_context.context.send_activity("❌ Nenhum pedido encontrado nesse mês.")
            return await self.mostrar_opcoes(step_context)

        pedidos = data.get("pedidos", [])
        quantidade_pedidos = data.get("quantidade_pedidos", 0)

        if quantidade_pedidos == 0 or not pedidos:
            await step_context.context.send_activity(
                f"❌ Nenhum pedido encontrado para o cartão {id_cartao} no período {mm_aaaa}."
            )
            return await self.mostrar_opcoes(step_context)

        await step_context.context.send_activity(
            f"📄 Foram encontrados {quantidade_pedidos} pedidos para o cartão {id_cartao} no período {mm_aaaa}.\n"
        )

        for pedido in pedidos:
            produtos_info = ""
            for produto in pedido.get("produtos", []):
                produtos_info += f"- {produto.get('nome_produto', 'Produto')} (Qtd: {produto.get('quantidade', '?')})\n"

            await step_context.context.send_activity(
                f"📅 Data: {pedido.get('data')}\n"
                f"📝 Número do pedido: {pedido.get('numero')}\n"
                f"💵 Valor total: R$ {pedido.get('preco_total')}\n"
                f"📦 Produtos:\n{produtos_info}"
            )

        return await self.mostrar_opcoes(step_context)

    async def mostrar_opcoes(self, step_context):
        card = HeroCard(
            title="📋 O que você deseja fazer agora?",
            buttons=[
                CardAction(type=ActionTypes.post_back, title="Consultar outro mês", value="consultar_outro"),
                CardAction(type=ActionTypes.post_back, title="Voltar ao menu principal", value="voltar_menu"),
            ],
        )
        await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))

        return await step_context.prompt(
            "ChoiceExtrato",
            PromptOptions(
                prompt=MessageFactory.text("Clique em uma opção acima ou digite sua escolha:"),
                retry_prompt=MessageFactory.text("❌ Opção inválida. Digite 'consultar_outro' ou 'voltar_menu'."),
            ),
        )

    async def next_action_step(self, step_context: WaterfallStepContext):
        option = step_context.result.lower()

        if option == "consultar_outro":
            await step_context.context.send_activity("🔄 Ok! Vamos consultar outro mês.")
            return await step_context.replace_dialog(self.initial_dialog_id)

        elif option == "voltar_menu":
            await step_context.context.send_activity("🏠 Voltando ao menu principal...")
            return await step_context.replace_dialog("MainDialog")

        await step_context.context.send_activity("🤔 Não entendi sua escolha. Voltando ao menu principal.")
        return await step_context.replace_dialog("MainDialog")
