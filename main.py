import os
import logging
import uuid
from flask import Flask, request
import requests
from base64 import b64decode
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from pagamento import criar_order_pix

# Variáveis de ambiente
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GRUPO_VIP_LINK = os.environ.get("GRUPO_VIP_LINK")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")  # Mercado Pago Access Token

# Flask app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Inicializa o bot
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Início
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bem-vindo! Use /assinar para gerar seu PIX.")

# Assinar
async def assinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referencia = f"user_{user_id}_{uuid.uuid4().hex[:8]}"

    pagamento = criar_order_pix(19.90, "Assinatura VIP - 1 mês", referencia)

    logging.info(f"Pagamento criado: {pagamento}")

    if pagamento:
        keyboard = [[
            InlineKeyboardButton("✅ Já paguei", callback_data=f"confirmar_{pagamento['order_id']}")
        ]]
        await update.message.reply_text(
            "✅ PIX gerado!\n\n"
            "Copie e cole o código Pix no seu app bancário:\n\n"
            f"`{pagamento['qr_code_string']}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        qr_bytes = BytesIO(b64decode(pagamento["qr_code_img_base64"]))
        qr_file = InputFile(qr_bytes, filename="qrcode.png")
        await update.message.reply_photo(photo=qr_file, caption="📸 Escaneie o QR Code")
    else:
        await update.message.reply_text("❌ Erro ao gerar pagamento.")

# Confirmar pagamento
async def confirmar_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Verificando pagamento...")

    order_id = query.data.replace("confirmar_", "")

    url = f"https://api.mercadopago.com/v1/orders/{order_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        status = data.get("status")

        if status == "closed":  # Pedido pago
            await query.edit_message_text(
                f"✅ Pagamento confirmado!\n\n🔓 Acesso liberado!\n{GRUPO_VIP_LINK}"
            )
        else:
            await query.edit_message_text("⚠️ Pagamento ainda não foi identificado.")
    else:
        await query.edit_message_text("❌ Erro ao verificar pagamento.")

# Adiciona handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("assinar", assinar))
application.add_handler(CallbackQueryHandler(confirmar_pagamento, pattern="confirmar_.*"))

# Rota Webhook Telegram
@app.post("/webhook")
async def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "🤖 Bot com Webhook está online!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="/webhook",
        webhook_url=f"{os.environ.get('RENDER_EXTERNAL_URL')}/webhook"
    )
