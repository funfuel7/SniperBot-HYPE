import os
import time
import requests
from web3 import Web3
from eth_account import Account

API_URL = "https://api.hyperliquid.xyz"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3()

account = Account.from_key(PRIVATE_KEY)
address = account.address

print("Using wallet:", address)

SYMBOL = "BTC"
SIZE = 0.001

# ==============================
# GET PRICE
# ==============================

def get_price():
    res = requests.post(f"{API_URL}/info", json={"type": "allMids"})
    data = res.json()
    return float(data[SYMBOL])

# ==============================
# GET NONCE
# ==============================

def get_nonce():
    return int(time.time() * 1000)

# ==============================
# SIGN TYPED DATA (CORRECT WAY)
# ==============================

def sign_order(action, nonce):
    message = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"}
            ],
            "Action": [
                {"name": "action", "type": "string"},
                {"name": "nonce", "type": "uint256"}
            ]
        },
        "primaryType": "Action",
        "domain": {"name": "Hyperliquid"},
        "message": {
            "action": str(action),
            "nonce": nonce
        }
    }

    signed = account.sign_message(
        Web3.solidity_keccak(['string'], [str(message)])
    )

    return signed.signature.hex()

# ==============================
# SEND ORDER
# ==============================

def send_order():
    price = get_price()
    nonce = get_nonce()

    print("\n🚀 TEST ORDER")
    print("Price:", price)

    action = {
        "type": "order",
        "orders": [
            {
                "coin": SYMBOL,
                "isBuy": True,
                "sz": SIZE,
                "limitPx": round(price, 2),
                "orderType": {"limit": {"tif": "Ioc"}}
            }
        ]
    }

    signature = sign_order(action, nonce)

    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "address": address
    }

    print("\n📤 PAYLOAD:", payload)

    res = requests.post(f"{API_URL}/exchange", json=payload)

    print("\n📥 RESPONSE:", res.text)

# ==============================
# MAIN
# ==============================

def run():
    print("🚀 BOT STARTED")

    send_order()

    while True:
        time.sleep(30)


if __name__ == "__main__":
    run()
