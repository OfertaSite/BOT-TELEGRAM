from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Pega o token do ambiente, setado na Render
BOT_TOKEN = os.getenv("8291584482:AAHXT9gACC7M6pW6t-5gC3bwjqNd1O9NEsU")

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
    # Render usa PORT automaticamente. Pegamos ela com getenv
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
