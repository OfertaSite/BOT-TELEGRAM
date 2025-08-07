from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route('/')
def home():
    return "🤖 Bot rodando! Envie mensagens no Telegram para testar."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text == "/start":
            send_message(chat_id, "Bem-vindo! Digite /preview para ver uma amostra.")

    return "ok", 200

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from pagamento import criar_order_pix

async def assinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referencia = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
    
    pagamento = criar_order_pix(19.90, "Assinatura VIP - 1 mês", referencia)

    if pagamento:
        keyboard = [[
            InlineKeyboardButton("✅ Já paguei", callback_data=f"confirmar_{referencia}")
        ]]

        await update.message.reply_text(
            "✅ PIX gerado!\n\n"
            "📥 Copie e cole o código Pix abaixo no seu app bancário:\n\n"
            f"`{pagamento['qr_code_string']}`\n\n"
            "📸 Escaneie o QR code enviado a seguir ou use o botão abaixo após pagar.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # Enviar imagem base64 como QR
        from base64 import b64decode
        from io import BytesIO
        from telegram import InputFile

        qr_bytes = BytesIO(b64decode(pagamento["qr_code_img_base64"]))
        qr_file = InputFile(qr_bytes, filename="qrcode.png")

        await update.message.reply_photo(photo=qr_file, caption="🧾 QR Code para pagamento via Pix")
    else:
        await update.message.reply_text("❌ Erro ao gerar o pagamento. Tente novamente mais tarde.")


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Rodando na porta {port}")
    app.run(host='0.0.0.0', port=port)
