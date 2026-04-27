from flask import Flask, request, session, redirect, url_for, render_template_string
import os
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ========== CONFIGURAÇÕES (ALTERE) ==========
PIX_KEY = "chave-aleatoria-da-conta-laranja"
MERCHANT_NAME = "10X Private Online"
MERCHANT_CITY = "SAO PAULO"
# =============================================

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
        :root {
            --gold: #C9A84C;
            --gold-light: #D4AF37;
            --bg: #060606;
            --card: #0D0D0D;
            --text: #FFFFFF;
            --text-dim: #A0A0A0;
            --border: #1F1F1F;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }
        .container { max-width: 680px; margin: 0 auto; padding: 40px 20px; }

        /* Logo */
        .logo { text-align: center; margin-bottom: 36px; }
        .logo .mark {
            font-size: 0.8rem; letter-spacing: 3px; color: var(--gold);
            text-transform: uppercase; margin-bottom: 4px;
        }
        .logo h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
        .logo .by { font-size: 0.75rem; color: #555; margin-top: 2px; }

        /* Hero */
        .hero { text-align: center; margin-bottom: 40px; }
        .hero .tag {
            display: inline-block; background: rgba(201,168,76,0.1); color: var(--gold);
            padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 16px;
            border: 1px solid rgba(201,168,76,0.2);
        }
        .hero h2 {
            font-size: 2.2rem; line-height: 1.2; margin-bottom: 10px;
            background: linear-gradient(135deg, #D4AF37, #F5E6B8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        /* Urgency */
        .urgency {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 20px 24px; margin-bottom: 32px; text-align: center;
        }
        .urgency p { margin-bottom: 10px; font-weight: 500; }
        .progress {
            background: #2A2A2A; border-radius: 10px; height: 6px; margin: 10px 0;
        }
        .progress-fill {
            background: linear-gradient(90deg, var(--gold), var(--gold-light));
            height: 100%; width: 84%; border-radius: 10px;
        }
        .urgency small { color: var(--text-dim); }

        /* Card */
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 16px; padding: 32px 28px; margin-bottom: 32px;
        }
        .card h3 {
            font-size: 1.4rem; margin-bottom: 16px; color: var(--gold);
        }

        /* Form */
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; margin-bottom: 6px; font-size: 0.9rem; color: #CCC; font-weight: 500; }
        .form-group input, .form-group select {
            width: 100%; padding: 14px 16px; background: #111; border: 1px solid #2A2A2A;
            border-radius: 10px; color: #FFF; font-size: 1rem; transition: 0.2s;
        }
        .form-group input:focus, .form-group select:focus { border-color: var(--gold); outline: none; }
        .form-group select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23C9A84C' fill='none'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 16px center; }

        .btn-gold {
            display: block; width: 100%; padding: 16px; background: linear-gradient(135deg, #C9A84C, #D4AF37);
            color: #0A0A0A; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: 700;
            cursor: pointer; transition: 0.3s; letter-spacing: 0.3px;
        }
        .btn-gold:hover { background: linear-gradient(135deg, #B8922E, #C9A84C); }

        /* Depoimentos */
        .depoimentos { margin: 32px 0; }
        .depoimento {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 20px; margin-bottom: 12px;
        }
        .depoimento .name { font-weight: 700; color: var(--gold); }
        .depoimento .cargo { font-size: 0.8rem; color: #777; margin-bottom: 8px; }
        .depoimento .text { font-size: 0.9rem; color: #BBB; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Logo -->
        <div class="logo">
            <div class="mark">10X PRIVATE ONLINE</div>
            <h1>Construa Riqueza Composta</h1>
            <div class="by">BY NITRO10X</div>
        </div>

        <!-- Hero -->
        <div class="hero">
            <div class="tag">AO VIVO · 22 E 23 DE MAIO</div>
            <h2>O evento que transforma empresários em multiplicadores de patrimônio</h2>
        </div>

        <!-- Urgency -->
        <div class="urgency">
            <p>⚠️ <strong>84% das vagas preenchidas</strong> — apenas 16% restante</p>
            <div class="progress"><div class="progress-fill"></div></div>
            <small>O valor aumenta automaticamente quando as vagas esgotarem</small>
        </div>

        <!-- Form card -->
        <div class="card">
            <h3>Descubra sua condição de acesso</h3>
            <p style="color:#AAA; margin-bottom:20px;">Responda abaixo e veja o valor personalizado para o seu momento.</p>
            <form method="POST">
                <div class="form-group">
                    <label>Nome completo</label>
                    <input type="text" name="nome" required placeholder="Como prefere ser chamado">
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
                    <label>Empresa</label>
                    <input type="text" name="empresa" required placeholder="Nome da sua empresa">
                </div>
                <div class="form-group">
                    <label>Em qual estágio você está?</label>
                    <select name="faturamento" required>
                        <option value="">Selecione seu momento...</option>
                        <option value="nunca">Nunca investi — quero começar</option>
                        <option value="iniciante">Já invisto, mas sem consistência</option>
                        <option value="intermediario">Invisto regularmente</option>
                        <option value="avancado">Sou investidor experiente</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Qual sua maior dor financeira hoje?</label>
                    <input type="text" name="dor" required placeholder="Ex: dinheiro parado, falta de tempo, medo de errar...">
                </div>
                <button type="submit" class="btn-gold">Ver minha condição de acesso</button>
            </form>
        </div>

        <!-- Depoimentos -->
        <div class="depoimentos">
            <div class="depoimento">
                <div class="name">Marco Costa</div>
                <div class="cargo">Empresário</div>
                <div class="text">"Em 2019, faturávamos cerca de R$12 milhões por ano. Esse ano vamos faturar mais de R$80 milhões."</div>
            </div>
            <div class="depoimento">
                <div class="name">Gustavo Mores</div>
                <div class="cargo">CEO · De R$40MM para R$1 Bi</div>
                <div class="text">"Em 2025 bati no bilhão. Isso só foi possível com o método 10X."</div>
            </div>
            <div class="depoimento">
                <div class="name">Sabrina Theil</div>
                <div class="cargo">Rede de Clínicas</div>
                <div class="text">"A nutricionista de 2019 hoje tem uma rede de clínicas. Só foi possível com o Pyero."</div>
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
    <title>Finalizar — 10X Private Online</title>
    <style>
        :root {
            --gold: #C9A84C; --gold-light: #D4AF37;
            --bg: #060606; --card: #0D0D0D; --text: #FFFFFF;
            --text-dim: #A0A0A0; --border: #1F1F1F;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg); color: var(--text); text-align: center;
            padding: 40px 20px; -webkit-font-smoothing: antialiased;
        }
        .logo { margin-bottom: 28px; }
        .logo .mark {
            font-size: 0.75rem; letter-spacing: 3px; color: var(--gold);
            text-transform: uppercase; margin-bottom: 2px;
        }
        .logo h2 { font-size: 1.5rem; font-weight: 700; }
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 16px; padding: 32px 24px; max-width: 480px; margin: 0 auto;
        }
        .preco-container { margin: 24px 0; }
        .preco-antigo { font-size: 1rem; color: #666; text-decoration: line-through; }
        .preco-novo { font-size: 3.5rem; font-weight: 800; color: var(--gold); line-height: 1; }
        .preco-novo span { font-size: 1rem; color: #AAA; font-weight: 400; }
        .qr-box {
            background: #FFF; border-radius: 16px; padding: 20px; display: inline-block;
            margin: 20px 0; border: 2px solid var(--gold);
        }
        .qr-box img { width: 200px; height: 200px; }
        .instrucoes { font-size: 0.9rem; color: #AAA; margin: 16px 0; }
        .btn-confirmar {
            display: block; width: 100%; padding: 16px; background: #25D366; color: #FFF;
            border: none; border-radius: 10px; font-size: 1.1rem; font-weight: 700;
            cursor: pointer; margin-top: 20px;
        }
        .garantia { margin-top: 20px; font-size: 0.8rem; color: #666; }
        .garantia span { color: var(--gold); }
    </style>
</head>
<body>
    <div class="logo">
        <div class="mark">10X PRIVATE ONLINE</div>
        <h2>Finalizar Inscrição</h2>
    </div>
    <div class="card">
        <p style="color:#AAA;">Condição personalizada para você:</p>
        <div class="preco-container">
            <div class="preco-antigo">R$ 197,00</div>
            <div class="preco-novo">R$ {{ preco }}<span>,00</span></div>
        </div>
        <p style="color:#CCC; margin-bottom:8px;">Pagamento único · Acesso vitalício</p>
        <p style="font-size:0.8rem; color:#888;">22 e 23 de Maio de 2026 — Zoom fechado</p>
        <div class="qr-box">
            <img src="data:image/png;base64,{{ qr_b64 }}" alt="QR Pix">
        </div>
        <p style="font-size:0.75rem; color:#666;">Abra o app do seu banco e escaneie o código</p>
        <button class="btn-confirmar" onclick="confirmar()">Já realizei o pagamento</button>
        <div class="garantia">
            <p><span>Garantia Incondicional de 7 dias:</span> se não gostar, devolvemos 100% do seu dinheiro.</p>
        </div>
    </div>
    <script>
        function confirmar() {
            alert("✅ Recebemos sua confirmação. Em instantes você receberá o link do Zoom no WhatsApp e e-mail cadastrados.");
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
