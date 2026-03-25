import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, Process, LLM

st.set_page_config(page_title="Agência de Marketing IA", page_icon="🤖", layout="wide")

# ==========================================
# CSS GLOBAL
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: #00f5d4;
        border: 1px solid #00f5d4;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 0.6rem 1.5rem;
    }
    .resultado-box {
        background: #0f3460;
        border-left: 4px solid #00f5d4;
        border-radius: 8px;
        padding: 1.5rem;
        color: #e0e0e0;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÃO DO ESCRITÓRIO
# ==========================================
def render_office(status_agentes):
    agentes_info = [
        {"nome": "Pesquisador", "emoji": "🔍"},
        {"nome": "Dir. Criativo", "emoji": "🎨"},
        {"nome": "Copywriter", "emoji": "✍️"},
        {"nome": "Eng. Prompts", "emoji": "🖼️"},
        {"nome": "Social Media", "emoji": "📱"},
    ]

    cards = ""
    for agente in agentes_info:
        status = status_agentes.get(agente["nome"], "espera")

        if status == "trabalhando":
            cor = "#00f5d4"
            texto = "⚙️ Trabalhando..."
            anim = "animation: pulse 1s infinite;"
        elif status == "concluido":
            cor = "#06d6a0"
            texto = "✅ Concluído"
            anim = ""
        else:
            cor = "#555"
            texto = "💤 Aguardando"
            anim = ""

        cards += f"""
        <div style="border:2px solid {cor}; padding:15px; border-radius:12px; text-align:center; {anim}">
            <div style="font-size:30px;">{agente['emoji']}</div>
            <div style="color:white;font-weight:bold;">{agente['nome']}</div>
            <div style="color:{cor}; font-size:12px;">{texto}</div>
        </div>
        """

    return f"""
    <style>
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0px #00f5d4; }}
        50% {{ box-shadow: 0 0 20px #00f5d4; }}
        100% {{ box-shadow: 0 0 0px #00f5d4; }}
    }}
    </style>
    <div style="display:flex; gap:10px; flex-wrap:wrap; justify-content:center;">
        {cards}
    </div>
    """

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    groq_api_key = st.text_input("🔑 API Key", type="password")
    tema = st.text_area("Tema da campanha")
    usar_pesquisador = st.checkbox("Pesquisador", True)
    usar_diretor = st.checkbox("Diretor Criativo", True)
    usar_copywriter = st.checkbox("Copywriter", True)
    usar_engenheiro = st.checkbox("Eng. Prompts", True)
    usar_social = st.checkbox("Social Media", True)

# ==========================================
# HEADER
# ==========================================
st.title("🤖 Agência de Marketing IA")

# ==========================================
# ESCRITÓRIO
# ==========================================
escritorio = st.empty()

status_inicial = {
    "Pesquisador": "espera",
    "Dir. Criativo": "espera",
    "Copywriter": "espera",
    "Eng. Prompts": "espera",
    "Social Media": "espera",
}

with escritorio:
    components.html(render_office(status_inicial), height=350)

# ==========================================
# BOTÃO
# ==========================================
if st.button("🚀 Iniciar Agência"):

    if not groq_api_key or not tema:
        st.error("Preencha os campos")
        st.stop()

    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.7
    )

    mapa_status = status_inicial.copy()
    concluidos = []
    resultado_final = ""

    def atualizar(nome):
        for k in mapa_status:
            if k == nome:
                mapa_status[k] = "trabalhando"
            elif k in concluidos:
                mapa_status[k] = "concluido"
            else:
                mapa_status[k] = "espera"

        with escritorio:
            components.html(render_office(mapa_status), height=350)

    # -------------------------
    # Pesquisador
    # -------------------------
    if usar_pesquisador:
        atualizar("Pesquisador")
        agente = Agent(role="Pesquisador", goal=tema, backstory="Analista", llm=llm)
        task = Task(
        description=f"Pesquise sobre {tema}",
        expected_output="Resumo com insights relevantes",
        agent=agente
        )
        r = Crew([agente], [task]).kickoff()
        resultado_final += f"\n\n### 🔍 Pesquisa\n{r}"
        concluidos.append("Pesquisador")

    # -------------------------
    # Diretor Criativo
    # -------------------------
    if usar_diretor:
        atualizar("Dir. Criativo")
        agente = Agent(role="Diretor Criativo", goal="Criar conceito", backstory="Criativo", llm=llm)
        task = Task(
        description=f"Crie conceito criativo para {tema}",
        expected_output="Slogan, tom de voz e direção visual",
        agent=agente
        )
        r = Crew([agente], [task]).kickoff()
        resultado_final += f"\n\n### 🎨 Conceito\n{r}"
        concluidos.append("Dir. Criativo")

    # -------------------------
    # Copywriter
    # -------------------------
    if usar_copywriter:
        atualizar("Copywriter")
        agente = Agent(role="Copywriter", goal="Criar textos", backstory="Copy", llm=llm)
        task = Task(
        description="Crie 3 legendas para Instagram",
        expected_output="3 textos com CTA e hashtags",
        agent=agente
        )
        r = Crew([agente], [task]).kickoff()
        resultado_final += f"\n\n### ✍️ Copy\n{r}"
        concluidos.append("Copywriter")

    # -------------------------
    # Engenheiro de Prompts
    # -------------------------
    if usar_engenheiro:
        atualizar("Eng. Prompts")
        agente = Agent(role="Prompt Engineer", goal="Criar prompts", backstory="IA", llm=llm)
        task = Task(
        description="Crie prompts para imagens",
        expected_output="3 prompts detalhados em inglês",
        agent=agente
        )
        r = Crew([agente], [task]).kickoff()
        resultado_final += f"\n\n### 🖼️ Prompts\n{r}"
        concluidos.append("Eng. Prompts")

    # -------------------------
    # Social Media
    # -------------------------
    if usar_social:
        atualizar("Social Media")
        agente = Agent(role="Social Media", goal="Criar cronograma", backstory="Estrategista", llm=llm)
        task = Task(
        description="Organize cronograma de posts",
        expected_output="Plano organizado de conteúdo",
        agent=agente
        )
        r = Crew([agente], [task]).kickoff()
        resultado_final += f"\n\n### 📱 Social\n{r}"
        concluidos.append("Social Media")

    # Final
    for k in mapa_status:
        mapa_status[k] = "concluido"

    with escritorio:
        components.html(render_office(mapa_status), height=350)

    st.success("✅ Campanha concluída!")
    st.markdown(f'<div class="resultado-box">{resultado_final}</div>', unsafe_allow_html=True)

    st.download_button(
        label="⬇️ Baixar resultado",
        data=resultado_final,
        file_name="campanha.txt"
    )
