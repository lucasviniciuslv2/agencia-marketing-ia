import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, Process, LLM
import time

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
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #00f5d4;
        color: #1a1a2e;
    }
    .resultado-box {
        background: #0f3460;
        border-left: 4px solid #00f5d4;
        border-radius: 8px;
        padding: 1.5rem;
        color: #e0e0e0;
        white-space: pre-wrap;
        font-size: 0.95rem;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÃO DO ESCRITÓRIO ANIMADO
# ==========================================
def render_office(status_agentes):
    agentes_info = [
        {"nome": "Pesquisador", "emoji": "🔍", "cargo": "Pesquisa de Mercado"},
        {"nome": "Dir. Criativo", "emoji": "🎨", "cargo": "Direção Criativa"},
        {"nome": "Copywriter", "emoji": "✍️", "cargo": "Redação"},
        {"nome": "Eng. Prompts", "emoji": "🖼️", "cargo": "Prompts Visuais"},
        {"nome": "Social Media", "emoji": "📱", "cargo": "Estratégia"},
    ]

    cards_html = ""
    for i, agente in enumerate(agentes_info):
        status = status_agentes.get(agente["nome"], "espera")
        if status == "trabalhando":
            cor_borda = "#00f5d4"
            cor_status = "#00f5d4"
            texto_status = "⚙️ Trabalhando..."
            animacao = "animation: pulsar 1s infinite;"
            bg = "background: rgba(0,245,212,0.08);"
        elif status == "concluido":
            cor_borda = "#06d6a0"
            cor_status = "#06d6a0"
            texto_status = "✅ Concluído"
            animacao = ""
            bg = "background: rgba(6,214,160,0.08);"
        else:
            cor_borda = "#2a2a4a"
            cor_status = "#888"
            texto_status = "💤 Aguardando"
            animacao = ""
            bg = "background: rgba(255,255,255,0.03);"

        cards_html += f"""
        <div style="
            border: 2px solid {cor_borda};
            border-radius: 16px;
            padding: 1.2rem;
            text-align: center;
            {bg}
            {animacao}
            transition: all 0.5s ease;
            min-width: 150px;
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">{agente['emoji']}</div>
            <div style="
                font-size: 1.5rem; margin-bottom: 0.5rem;
            ">🧑‍💻</div>
            <div style="
                color: white;
                font-weight: 700;
                font-size: 0.95rem;
                margin-bottom: 0.2rem;
            ">{agente['nome']}</div>
            <div style="
                color: #aaa;
                font-size: 0.75rem;
                margin-bottom: 0.5rem;
            ">{agente['cargo']}</div>
            <div style="
                color: {cor_status};
                font-size: 0.8rem;
                font-weight: 600;
            ">{texto_status}</div>
        </div>
        """

    html = f"""
    <style>
        @keyframes pulsar {{
            0%   {{ box-shadow: 0 0 0px #00f5d4; }}
            50%  {{ box-shadow: 0 0 18px #00f5d4; }}
            100% {{ box-shadow: 0 0 0px #00f5d4; }}
        }}
    </style>
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid #2a2a4a;
        margin-bottom: 1.5rem;
    ">
        <div style="
            text-align: center;
            color: #00f5d4;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            letter-spacing: 2px;
            text-transform: uppercase;
        ">🏢 Escritório da Agência</div>
        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
        ">
            {cards_html}
        </div>
    </div>
    """
    return html

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    groq_api_key = st.text_input("🔑 Sua chave da API Groq", type="password")
    st.markdown("---")
    st.markdown("## 🎯 Tema da Campanha")
    tema = st.text_area(
        "Descreva o tema:",
        placeholder="Ex: Lançamento de curso de fotografia para iniciantes...",
        height=120
    )
    st.markdown("---")
    st.markdown("## 👥 Agentes Ativos")
    usar_pesquisador = st.checkbox("🔍 Pesquisador de Mercado", value=True)
    usar_diretor     = st.checkbox("🎨 Diretor Criativo", value=True)
    usar_copywriter  = st.checkbox("✍️ Copywriter", value=True)
    usar_engenheiro  = st.checkbox("🖼️ Engenheiro de Prompts", value=True)
    usar_social      = st.checkbox("📱 Social Media", value=True)

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 1rem 0;">
    <h1 style="color:#00f5d4; font-size:2.2rem; margin-bottom:0.3rem;">🤖 Agência de Marketing com IA</h1>
    <p style="color:#aaa; font-size:1rem;">Configure o tema, escolha os agentes e acione sua equipe!</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# ESCRITÓRIO — estado inicial
# ==========================================
status_inicial = {
    "Pesquisador": "espera",
    "Dir. Criativo": "espera",
    "Copywriter": "espera",
    "Eng. Prompts": "espera",
    "Social Media": "espera",
}
escritorio = st.empty()
with escritorio:
    components.html(render_office(status_inicial), height=520)

# ==========================================
# BOTÃO PRINCIPAL
# ==========================================
iniciar = st.button("🚀 Iniciar Agência", use_container_width=True)

if iniciar:
    if not groq_api_key:
        st.error("⚠️ Insira sua chave da API Groq na barra lateral!")
        st.stop()
    if not tema.strip():
        st.error("⚠️ Descreva o tema da campanha na barra lateral!")
        st.stop()

    meu_llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.7,
        max_tokens=1024,
        max_retries=2
    )

    agentes = []
    tarefas = []
    mapa_status = {
        "Pesquisador": "espera",
        "Dir. Criativo": "espera",
        "Copywriter": "espera",
        "Eng. Prompts": "espera",
        "Social Media": "espera",
    }

   def atualizar_escritorio(agente_ativo, concluidos):
    for k in mapa_status:
        if k == agente_ativo:
            mapa_status[k] = "trabalhando"
        elif k in concluidos:
            mapa_status[k] = "concluido"
        else:
            mapa_status[k] = "espera"

    with escritorio:
        components.html(render_office(mapa_status), height=520)

    concluidos = []
    resultado_final = ""

    time.sleep(0.5)
    # --- Pesquisador ---
    if usar_pesquisador:
        atualizar_escritorio("Pesquisador", concluidos)
        pesquisador = Agent(
            role='Pesquisador de Mercado e Tendências',
            goal=f'Analisar o mercado atual para: {tema}',
            backstory='Analista obcecado por tendências e comportamento do consumidor.',
            verbose=False, llm=meu_llm
        )
        t1 = Task(
            description=f'Pesquise tendências para: {tema}. Entregue 3 parágrafos com insights.',
            expected_output='Resumo de mercado com principais insights.',
            agent=pesquisador
        )
        agentes.append(pesquisador)
        tarefas.append(t1)
        crew_parcial = Crew(agents=[pesquisador], tasks=[t1], process=Process.sequential, max_rpm=20)
        r = crew_parcial.kickoff()
        resultado_final += f"\n\n### 🔍 Pesquisa de Mercado\n{r}"
        concluidos.append("Pesquisador")

    # --- Diretor Criativo ---
    if usar_diretor:
        atualizar_escritorio("Dir. Criativo", concluidos)
        diretor = Agent(
            role='Diretor Criativo Sênior',
            goal='Criar o conceito central da campanha com base na pesquisa',
            backstory='Premiado diretor que define tom de voz e estética visual.',
            verbose=False, llm=meu_llm
        )
        t2 = Task(
            description=f'Com base na pesquisa sobre "{tema}", crie o conceito: Slogan, Tom de Voz e Estética Visual.',
            expected_output='Diretrizes criativas da campanha.',
            agent=diretor
        )
        agentes.append(diretor)
        tarefas.append(t2)
        crew_parcial = Crew(agents=[diretor], tasks=[t2], process=Process.sequential, max_rpm=20)
        r = crew_parcial.kickoff()
        resultado_final += f"\n\n### 🎨 Conceito Criativo\n{r}"
        concluidos.append("Dir. Criativo")

    # --- Copywriter ---
    if usar_copywriter:
        atualizar_escritorio("Copywriter", concluidos)
        copywriter = Agent(
            role='Copywriter de Conversão',
            goal='Escrever textos persuasivos seguindo o conceito da campanha',
            backstory='Mestre das palavras e especialista em gatilhos mentais.',
            verbose=False, llm=meu_llm
        )
        t3 = Task(
            description='Escreva 3 legendas para Instagram: topo, meio e fundo de funil.',
            expected_output='Três textos completos com emojis e hashtags.',
            agent=copywriter
        )
        agentes.append(copywriter)
        tarefas.append(t3)
        crew_parcial = Crew(agents=[copywriter], tasks=[t3], process=Process.sequential, max_rpm=20)
        r = crew_parcial.kickoff()
        resultado_final += f"\n\n### ✍️ Textos para Instagram\n{r}"
        concluidos.append("Copywriter")

    # --- Engenheiro de Prompts ---
    if usar_engenheiro:
        atualizar_escritorio("Eng. Prompts", concluidos)
        engenheiro = Agent(
            role='Engenheiro de Prompts Visuais',
            goal='Criar prompts detalhados para IA geradora de imagens',
            backstory='Especialista em Midjourney e geração de imagens com IA.',
            verbose=False, llm=meu_llm
        )
        t4 = Task(
            description='Escreva 3 prompts em inglês ultra-detalhados para gerar as imagens dos posts.',
            expected_output='Três prompts descrevendo sujeito, cenário e estilo.',
            agent=engenheiro
        )
        agentes.append(engenheiro)
        tarefas.append(t4)
        crew_parcial = Crew(agents=[engenheiro], tasks=[t4], process=Process.sequential, max_rpm=20)
        r = crew_parcial.kickoff()
        resultado_final += f"\n\n### 🖼️ Prompts Visuais\n{r}"
        concluidos.append("Eng. Prompts")

    # --- Social Media ---
    if usar_social:
        atualizar_escritorio("Social Media", concluidos)
        social = Agent(
            role='Estrategista de Social Media',
            goal='Organizar tudo em um cronograma pronto para uso',
            backstory='Expert em algoritmos e engajamento nas redes sociais.',
            verbose=False, llm=meu_llm
        )
        t5 = Task(
            description='Monte um documento final organizado com textos e prompts de cada post.',
            expected_output='Cronograma final pronto para o cliente.',
            agent=social
        )
        agentes.append(social)
        tarefas.append(t5)
        crew_parcial = Crew(agents=[social], tasks=[t5], process=Process.sequential, max_rpm=20)
        r = crew_parcial.kickoff()
        resultado_final += f"\n\n### 📱 Cronograma Final\n{r}"
        concluidos.append("Social Media")

    # Todos concluídos
    for k in mapa_status:
        mapa_status[k] = "concluido"
    with escritorio:components.html(render_office(mapa_status), height=520)

    st.success("✅ Campanha concluída com sucesso!")
    st.markdown("---")
    st.markdown("## 📋 Resultado Final da Agência")
    st.markdown(f'<div class="resultado-box">{resultado_final}</div>', unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Baixar Resultado",
        data=resultado_final,
        file_name="campanha.txt",
        mime="text/plain",
        use_container_width=True
    )
