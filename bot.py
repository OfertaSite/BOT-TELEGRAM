import os
import uuid
import logging
from io import BytesIO
from base64 import b64decode

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from pagamento import criar_order_pix

BOT_TOKEN = os.environ.get("8291584482:AAHXT9gACC7M6pW6t-5gC3bwjqNd1O9NEsU")
GRUPO_VIP_LINK = os.environ.get("https://t.me/+n5fFL4LvDDMzMThh")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bem-vindo! Use /assinar para ver os planos.")

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
            "Copie e cole o código Pix no seu app bancário:\n\n"
            f"`{pagamento['qr_code_string']}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        qr_bytes = BytesIO(b64decode(pagamento["qr_code_img_base64"]))
        qr_file = InputFile(qr_bytes, filename="qrcode.png")
        await update.message.reply_photo(photo=qr_file, caption="📸 Escaneie o QR code")
    else:
        await update.message.reply_text("❌ Erro ao gerar pagamento.")

async def confirmar_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Verificando...")

    # Simulação de confirmação manual
    await query.edit_message_text(
        "✅ Pagamento confirmado!\n\n"
        f"🔓 Aqui está seu acesso VIP:\n{GRUPO_VIP_LINK}"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("assinar", assinar))
    app.add_handler(CallbackQueryHandler(confirmar_pagamento, pattern="confirmar_.*"))
    app.run_polling()

if __name__ == '__main__':
    main()
