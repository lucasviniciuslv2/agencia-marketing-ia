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
    # Definição dos 6 agentes baseada na sua foto
    agentes = [
        {"id": "Pesquisador", "nome": "Pedro Pesquisa", "emoji": "🔍", "avatar": "👨‍💻"},
        {"id": "Dir. Criativo", "nome": "Diana Didática", "emoji": "📚", "avatar": "👩‍💻"},
        {"id": "Estrategista", "nome": "Estela Estratégia", "emoji": "💼", "avatar": "👩‍💼"},
        {"id": "Eng. Prompts", "nome": "Lucas Landing", "emoji": "🌐", "avatar": "👨‍🚀"},
        {"id": "Social Media", "nome": "Marcos Material", "emoji": "📦", "avatar": "👨‍🎨"},
        {"id": "Revisor", "nome": "Renata Revisão", "emoji": "✅", "avatar": "👩‍🔬"},
    ]

    html_cards = ""
    for ag in agentes:  # Corrigido para 'in'
        status = status_agentes.get(ag["id"], "espera")
        
        # Lógica de estilo por status
        glow_class = ""
        opacidade = "0.5"
        cor_monitor = "#1e1e1e" # Escuro
        
        if status == "trabalhando":
            glow_class = "trabalhando-anim"
            opacidade = "1"
            cor_monitor = "#00d4ff" # Azul brilhante
        elif status == "concluido":
            opacidade = "1"
            cor_monitor = "#06d6a0" # Verde

        html_cards += f"""
        <div class="baia-container" style="opacity: {opacidade};">
            <!-- Placa de Nome Estilo Foto -->
            <div class="name-tag">
                <span class="emoji-status">{ag['emoji']}</span>
                <span class="nome-texto">{ag['nome']}</span>
                <div class="dot {status}"></div>
            </div>
            
            <!-- Mesa e Computador -->
            <div class="mesa">
                <div class="monitor-suporte"></div>
                <div class="monitor {glow_class}" style="background: {cor_monitor};">
                    <div class="tela-reflexo"></div>
                </div>
                <div class="teclado"></div>
                <div class="personagem {'animar-pulo' if status == 'trabalhando' else ''}">{ag['avatar']}</div>
            </div>
            <div class="chao-madeira"></div>
        </div>
        """

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@600&display=swap');
        
        body {{ background-color: #0e1117; margin: 0; padding: 0; }}
        
        .office-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px 10px;
            padding: 20px;
            background: #1a1c24;
            border-radius: 15px;
            justify-items: center;
        }}

        .baia-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: all 0.3s ease;
        }}

        .name-tag {{
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid #444;
            margin-bottom: 8px;
        }}

        .dot {{ height: 8px; width: 8px; border-radius: 50%; }}
        .espera {{ background: #555; }}
        .trabalhando {{ background: #00f5d4; box-shadow: 0 0 10px #00f5d4; }}
        .concluido {{ background: #06d6a0; }}

        .mesa {{
            position: relative;
            width: 140px;
            height: 80px;
            background: #d1d1d1;
            border-radius: 4px 4px 0 0;
            display: flex;
            justify-content: center;
        }}

        .monitor {{
            width: 70px;
            height: 40px;
            border: 3px solid #333;
            border-radius: 4px;
            position: absolute;
            top: 8px;
        }}

        .monitor-suporte {{ width: 15px; height: 8px; background: #333; position: absolute; top: 48px; }}
        .teclado {{ width: 40px; height: 4px; background: #999; position: absolute; top: 62px; border-radius: 2px; }}

        .personagem {{
            font-size: 35px;
            position: absolute;
            bottom: -10px;
            z-index: 5;
        }}

        .chao-madeira {{
            width: 170px;
            height: 12px;
            background: linear-gradient(to bottom, #5d3a37, #3e2723);
            border-top: 2px solid #795548;
        }}

        /* Animações */
        .trabalhando-anim {{ animation: monitor-pulse 1.5s infinite alternate; }}
        @keyframes monitor-pulse {{
            from {{ box-shadow: 0 0 2px #00d4ff; }}
            to {{ box-shadow: 0 0 15px #00d4ff; }}
        }}

        .animar-pulo {{ animation: typing 0.6s infinite alternate ease-in-out; }}
        @keyframes typing {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-5px); }}
        }}
    </style>

    <div class="office-grid">
        {html_cards}
    </div>
    """

# ==========================================
# LÓGICA DO APP
# ==========================================

st.title("🏢 Agência IA em Tempo Real")

with st.sidebar:
    st.header("⚙️ Configuração")
    groq_api_key = st.text_input("🔑 Groq API Key", type="password")
    tema_campanha = st.text_input("🎯 Tema da Campanha", placeholder="Ex: Café Orgânico")
    btn_iniciar = st.button("🚀 Iniciar Trabalho")

# Inicializa o estado dos agentes
if 'status_agentes' not in st.session_state:
    st.session_state.status_agentes = {
        "Pesquisador": "espera", "Dir. Criativo": "espera", "Estrategista": "espera",
        "Eng. Prompts": "espera", "Social Media": "espera", "Revisor": "espera"
    }

# Mostra o escritório
container_escritorio = st.empty()
with container_escritorio:
    components.html(render_office_virtual(st.session_state.status_agentes), height=420)

if btn_iniciar:
    if not groq_api_key or not tema_campanha:
        st.warning("Preencha a API Key e o Tema.")
    else:
        try:
            llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_api_key)

            # Fluxo de Trabalho (Exemplo de 3 passos para não demorar)
            workflow = [
                ("Pesquisador", "Pedro Pesquisa", f"Pesquise tendências para {tema_campanha}"),
                ("Dir. Criativo", "Diana Didática", f"Crie um slogan para {tema_campanha}"),
                ("Social Media", "Marcos Material", f"Crie um post de Instagram para {tema_campanha}")
            ]

            resultados = []

            for id_ag, nome_ag, tarefa_txt in workflow:
                # 1. Agente começa a trabalhar
                st.session_state.status_agentes[id_ag] = "trabalhando"
                with container_escritorio:
                    components.html(render_office_virtual(st.session_state.status_agentes), height=420)

                # 2. Execução da IA
                agente = Agent(role=nome_ag, goal=tarefa_txt, backstory="Expert", llm=llm)
                tarefa = Task(description=tarefa_txt, expected_output="Um parágrafo curto.", agent=agente)
                
                # CORREÇÃO: Argumentos nomeados tasks= e agents=
                crew = Crew(agents=[agente], tasks=[tarefa])
                res = crew.kickoff()
                
                # 3. Agente termina
                st.session_state.status_agentes[id_ag] = "concluido"
                resultados.append(f"**{nome_ag}**: {res.raw}")
                
                with container_escritorio:
                    components.html(render_office_virtual(st.session_state.status_agentes), height=420)
                
                time.sleep(1) # Pequena pausa para vermos o efeito

            st.success("🎯 Campanha finalizada!")
            for r in resultados:
                st.markdown(r)

        except Exception as e:
            st.error(f"Erro: {e}")
