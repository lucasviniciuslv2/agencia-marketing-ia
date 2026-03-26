import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
import time
import urllib.parse 

# Tenta importar a ferramenta de busca da LangChain (mais estável)
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
except ImportError:
    search_tool = None

# Configuração da Página
st.set_page_config(page_title="Agência Marketing IA", page_icon="🤖", layout="wide")

# ==========================================
# FUNÇÕES DE APOIO
# ==========================================
def nova_campanha():
    st.session_state.resultado_final = ""
    st.session_state.prompt_gerado = ""
    st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}
    if "tema_input" in st.session_state:
        st.session_state["tema_input"] = ""

def gerar_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Estrategia - Agencia IA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    texto_limpo = texto.replace('###', '').replace('**', '').replace('##', '').replace('-', '')
    line_text = texto_limpo.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=line_text)
    return pdf.output()

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
if 'prompt_gerado' not in st.session_state: st.session_state.prompt_gerado = ""
if 'status' not in st.session_state: st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    groq_key = st.text_input("🔑 Groq API Key", type="password")
    tema = st.text_area("🎯 Tema da Campanha", placeholder="Ex: Hamburgueria", key="tema_input")
    st.subheader("👥 Time Ativo")
    dict_selecionados = {
        "pesquisador": st.checkbox("Pesquisador (Web Search)", True),
        "diretor": st.checkbox("Dir. Criativo", True),
        "copywriter": st.checkbox("Copywriter", True),
        "engenheiro": st.checkbox("Eng. Prompts (Image Gen)", True),
        "social": st.checkbox("Social Media", True)
    }
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1: btn_iniciar = st.button("🚀 Iniciar", use_container_width=True)
    with col_btn2: st.button("🧹 Resetar", on_click=nova_campanha, use_container_width=True)

st.title("🤖 Escritório Digital IA")
escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_selecionados), height=400)

# ==========================================
# LÓGICA DE EXECUÇÃO
# ==========================================
if btn_iniciar:
    if not groq_key or not tema:
        st.error("Preencha a chave e o tema!")
    else:
        st.session_state.resultado_final = ""
        st.session_state.prompt_gerado = ""
        for k in st.session_state.status: st.session_state.status[k] = "espera"
        
        llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_key)
        
        # Define as ferramentas do Pesquisador
        pesquisa_tools = [search_tool] if search_tool else []

        agentes_jobs = [
            ("pesquisador", "Pesquisador", f"PESQUISE NA WEB tendências atuais e público para {tema}.", pesquisa_tools),
            ("diretor", "Dir. Criativo", f"Crie slogan e conceito central para {tema}.", []),
            ("copywriter", "Copywriter", f"Escreva 3 legendas de Instagram para {tema}.", []),
            ("engenheiro", "Eng. Prompts", f"Dê sua visão estratégica e gere apenas UM prompt técnico final em INGLÊS para {tema}.", []),
            ("social", "Social Media", f"Monte o cronograma de 5 dias.", [])
        ]

        contexto_acumulado = ""
        status_log = st.status("🚀 Iniciando agência...", expanded=True)
        
        try:
            for id_ag, nome_ag, task_desc, ag_tools in agentes_jobs:
                if dict_selecionados[id_ag]:
                    status_log.update(label=f"⚙️ {nome_ag} está trabalhando...", state="running")
                    
                    st.session_state.status[id_ag] = "trabalhando"
                    with escritorio_container:
                        components.html(render_office(st.session_state.status, dict_selecionados), height=400)

                    tarefa_completa = f"{task_desc}\n\nContexto: {contexto_acumulado}"
                    
                    ag = Agent(role=nome_ag, goal=task_desc, backstory="Expert.", llm=llm, tools=ag_tools)
                    ts = Task(description=tarefa_completa, expected_output="Resultado profissional.", agent=ag)
                    
                    res = Crew(agents=[ag], tasks=[ts], max_rpm=3).kickoff()
                    
                    if id_ag == "engenheiro":
                        # Limpa o prompt para a imagem
                        clean_p = res.raw.split("Prompt:")[-1] if "Prompt:" in res.raw else res.raw
                        st.session_state.prompt_gerado = clean_p.strip()

                    st.session_state.resultado_final += f"### {nome_ag.upper()}\n{res.raw}\n\n---\n"
                    contexto_acumulado += f"\n[{nome_ag}: {res.raw}]"
                    
                    st.session_state.status[id_ag] = "concluido"
                    with escritorio_container:
                        components.html(render_office(st.session_state.status, dict_selecionados), height=400)
                    
                    time.sleep(5) # Delay maior para evitar Rate Limit na Groq

            status_log.update(label="🎯 Trabalho Finalizado!", state="complete", expanded=False)

        except Exception as e:
            status_log.update(label="❌ Erro na execução", state="error")
            st.error(f"Erro: {e}")

# ==========================================
# EXIBIÇÃO E IMAGEM
# ==========================================
if st.session_state.resultado_final:
    
    if st.session_state.prompt_gerado:
        st.markdown("### 🖼️ Conceito Visual Gerado")
        p_limpo = st.session_state.prompt_gerado.replace("\n", " ").replace('"', '').replace('`', '').strip()
        p_url = urllib.parse.quote(p_limpo)
        image_url = f"https://pollinations.ai/p/{p_url}?width=1024&height=1024&model=flux"
        st.image(image_url, caption="Arte conceitual gerada via Pollinations IA", use_container_width=True)

    st.markdown("### 📄 Relatório de Entrega")
    st.info(st.session_state.resultado_final)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.download_button("⬇️ Baixar TXT", st.session_state.resultado_final, "campanha.txt")
    with c2:
        try:
            pdf_data = gerar_pdf(st.session_state.resultado_final)
            st.download_button("⬇️ Baixar PDF", bytes(pdf_data), "campanha.pdf", "application/pdf")
        except: st.warning("Erro no PDF.")
    with c3: st.button("🔄 Nova Campanha", on_click=nova_campanha)
