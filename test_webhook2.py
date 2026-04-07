import os
import requests
from dotenv import load_dotenv

load_dotenv()
secret = os.getenv('WEBHOOK_SECRET')
url = "https://taynaribeiro.pythonanywhere.com/webhook"

headers = {
    "X-Telegram-Bot-Api-Secret-Token": secret,
    "Content-Type": "application/json"
}

data = {
    "update_id": 123456,
    "message": {
        "message_id": 2,
        "from": {"id": 1234567, "is_bot": False, "first_name": "Test"},
        "chat": {"id": 1234567, "type": "private"},
        "date": 1234567890,
        "text": "/start"
    }
}

r = requests.post(url, headers=headers, json=data)
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}")
