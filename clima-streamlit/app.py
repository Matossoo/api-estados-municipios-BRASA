from flask import Flask, jsonify
import requests

app = Flask(__name__)


@app.route("/")
def inicio():
    return jsonify({"mensagem": "API de estados e municípios. Use /estados ou /estados/SC/municipios"})


@app.route("/estados")
def listar_estados():

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"

    resposta = requests.get(url)

    if resposta.status_code == 200:

        dados = resposta.json()

        estados = []

        for estado in dados:
            estados.append({"sigla": estado["sigla"], "nome": estado["nome"]})

        return jsonify({"total": len(estados), "estados": estados})

    else:
        return jsonify({"erro": "Não foi possível consultar os estados."}), 502


@app.route("/estados/<uf>/municipios")
def listar_municipios(uf):

    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios?orderBy=nome"

    resposta = requests.get(url)

    if resposta.status_code == 200:

        dados = resposta.json()

        municipios = []

        for municipio in dados:
            municipios.append(municipio["nome"])

        return jsonify({"uf": uf.upper(), "total": len(municipios), "municipios": municipios})

    else:
        return jsonify({"erro": "Não foi possível consultar o estado."}), 404


if __name__ == "__main__":
    app.run(debug=True)