from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Agora pega o token corretamente da variável de ambiente BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text == "/start":
            send_message(chat_id, "Bem-vindo! Digite /preview para ver uma amostra.")

    return "ok", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
