import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
import PyPDF2
import time

# IMPORTAÇÃO DA BUSCA
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
except:
    search_tool = None

st.set_page_config(page_title="Agência IA Premium", page_icon="🏢", layout="wide")

# ==========================================
# MOTOR VISUAL: O NOVO ESCRITÓRIO 2.5D
# ==========================================
def render_office_premium(status_agentes, selecionados):
    agentes_config = [
        {"id": "pesquisador", "nome": "Pesquisador", "emoji": "🔍", "avatar": "👨‍💻", "msg": "Buscando dados..."},
        {"id": "diretor", "nome": "Dir. Criativo", "emoji": "🎨", "avatar": "👩‍🎨", "msg": "Criando conceito..."},
        {"id": "copywriter", "nome": "Copywriter", "emoji": "✍️", "avatar": "✍️", "msg": "Escrevendo..."},
        {"id": "engenheiro", "nome": "Eng. Prompts", "emoji": "🖼️", "avatar": "👨‍🚀", "msg": "Afinando prompts..."},
        {"id": "social", "nome": "Social Media", "emoji": "📱", "avatar": "🤳", "msg": "Organizando posts..."},
    ]

    cards_html = ""
    for ag in agentes_config:
        status = status_agentes.get(ag["id"], "espera")
        ativo = selecionados.get(ag["id"], False)
        
        # Lógica de estilo
        opacity = "1" if ativo else "0.3"
        is_working = status == "trabalhando"
        glow = "working-glow" if is_working else ""
        done_mark = "✅" if status == "concluido" else ""
        
        # Balão de pensamento só aparece se estiver trabalhando
        thought_balloon = f'<div class="thought-balloon">{ag["msg"]}</div>' if is_working else ""

        cards_html += f"""
        <div class="baia-wrapper" style="opacity: {opacity};">
            {thought_balloon}
            <div class="name-tag">{ag['emoji']} {ag['nome']} {done_mark}</div>
            <div class="station {glow}">
                <div class="monitor-screen">{'⚡' if is_working else ''}</div>
                <div class="keyboard"></div>
                <div class="avatar {'jump-anim' if is_working else ''}">{ag['avatar']}</div>
            </div>
        </div>
        """

    return f"""
    <style>
        :root {{ --neon: #00f5d4; --dark: #0a0a12; }}
        body {{ background: var(--dark); font-family: sans-serif; margin: 0; overflow: hidden; }}
        
        /* O Cenário do Escritório */
        .office-floor {{
            background: linear-gradient(180deg, #161625 0%, #0a0a12 100%);
            padding: 40px 20px;
            border-radius: 20px;
            border: 2px solid #1e1e30;
            display: flex;
            flex-direction: column;
            align-items: center;
            perspective: 1000px;
        }}

        /* Área de Lounge no Topo */
        .lounge {{
            width: 100%;
            display: flex;
            justify-content: flex-end;
            gap: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #1e1e30;
            margin-bottom: 30px;
            font-size: 20px;
        }}

        .grid-agentes {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 40px;
            justify-items: center;
        }}

        .baia-wrapper {{
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        /* Balão de Pensamento */
        .thought-balloon {{
            position: absolute;
            top: -45px;
            background: white;
            color: black;
            padding: 5px 10px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            animation: float 2s infinite ease-in-out;
            white-space: nowrap;
        }}
        .thought-balloon::after {{
            content: '';
            position: absolute;
            bottom: -5px;
            left: 50%;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid white;
            transform: translateX(-50%);
        }}

        .name-tag {{
            background: #000;
            color: #fff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            margin-bottom: 8px;
            border: 1px solid #333;
        }}

        /* A Mesa/Estação */
        .station {{
            width: 120px;
            height: 70px;
            background: #2a2a3a;
            border-radius: 8px 8px 0 0;
            position: relative;
            transform: rotateX(20deg);
            box-shadow: 0 10px 0 #1a1a2a;
            display: flex;
            justify-content: center;
        }}

        .monitor-screen {{
            width: 60px;
            height: 35px;
            background: #111;
            border: 3px solid #444;
            border-radius: 4px;
            position: absolute;
            top: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--neon);
            font-size: 12px;
        }}

        .keyboard {{
            width: 40px;
            height: 4px;
            background: #555;
            position: absolute;
            bottom: 15px;
            border-radius: 2px;
        }}

        .avatar {{
            font-size: 40px;
            position: absolute;
            bottom: -15px;
            z-index: 10;
            filter: drop-shadow(0 5px 5px rgba(0,0,0,0.5));
        }}

        /* Efeitos de Neon e Animação */
        .working-glow {{
            box-shadow: 0 0 30px var(--neon), 0 10px 0 #1a1a2a;
            border: 1px solid var(--neon);
        }}
        .working-glow .monitor-screen {{
            background: #002a25;
            border-color: var(--neon);
            box-shadow: inset 0 0 10px var(--neon);
        }}

        @keyframes jump {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-8px); }} }}
        .jump-anim {{ animation: jump 0.4s infinite alternate; }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}
    </style>

    <div class="office-floor">
        <div class="lounge">
            <span title="Máquina de Café">☕</span>
            <span title="Área de Descanso">🛋️</span>
            <span title="Plantas">🌿</span>
        </div>
        <div class="grid-agentes">
            {cards_html}
        </div>
    </div>
    """

# ==========================================
# LÓGICA DO APP (Simplificada para manter as chaves que você já tem)
# ==========================================

# (Mantenha aqui as suas funções extrair_texto_pdf, gerar_pdf, nova_campanha que já funcionam)
def extrair_texto_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    texto = ""
    for page in pdf_reader.pages:
        texto += page.extract_text()
    return texto

def nova_campanha():
    st.session_state.resultado_final = ""
    st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}
    if "tema_input" in st.session_state: st.session_state["tema_input"] = ""

with st.sidebar:
    st.header("🔑 APIs")
    k_groq = st.text_input("Groq Key", type="password")
    k_gemini = st.text_input("Gemini Key", type="password")
    k_mistral = st.text_input("Mistral Key", type="password")
    st.divider()
    tema = st.text_area("🎯 Tema", key="tema_input")
    arquivo_briefing = st.file_uploader("📁 PDF", type=["pdf"])
    st.divider()
    dict_sel = {
        "pesquisador": st.checkbox("Pesquisador", True),
        "diretor": st.checkbox("Dir. Criativo", True),
        "copywriter": st.checkbox("Copywriter", True),
        "engenheiro": st.checkbox("Eng. Prompts", True),
        "social": st.checkbox("Social Media", True)
    }
    btn_iniciar = st.button("🚀 Iniciar Ciclo")
    st.button("🧹 Reset", on_click=nova_campanha)

st.title("🤖 Escritório Digital de Elite")

# Inicializa Status se não existir
if 'status' not in st.session_state:
    st.session_state.status = {k: "espera" for k in dict_sel.keys()}

# Renderiza o novo escritório
escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office_premium(st.session_state.status, dict_sel), height=450)

# Lógica de Execução (Utilize a lógica Multi-LLM que já criamos antes)
if btn_iniciar:
    if not k_groq or not tema:
        st.error("Chave Groq e Tema são necessários!")
    else:
        # (Lógica do btn_iniciar que já tínhamos: Roteamento de APIs, CrewAI, context_acumulado...)
        # Apenas certifique-se de atualizar o escritorio_container dentro do loop:
        # st.session_state.status[id_ag] = "trabalhando"
        # with escritorio_container: components.html(render_office_premium(...), height=450)
        
        # EXEMPLO SIMPLIFICADO DO LOOP PARA TESTE VISUAL:
        for id_ag in dict_sel:
            if dict_sel[id_ag]:
                st.session_state.status[id_ag] = "trabalhando"
                with escritorio_container:
                    components.html(render_office_premium(st.session_state.status, dict_sel), height=450)
                
                time.sleep(2) # Simulando trabalho para você ver o novo visual
                
                st.session_state.status[id_ag] = "concluido"
                with escritorio_container:
                    components.html(render_office_premium(st.session_state.status, dict_sel), height=450)

        st.success("Visual do escritório reformado com sucesso!")
