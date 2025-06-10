from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import HeroCard, CardAction, ActionTypes
from botbuilder.core import CardFactory
from api.pedido_api import PedidoAPI
from api.user_api import UserAPI
from data_models.user_profile import UserProfile
import re

class ComprarProdutoDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super().__init__("ComprarProdutoDialog")
        self.user_state = user_state

        # Prompts
        self.add_dialog(TextPrompt("QuantidadePrompt", self.validate_quantidade))
        self.add_dialog(TextPrompt("CartaoIdPrompt", self.validate_id))
        self.add_dialog(TextPrompt("cvvPrompt", self.validate_cvv))
        self.add_dialog(TextPrompt("EnderecoIdPrompt", self.validate_id))
        self.add_dialog(TextPrompt("ChoiceDentro"))

        self.add_dialog(
            WaterfallDialog(
                "comprarProdutoWaterfall",
                [
                    self.get_usuario_id_step,
                    self.quantidade_step,
                    self.cvv_step,
                    self.escolher_endereco_step,
                    self.confirmar_pedido_step,
                    self.escolher_acao_apos_erro_step,
                    self.next_action_step,
                ]
            )
        )

        self.initial_dialog_id = "comprarProdutoWaterfall"

    async def validate_quantidade(self, prompt_context):
        return prompt_context.recognized.value.isdigit() and int(prompt_context.recognized.value) > 0

    async def validate_cvv(self, prompt_context):
        cvv = prompt_context.recognized.value
        return cvv.isdigit() and len(cvv) in (3, 4)

    async def validate_id(self, prompt_context):
        return prompt_context.recognized.value.isdigit()

    async def get_usuario_id_step(self, step_context: WaterfallStepContext):
        user_profile_accessor = self.user_state.create_property("UserProfile")
        user_profile = await user_profile_accessor.get(step_context.context, UserProfile)

        if not user_profile.cpf:
            await step_context.context.send_activity("❌ CPF não encontrado. Volte ao menu principal.")
            return await step_context.end_dialog()

        user_api = UserAPI()
        usuario_info = user_api.get_usuario_by_cpf(user_profile.cpf)
        step_context.values["usuario_id"] = usuario_info["id"]

        step_context.values["productId"] = step_context.options.get("productId")
        step_context.values["productName"] = step_context.options.get("productName")
        step_context.values["categoria_produto"] = step_context.options.get("productcategory")

        return await step_context.prompt(
            "QuantidadePrompt",
            PromptOptions(
                prompt=MessageFactory.text("#️⃣ Digite a quantidade desejada:"),
                retry_prompt=MessageFactory.text("❌ Quantidade inválida. Digite um número maior que 0."),
            )
        )

    async def quantidade_step(self, step_context: WaterfallStepContext):
        step_context.values["quantidade"] = int(step_context.result)

        # Buscar cartões
        user_profile_accessor = self.user_state.create_property("UserProfile")
        user_profile = await user_profile_accessor.get(step_context.context, UserProfile)

        user_api = UserAPI()
        cartoes = user_api.get_cartoes_by_cpf(user_profile.cpf)

        buttons = [
            CardAction(
                type=ActionTypes.post_back,
                title=f"Usar cartão {cartao['numero']}",
                value=str(cartao["id"]),
            ) for cartao in cartoes
        ]

        card = HeroCard(
            title="💳 Selecione um cartão para usar:",
            buttons=buttons
        )

        await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))

        return await step_context.prompt(
            "CartaoIdPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Clique no botão do cartão selecionado"),
                retry_prompt=MessageFactory.text("❌ ID inválido."),
            )
        )

    async def cvv_step(self, step_context: WaterfallStepContext):
        step_context.values["id_cartao"] = int(step_context.result)
        return await step_context.prompt(
            "cvvPrompt",
            PromptOptions(
                prompt=MessageFactory.text("🔐 Digite o CVV do cartão selecionado:"),
                retry_prompt=MessageFactory.text("❌ CVV inválido."),
            )
        )

    async def escolher_endereco_step(self, step_context: WaterfallStepContext):
        step_context.values["cvv"] = step_context.result

        # Buscar endereços
        user_profile_accessor = self.user_state.create_property("UserProfile")
        user_profile = await user_profile_accessor.get(step_context.context, UserProfile)

        user_api = UserAPI()
        enderecos = user_api.get_enderecos_by_cpf(user_profile.cpf)

        buttons = [
            CardAction(
                type=ActionTypes.post_back,
                title=f"Usar endereço: {endereco['descricao']}",
                value=str(endereco["id"]),
            ) for endereco in enderecos
        ]

        card = HeroCard(
            title="🏠 Selecione um endereço de entrega:",
            buttons=buttons
        )

        await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))

        return await step_context.prompt(
            "EnderecoIdPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Clique no botão do endereço selecionado"),
                retry_prompt=MessageFactory.text("❌ ID inválido."),
            )
        )

    async def confirmar_pedido_step(self, step_context: WaterfallStepContext):
        step_context.values["id_endereco"] = int(step_context.result)
        pedido_api = PedidoAPI()

        pedido_data = {
            "usuario": step_context.values["usuario_id"],
            "produtos": [{
                "id_produto": step_context.values["productId"],
                "categoria_produto": step_context.values["categoria_produto"],
                "quantidade": step_context.values["quantidade"]
            }],
            "id_cartao": step_context.values["id_cartao"],
            "cvv": step_context.values["cvv"],
            "id_endereco": step_context.values["id_endereco"]
        }

        response = pedido_api.post_pedidos(pedido_data)
        if "mensagem" in response:
            await step_context.context.send_activity(f"❌ Erro ao criar pedido: {response['mensagem']}")
            return await step_context.next("erro_pedido")
        if "error" in response:
            await step_context.context.send_activity(f"❌ Erro ao criar pedido: {response['error']}")
        else:
            # Tenta extrair o número do pedido da string de "success"
            success_msg = response.get("success", "")
            match = re.search(r"Pedido #(\d+)", success_msg)
            if match:
                pedido_id = match.group(1)
            else:
                pedido_id = "desconhecido"

            await step_context.context.send_activity(
                f"✅ Pedido criado com sucesso!\n\n"
                f"📝 Número do pedido: {pedido_id}\n"
                f"📦 Produto: {step_context.values['productName']} (Qtd: {step_context.values['quantidade']})\n"
                f"🪪 Usuário ID: {step_context.values['usuario_id']}\n"
                f"💳 Cartão ID: {step_context.values['id_cartao']}\n"
                f"🏠 Endereço ID: {step_context.values['id_endereco']}"
            )

        return await step_context.end_dialog()
    
    async def escolher_acao_apos_erro_step(self, step_context: WaterfallStepContext):
        result = step_context.result
        # HeroCard com as opções após erro
        card = HeroCard(
            title="⚠️ O que você gostaria de fazer agora?",
            buttons=[
                CardAction(type=ActionTypes.post_back, title="🔁 Refazer o pedido", value="refazer_pedido"),
                CardAction(type=ActionTypes.post_back, title="🏠 Voltar ao menu principal", value="voltar_menu"),
            ],
        )
        await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))

        return await step_context.prompt(
            "ChoiceDentro",
            PromptOptions(
                prompt=MessageFactory.text("Clique em uma opção acima."),
                retry_prompt=MessageFactory.text("❌ Opção inválida. Digite ou clique em 'refazer_pedido' ou 'voltar_menu'."),
            ),
        )


    async def next_action_step(self, step_context: WaterfallStepContext):
        option = step_context.result.lower()

        if option == "refazer_pedido":
            await step_context.context.send_activity("🔁 Vamos tentar refazer o pedido.")
            return await step_context.replace_dialog(self.initial_dialog_id, step_context.options)

        elif option == "voltar_menu":
            await step_context.context.send_activity("🏠 Voltando ao menu principal...")
            return await step_context.replace_dialog("MainDialog")

        await step_context.context.send_activity("🤔 Não entendi sua escolha. Voltando ao menu principal.")
        return await step_context.replace_dialog("MainDialog")