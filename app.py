import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF # Importação para o PDF

# Configuração da Página
st.set_page_config(page_title="Agência Marketing IA", page_icon="🤖", layout="wide")

# ==========================================
# FUNÇÃO PARA GERAR O PDF
# ==========================================
def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Título do Relatório
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Campanha - Agencia IA", ln=True, align='C')
    pdf.ln(10)
    
    # Corpo do texto
    pdf.set_font("Arial", size=12)
    
    # Limpeza simples para evitar erros de caracteres especiais no FPDF básico
    # (Em apps profissionais, carregaríamos uma fonte .ttf com suporte a UTF-8 completo)
    texto_limpo = texto.replace('###', '').replace('**', '').replace('##', '')
    
    # Escreve o texto no PDF (multi_cell lida com quebra de linha)
    pdf.multi_cell(0, 10, txt=texto_limpo.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S') # Retorna como string/bytes

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
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Configurações")
    groq_key = st.text_input("Groq API Key", type="password")
    tema = st.text_area("Tema da campanha")
    st.subheader("👥 Selecione o Time")
    sel_pesquisador = st.checkbox("Pesquisador", True)
    sel_diretor = st.checkbox("Dir. Criativo", True)
    sel_copy = st.checkbox("Copywriter", True)
    sel_eng = st.checkbox("Eng. Prompts", True)
    sel_social = st.checkbox("Social Media", True)
    dict_selecionados = {"pesquisador": sel_pesquisador, "diretor": sel_diretor, "copywriter": sel_copy, "engenheiro": sel_eng, "social": sel_social}

st.title("🤖 Agência Marketing IA")

if 'status' not in st.session_state:
    st.session_state.status = {k: "espera" for k in dict_selecionados.keys()}

escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_selecionados), height=350)

# ==========================================
# EXECUÇÃO
# ==========================================
if st.button("🚀 Iniciar Agência"):
    if not groq_key or not tema:
        st.error("Preencha a chave e o tema!")
        st.stop()

    llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_key)
    resultado_final = ""

    agentes_jobs = [
        ("pesquisador", "Pesquisador", f"Pesquise tendências para {tema}"),
        ("diretor", "Diretor Criativo", f"Crie slogan e conceito para {tema}"),
        ("copywriter", "Copywriter", f"Escreva 3 legendas para {tema}"),
        ("engenheiro", "Eng. Prompts", f"Prompts de imagem em inglês para {tema}"),
        ("social", "Social Media", f"Cronograma de posts para {tema}")
    ]

    for id_ag, nome_ag, task_desc in agentes_jobs:
        if dict_selecionados[id_ag]:
            st.session_state.status[id_ag] = "trabalhando"
            with escritorio_container:
                components.html(render_office(st.session_state.status, dict_selecionados), height=350)

            ag = Agent(role=nome_ag, goal=task_desc, backstory="Expert", llm=llm)
            ts = Task(description=task_desc, expected_output="Resultado curto.", agent=ag)
            crew = Crew(agents=[ag], tasks=[ts])
            res = crew.kickoff()
            
            resultado_final += f"--- {nome_ag.upper()} ---\n{res.raw}\n\n"

            st.session_state.status[id_ag] = "concluido"
            with escritorio_container:
                components.html(render_office(st.session_state.status, dict_selecionados), height=350)

    st.success("✅ Campanha concluída!")
    st.markdown(resultado_final)

    # COLUNAS PARA OS BOTÕES
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="⬇️ Baixar em TXT",
            data=resultado_final,
            file_name="campanha.txt",
            mime="text/plain"
        )
    
    with col2:
        # Gera os bytes do PDF
        pdf_bytes = gerar_pdf(resultado_final)
        st.download_button(
            label="⬇️ Baixar em PDF",
            data=pdf_bytes,
            file_name="campanha.pdf",
            mime="application/pdf"
        )
