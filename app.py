import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
import time # Importante para as pausas

# Configuração da Página
st.set_page_config(page_title="Agência Marketing IA", page_icon="🤖", layout="wide")

# ==========================================
# FUNÇÃO PARA GERAR O PDF
# ==========================================
def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Estrategia - Agencia IA", ln=True, align='C')
    pdf.ln(10)
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
        html_cards += f"""<div class="baia-container" style="opacity: {opacidade};"><div class="name-tag"><span>{ag['emoji']} {ag['nome']}</span><span style="margin-left:8px;">{status_texto}</span></div><div class="mesa"><div class="monitor {glow_class}" style="background: {cor_monitor};"></div><div class="personagem {'animar-pulo' if status == 'trabalhando' else ''}">{ag['avatar']}</div></div><div class="chao-madeira"></div></div>"""
    return f"""<style>.office-grid {{display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px; background: #111; border-radius: 15px; justify-items: center;}}.baia-container {{ display: flex; flex-direction: column; align-items: center; transition: 0.3s; width: 150px; }}.name-tag {{background: #000; color: #fff; padding: 5px 12px; border-radius: 10px; font-size: 11px; font-family: sans-serif; margin-bottom: 5px; border: 1px solid #333; white-space: nowrap;}}.mesa {{position: relative; width: 120px; height: 60px; background: #bbb; border-radius: 5px; display: flex; justify-content: center;}}.monitor {{width: 50px; height: 30px; border: 3px solid #333; border-radius: 3px; position: absolute; top: 5px; transition: 0.5s;}}.personagem {{ font-size: 30px; position: absolute; bottom: -8px; z-index: 5; }}.chao-madeira {{ width: 140px; height: 8px; background: #4a2c2a; border-top: 2px solid #5d3a37; }}.trabalhando-anim {{ animation: pulse 1s infinite alternate; }}@keyframes pulse {{ from {{ box-shadow: 0 0 2px #00d4ff; }} to {{ box-shadow: 0 0 15px #00d4ff; }} }}.animar-pulo {{ animation: jump 0.5s infinite alternate; }}@keyframes jump {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-5px); }} }}</style><div class="office-grid">{html_cards}</div>"""

# ==========================================
# INICIALIZAÇÃO
# ==========================================
if 'resultado_final' not in st.session_state: st.session_state.resultado_final = ""
if 'status' not in st.session_state: st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}

with st.sidebar:
    st.header("⚙️ Configurações")
    groq_key = st.text_input("Groq API Key", type="password")
    tema = st.text_area("Tema da campanha", placeholder="Ex: Hamburgueria artesanal")
    st.subheader("👥 Selecione o Time")
    dict_selecionados = {
        "pesquisador": st.checkbox("Pesquisador", True),
        "diretor": st.checkbox("Dir. Criativo", True),
        "copywriter": st.checkbox("Copywriter", True),
        "engenheiro": st.checkbox("Eng. Prompts", True),
        "social": st.checkbox("Social Media", True)
    }
    btn_iniciar = st.button("🚀 Iniciar Ciclo de Trabalho")

st.title("🤖 Agência IA Corporativa")
escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_selecionados), height=400)

# ==========================================
# LOGICA PRINCIPAL COM PROTEÇÃO DE TAXA
# ==========================================
if btn_iniciar:
    if not groq_key or not tema:
        st.error("Preencha a chave e o tema!")
    else:
        st.session_state.resultado_final = ""
        for k in st.session_state.status: st.session_state.status[k] = "espera"
        
        # LLM com limites configurados
        llm = LLM(
            model="groq/llama-3.3-70b-versatile", 
            api_key=groq_key,
            max_tokens=2048 # Limita o tamanho da resposta para economizar TPM
        )
        
        agentes_jobs = [
            ("pesquisador", "Pesquisador", f"Analise o público e diferenciais para {tema}."),
            ("diretor", "Dir. Criativo", f"Crie um Slogan e conceito criativo para {tema}."),
            ("copywriter", "Copywriter", f"Escreva 3 legendas persuasivas para {tema}."),
            ("engenheiro", "Eng. Prompts", f"Dê sua opinião estratégica visual e gere 3 prompts técnicos em INGLÊS para {tema}."),
            ("social", "Social Media", f"Crie um cronograma de 5 dias integrando tudo para {tema}.")
        ]

        contexto_acumulado = ""
        try:
            for id_ag, nome_ag, task_desc in agentes_jobs:
                if dict_selecionados[id_ag]:
                    # Atualiza Status Visual
                    st.session_state.status[id_ag] = "trabalhando"
                    with escritorio_container:
                        components.html(render_office(st.session_state.status, dict_selecionados), height=400)

                    # Tarefa
                    tarefa_completa = f"{task_desc}\n\nContexto: {contexto_acumulado}"
                    ag = Agent(role=nome_ag, goal=task_desc, backstory="Especialista Sênior prático.", llm=llm)
                    ts = Task(description=tarefa_completa, expected_output="Entrega curta e direta.", agent=ag)
                    
                    # PROTEÇÃO 1: Definir max_rpm no Crew para evitar disparos rápidos
                    crew = Crew(agents=[ag], tasks=[ts], max_rpm=10) # No máximo 10 requisições por minuto
                    
                    res = crew.kickoff()
                    
                    # Salva
                    st.session_state.resultado_final += f"--- {nome_ag.upper()} ---\n{res.raw}\n\n"
                    contexto_acumulado += f"\n[{nome_ag}: {res.raw}]"
                    
                    # Conclui Agente
                    st.session_state.status[id_ag] = "concluido"
                    with escritorio_container:
                        components.html(render_office(st.session_state.status, dict_selecionados), height=400)
                    
                    # PROTEÇÃO 2: Pausa de segurança entre agentes (Cool-down)
                    # Isso evita que o segundo agente bata no limite de tokens do primeiro
                    with st.spinner(f"{nome_ag} terminou. Preparando próximo agente..."):
                        time.sleep(10) # 10 segundos de descanso

            st.success("🎯 Projeto finalizado!")

        except Exception as e:
            if "rate_limit" in str(e).lower():
                st.error("🚨 Limite da Groq atingido! Aguarde 60 segundos e tente novamente. Dica: Use menos agentes por vez ou aumente a pausa no código.")
            else:
                st.error(f"Erro inesperado: {e}")

# ==========================================
# DOWNLOADS
# ==========================================
if st.session_state.resultado_final:
    st.markdown("### 📄 Resultado Final")
    st.info(st.session_state.resultado_final)
    col1, col2 = st.columns(2)
    with col1: st.download_button("⬇️ TXT", st.session_state.resultado_final, "campanha.txt")
    with col2:
        try:
            pdf_data = gerar_pdf(st.session_state.resultado_final)
            st.download_button("⬇️ PDF", bytes(pdf_data), "campanha.pdf", "application/pdf")
        except: st.warning("Erro ao gerar PDF.")
