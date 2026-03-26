import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
import time
import urllib.parse
import re

# Configuração da Página
st.set_page_config(page_title="Agência Marketing IA", page_icon="🏢", layout="wide")

# ==========================================
# FUNÇÕES DE SUPORTE (EXTRAÇÃO INTELIGENTE)
# ==========================================
def extrair_e_limpar_prompt(texto_bruto):
    """Tenta extrair o prompt por tags, se falhar, pega o último parágrafo"""
    # 1. Tenta extrair pelas tags (flexível com espaços)
    match = re.search(r"\[\s*PROMPT_VISUAL\s*\](.*?)\[\s*/PROMPT_VISUAL\s*\]", texto_bruto, re.DOTALL | re.IGNORECASE)
    
    if match:
        prompt = match.group(1).strip()
    else:
        # 2. PLANO B: Pega o último parágrafo que tenha mais de 20 caracteres
        paragrafos = [p.strip() for p in texto_bruto.split('\n') if len(p.strip()) > 20]
        prompt = paragrafos[-1] if paragrafos else ""

    # 3. Limpeza Final (Sanitização)
    # Remove markdown (**), aspas ("), caracteres especiais e deixa apenas texto básico
    prompt = re.sub(r'[\*\#\"\'\`\-\_]', '', prompt)
    # Remove prefixos teimosos
    prompt = re.sub(r'^(Prompt|Visual|Descrição):', '', prompt, flags=re.IGNORECASE).strip()
    
    # Se o prompt for muito curto, retorna None para não quebrar a URL
    return prompt if len(prompt) > 5 else None

def nova_campanha():
    st.session_state.resultado_final = ""
    st.session_state.prompt_limpo = None
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
if 'prompt_limpo' not in st.session_state: st.session_state.prompt_limpo = None
if 'status' not in st.session_state: st.session_state.status = {k: "espera" for k in ["pesquisador", "diretor", "copywriter", "engenheiro", "social"]}

with st.sidebar:
    st.header("⚙️ Configurações")
    groq_key = st.text_input("🔑 Groq API Key", type="password")
    tema = st.text_area("🎯 Tema da Campanha", key="tema_input")
    st.divider()
    dict_sel = {
        "pesquisador": st.checkbox("Pesquisador", True),
        "diretor": st.checkbox("Dir. Criativo", True),
        "copywriter": st.checkbox("Copywriter", True),
        "engenheiro": st.checkbox("Eng. Prompts", True),
        "social": st.checkbox("Social Media", True)
    }
    btn_iniciar = st.button("🚀 Iniciar Agência")
    st.button("🧹 Nova Campanha", on_click=nova_campanha)

st.title("🤖 Escritório Digital IA")
escritorio_container = st.empty()
with escritorio_container:
    components.html(render_office(st.session_state.status, dict_sel), height=400)

# ==========================================
# EXECUÇÃO
# ==========================================
if btn_iniciar:
    if not groq_key or not tema:
        st.error("Preencha a chave e o tema!")
    else:
        st.session_state.resultado_final = ""
        st.session_state.prompt_limpo = None
        for k in st.session_state.status: st.session_state.status[k] = "espera"
        
        llm = LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_key)
        
        agentes_jobs = [
            ("pesquisador", "Pesquisador", f"Analise público e mercado para {tema}."),
            ("diretor", "Dir. Criativo", f"Crie slogan e conceito para {tema}."),
            ("copywriter", "Copywriter", f"Escreva 3 legendas de Instagram para {tema}."),
            ("engenheiro", "Eng. Prompts", f"""Gere 3 variações de prompts para {tema}. 
             No final, escreva o melhor prompt técnico em INGLÊS entre as tags [PROMPT_VISUAL] e [/PROMPT_VISUAL]."""),
            ("social", "Social Media", f"Monte um cronograma de 5 dias.")
        ]

        contexto = ""
        status_box = st.status("🏗️ Processando campanha...")

        for id_ag, nome_ag, task_desc in agentes_jobs:
            if dict_sel[id_ag]:
                status_box.update(label=f"⚙️ {nome_ag} trabalhando...", state="running")
                st.session_state.status[id_ag] = "trabalhando"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_sel), height=400)

                ag = Agent(role=nome_ag, goal=task_desc, backstory="Expert Sênior.", llm=llm)
                ts = Task(description=f"{task_desc}\nContexto: {contexto}", expected_output="Um relatório limpo.", agent=ag)
                res = Crew(agents=[ag], tasks=[ts]).kickoff()
                
                st.session_state.resultado_final += f"### {nome_ag.upper()}\n{res.raw}\n\n---\n"
                contexto += f"\n[{nome_ag}: {res.raw}]"

                if id_ag == "engenheiro":
                    st.session_state.prompt_limpo = extrair_e_limpar_prompt(res.raw)
                
                st.session_state.status[id_ag] = "concluido"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_sel), height=400)
                time.sleep(1)

        status_box.update(label="✅ Finalizado!", state="complete")

# ==========================================
# EXIBIÇÃO DE RESULTADOS
# ==========================================
if st.session_state.resultado_final:
    
    # 🎨 Geração de Imagem
    if st.session_state.prompt_limpo:
        st.divider()
        st.subheader("🎨 Amostra Visual da Identidade")
        
        # Codificação segura
        p_url = urllib.parse.quote(st.session_state.prompt_limpo)
        url_final = f"https://pollinations.ai/p/{p_url}?width=1024&height=1024&model=flux&seed={int(time.time())}"
        
        col_img, col_txt = st.columns([2, 1])
        with col_img:
            st.image(url_final, use_container_width=True)
        with col_txt:
            st.write("**Prompt Detectado:**")
            st.info(st.session_state.prompt_limpo)
            st.link_button("🚀 Abrir Link Direto da Imagem", url_final)
        st.divider()
    else:
        st.warning("⚠️ O Engenheiro não gerou um prompt válido para a imagem.")

    st.markdown("### 📄 Relatório Estratégico")
    st.info(st.session_state.resultado_final)
    
    c1, c2 = st.columns(2)
    with c1: st.download_button("⬇️ Baixar TXT", st.session_state.resultado_final, "campanha.txt")
    with c2:
        try:
            pdf_data = gerar_pdf(st.session_state.resultado_final)
            st.download_button("⬇️ Baixar PDF", bytes(pdf_data), "campanha.pdf", "application/pdf")
        except: st.warning("Erro no PDF.")
