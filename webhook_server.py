from flask import Flask, request, jsonify
import hmac
import hashlib
import json
from datetime import datetime

app = Flask(__name__)

ALCHEMY_SIGNING_KEY = "nEQfWc6DNi6VeiWGNW8DHfRd4CvPC2R7"

def verify_signature(payload, signature):
    """Verifica que el webhook viene de Alchemy"""
    expected = hmac.new(
        ALCHEMY_SIGNING_KEY.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route("/webhook/alchemy", methods=["POST"])
def alchemy_webhook():
    signature = request.headers.get("X-Alchemy-Signature", "")

    # Verificar firma (opcional pero recomendado)
    # if not verify_signature(request.data, signature):
    #     return jsonify({"error": "Invalid signature"}), 401

    data = request.json
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*50}")
    print(f"[{timestamp}] Webhook recibido!")
    print(f"{'='*50}")

    event_type = data.get("type", "unknown")
    print(f"Tipo: {event_type}")

    if "event" in data:
        event = data["event"]
        print(f"Network: {event.get('network', 'N/A')}")

        activity = event.get("activity", [])
        for tx in activity:
            print(f"\n--- Transaccion ---")
            print(f"  From: {tx.get('fromAddress', 'N/A')}")
            print(f"  To: {tx.get('toAddress', 'N/A')}")
            print(f"  Value: {tx.get('value', 0)} {tx.get('asset', '')}")
            print(f"  Hash: {tx.get('hash', 'N/A')}")
            print(f"  Category: {tx.get('category', 'N/A')}")

    # Log completo para debug
    print(f"\nPayload completo:")
    print(json.dumps(data, indent=2))

    return jsonify({"status": "ok"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "alchemy-webhook"}), 200

@app.route("/", methods=["GET"])
def home():
    return """
    <h1>Alchemy Webhook Server</h1>
    <p>Endpoints:</p>
    <ul>
        <li><code>POST /webhook/alchemy</code> - Recibe webhooks de Alchemy</li>
        <li><code>GET /health</code> - Health check</li>
    </ul>
    <p>Estado: Activo</p>
    """

if __name__ == "__main__":
    print("="*50)
    print("Alchemy Webhook Server")
    print("="*50)
    print("Endpoint: http://localhost:80/webhook/alchemy")
    print("Health:   http://localhost:80/health")
    print("="*50)
    app.run(host="0.0.0.0", port=80, debug=True)
