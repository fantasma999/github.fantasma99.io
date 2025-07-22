from flask import Flask, render_template, request, redirect, jsonify, session
import os, random, json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("CHAVE_SECRETA", "minha-chave-secreta")

APP_INFO = {
    "versao": "1.0",
    "autor": "Gregório Casimiro Gime",
    "nome_do_app": "GCG Caçador",
    "endereco_padrao_de_saque": os.getenv("ENDERECO_PADRAO_SAQUE")
}

ADMIN_USER = "admin"
ADMIN_PASS = os.getenv("ADMIN_SENHA")

btc_data = {"enderecos_encontrados": 0, "btc_total": 0.0}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user = request.form["usuario"]
        senha = request.form["senha"]
        if user == ADMIN_USER and senha == ADMIN_PASS:
            session["autenticado"] = True
            return redirect("/painel")
        else:
            return render_template("index.html", erro="Login inválido.")
    return render_template("index.html", erro="")

@app.route("/painel")
def painel():
    if not session.get("autenticado"):
        return redirect("/")
    return render_template("painel.html", dados=btc_data)

@app.route("/verificar")
def verificar():
    btc_data["enderecos_encontrados"] = random.randint(1, 5)
    btc_data["btc_total"] = round(random.uniform(0.01, 0.5), 8)
    with open("transacoes_log.json", "w") as f:
        json.dump(btc_data, f, indent=4)
    return redirect("/painel")

@app.route("/sacar", methods=["POST"])
def sacar():
    endereco = request.form.get("endereco") or APP_INFO["endereco_padrao_de_saque"]
    try:
        with open("transacoes_log.json") as f:
            dados = json.load(f)
    except:
        return jsonify({"status": "erro", "mensagem": "Erro ao carregar dados."})

    if dados["btc_total"] > 0:
        resultado = {
            "status": "sucesso",
            "enviado_para": endereco,
            "quantidade": dados["btc_total"]
        }
        btc_data["btc_total"] = 0.0
    else:
        resultado = {
            "status": "falha",
            "motivo": "Nenhum BTC disponível."
        }

    return jsonify(resultado)

# Compatibilidade com Render
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
