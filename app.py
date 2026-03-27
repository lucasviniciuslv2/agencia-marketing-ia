import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
import PyPDF2
import time

# IMPORTAÇÃO DA BUSCA (SKILL WEB)
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
except:
    search_tool = None

# Configuração da Página
st.set_page_config(page_title="Agência IA Premium Multi-Modelo", page_icon="🏢", layout="wide")

# ==========================================
# SKILL: LEITURA DE PDF (GIGANTE)
# ==========================================
def extrair_texto_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    texto = ""
    for page in pdf_reader.pages:
        texto += page.extract_text()
    return texto

# ==========================================
# UI E FUNÇÕES DE APOIO
# ==========================================
def nova_campanha():
    st.session_state.resultado_final = ""
    st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}
    if "tema_input" in st.session_state: st.session_state["tema_input"] = ""

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
        glow_class = ""; opacidade = "1" if foi_selecionado else "0.2"; cor_monitor = "#1e1e1e"; status_texto = "💤"
        if foi_selecionado:
            if status == "trabalhando": glow_class = "trabalhando-anim"; cor_monitor = "#00d4ff"; status_texto = "⚙️"
            elif status == "concluido": cor_monitor = "#06d6a0"; status_texto = "✅"
            else: status_texto = "⏳"
        html_cards += f"""<div class="baia-container" style="opacity: {opacidade};"><div class="name-tag"><span>{ag['emoji']} {ag['nome']}</span><span style="margin-left:8px;">{status_texto}</span></div><div class="mesa"><div class="monitor {glow_class}" style="background: {cor_monitor};"></div><div class="personagem {'animar-pulo' if status == 'trabalhando' else ''}">{ag['avatar']}</div></div><div class="chao-madeira"></div></div>"""
    return f"""<style>.office-grid {{display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px; background: #111; border-radius: 15px; justify-items: center;}}.baia-container {{ display: flex; flex-direction: column; align-items: center; transition: 0.3s; width: 150px; }}.name-tag {{background: #000; color: #fff; padding: 5px 12px; border-radius: 10px; font-size: 11px; font-family: sans-serif; margin-bottom: 5px; border: 1px solid #333; white-space: nowrap;}}.mesa {{position: relative; width: 120px; height: 60px; background: #bbb; border-radius: 5px; display: flex; justify-content: center;}}.monitor {{width: 50px; height: 30px; border: 3px solid #333; border-radius: 3px; position: absolute; top: 5px; transition: 0.5s;}}.personagem {{ font-size: 30px; position: absolute; bottom: -8px; z-index: 5; }}.chao-madeira {{ width: 140px; height: 8px; background: #4a2c2a; border-top: 2px solid #5d3a37; }}.trabalhando-anim {{ animation: pulse 1s infinite alternate; }}@keyframes pulse {{ from {{ box-shadow: 0 0 2px #00d4ff; }} to {{ box-shadow: 0 0 15px #00d4ff; }} }}.animar-pulo {{ animation: jump 0.5s infinite alternate; }}@keyframes jump {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-5px); }} }}</style><div class="office-grid">{html_cards}</div>"""

# ==========================================
# INICIALIZAÇÃO DE ESTADO
# ==========================================
if 'resultado_final' not in st.session_state: st.session_state.resultado_final = ""
if 'status' not in st.session_state: 
    st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}

# ==========================================
# SIDEBAR - CENTRAL DE CHAVES
# ==========================================
with st.sidebar:
    st.header("🔑 Central de IAs")
    k_groq = st.text_input("Groq Key (Velocidade)", type="password")
    k_gemini = st.text_input("Gemini Key (Contexto/Briefing)", type="password")
    k_mistral = st.text_input("Mistral Key (Técnica)", type="password")
    
    st.divider()
    tema = st.text_area("🎯 Tema Principal", key="tema_input")
    arquivo_briefing = st.file_uploader("📁 PDF de Briefing (Opcional)", type=["pdf"])
    
    st.subheader("👥 Time Ativo")
    dict_sel = {
        "pesquisador": st.checkbox("Pesquisador", True),
        "diretor": st.checkbox("Dir. Criativo", True),
        "copywriter": st.checkbox("Copywriter", True),
        "engenheiro": st.checkbox("Eng. Prompts", True),
        "social": st.checkbox("Social Media", True)
    }
    
    col1, col2 = st.columns(2)
    with col1: btn_iniciar = st.button("🚀 Iniciar")
    with col2: st.button("🧹 Reset", on_click=nova_campanha)

st.title("🤖 Agência IA Corporativa (Multi-Modelo)")

# Escritório Virtual
escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_sel), height=400)

# ==========================================
# LÓGICA DE EXECUÇÃO MULTI-LLM
# ==========================================
if btn_iniciar:
    if not k_groq or not tema:
        st.error("Pelo menos a Groq API Key e o Tema são necessários!")
    else:
        # 1. Processamento de Briefing Extra
        texto_briefing = extrair_texto_pdf(arquivo_briefing) if arquivo_briefing else ""
        
        # 2. Configuração das Instâncias de LLM (Roteamento Inteligente)
        # Gemini para contexto pesado
        llm_gemini = LLM(model="gemini/gemini-1.5-flash", api_key=k_gemini) if k_gemini else LLM(model="groq/llama-3.3-70b-versatile", api_key=k_groq)
        # Mistral para técnica
        llm_mistral = LLM(model="mistral/mistral-large-latest", api_key=k_mistral) if k_mistral else LLM(model="groq/llama-3.3-70b-versatile", api_key=k_groq)
        # Groq para velocidade de redação
        llm_groq = LLM(model="groq/llama-3.3-70b-versatile", api_key=k_groq)

        # Mapeamento do Trabalho
        agentes_jobs = [
            ("pesquisador", "Pesquisador", llm_gemini, 
             f"Analise o tema {tema} usando este briefing extra: {texto_briefing}. Pesquise na web tendências."),
            
            ("diretor", "Dir. Criativo", llm_gemini, 
             f"Com base na análise do briefing, crie o conceito e slogan para {tema}."),
            
            ("copywriter", "Copywriter", llm_groq, 
             f"Escreva 3 legendas magnéticas para Instagram focadas no público de {tema}."),
            
            ("engenheiro", "Eng. Prompts", llm_mistral, 
             f"Gere a estratégia visual e 3 prompts técnicos em Inglês para {tema}."),
            
            ("social", "Social Media", llm_groq, 
             f"Monte um cronograma de 5 dias integrando as entregas da equipe.")
        ]

        contexto_acumulado = f"[BRIEFING DO CLIENTE]: {texto_briefing}\n" if texto_briefing else ""
        st.session_state.resultado_final = ""
        log_status = st.status("🏗️ Orquestrando agência Multi-Modelo...")

        for id_ag, nome_ag, llm_modelo, task_desc in agentes_jobs:
            if dict_sel[id_ag]:
                # UI: Trabalhando
                log_status.update(label=f"⚙️ {nome_ag} usando {llm_modelo.model}...", state="running")
                st.session_state.status[id_ag] = "trabalhando"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_sel), height=400)

                # Execução
                tarefa_completa = f"{task_desc}\n\nUSE O CONTEXTO ANTERIOR: {contexto_acumulado}"
                ag = Agent(role=nome_ag, goal=task_desc, backstory="Expert Sênior.", llm=llm_modelo, tools=[search_tool] if (id_ag=="pesquisador" and search_tool) else [])
                ts = Task(description=tarefa_completa, expected_output="Resultado profissional detalhado.", agent=ag)
                
                try:
                    res = Crew(agents=[ag], tasks=[ts], max_rpm=2).kickoff()
                    st.session_state.resultado_final += f"### {nome_ag.upper()} (via {llm_modelo.model})\n{res.raw}\n\n---\n"
                    contexto_acumulado += f"\n[{nome_ag}: {res.raw}]"
                    
                    # Concluído
                    st.session_state.status[id_ag] = "concluido"
                    with escritorio_container:
                        components.html(render_office(st.session_state.status, dict_sel), height=400)
                    time.sleep(2)
                except Exception as e:
                    st.error(f"Erro com {nome_ag}: {e}")
                    break

        log_status.update(label="✅ Projeto Concluído com Sucesso!", state="complete")

# Exibição
if st.session_state.resultado_final:
    st.info(st.session_state.resultado_final)
    st.download_button("⬇️ Baixar TXT", st.session_state.resultado_final, "campanha_multi_ia.txt")
