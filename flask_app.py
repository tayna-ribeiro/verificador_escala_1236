import sys
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update

# Adiciona o diretório atual ao sys.path (Necessário no PythonAnywhere)
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from bot import setup_application
from dotenv import load_dotenv

# Força o carregamento do .env do diretório do projeto no servidor WSGI
load_dotenv(os.path.join(path, '.env'))

app = Flask(__name__)

# Instância global do Telegram App e Loop Event para não explodir por concorrência
telegram_app = None

# Cria um loop permanente para que a aplicação do Telegram não crie referências 'mortas'
global_loop = asyncio.new_event_loop()
asyncio.set_event_loop(global_loop)

# Uma camada extra de segurança para o webhook
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
if not WEBHOOK_SECRET:
    raise ValueError("Por segurança, defina um WEBHOOK_SECRET no arquivo .env (O painel do PythonAnywhere deve estar lendo esse arquivo)")

async def init_bot():
    """Inicializa a aplicação do telegram que processará as requisições"""
    global telegram_app
    if telegram_app is None:
        try:
            telegram_app = setup_application()
            await telegram_app.initialize()
            print("Bot inicializado com sucesso!")
        except Exception as e:
            print(f"Erro ao inicializar o bot: {e}")

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    # Verifica se a chamada realmente veio do Telegram
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != WEBHOOK_SECRET:
        return jsonify({"erro": "Acesso não autorizado ou token incorreto"}), 403

    try:
        update_data = request.get_json(force=True)
    except Exception:
        return jsonify({"erro": "Dados inválidos"}), 400
        
    if not update_data:
        return jsonify({"erro": "Body vazio"}), 400

    async def process_update():
        await init_bot()
        if telegram_app is not None:
            update = Update.de_json(update_data, telegram_app.bot)
            await telegram_app.process_update(update)

    # Executa a tarefa no loop persistente em vez de criar um efêmero
    try:
        global_loop.run_until_complete(process_update())
    except Exception as e:
        print(f"Erro no processamento: {e}")
        
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return "✅ Servidor Webhook do Bot do Telegram está online e conectado!"

if __name__ == '__main__':
    app.run(port=8000, debug=True)
