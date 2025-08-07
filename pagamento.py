import requests
import uuid
import os

ACCESS_TOKEN = "TEST-6493240016618428-080712-5beedde3d93eedec2a167e46994ed539-1782895287"


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
        return {
            "order_id": data["id"],
            "qr_code_string": data["qr_data"]["qr_code"],
            "qr_code_img_base64": data["qr_data"]["image"]
        }
    else:
        print(f"Erro: {response.status_code} - {response.text}")
        return None
