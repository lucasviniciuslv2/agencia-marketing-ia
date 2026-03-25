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
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÃO DO ESCRITÓRIO (UI)
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
        <div style="border:2px solid {cor}; padding:15px; border-radius:12px; text-align:center; {anim} min-width: 120px;">
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
    <div style="display:flex; gap:10px; flex-wrap:wrap; justify-content:center; padding: 20px; background: #16213e; border-radius: 15px;">
        {cards}
    </div>
    """

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    groq_api_key = st.text_input("🔑 Groq API Key", type="password")
    tema = st.text_area("Qual o tema/produto da campanha?", placeholder="Ex: Um novo café artesanal orgânico")
    
    st.markdown("---")
    st.markdown("### Agentes Ativos")
    usar_pesquisador = st.checkbox("Pesquisador", True)
    usar_diretor = st.checkbox("Diretor Criativo", True)
    usar_copywriter = st.checkbox("Copywriter", True)
    usar_engenheiro = st.checkbox("Eng. Prompts", True)
    usar_social = st.checkbox("Social Media", True)

# ==========================================
# HEADER
# ==========================================
st.title("🤖 Agência de Marketing IA")
st.markdown("Veja sua equipe de agentes trabalhando em tempo real.")

# ==========================================
# ESCRITÓRIO (AREA DE STATUS)
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
    components.html(render_office(status_inicial), height=250)

# ==========================================
# LÓGICA DE EXECUÇÃO
# ==========================================
if st.button("🚀 Iniciar Agência"):

    if not groq_api_key or not tema:
        st.error("Por favor, insira a API Key e o Tema da campanha.")
        st.stop()

    # Configuração do LLM (Groq)
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.7
    )

    mapa_status = status_inicial.copy()
    concluidos = []
    resultado_final = ""

    def atualizar_ui(nome_ativo):
        """Atualiza visualmente o status dos agentes no Streamlit"""
        for k in mapa_status:
            if k == nome_ativo:
                mapa_status[k] = "trabalhando"
            elif k in concluidos:
                mapa_status[k] = "concluido"
            else:
                mapa_status[k] = "espera"
        
        with escritorio:
            components.html(render_office(mapa_status), height=250)

    try:
        # -------------------------
        # 1. Pesquisador
        # -------------------------
        if usar_pesquisador:
            atualizar_ui("Pesquisador")
            agente = Agent(role="Pesquisador", goal=f"Pesquisar tendências para {tema}", backstory="Especialista em análise de mercado e tendências digitais.", llm=llm)
            task = Task(
                description=f"Faça uma pesquisa rápida sobre {tema}. Foque em público-alvo e diferenciais.",
                expected_output="Um resumo de 3 parágrafos sobre o mercado e público.",
                agent=agente
            )
            # CORREÇÃO: Argumentos nomeados e .raw no resultado
            crew = Crew(agents=[agente], tasks=[task], verbose=False)
            response = crew.kickoff()
            resultado_final += f"## 🔍 Resultado da Pesquisa\n{response.raw}\n\n---\n"
            concluidos.append("Pesquisador")

        # -------------------------
        # 2. Diretor Criativo
        # -------------------------
        if usar_diretor:
            atualizar_ui("Dir. Criativo")
            agente = Agent(role="Diretor Criativo", goal="Definir o conceito visual e tom de voz", backstory="Diretor de arte premiado com foco em branding.", llm=llm)
            task = Task(
                description=f"Com base no tema {tema}, crie um conceito criativo, um slogan e defina o tom de voz da campanha.",
                expected_output="Conceito criativo, Slogan e Tom de voz detalhado.",
                agent=agente
            )
            crew = Crew(agents=[agente], tasks=[task], verbose=False)
            response = crew.kickoff()
            resultado_final += f"## 🎨 Conceito Criativo\n{response.raw}\n\n---\n"
            concluidos.append("Dir. Criativo")

        # -------------------------
        # 3. Copywriter
        # -------------------------
        if usar_copywriter:
            atualizar_ui("Copywriter")
            agente = Agent(role="Copywriter", goal="Escrever legendas persuasivas", backstory="Especialista em copywriting focado em conversão e engajamento.", llm=llm)
            task = Task(
                description=f"Escreva 3 legendas para posts de Instagram sobre {tema} usando o conceito criado anteriormente.",
                expected_output="3 opções de legendas com emojis e hashtags.",
                agent=agente
            )
            crew = Crew(agents=[agente], tasks=[task], verbose=False)
            response = crew.kickoff()
            resultado_final += f"## ✍️ Copywriting (Redação)\n{response.raw}\n\n---\n"
            concluidos.append("Copywriter")

        # -------------------------
        # 4. Engenheiro de Prompts
        # -------------------------
        if usar_engenheiro:
            atualizar_ui("Eng. Prompts")
            agente = Agent(role="Engenheiro de Prompts", goal="Criar comandos para geradores de imagem", backstory="Especialista em transformar conceitos em imagens via Midjourney/DALL-E.", llm=llm)
            task = Task(
                description=f"Crie 3 prompts detalhados em INGLÊS para gerar imagens realistas de propaganda para {tema}.",
                expected_output="3 prompts em inglês focados em qualidade fotorealista.",
                agent=agente
            )
            crew = Crew(agents=[agente], tasks=[task], verbose=False)
            response = crew.kickoff()
            resultado_final += f"## 🖼️ Prompts para Imagens (IA)\n{response.raw}\n\n---\n"
            concluidos.append("Eng. Prompts")

        # -------------------------
        # 5. Social Media
        # -------------------------
        if usar_social:
            atualizar_ui("Social Media")
            agente = Agent(role="Social Media", goal="Criar calendário de postagens", backstory="Estrategista de redes sociais focado em crescimento orgânico.", llm=llm)
            task = Task(
                description=f"Crie um plano de postagem de 5 dias para o lançamento de {tema}.",
                expected_output="Um cronograma simples de segunda a sexta com ideias de posts.",
                agent=agente
            )
            crew = Crew(agents=[agente], tasks=[task], verbose=False)
            response = crew.kickoff()
            resultado_final += f"## 📱 Cronograma Social Media\n{response.raw}\n\n"
            concluidos.append("Social Media")

        # Finalização da UI
        for k in mapa_status:
            mapa_status[k] = "concluido"
        with escritorio:
            components.html(render_office(mapa_status), height=250)

        st.success("✅ Campanha gerada com sucesso!")
        
        # Exibição do Resultado
        st.markdown(f'<div class="resultado-box">{resultado_final}</div>', unsafe_allow_html=True)

        # Botão de Download
        st.download_button(
            label="⬇️ Baixar Relatório Completo",
            data=resultado_final,
            file_name="campanha_marketing_ia.md",
            mime="text/markdown"
        )

    except Exception as e:
        st.error(f"Ocorreu um erro durante a execução: {str(e)}")
        st.info("Dica: Verifique se sua API Key da Groq é válida e se você tem saldo/limite disponível.")
