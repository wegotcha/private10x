from flask import Flask, request, send_file
import qrcode
import io
import os

app = Flask(__name__)

# ========== CONFIGURAÇÕES (ALTERE TUDO) ==========
PIX_KEY = "sua-chave-pix-laranja"      # chave aleatória da conta laranja
MERCHANT_NAME = "Riqueza Composta"
MERCHANT_CITY = "SAO PAULO"
AMOUNT = 97.00
# =================================================

# Rota para o QR code da criptomoeda (imagem estática "pagamento_cripto.png")
@app.route("/qr_cripto")
def qr_cripto():
    return send_file("pagamento_cripto.png", mimetype="image/png")

def gerar_crc16(payload):
    crc = 0xFFFF
    for byte in payload.encode("ascii"):
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, "04X")

def gerar_pix_payload():
    base = (
        f"00020126360014br.gov.bcb.pix0114{PIX_KEY}"
        f"520400005303986540{str(int(AMOUNT)).zfill(2)}"
        f"5802BR5922{MERCHANT_NAME}6009{MERCHANT_CITY}62070503***"
    )
    crc = gerar_crc16(base + "6304")
    return base + "6304" + crc

@app.route("/")
def pagina():
    if not os.path.exists("index.html"):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Riqueza Composta – Pablo Marçal e Pyero Tavolazzi</title>
    <style>
        body {{ font-family: Arial; background: #111; color: #fff; text-align: center; padding: 40px; }}
        .card {{ background: #222; border-radius: 15px; padding: 30px; max-width: 400px; margin: auto; box-shadow: 0 4px 8px rgba(255,215,0,0.2); }}
        .price {{ font-size: 2em; color: #ffd700; }}
        .btn {{ background: #25D366; color: white; border: none; padding: 15px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 15px; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>Riqueza Composta</h2>
        <p>Palestra exclusiva com <strong>Pablo Marçal</strong> e <strong>Pyero Tavolazzi</strong><br>
        Últimas vagas – condição especial de lançamento</p>
        <p class="price">R$ 97,00</p>

        <p>Pague via Pix:</p>
        <img id="qr" src="/qrcode" alt="QR Code Pix" style="width:200px; height:200px;">
        <p><small>Use o app do seu banco</small></p>
        <button class="btn" id="btn-confirm" onclick="confirmar()">Já paguei</button>
        <div id="msg-ok" class="hidden" style="color:#ffd700; margin-top:15px;">
            ✅ Pagamento identificado! Você receberá o link do Zoom em instantes via WhatsApp.
        </div>

        <div style="margin-top: 25px;">
            <h3>Ou pague com Criptomoeda</h3>
            <p style="font-size: 0.8em; color: #aaa;">(Bitcoin, Monero e outras)</p>
            <img id="qr-cripto" src="/qr_cripto" alt="QR Code para pagamento com criptomoeda" style="width:200px; height:200px; margin: 10px auto;">
            <p style="font-size: 0.7em; color: #888;">Após o pagamento, o ingresso será enviado automaticamente.</p>
            <button class="btn" style="background:#f7931a;" onclick="confirmarCripto()">Já paguei com Cripto</button>
            <div id="msg-cripto-ok" class="hidden" style="color:#ffd700; margin-top:15px;">
                ✅ Verificaremos manualmente. Você receberá o link em breve!
            </div>
        </div>
    </div>
    <script>
        function confirmar() {{
            document.getElementById("btn-confirm").style.display = "none";
            document.getElementById("msg-ok").classList.remove("hidden");
            fetch("/confirmar", {{method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify({{status: "pago"}})}});
        }}
        function confirmarCripto() {{
            document.getElementById("qr-cripto").style.display = "none";
            document.querySelector("button[onclick='confirmarCripto()']").style.display = "none";
            document.getElementById("msg-cripto-ok").classList.remove("hidden");
            fetch("/confirmar", {{method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify({{status: "cripto"}})}});
        }}
    </script>
</body>
</html>"""
        with open("index.html", "w") as f:
            f.write(html)
    return send_file("index.html")

@app.route("/qrcode")
def qr():
    payload = gerar_pix_payload()
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/confirmar", methods=["POST"])
def confirmar():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
