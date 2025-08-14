import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")  # Token do Mercado Pago
USER_ID = os.environ.get("MP_USER_ID")         # ID da sua conta Mercado Pago
EXTERNAL_POS_ID = "SUPERVIPBOT001"             # POS cadastrado no Mercado Pago

def criar_order_pix(valor, descricao, referencia_externa):
    """
    Cria um QR Code Pix dinâmico usando a API oficial do Mercado Pago
    """
    if not ACCESS_TOKEN:
        print("❌ ACCESS_TOKEN não configurado")
        return None
    if not USER_ID:
        print("❌ MP_USER_ID não configurado")
        return None

    url = f"https://api.mercadopago.com/instore/orders/qr/seller/collectors/{USER_ID}/pos/{EXTERNAL_POS_ID}/qrs"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Idempotency-Key": str(uuid.uuid4())
    }

    body = {
        "title": descricao,
        "description": descricao,
        "external_reference": referencia_externa,
        "notification_url": "https://webhook.site/seu-endpoint",  # Trocar para seu webhook real
        "total_amount": float(valor),
        "items": [
            {
                "title": descricao,
                "unit_price": float(valor),
                "quantity": 1,
                "unit_measure": "unit",
                "total_amount": float(valor)
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code in (200, 201):
        data = response.json()
        return {
            "order_id": data.get("id"),
            "qr_code_string": data.get("qr_data"),
            "qr_code_img_base64": data.get("qr_image")
        }
    else:
        print(f"❌ Erro ao criar QR Code Pix ({response.status_code}): {response.text}")
        return None
