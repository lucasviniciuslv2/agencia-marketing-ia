import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="Agência Marketing IA", page_icon="🤖", layout="wide")

# ==========================================
# FUNÇÃO PARA GERAR O PDF
# ==========================================
def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Estrategia - Agencia IA", ln=True, align='C')
    pdf.ln(10)
    
    # Conteúdo (Limpando markdown para evitar quebra no FPDF básico)
    pdf.set_font("Arial", size=11)
    texto_limpo = texto.replace('###', '').replace('**', '').replace('##', '').replace('-', '')
    line_text = texto_limpo.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=line_text)
    
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
        glow_class = ""; opacidade = "1" if foi_selecionado else "0.2"
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
    return f"""<style>.office-grid {{display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px; background: #111; border-radius: 15px; justify-items: center;}}.baia-container {{ display: flex; flex-direction: column; align-items: center; transition: 0.3s; width: 150px; }}.name-tag {{background: #000; color: #fff; padding: 5px 12px; border-radius: 10px; font-size: 11px; font-family: sans-serif; margin-bottom: 5px; border: 1px solid #333; white-space: nowrap;}}.mesa {{position: relative; width: 120px; height: 60px; background: #bbb; border-radius: 5px; display: flex; justify-content: center;}}.monitor {{width: 50px; height: 30px; border: 3px solid #333; border-radius: 3px; position: absolute; top: 5px; transition: 0.5s;}}.personagem {{ font-size: 30px; position: absolute; bottom: -8px; z-index: 5; }}.chao-madeira {{ width: 140px; height: 8px; background: #4a2c2a; border-top: 2px solid #5d3a37; }}.trabalhando-anim {{ animation: pulse 1s infinite alternate; }}@keyframes pulse {{ from {{ box-shadow: 0 0 2px #00d4ff; }} to {{ box-shadow: 0 0 15px #00d4ff; }} }}.animar-pulo {{ animation: jump 0.5s infinite alternate; }}@keyframes jump {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-5px); }} }}</style><div class="office-grid">{html_cards}</div>"""

# ==========================================
# INICIALIZAÇÃO DA MEMÓRIA
# ==========================================
if 'resultado_final' not in st.session_state:
    st.session_state.resultado_final = ""
if 'status' not in st.session_state:
    st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Configurações")
    groq_key = st.text_input("Groq API Key", type="password")
    tema = st.text_area("Tema da campanha", placeholder="Ex: Hamburgueria artesanal de luxo")
    st.subheader("👥 Selecione o Time")
    sel_pesq = st.checkbox("Pesquisador", True)
    sel_dir = st.checkbox("Dir. Criativo", True)
    sel_copy = st.checkbox("Copywriter", True)
    sel_eng = st.checkbox("Eng. Prompts", True)
    sel_soc = st.checkbox("Social Media", True)
    dict_selecionados = {"pesquisador": sel_pesq, "diretor": sel_dir, "copywriter": sel_copy, "engenheiro": sel_eng, "social": sel_soc}

st.title("🤖 Agência IA Corporativa")

# Renderiza Escritório
escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_selecionados), height=400)

# ==========================================
# EXECUÇÃO DO PROJETO
# ==========================================
if st.button("🚀 Iniciar Ciclo de Trabalho"):
    if not groq_key or not tema:
        st.error("Preencha a chave e o tema!")
    else:
        st.session_state.resultado_final = ""
        for k in st.session_state.status: st.session_state.status[k] = "espera"
        
        llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_key)
        
        # DEFINIÇÃO DAS TAREFAS (Jobs)
        agentes_jobs = [
            ("pesquisador", "Pesquisador", 
             f"Analise o público-alvo, tendências visuais e diferenciais para {tema}."),
            
            ("diretor", "Diretor Criativo", 
             f"Crie um Slogan marcante e defina o conceito criativo (identidade central) para {tema}."),
            
            ("copywriter", "Copywriter", 
             f"Crie 3 legendas de alta conversão para redes sociais para {tema}."),
            
            ("engenheiro", "Eng. Prompts", 
             f"""Dê sua opinião estratégica sobre o estilo visual ideal para {tema} (iluminação, cores, atmosfera). 
             Depois, gere 3 prompts técnicos em INGLÊS no estilo Midjourney/Flux (com tags técnicas) que reflitam essa visão."""),
            
            ("social", "Social Media", 
             f"Organize um cronograma de 5 dias integrando todas as entregas acima para {tema}.")
        ]

        contexto_acumulado = ""

        for id_ag, nome_ag, task_desc in agentes_jobs:
            if dict_selecionados[id_ag]:
                # 1. Update UI: Working
                st.session_state.status[id_ag] = "trabalhando"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_selecionados), height=400)

                # Contexto: O agente atual lê o que os anteriores fizeram
                tarefa_completa = f"{task_desc}\n\nConsidere o que já foi feito pela equipe: {contexto_acumulado}"

                ag = Agent(
                    role=nome_ag, 
                    goal=task_desc, 
                    backstory="Especialista Sênior focado em resultados executivos e técnicos de alta performance.", 
                    llm=llm
                )
                ts = Task(description=tarefa_completa, expected_output="Uma entrega profissional e prática.", agent=ag)
                
                res = Crew(agents=[ag], tasks=[ts]).kickoff()
                
                # Salva o progresso e o contexto
                st.session_state.resultado_final += f"--- {nome_ag.upper()} ---\n{res.raw}\n\n"
                contexto_acumulado += f"\n[{nome_ag} definiu: {res.raw}]"
                
                # 2. Update UI: Done
                st.session_state.status[id_ag] = "concluido"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_selecionados), height=400)
        
        st.success("🎯 Projeto finalizado com sucesso!")

# ==========================================
# RESULTADOS E DOWNLOADS
# ==========================================
if st.session_state.resultado_final:
    st.markdown("### 📄 Resultado da Agência")
    st.info(st.session_state.resultado_final)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(label="⬇️ Baixar TXT", data=st.session_state.resultado_final, file_name="campanha.txt", mime="text/plain")
    with col2:
        try:
            pdf_data = gerar_pdf(st.session_state.resultado_final)
            st.download_button(label="⬇️ Baixar PDF", data=bytes(pdf_data), file_name="campanha.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
