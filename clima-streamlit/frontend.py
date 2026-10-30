import base64
import html
from pathlib import Path

import requests
import streamlit as st

try:
    from bandeiras_estados import BANDEIRAS
except ImportError:
    BANDEIRAS = {}  # sem o arquivo, o app funciona normalmente, só sem as bandeiras

# Endereço da API Flask (o app.py precisa estar rodando)
API = "http://127.0.0.1:5000"

st.set_page_config(page_title="Estados e Municípios", layout="centered")

# ---------- Estilo: verde, amarelo, azul e branco (cores da bandeira) ----------
# Todas as cores são definidas aqui para funcionar tanto no tema claro quanto no escuro.
st.markdown("""
<style>
:root { --verde:#009C3B; --verde-claro:#E8F5EC; --amarelo:#FFDF00; --azul:#002776; }

.stApp { background: #FFFFFF; }
.block-container { padding-top: 2rem; max-width: 900px; }

/* Cabeçalho */
.topo { background: linear-gradient(135deg, #00A83F 0%, #007F31 100%);
        border-bottom: 8px solid var(--amarelo); border-radius: 18px;
        padding: 34px 16px; text-align: center; margin-bottom: 26px;
        box-shadow: 0 6px 18px rgba(0, 39, 118, 0.18); }
.topo h1 { color: #FFFFFF; margin: 0; font-size: 2.2rem; letter-spacing: 0.5px; }
.topo p { color: var(--amarelo); margin: 8px 0 0 0; font-weight: 600; font-size: 1.05rem; }

/* Rótulos dos campos (Escolha um estado / Buscar município) */
label, label p, div[data-testid="stWidgetLabel"] p {
        color: var(--azul) !important; font-weight: 700 !important; font-size: 1rem !important; }

/* Abas */
div[data-baseweb="tab-list"] { gap: 8px; }
button[data-baseweb="tab"] { background: var(--verde-claro); border-radius: 12px 12px 0 0;
        padding: 10px 28px; height: auto; }
button[data-baseweb="tab"] p { color: var(--azul) !important; font-weight: 700; font-size: 1.05rem; }
button[data-baseweb="tab"][aria-selected="true"] { background: var(--azul); }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--amarelo) !important; }
div[data-baseweb="tab-highlight"] { background: var(--amarelo) !important; height: 4px; }
div[data-baseweb="tab-border"] { background: var(--azul) !important; height: 2px; }

/* Campo de seleção e campo de texto */
div[data-baseweb="select"] > div, div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background: #FFFFFF !important; border-color: var(--azul) !important; border-radius: 10px; }
div[data-baseweb="select"] > div { border: 2px solid var(--azul); }
div[data-baseweb="select"] *, input { color: var(--azul) !important; }
input { background: #FFFFFF !important; font-weight: 600; }
input::placeholder { color: #6B7FA8 !important; font-weight: 400; }
div[data-baseweb="select"] svg { fill: var(--azul) !important; }
ul[role="listbox"], div[data-baseweb="popover"] > div { background: #FFFFFF !important; }
li[role="option"] { background: #FFFFFF !important; color: var(--azul) !important; }
li[role="option"]:hover, li[aria-selected="true"] { background: var(--verde-claro) !important; }

/* Faixa de total */
.total { background: var(--azul); color: #FFFFFF; border-radius: 12px; padding: 12px 18px;
        border-left: 8px solid var(--amarelo); margin: 14px 0 18px 0; font-weight: 600; }
.total span { color: var(--amarelo); font-size: 1.5rem; font-weight: 800; margin: 0 4px; }

/* Cartões dos estados */
.grade { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; }
.cartao { background: #FFFFFF; border: 1px solid #BFE3CB; border-left: 8px solid var(--amarelo);
        border-radius: 12px; padding: 12px 14px; color: var(--azul); font-weight: 600;
        transition: box-shadow .15s, border-color .15s; }
.cartao:hover { border-color: var(--verde); box-shadow: 0 6px 14px rgba(0, 156, 59, 0.22); }
.cartao b { background: var(--azul); color: var(--amarelo); border-radius: 8px;
        padding: 3px 10px; margin-right: 10px; }

/* Lista de municípios */
.lista { max-height: 430px; overflow-y: auto; background: #F7FBF8;
        border: 2px solid var(--azul); border-radius: 14px; padding: 12px; }
.chip { display: inline-block; background: #FFFFFF; color: var(--azul); border: 1.5px solid var(--verde);
        border-radius: 20px; padding: 4px 14px; margin: 4px; font-size: 0.92rem; font-weight: 500; }
.chip:hover { background: var(--verde); color: #FFFFFF; }

/* Painel com a bandeira do estado (aparece no canto inferior direito ao passar o mouse) */
.previa { display: none; position: fixed; right: 24px; bottom: 24px; width: 240px; z-index: 50;
        background: #FFFFFF; border: 3px solid var(--amarelo); border-radius: 16px; padding: 12px;
        box-shadow: 0 10px 26px rgba(0, 39, 118, 0.35); text-align: center; pointer-events: none;
        animation: aparecer .2s ease-out; }
.cartao:hover .previa { display: block; }
.previa small { display: block; color: var(--verde); font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; margin-bottom: 6px; }
.previa img { width: 100%; border-radius: 8px; border: 1px solid #C9D3E6; display: block; }
.previa .nome { display: block; margin-top: 8px; color: var(--azul); font-weight: 800; font-size: 1.05rem; }
@keyframes aparecer { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }

.rodape { text-align: center; color: var(--azul); opacity: 0.7; margin-top: 28px; font-size: 0.85rem; }
</style>
<div class="topo">
  <h1>Estados e Municípios</h1>
  <p>Consulte os estados do Brasil e seus municípios</p>
</div>
""", unsafe_allow_html=True)


# ---------- Bandeiras do Brasil nas laterais (usa o arquivo bandeira.png) ----------
caminho_bandeira = Path(__file__).parent / "bandeira.png"
if caminho_bandeira.exists():
    bandeira_b64 = base64.b64encode(caminho_bandeira.read_bytes()).decode()
    st.markdown(f"""
    <style>
    .bandeira {{ position: fixed; top: 50%; transform: translateY(-50%);
        width: clamp(110px, calc((100vw - 900px) / 2 - 60px), 300px); aspect-ratio: 3 / 2;
        background: url("data:image/png;base64,{bandeira_b64}") center / cover no-repeat;
        border-radius: 10px; border: 3px solid #FFDF00;
        box-shadow: 0 8px 20px rgba(0, 39, 118, 0.3); pointer-events: none; z-index: 1; }}
    .bandeira.esq {{ left: 24px; }}
    .bandeira.dir {{ right: 24px; }}
    @media (max-width: 1150px) {{ .bandeira {{ display: none; }} }}
    </style>
    <div class="bandeira esq"></div>
    <div class="bandeira dir"></div>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def buscar(caminho):
    """Consulta a API Flask e devolve o JSON."""
    resposta = requests.get(API + caminho, timeout=15)
    resposta.raise_for_status()
    return resposta.json()


# ---------- Carrega os estados (mostra erro amigável se a API estiver desligada) ----------
try:
    estados = buscar("/estados")["estados"]
except requests.exceptions.ConnectionError:
    st.error("A API não está rodando. Abra outro terminal e execute: python app.py")
    st.stop()
except requests.exceptions.RequestException:
    st.error("Não foi possível obter os dados da API.")
    st.stop()

aba1, aba2 = st.tabs(["Estados", "Municípios"])

# ---------- Aba 1: todos os estados ----------
with aba1:
    st.markdown(f'<div class="total">Total de estados:<span>{len(estados)}</span></div>',
                unsafe_allow_html=True)
    def criar_cartao(e):
        """Monta o cartão do estado; a bandeira aparece ao passar o mouse."""
        sigla, nome = html.escape(e["sigla"]), html.escape(e["nome"])
        previa = ""
        if e["sigla"] in BANDEIRAS:
            previa = (f'<div class="previa"><small>Bandeira</small>'
                      f'<img src="data:image/png;base64,{BANDEIRAS[e["sigla"]]}" alt="Bandeira de {nome}">'
                      f'<span class="nome">{nome}</span></div>')
        return f'<div class="cartao"><b>{sigla}</b>{nome}{previa}</div>'

    cartoes = "".join(criar_cartao(e) for e in estados)
    st.markdown(f'<div class="grade">{cartoes}</div>', unsafe_allow_html=True)

# ---------- Aba 2: municípios de um estado ----------
with aba2:
    escolha = st.selectbox("Escolha um estado", estados,
                           format_func=lambda e: f'{e["sigla"]} - {e["nome"]}')
    try:
        dados = buscar(f'/estados/{escolha["sigla"]}/municipios')
    except requests.exceptions.RequestException:
        st.error("Não foi possível obter os municípios.")
        st.stop()

    filtro = st.text_input("Buscar município", placeholder="Digite parte do nome...")
    municipios = [m for m in dados["municipios"] if filtro.lower() in m.lower()]

    st.markdown(f'<div class="total">{html.escape(escolha["nome"])}:'
                f'<span>{len(municipios)}</span>município(s)</div>', unsafe_allow_html=True)

    if municipios:
        chips = "".join(f'<span class="chip">{html.escape(m)}</span>' for m in municipios)
        st.markdown(f'<div class="lista">{chips}</div>', unsafe_allow_html=True)
    else:
        st.warning("Nenhum município encontrado.")

st.markdown('<div class="rodape">Dados: IBGE</div>', unsafe_allow_html=True)