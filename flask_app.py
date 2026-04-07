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

# Instância global
telegram_app = None

import threading
import asyncio
from bot import setup_application

bg_loop = asyncio.new_event_loop()
_thread_started = False
_thread_lock = threading.Lock()
_bot_ready = threading.Event()

def start_background_loop(l):
    asyncio.set_event_loop(l)
    l.run_forever()

async def init_bot():
    """Inicializa a aplicação do telegram que processará as requisições"""
    global telegram_app
    if telegram_app is None:
        try:
            telegram_app = setup_application()
            await telegram_app.initialize()
            await telegram_app.start()
            print("Bot inicializado com sucesso!")
        except Exception as e:
            print(f"Erro ao inicializar o bot: {e}")
        finally:
            _bot_ready.set()

def ensure_background_thread():
    global _thread_started
    with _thread_lock:
        if not _thread_started:
            threading.Thread(target=start_background_loop, args=(bg_loop,), daemon=True).start()
            asyncio.run_coroutine_threadsafe(init_bot(), bg_loop)
            _thread_started = True

# Uma camada extra de segurança para o webhook
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
if not WEBHOOK_SECRET:
    raise ValueError("Por segurança, defina um WEBHOOK_SECRET no arquivo .env")

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    ensure_background_thread()
    # Aguarda o bot inicializar no background antes de prosseguir com a requisição
    _bot_ready.wait(timeout=10)

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

    if telegram_app is not None:
        try:
            update = Update.de_json(update_data, telegram_app.bot)
            # Joga a execução do update para a thread do asyncio em background
            future = asyncio.run_coroutine_threadsafe(telegram_app.process_update(update), bg_loop)
            
            # Printa qualquer erro silencioso jogando-o no arquivo error.log
            def check_error(f):
                try:
                    f.result()
                except Exception as ex:
                    import traceback
                    print(f"Erro fatal no processamento assíncrono: {ex}")
                    traceback.print_exc()
            future.add_done_callback(check_error)

        except Exception as e:
            print(f"Erro no enviou ao loop: {e}")
            
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return "✅ Servidor Webhook do Bot do Telegram está online e conectado!"

if __name__ == '__main__':
    app.run(port=8000, debug=True)
