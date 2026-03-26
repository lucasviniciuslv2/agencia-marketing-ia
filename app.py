import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="Agência Marketing IA", page_icon="🤖", layout="wide")

# ==========================================
# FUNÇÃO PARA GERAR O PDF (Ajustada para fpdf2)
# ==========================================
def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Campanha IA", ln=True, align='C')
    pdf.ln(10)
    
    # Conteúdo
    pdf.set_font("Arial", size=12)
    # Remove caracteres que o PDF básico não entende
    texto_limpo = texto.replace('###', '').replace('**', '').replace('##', '').replace('-', '')
    
    # Tratamento de codificação para evitar erros de acentuação
    line_text = texto_limpo.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=line_text)
    
    # Retorna os bytes do PDF
    return pdf.output()

# ==========================================
# MOTOR VISUAL DO ESCRITÓRIO
# ==========================================
def render_office(status_agentes, selecionados):
    agentes_config = [
        {"id": "pesquisador", "nome": "Pesquisador", "emoji": "🔍", "avatar": "👨‍💻"},
        {"id": "diretor", "nome": "Dir. Criativo", "emoji": "🎨", "avatar": "👩‍🎨"},
        {"id": "copywriter", "nome": "Copywriter", "emoji": "✍️", "avatar": "✍️"},
        {"id": "engenheiro", "nome": "Eng. Prompts", "emoji": "🖼️", "avatar": "👨‍🚀"},
        {"id": "social", "nome": "Social Media", "emoji": "📱", "avatar": "🤳"},
    ]
    html_cards = ""
    for ag in agentes_config:
        status = status_agentes.get(ag["id"], "espera")
        foi_selecionado = selecionados.get(ag["id"], False)
        glow_class = ""; opacidade = "1" if foi_selecionado else "0.15"
        cor_monitor = "#1e1e1e"; status_texto = "💤"
        if foi_selecionado:
            if status == "trabalhando":
                glow_class = "trabalhando-anim"; cor_monitor = "#00d4ff"; status_texto = "⚙️"
            elif status == "concluido":
                cor_monitor = "#06d6a0"; status_texto = "✅"
            else: status_texto = "⏳"
        html_cards += f"""
        <div class="baia-container" style="opacity: {opacidade};">
            <div class="name-tag"><span>{ag['emoji']} {ag['nome']}</span><span style="margin-left:8px;">{status_texto}</span></div>
            <div class="mesa"><div class="monitor {glow_class}" style="background: {cor_monitor};"></div><div class="personagem {'animar-pulo' if status == 'trabalhando' else ''}">{ag['avatar']}</div></div>
            <div class="chao-madeira"></div>
        </div>
        """
    return f"""<style>.office-grid {{display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px; background: #111; border-radius: 15px; justify-items: center;}}.baia-container {{ display: flex; flex-direction: column; align-items: center; transition: 0.3s; }}.name-tag {{background: #000; color: #fff; padding: 5px 12px; border-radius: 10px; font-size: 12px; font-family: sans-serif; margin-bottom: 5px; border: 1px solid #333;}}.mesa {{position: relative; width: 120px; height: 60px; background: #bbb; border-radius: 5px; display: flex; justify-content: center;}}.monitor {{width: 50px; height: 30px; border: 3px solid #333; border-radius: 3px; position: absolute; top: 5px; transition: 0.5s;}}.personagem {{ font-size: 30px; position: absolute; bottom: -8px; z-index: 5; }}.chao-madeira {{ width: 150px; height: 8px; background: #4a2c2a; border-top: 2px solid #5d3a37; }}.trabalhando-anim {{ animation: pulse 1s infinite alternate; }}@keyframes pulse {{ from {{ box-shadow: 0 0 2px #00d4ff; }} to {{ box-shadow: 0 0 15px #00d4ff; }} }}.animar-pulo {{ animation: jump 0.5s infinite alternate; }}@keyframes jump {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-5px); }} }}</style><div class="office-grid">{html_cards}</div>"""

# ==========================================
# INICIALIZAÇÃO DA MEMÓRIA (SESSION STATE)
# ==========================================
if 'resultado_final' not in st.session_state:
    st.session_state.resultado_final = ""
if 'status' not in st.session_state:
    st.session_state.status = {"pesquisador": "espera", "diretor": "espera", "copywriter": "espera", "engenheiro": "espera", "social": "espera"}

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Configurações")
    groq_key = st.text_input("Groq API Key", type="password")
    tema = st.text_area("Tema da campanha")
    st.subheader("👥 Selecione o Time")
    sel_pesq = st.checkbox("Pesquisador", True)
    sel_dir = st.checkbox("Dir. Criativo", True)
    sel_copy = st.checkbox("Copywriter", True)
    sel_eng = st.checkbox("Eng. Prompts", True)
    sel_soc = st.checkbox("Social Media", True)
    dict_selecionados = {"pesquisador": sel_pesq, "diretor": sel_dir, "copywriter": sel_copy, "engenheiro": sel_eng, "social": sel_soc}

st.title("🤖 Agência Marketing IA")

# Renderiza Escritório
escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_selecionados), height=350)

# ==========================================
# BOTÃO DE INICIAR
# ==========================================
if st.button("🚀 Iniciar Agência"):
    if not groq_key or not tema:
        st.error("Preencha a chave e o tema!")
    else:
        st.session_state.resultado_final = "" # Limpa resultado anterior
        llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_key)
        
        agentes_jobs = [
            ("pesquisador", "Pesquisador", f"Analise o mercado para {tema}"),
            ("diretor", "Diretor Criativo", f"Conceito e slogan para {tema}"),
            ("copywriter", "Copywriter", f"Legendas para {tema}"),
            ("engenheiro", "Eng. Prompts", f"Prompts IA em inglês para {tema}"),
            ("social", "Social Media", f"Cronograma para {tema}")
        ]

        for id_ag, nome_ag, task_desc in agentes_jobs:
            if dict_selecionados[id_ag]:
                st.session_state.status[id_ag] = "trabalhando"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_selecionados), height=350)

                ag = Agent(role=nome_ag, goal=task_desc, backstory="Expert", llm=llm)
                ts = Task(description=task_desc, expected_output="Resumo curto.", agent=ag)
                res = Crew(agents=[ag], tasks=[ts]).kickoff()
                
                st.session_state.resultado_final += f"--- {nome_ag.upper()} ---\n{res.raw}\n\n"
                st.session_state.status[id_ag] = "concluido"
                
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_selecionados), height=350)
        
        st.success("Trabalho concluído!")

# ==========================================
# EXIBIÇÃO DOS RESULTADOS E DOWNLOADS (FORA DO BOTÃO START)
# ==========================================
if st.session_state.resultado_final:
    st.markdown("### 📄 Relatório
