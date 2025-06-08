from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.schema import ActionTypes, HeroCard, CardAction, CardImage
from botbuilder.core import CardFactory
from api.product_api import ProductAPI
from dialogs.comprar_produto_dialog import ComprarProdutoDialog
from botbuilder.core import UserState

class ConsultarProdutosDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ConsultarProdutosDialog, self).__init__("ConsultarProdutosDialog")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt("ChoiceDentro"))
        self.add_dialog(ComprarProdutoDialog(user_state))

        self.add_dialog(
            WaterfallDialog(
                "consultarProdutoWaterfall",
                [
                    self.product_name_step,
                    self.product_name_search_step,
                    self.next_action_step
                ],
            )
        )

        self.initial_dialog_id = "consultarProdutoWaterfall"

    async def product_name_step(self, step_context: WaterfallStepContext):
        prompt_message = MessageFactory.text("Por favor, digite o nome do produto que você deseja consultar.")
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Desculpe, não consegui entender. Por favor, digite o nome do produto novamente."),
        )
        return await step_context.prompt(TextPrompt.__name__, prompt_options)

    async def product_name_search_step(self, step_context: WaterfallStepContext):
        product_name = step_context.result.strip()

        produto_api = ProductAPI()

        try:
            response = produto_api.search_product(product_name)
        except Exception as e:
            await step_context.context.send_activity(f"Erro ao consultar produtos: {str(e)}")
            return await step_context.replace_dialog("MainDialog")

        if isinstance(response, dict) and "error" in response:
            await step_context.context.send_activity(response["error"])

        elif isinstance(response, list) and not response:
            await step_context.context.send_activity("❌ Produto não encontrado.")

        elif isinstance(response, list):
            await step_context.context.send_activity(f"🔎 Produtos encontrados para: **{product_name}**")

            for produto in response:
                card = CardFactory.hero_card(
                    HeroCard(
                        title=produto["nome"],
                        text=f"💲 Preço: R$ {produto['preco']}",
                        subtitle=produto["descricao"],
                        images=[CardImage(url=imagem) for imagem in produto.get("imagens", [])],
                        buttons=[
                            CardAction(
                                type=ActionTypes.post_back,
                                title=f"Comprar {produto['nome']}",
                                value={
                                    "acao": "comprar",
                                    "productId": produto["id"],
                                    "productName": produto["nome"],
                                },
                            )
                        ],
                    )
                )
                await step_context.context.send_activity(MessageFactory.attachment(card))

        else:
            await step_context.context.send_activity("❌ Erro inesperado ao processar resposta da API.")

        # SEMPRE perguntar o que deseja fazer
        return await step_context.prompt(
            "ChoiceDentro",
            PromptOptions(
                prompt=MessageFactory.text("O que deseja fazer agora?"),
                choices=[
                    Choice("Consultar outro produto"),
                    Choice("Voltar ao menu principal"),
                ],
            ),
        )

    async def next_action_step(self, step_context: WaterfallStepContext):
        result = step_context.result

        # Verifica se foi retornado um Choice válido
        option = ""
        if hasattr(result, "value"):
            option = result.value.lower()
        elif isinstance(result, str):
            option = result.lower()
        else:
            await step_context.context.send_activity("⚠️ Opção inválida. Retornando ao menu principal.")
            return await step_context.replace_dialog("MainDialog")

        if option == "consultar outro produto":
            await step_context.context.send_activity("🔍 Vamos consultar outro produto.")
            return await step_context.replace_dialog(self.initial_dialog_id)

        elif option == "voltar ao menu principal":
            # Manda para o MainDialog com a flag de "voltar_menu"
            return await step_context.replace_dialog("MainDialog", {"acao": "voltar_menu"})

        # fallback — se der algo errado, volta para MainDialog
        await step_context.context.send_activity("⚠️ Opção não reconhecida. Retornando ao menu principal.")
        return await step_context.replace_dialog("MainDialog")
