import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM

st.set_page_config(page_title="Agência Virtual IA", page_icon="🏢", layout="wide")

# ==========================================
# CSS PARA O ESTILO DO ESCRITÓRIO
# ==========================================
def render_office_virtual(status_agentes):
    # Configuração dos Agentes baseada na sua foto
    agentes = [
        {"id": "Pesquisador", "nome": "Pedro Pesquisa", "emoji": "🔍", "avatar": "👨‍💻"},
        {"id": "Dir. Criativo", "nome": "Diana Didática", "emoji": "📚", "avatar": "👩‍💻"},
        {"id": "Copywriter", "nome": "Estela Estratégia", "emoji": "💼", "avatar": "👩‍💼"},
        {"id": "Eng. Prompts", "nome": "Lucas Landing", "emoji": "🌐", "avatar": "👨‍🚀"},
        {"id": "Social Media", "nome": "Marcos Material", "emoji": "📦", "avatar": "👨‍🎨"},
        {"id": "Revisor", "nome": "Renata Revisão", "emoji": "✅", "avatar": "👩‍🔬"},
    ]

    html_cards = ""
    for ag em agentes:
        status = status_agentes.get(ag["id"], "espera")
        
        # Lógica de cores e animação
        glow_class = ""
        status_label = "Dormindo..."
        opacidade = "0.4"
        cor_monitor = "#1e1e1e" # Desligado
        
        if status == "trabalhando":
            glow_class = "trabalhando-anim"
            status_label = "Digitando..."
            opacidade = "1"
            cor_monitor = "#00d4ff" # Ligado/Brilhando
        elif status == "concluido":
            status_label = "Tarefa Pronta!"
            opacidade = "1"
            cor_monitor = "#00ff88" # Verde Sucesso

        html_cards += f"""
        <div class="baia-container" style="opacity: {opacidade};">
            <!-- Placa de Nome -->
            <div class="name-tag">
                <span class="emoji-status">{ag['emoji']}</span>
                <span class="nome-texto">{ag['nome']}</span>
                <span class="dot {status}"></span>
            </div>
            
            <!-- Mesa e Computador -->
            <div class="mesa">
                <div class="monitor-suporte"></div>
                <div class="monitor {glow_class}" style="background: {cor_monitor};">
                    <div class="tela-reflexo"></div>
                </div>
                <div class="teclado"></div>
                <div class="personagem">{ag['avatar']}</div>
            </div>
            <div class="chao-madeira"></div>
        </div>
        """

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@700&display=swap');
        
        body {{ background-color: #0a0a23; margin: 0; padding: 0; }}
        
        .office-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 40px 20px;
            padding: 20px;
            background: #101030;
            border-radius: 10px;
            border: 4px solid #1e1e4e;
        }}

        .baia-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: all 0.5s ease;
        }}

        /* Placa de Nome */
        .name-tag {{
            background: #000;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-family: 'Courier Prime', monospace;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            border: 1px solid #444;
            margin-bottom: 10px;
            z-index: 10;
        }}

        .dot {{ height: 10px; width: 10px; border-radius: 50%; display: inline-block; }}
        .espera {{ background: #555; }}
        .trabalhando {{ background: #00f5d4; box-shadow: 0 0 10px #00f5d4; }}
        .concluido {{ background: #06d6a0; }}

        /* O Computador */
        .mesa {{
            position: relative;
            width: 160px;
            height: 100px;
            background: #e0e0e0;
            border-radius: 5px 5px 0 0;
            display: flex;
            justify-content: center;
        }}

        .monitor {{
            width: 80px;
            height: 50px;
            border: 4px solid #333;
            border-radius: 5px;
            position: absolute;
            top: 10px;
            overflow: hidden;
        }}

        .monitor-suporte {{
            width: 20px;
            height: 10px;
            background: #333;
            position: absolute;
            top: 60px;
        }}

        .teclado {{
            width: 50px;
            height: 5px;
            background: #999;
            position: absolute;
            top: 75px;
            border-radius: 2px;
        }}

        .personagem {{
            font-size: 40px;
            position: absolute;
            bottom: -15px;
            z-index: 5;
        }}

        .chao-madeira {{
            width: 200px;
            height: 15px;
            background: linear-gradient(to bottom, #4a2c2a, #301a19);
            border-top: 2px solid #5d3a37;
        }}

        /* Animação de Trabalho */
        .trabalhando-anim {{
            animation: monitor-glow 1s infinite alternate;
        }}

        @keyframes monitor-glow {{
            from {{ box-shadow: 0 0 5px #00d4ff; }}
            to {{ box-shadow: 0 0 25px #00d4ff; }}
        }}

        .personagem {{
            animation: typing 0.5s infinite alternate ease-in-out;
        }}
        @keyframes typing {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-3px); }}
        }}
    </style>

    <div class="office-grid">
        {html_cards}
    </div>
    """

# ==========================================
# CÓDIGO DO STREAMLIT (LÓGICA)
# ==========================================

st.title("🏢 Meu Escritório de IA")

# Barra Lateral
with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("Groq API Key", type="password")
    tema = st.text_input("Tema do Projeto")
    botao_start = st.button("🚀 Colocar Equipe para Trabalhar")

# Estado inicial dos agentes
if 'status' not in st.session_state:
    st.session_state.status = {
        "Pesquisador": "espera", "Dir. Criativo": "espera", "Copywriter": "espera",
        "Eng. Prompts": "espera", "Social Media": "espera", "Revisor": "espera"
    }

# Renderiza o escritório
escritorio_placeholder = st.empty()
with escritorio_placeholder:
    components.html(render_office_virtual(st.session_state.status), height=450)

if botao_start:
    if not api_key or not tema:
        st.error("Preencha a chave e o tema!")
    else:
        llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=api_key)
        
        # Lista de agentes para iterar (exemplo simplificado)
        lista_trabalho = [
            ("Pesquisador", "Pedro Pesquisa", "Pesquise sobre o tema"),
            ("Dir. Criativo", "Diana Didática", "Crie um conceito"),
            ("Copywriter", "Estela Estratégia", "Escreva as legendas")
        ]

        for id_agente, nome, tarefa_texto in lista_trabalho:
            # 1. Atualiza para trabalhando
            st.session_state.status[id_agente] = "trabalhando"
            with escritorio_placeholder:
                components.html(render_office_virtual(st.session_state.status), height=450)
            
            # 2. Executa a CrewAI
            agente = Agent(role=nome, goal=tarefa_texto, backstory="Expert", llm=llm)
            tarefa = Task(description=tarefa_texto, expected_output="Resultado curto", agent=agente)
            crew = Crew(agents=[agente], tasks=[tarefa])
            resultado = crew.kickoff()
            
            # 3. Finaliza agente
            st.session_state.status[id_agente] = "concluido"
            st.write(f"**{nome} entrega:** {resultado.raw}")

        with escritorio_placeholder:
            components.html(render_office_virtual(st.session_state.status), height=450)
        st.success("Trabalho concluído!")
