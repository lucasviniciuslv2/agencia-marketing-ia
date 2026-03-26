import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
import time

# IMPORTAÇÃO DA FERRAMENTA DE BUSCA (VIA LANGCHAIN PARA ESTABILIDADE)
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
except Exception:
    search_tool = None

# Configuração da Página
st.set_page_config(page_title="Agência Marketing IA", page_icon="🏢", layout="wide")

# ==========================================
# FUNÇÕES DE SUPORTE (RESET E PDF)
# ==========================================
def nova_campanha():
    """Reseta o estado da aplicação via callback"""
    st.session_state.resultado_final = ""
    st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}
    if "tema_input" in st.session_state:
        st.session_state["tema_input"] = ""

def gerar_pdf(texto):
    """Gera o PDF do relatório final"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Estrategia - Agencia IA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    # Limpeza para evitar erros de codificação Latin-1 no PDF
    texto_limpo = texto.replace('###', '').replace('**', '').replace('##', '').replace('-', ' ')
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
            <div class="mesa">
                <div class="monitor {glow_class}" style="background: {cor_monitor};"></div>
                <div class="personagem {'animar-pulo' if status == 'trabalhando' else ''}">{ag['avatar']}</div>
            </div>
            <div class="chao-madeira"></div>
        </div>
        """
    return f"""<style>.office-grid {{display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px; background: #111; border-radius: 15px; justify-items: center;}}.baia-container {{ display: flex; flex-direction: column; align-items: center; transition: 0.3s; width: 150px; }}.name-tag {{background: #000; color: #fff; padding: 5px 12px; border-radius: 10px; font-size: 11px; font-family: sans-serif; margin-bottom: 5px; border: 1px solid #333; white-space: nowrap;}}.mesa {{position: relative; width: 120px; height: 60px; background: #bbb; border-radius: 5px; display: flex; justify-content: center;}}.monitor {{width: 50px; height: 30px; border: 3px solid #333; border-radius: 3px; position: absolute; top: 5px; transition: 0.5s;}}.personagem {{ font-size: 30px; position: absolute; bottom: -8px; z-index: 5; }}.chao-madeira {{ width: 140px; height: 8px; background: #4a2c2a; border-top: 2px solid #5d3a37; }}.trabalhando-anim {{ animation: pulse 1s infinite alternate; }}@keyframes pulse {{ from {{ box-shadow: 0 0 2px #00d4ff; }} to {{ box-shadow: 0 0 15px #00d4ff; }} }}.animar-pulo {{ animation: jump 0.5s infinite alternate; }}@keyframes jump {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-5px); }} }}</style><div class="office-grid">{html_cards}</div>"""

# ==========================================
# INICIALIZAÇÃO DE ESTADO
# ==========================================
if 'resultado_final' not in st.session_state: st.session_state.resultado_final = ""
if 'status' not in st.session_state: 
    st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    groq_key = st.text_input("🔑 Groq API Key", type="password")
    tema = st.text_area("🎯 Tema do Projeto", placeholder="Ex: Hamburgueria artesanal sustentável", key="tema_input")
    
    st.subheader("👥 Time Ativo")
    dict_sel = {
        "pesquisador": st.checkbox("Pesquisador (Web Search Ativo)", True),
        "diretor": st.checkbox("Dir. Criativo", True),
        "copywriter": st.checkbox("Copywriter", True),
        "engenheiro": st.checkbox("Eng. Prompts (Híbrido)", True),
        "social": st.checkbox("Social Media", True)
    }
    
    col_b1, col_b2 = st.columns(2)
    with col_b1: btn_iniciar = st.button("🚀 Iniciar Ciclo")
    with col_b2: st.button("🧹 Resetar", on_click=nova_campanha)

st.title("🤖 Escritório Digital IA")

escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_sel), height=400)

# ==========================================
# LÓGICA DE EXECUÇÃO
# ==========================================
if btn_iniciar:
    if not groq_key or not tema:
        st.error("Chave e Tema são obrigatórios!")
    else:
        st.session_state.resultado_final = ""
        for k in st.session_state.status: st.session_state.status[k] = "espera"
        
        llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_key)
        pesquisa_tools = [search_tool] if (search_tool and dict_sel["pesquisador"]) else []

        # TAREFAS COM SKILLS DE BUSCA E CONTEXTO
        agentes_jobs = [
            ("pesquisador", "Pesquisador", 
             f"PESQUISE NA WEB tendências, concorrentes reais e dores do público para {tema}. Use dados atuais.", pesquisa_tools),
            
            ("diretor", "Dir. Criativo", 
             f"Com base nos dados da pesquisa, defina o conceito criativo e um slogan matador para {tema}.", []),
            
            ("copywriter", "Copywriter", 
             f"Escreva 3 legendas de Instagram usando Storytelling e os insights da pesquisa para {tema}.", []),
            
            ("engenheiro", "Eng. Prompts", 
             f"Dê sua consultoria de estilo visual em Português E forneça 3 Prompts Técnicos em Inglês para Midjourney/Flux sobre {tema}.", []),
            
            ("social", "Social Media", 
             f"Monte um cronograma de 5 dias organizando todo o material da equipe para {tema}.", [])
        ]

        contexto_acumulado = ""
        status_log = st.status("🏗️ Orquestrando equipe...")

        for id_ag, nome_ag, task_desc, tools in agentes_jobs:
            if dict_sel[id_ag]:
                status_log.update(label=f"⚙️ {nome_ag} trabalhando...", state="running")
                st.session_state.status[id_ag] = "trabalhando"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_sel), height=400)

                tarefa_completa = f"{task_desc}\n\nUSE O CONTEXTO ANTERIOR: {contexto_acumulado}"
                
                ag = Agent(role=nome_ag, goal=task_desc, backstory="Especialista Sênior com foco em resultados práticos.", llm=llm, tools=tools)
                ts = Task(description=tarefa_completa, expected_output="Um relatório técnico-criativo completo.", agent=ag)
                
                try:
                    res = Crew(agents=[ag], tasks=[ts], max_rpm=3).kickoff()
                    st.session_state.resultado_final += f"### {nome_ag.upper()}\n{res.raw}\n\n---\n"
                    contexto_acumulado += f"\n[{nome_ag} definiu: {res.raw}]"
                    
                    st.session_state.status[id_ag] = "concluido"
                    with escritorio_container:
                        components.html(render_office(st.session_state.status, dict_sel), height=400)
                    time.sleep(5) # Delay anti-bloqueio Groq
                except Exception as e:
                    st.error(f"Erro com {nome_ag}: {e}")
                    break

        status_log.update(label="✅ Campanha Concluída!", state="complete")

# ==========================================
# RESULTADOS E DOWNLOADS
# ==========================================
if st.session_state.resultado_final:
    st.markdown("### 📄 Relatório Estratégico Final")
    st.info(st.session_state.resultado_final)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.download_button("⬇️ Baixar TXT", st.session_state.resultado_final, "campanha.txt")
    with c2:
        try:
            pdf_b = gerar_pdf(st.session_state.resultado_final)
            st.download_button("⬇️ Baixar PDF", bytes(pdf_b), "campanha.pdf", "application/pdf")
        except: st.warning("PDF indisponível (Erro de codificação). Use TXT.")
    with c3: st.button("🔄 Nova Campanha", on_click=nova_campanha)
