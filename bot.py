import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

# Classe Calculadora (movida do verificador.py)
class CalculadoraEscala:
    def __init__(self, data_base_trabalho: str):
        self.data_base = datetime.strptime(data_base_trabalho, "%d/%m/%Y")

    def verificar_dia(self, data_consulta_str: str) -> str:
        try:
            data_consulta = datetime.strptime(data_consulta_str, "%d/%m/%Y")
            diferenca = (data_consulta - self.data_base).days
            if diferenca % 2 == 0:
                return "Trabalha 🏢"
            else:
                return "Folga 🏖️"
        except ValueError:
            return "Formato inválido. Use DD/MM/AAAA."

# Carrega a variável de ambiente
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

DATA_BASE, DATA_CONSULTA = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    nome = user.first_name if user else "usuário"
    
    keyboard = [
        [InlineKeyboardButton("🔍 Verificar Minha Escala", callback_data="verificar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Olá, *{nome}*! 👋\n\n"
        "Sou o seu assistente de escalas 12x36.\n"
        "Posso te ajudar a saber rapidamente se você trabalha ou folga em qualquer data!\n\n"
        "Para começar agora, basta clicar no botão abaixo ou digitar /verificar",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def iniciar_verificacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = "📝 Vamos lá! Primeiro, me diga: *qual foi a data do seu último plantão (dia de trabalho)?*\n\n" \
          "Por favor, digite no formato de data normal. Ex: 01/04/2026"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")
    
    return DATA_BASE

def _validar_data(texto: str) -> bool:
    """Retorna True se o texto for uma data válida no formato DD/MM/AAAA."""
    try:
        datetime.strptime(texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False

async def receber_data_base(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    
    if not _validar_data(texto):
        await update.message.reply_text(
            "⚠️ Data inválida! Por favor, use o formato *DD/MM/AAAA*.\n"
            "Exemplo: `01/04/2026`\n\n"
            "Tente novamente:",
            parse_mode="Markdown"
        )
        return DATA_BASE  # Fica no mesmo estado, aguardando nova tentativa
    
    context.user_data['data_base'] = texto
    await update.message.reply_text(
        f"✅ Beleza! Salvei sua data base: *{texto}*\n\n"
        "Agora me diga: *qual é a data que você quer consultar?*\n"
        "Mesmo formato. Ex: `15/05/2026`",
        parse_mode="Markdown"
    )
    return DATA_CONSULTA

async def receber_data_consulta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data_consulta = update.message.text.strip()
    data_base = context.user_data.get('data_base')
    
    if not _validar_data(data_consulta):
        await update.message.reply_text(
            "⚠️ Data inválida! Por favor, use o formato *DD/MM/AAAA*.\n"
            "Exemplo: `15/05/2026`\n\n"
            "Tente novamente:",
            parse_mode="Markdown"
        )
        return DATA_CONSULTA  # Fica no mesmo estado, aguardando nova tentativa
    
    escala = CalculadoraEscala(data_base_trabalho=data_base)
    resultado = escala.verificar_dia(data_consulta)
    
    await update.message.reply_text(
        f"📅 *Resultado para o dia {data_consulta}:*\n\n"
        f"Você estará de: {resultado}!\n\n"
        "Quer checar outra data? É só enviar qualquer mensagem ou digitar /verificar.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END



async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Processo cancelado. É só chamar /verificar quando precisar!")
    return ConversationHandler.END

async def mensagem_fora_de_contexto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde a mensagens de texto enviadas fora de qualquer fluxo ativo."""
    keyboard = [
        [InlineKeyboardButton("🔍 Verificar Minha Escala", callback_data="verificar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Não entendi. 😅 Use o botão abaixo ou digite /verificar para consultar sua escala!",
        reply_markup=reply_markup
    )

def setup_application():
    if not TOKEN:
        raise ValueError("BOT_TOKEN não encontrado no arquivo .env!")

    builder = ApplicationBuilder().token(TOKEN)
    
    # Em contas gratuitas do PythonAnywhere o uWSGI as vezes perde as variáveis de ambiente do Proxy
    # Configurar explicitamente resolve problemas de timeout/bloqueio reverso.
    if os.environ.get('PYTHONANYWHERE_SITE'):
        proxy = "http://proxy.server:3128"
        builder = builder.proxy(proxy).get_updates_proxy(proxy)

    app = builder.build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("verificar", iniciar_verificacao),
            CallbackQueryHandler(iniciar_verificacao, pattern="^verificar$"),
        ],
        states={
            DATA_BASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_base)],
            DATA_CONSULTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_consulta)],
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar),
            CommandHandler("start", start),
            CommandHandler("verificar", iniciar_verificacao),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    # Handler para textos enviados completamente fora do fluxo de conversa
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem_fora_de_contexto))
    return app

def main():
    try:
        app = setup_application()
    except ValueError as e:
        print(f"Erro: {e}")
        return

    print("\n" + "="*40)
    print(" 🤖 O Bot foi iniciado com sucesso!")
    print("="*40)
    print(" 📈 Pronto para verificar escalas.")
    print(" 📱 Vá no Telegram e envie /start")
    print("="*40)
    print(" Pressione Ctrl+C para desligar.\n")
    app.run_polling()

if __name__ == '__main__':
    main()
