import requests
import uuid
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def criar_order_pix(valor, descricao, referencia_externa):
    url = "https://api.mercadopago.com/v1/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Idempotency-Key": str(uuid.uuid4())
    }

    body = {
        "type": "qr",
        "total_amount": str(valor),
        "description": descricao,
        "external_reference": referencia_externa,
        "expiration_time": "PT15M",
        "config": {
            "qr": {
                "external_pos_id": "SUPERVIPBOT001",
                "mode": "dynamic"
            }
        },
        "items": [
            {
                "title": descricao,
                "unit_price": str(valor),
                "quantity": 1
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 201:
        data = response.json()
        print("✅ Pedido criado com sucesso:", data)
        return {
            "order_id": data.get("id"),
            "qr_code_string": data.get("qr_data", {}).get("qr_code"),
            "qr_code_img_base64": data.get("qr_data", {}).get("image")
        }
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
        return None
