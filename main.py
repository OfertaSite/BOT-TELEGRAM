import os
import logging
import requests
import uuid
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, ContextTypes
from io import BytesIO
from base64 import b64decode
from pagamento import criar_order_pix

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GRUPO_VIP_LINK = os.environ.get("GRUPO_VIP_LINK")
bot = Bot(token=BOT_TOKEN)

dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4)

# HANDLERS

def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text("👋 Bem-vindo! Use /assinar para acessar o conteúdo VIP.")

def assinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referencia = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
    
    pagamento = criar_order_pix(19.90, "Assinatura VIP - 1 mês", referencia)

    if pagamento:
        keyboard = [[
            InlineKeyboardButton("✅ Já paguei", callback_data=f"confirmar_{referencia}")
        ]]

        update.message.reply_text(
            "✅ PIX gerado!\n\n"
            "📥 Copie o código Pix abaixo e pague no seu app bancário:\n\n"
            f"`{pagamento['qr_code_string']}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        qr_bytes = BytesIO(b64decode(pagamento["qr_code_img_base64"]))
        qr_file = InputFile(qr_bytes, filename="qrcode.png")
        update.message.reply_photo(photo=qr_file, caption="📸 Escaneie o QR Code")
    else:
        update.message.reply_text("❌ Erro ao gerar o pagamento. Tente novamente.")

def confirmar_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer("Verificando...")

    query.edit_message_text(
        f"✅ Pagamento confirmado!\n\n🔓 Acesso liberado!\n{GRUPO_VIP_LINK}"
    )

# REGISTRAR HANDLERS
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("assinar", assinar))
dispatcher.add_handler(CallbackQueryHandler(confirmar_pagamento, pattern="confirmar_.*"))

# FLASK ROUTES
@app.route("/")
def index():
    return "🤖 Bot online com Webhook"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

if __name__ == '__main__':
    app.run(port=5000)
