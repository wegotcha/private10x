from flask import Flask, request, session, redirect, url_for, render_template_string
import os
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ========== SUBSTITUA ==========
PIX_KEY = "chave-aleatoria-da-conta-laranja"   # ex: 1a2b3c4d-...@picpay
MERCHANT_NAME = "10X Private Online"
MERCHANT_CITY = "SAO PAULO"
# ==============================

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

def gerar_qr_pix(valor):
    amount_str = str(int(valor)).zfill(2)
    payload = (
        f"00020126360014br.gov.bcb.pix0114{PIX_KEY}"
        f"520400005303986540{amount_str}"
        f"5802BR5922{MERCHANT_NAME}6009{MERCHANT_CITY}62070503***"
    )
    return payload + "6304" + gerar_crc16(payload + "6304")

def qr_para_base64(valor):
    payload = gerar_qr_pix(valor)
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

PRECOS = {
    "nunca": 47,
    "iniciante": 67,
    "intermediario": 97,
    "avancado": 147,
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome", ""),
            "cpf": request.form.get("cpf", ""),
            "cnpj": request.form.get("cnpj", ""),
            "empresa": request.form.get("empresa", ""),
            "faturamento": request.form.get("faturamento", ""),
            "dor": request.form.get("dor", ""),
        }
        preco = PRECOS.get(dados["faturamento"], 72)
        session["dados"] = dados
        session["preco"] = preco
        return redirect(url_for("checkout"))
    return render_template_string(HTML_INDEX)

@app.route("/checkout")
def checkout():
    preco = session.get("preco", 72)
    qr_b64 = qr_para_base64(preco)
    return render_template_string(HTML_CHECKOUT, preco=preco, qr_b64=qr_b64)

HTML_INDEX = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>10X Private Online — Construa Riqueza Composta</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: #0a0a0a;
            color: #fff;
            line-height: 1.6;
        }
        .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
        .hero { text-align: center; margin-bottom: 40px; }
        .hero h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #d4af37, #f5e6b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .hero p { color: #aaa; font-size: 1.1em; }
        .mentores { display: flex; justify-content: center; gap: 20px; margin: 30px 0; flex-wrap: wrap; }
        .mentor { text-align: center; flex: 1; min-width: 140px; }
        .mentor-avatar {
            width: 80px; height: 80px; border-radius: 50%;
            background: #222; border: 2px solid #d4af37;
            margin: 0 auto 10px; display: flex; align-items: center;
            justify-content: center; font-size: 2em;
        }
        .card {
            background: #1a1a1a; border: 1px solid #333; border-radius: 12px;
            padding: 30px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(212, 175, 55, 0.1);
        }
        .card h2 { color: #d4af37; margin-bottom: 15px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; color: #ccc; font-weight: 500; }
        .form-group input, .form-group select {
            width: 100%; padding: 12px; background: #111; border: 1px solid #333;
            border-radius: 8px; color: #fff; font-size: 1em;
        }
        .form-group input:focus, .form-group select:focus { border-color: #d4af37; outline: none; }
        .btn {
            display: block; width: 100%; padding: 16px;
            background: linear-gradient(135deg, #d4af37, #c5a54b); color: #0a0a0a;
            border: none; border-radius: 8px; font-size: 1.1em; font-weight: bold;
            cursor: pointer; transition: 0.3s;
        }
        .btn:hover { background: linear-gradient(135deg, #c5a54b, #b8942e); }
        .depoimentos { margin: 30px 0; font-size: 0.9em; color: #888; text-align: center; }
        .depoimento { background: #111; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
        .depoimento strong { color: #d4af37; }
        .urgencia {
            text-align: center; background: #1a1a1a; padding: 20px;
            border-radius: 12px; margin-bottom: 30px;
        }
        .progress-bar { background: #333; border-radius: 10px; height: 8px; margin: 10px 0; }
        .progress-fill { background: #d4af37; height: 100%; width: 86%; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>10X Private Online</h1>
            <p>Construa Riqueza Composta com Pyero Tavolazzi &amp; Pablo Marçal</p>
        </div>

        <div class="mentores">
            <div class="mentor">
                <div class="mentor-avatar">👤</div>
                <strong>Pyero Tavolazzi</strong>
                <p style="font-size:0.8em;color:#888;">Estrategista de riqueza</p>
            </div>
            <div class="mentor">
                <div class="mentor-avatar">👤</div>
                <strong>Pablo Marçal</strong>
                <p style="font-size:0.8em;color:#888;">Mentor de negócios</p>
            </div>
        </div>

        <div class="urgencia">
            <p>⚠️ <strong>86% das vagas preenchidas</strong> — 14% restante</p>
            <div class="progress-bar"><div class="progress-fill"></div></div>
            <p style="font-size:0.9em;color:#d4af37;">O preço muda quando as vagas esgotarem</p>
        </div>

        <div class="card">
            <h2>Responda e descubra seu investimento</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Nome completo</label>
                    <input type="text" name="nome" required placeholder="Seu nome">
                </div>
                <div class="form-group">
                    <label>CPF</label>
                    <input type="text" name="cpf" required placeholder="000.000.000-00">
                </div>
                <div class="form-group">
                    <label>CNPJ (opcional)</label>
                    <input type="text" name="cnpj" placeholder="00.000.000/0001-00">
                </div>
                <div class="form-group">
                    <label>Nome da Empresa</label>
                    <input type="text" name="empresa" required placeholder="Sua empresa">
                </div>
                <div class="form-group">
                    <label>Nível de experiência com investimentos/negócios</label>
                    <select name="faturamento" required>
                        <option value="">Selecione...</option>
                        <option value="nunca">Nunca investi</option>
                        <option value="iniciante">Já fiz alguns investimentos</option>
                        <option value="intermediario">Invisto regularmente</option>
                        <option value="avancado">Sou investidor experiente</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Qual sua maior dor ou desafio hoje?</label>
                    <input type="text" name="dor" required placeholder="Ex: falta de tempo, capital parado...">
                </div>
                <button type="submit" class="btn">Ver meu investimento</button>
            </form>
        </div>

        <div class="depoimentos">
            <div class="depoimento">
                <strong>Marcelo Costa</strong> — "De R$12M para R$60M/ano. O 10X mudou tudo."
            </div>
            <div class="depoimento">
                <strong>Gustavo Meres</strong> — "De R$40M para R$1 Bilhão. Isso funciona."
            </div>
        </div>
    </div>
</body>
</html>"""

HTML_CHECKOUT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finalizar Inscrição — 10X Private Online</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: #0a0a0a; color: #fff; text-align: center;
            padding: 40px 20px;
        }
        .card {
            background: #1a1a1a; border: 1px solid #333; border-radius: 12px;
            padding: 30px; max-width: 450px; margin: 0 auto;
            box-shadow: 0 4px 20px rgba(212, 175, 55, 0.15);
        }
        h2 { color: #d4af37; margin-bottom: 15px; }
        .preco {
            font-size: 3em; color: #d4af37; margin: 20px 0; font-weight: bold;
        }
        .preco small { font-size: 0.4em; color: #888; text-decoration: line-through; }
        .qr-container { margin: 20px auto; }
        .qr-container img {
            border: 2px solid #d4af37; border-radius: 12px;
            padding: 10px; background: #fff;
        }
        .instrucoes { margin: 20px 0; font-size: 0.9em; color: #aaa; }
        .btn-confirmar {
            display: block; width: 100%; padding: 16px;
            background: #25D366; color: #fff; border: none;
            border-radius: 8px; font-size: 1.1em; font-weight: bold;
            cursor: pointer; margin-top: 20px;
        }
        .garantia { margin-top: 20px; font-size: 0.8em; color: #888; }
        .garantia span { color: #d4af37; }
    </style>
</head>
<body>
    <div class="card">
        <h2>✅ Dados recebidos!</h2>
        <p>Com base no seu perfil, seu investimento é:</p>
        <div class="preco">
            <small>R$197</small> R${{ preco }}
        </div>
        <p style="color:#aaa;">Pagamento único — acesso vitalício</p>
        <div class="qr-container">
            <p>Escaneie o QR Code com seu app bancário:</p>
            <img src="data:image/png;base64,{{ qr_b64 }}" alt="QR Code Pix" width="220">
        </div>
        <p style="font-size:0.8em;color:#888;">Ou copie a chave: {{ PIX_KEY }}</p>
        <button class="btn-confirmar" onclick="confirmar()">Já paguei</button>
        <div class="garantia">
            <p><span>Garantia de 7 dias:</span> se não gostar, devolvemos seu dinheiro.</p>
            <p>22 e 23 de Maio de 2026 — Zoom fechado</p>
        </div>
    </div>
    <script>
        function confirmar() {
            alert("✅ Pagamento em verificação. Em instantes você receberá o link do Zoom por e-mail/WhatsApp.");
            fetch("/confirmar", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({status:"pago"})});
        }
    </script>
</body>
</html>"""

@app.route("/confirmar", methods=["POST"])
def confirmar():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
