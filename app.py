import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
import time

# Configuração da página
st.set_page_config(page_title="Agência Virtual IA", page_icon="🏢", layout="wide")

# ==========================================
# CSS E HTML PARA O ESCRITÓRIO (O LOOK DO VÍDEO)
# ==========================================
def render_office_virtual(status_agentes):
    agentes_config = [
        {"id": "Pesquisador", "nome": "Pedro Pesquisa", "emoji": "🔍", "avatar": "👨‍💻"},
        {"id": "Dir. Criativo", "nome": "Diana Didática", "emoji": "📚", "avatar": "👩‍💻"},
        {"id": "Estrategista", "nome": "Estela Estratégia", "emoji": "💼", "avatar": "👩‍💼"},
        {"id": "Eng. Prompts", "nome": "Lucas Landing", "emoji": "🌐", "avatar": "👨‍🚀"},
        {"id": "Social Media", "nome": "Marcos Material", "emoji": "📦", "avatar": "👨‍🎨"},
        {"id": "Revisor", "nome": "Renata Revisão", "emoji": "✅", "avatar": "👩‍🔬"},
    ]

    html_cards = ""
    for ag in agentes_config:
        status = status_agentes.get(ag["id"], "espera")
        
        # Lógica de estilo por status
        glow_class = ""
        opacidade = "0.5"
        cor_monitor = "#1e1e1e"
        
        if status == "trabalhando":
            glow_class = "trabalhando-anim"
            opacidade = "1"
            cor_monitor = "#00d4ff"
        elif status == "concluido":
            opacidade = "1"
            cor_monitor = "#06d6a0"

        html_cards += f"""
        <div class="baia-container" style="opacity: {opacidade};">
            <div class="name-tag">
                <span class="emoji-status">{ag['emoji']}</span>
                <span class="nome-texto">{ag['nome']}</span>
                <div class="dot {status}"></div>
            </div>
            <div class="mesa">
                <div class="monitor-suporte"></div>
                <div class="monitor {glow_class}" style="background: {cor_monitor};"></div>
                <div class="teclado"></div>
                <div class="personagem {'animar-pulo' if status == 'trabalhando' else ''}">{ag['avatar']}</div>
            </div>
            <div class="chao-madeira"></div>
        </div>
        """

    return f"""
    <style>
        body {{ background-color: #0e1117; margin: 0; }}
        .office-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px 10px;
            padding: 20px;
            background: #1a1c24;
            border-radius: 15px;
            justify-items: center;
        }}
        .baia-container {{ display: flex; flex-direction: column; align-items: center; transition: all 0.3s; }}
        .name-tag {{
            background: rgba(0,0,0,0.8); color: white; padding: 4px 12px; border-radius: 15px;
            font-family: sans-serif; font-size: 12px; display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
        }}
        .dot {{ height: 8px; width: 8px; border-radius: 50%; }}
        .espera {{ background: #555; }}
        .trabalhando {{ background: #00f5d4; box-shadow: 0 0 10px #00f5d4; }}
        .concluido {{ background: #06d6a0; }}
        .mesa {{ position: relative; width: 130px; height: 70px; background: #d1d1d1; border-radius: 4px; display: flex; justify-content: center; }}
        .monitor {{ width: 60px; height: 35px; border: 3px solid #333; border-radius: 4px; position: absolute; top: 8px; }}
        .monitor-suporte {{ width: 12px; height: 6px; background: #333; position: absolute; top: 43px; }}
        .teclado {{ width: 35px; height: 3px; background: #999; position: absolute; top: 55px; }}
        .personagem {{ font-size: 30px; position: absolute; bottom: -10px; z-index: 5; }}
        .chao-madeira {{ width: 160px; height: 10px; background: #5d3a37; border-top: 2px solid #795548; }}
        .trabalhando-anim {{ animation: monitor-pulse 1.5s infinite alternate; }}
        @keyframes monitor-pulse {{ from {{ box-shadow: 0 0 2px #00d4ff; }} to {{ box-shadow: 0 0 15px #00d4ff; }} }}
        .animar-pulo {{ animation: typing 0.6s infinite alternate; }}
        @keyframes typing {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-5px); }} }}
    </style>
    <div class="office-grid">{html_cards}</div>
    """

# ==========================================
# SIDEBAR (OPÇÕES DE QUEM PARTICIPA)
# ==========================================
with st.sidebar:
    st.header("⚙️ Configurações")
    groq_api_key = st.text_input("🔑 Groq API Key", type="password")
    tema_campanha = st.text_area("🎯 Tema da Campanha", placeholder="Ex: Café Orgânico para Geração Z")
    
    st.markdown("---")
    st.subheader("👥 Quem deve trabalhar?")
    check_pesquisador = st.checkbox("Pedro Pesquisa", value=True)
    check_diretor = st.checkbox("Diana Didática", value=True)
    check_estrategista = st.checkbox("Estela Estratégia", value=True)
    check_prompts = st.checkbox("Lucas Landing", value=True)
    check_social = st.checkbox("Marcos Material", value=True)
    check_revisor = st.checkbox("Renata Revisão", value=True)
    
    btn_iniciar = st.button("🚀 Iniciar Agência")

# ==========================================
# ESTADO INICIAL E RENDERIZAÇÃO
# ==========================================
if 'status_agentes' not in st.session_state:
    st.session_state.status_agentes = {
        "Pesquisador": "espera", "Dir. Criativo": "espera", "Estrategista": "espera",
        "Eng. Prompts": "espera", "Social Media": "espera", "Revisor": "espera"
    }

st.title("🤖 Escritório Virtual de Marketing")

container_escritorio = st.empty()
with container_escritorio:
    components.html(render_office_virtual(st.session_state.status_agentes), height=420)

# ==========================================
# LÓGICA DE EXECUÇÃO
# ==========================================
if btn_iniciar:
    if not groq_api_key or not tema_campanha:
        st.error("Por favor, preencha a chave de API e o tema da campanha.")
        st.stop()

    # Resetar status para início
    for k in st.session_state.status_agentes:
        st.session_state.status_agentes[k] = "espera"

    llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_api_key)
    
    # Montar lista de quem vai trabalhar baseada nos checkboxes
    workflow = []
    if check_pesquisador: workflow.append(("Pesquisador", "Pedro Pesquisa", f"Analise tendências de mercado para {tema_campanha}"))
    if check_diretor: workflow.append(("Dir. Criativo", "Diana Didática", f"Crie um conceito criativo e slogan para {tema_campanha}"))
    if check_estrategista: workflow.append(("Estrategista", "Estela Estratégia", f"Crie a estratégia de funil de vendas para {tema_campanha}"))
    if check_prompts: workflow.append(("Eng. Prompts", "Lucas Landing", f"Crie prompts de imagem para {tema_campanha}"))
    if check_social: workflow.append(("Social Media", "Marcos Material", f"Crie 3 posts de redes sociais para {tema_campanha}"))
    if check_revisor: workflow.append(("Revisor", "Renata Revisão", "Revise todos os textos anteriores buscando erros gramaticais e tom de voz."))

    if not workflow:
        st.warning("Selecione pelo menos um agente!")
        st.stop()

    resultado_final = ""

    for id_ag, nome_ag, tarefa_txt in workflow:
        # Atualiza visual para TRABALHANDO
        st.session_state.status_agentes[id_ag] = "trabalhando"
        with container_escritorio:
            components.html(render_office_virtual(st.session_state.status_agentes), height=420)

        # Executa CrewAI
        agente = Agent(role=nome_ag, goal=tarefa_txt, backstory="Especialista Sênior", llm=llm)
        tarefa = Task(description=tarefa_txt, expected_output="Um relatório conciso.", agent=agente)
        crew = Crew(agents=[agente], tasks=[tarefa])
        
        try:
            resposta = crew.kickoff()
            resultado_final += f"### {nome_ag}\n{resposta.raw}\n\n---\n"
            
            # Atualiza visual para CONCLUÍDO
            st.session_state.status_agentes[id_ag] = "concluido"
            with container_escritorio:
                components.html(render_office_virtual(st.session_state.status_agentes), height=420)
        except Exception as e:
            st.error(f"Erro com {nome_ag}: {e}")
            break

    st.success("✅ Equipe finalizou o projeto!")
    st.markdown(resultado_final)
