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
# FUNÇÕES DE SUPORTE
# ==========================================
def clean_visual_prompt(text):
    """Extrai e limpa o prompt de forma agressiva para evitar URLs quebradas"""
    # Procura por [PROMPT_VISUAL]texto[/PROMPT_VISUAL]
    pattern = r"\[PROMPT_VISUAL\](.*?)\[/PROMPT_VISUAL\]"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        prompt = match.group(1).strip()
        # Remove markdown, aspas, backticks e quebras de linha
        prompt = prompt.replace('`', '').replace('"', '').replace("'", "").replace('\n', ' ')
        # Remove prefixos comuns que a IA insere por erro
        prompt = re.sub(r'^(prompt|visual prompt|image prompt):\s*', '', prompt, flags=re.IGNORECASE)
        return prompt
    return None

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
             IMPORTANTE: Após as variações, escreva apenas UMA linha final contendo o melhor prompt em inglês cercado por tags. 
             Exemplo: [PROMPT_VISUAL] A luxury coffee cup on a marble table, cinematic lighting, 8k [/PROMPT_VISUAL]. 
             NÃO use aspas ou Markdown dentro das tags."""),
            ("social", "Social Media", f"Monte um cronograma de 5 dias.")
        ]

        contexto = ""
        status_box = st.status("🏗️ Iniciando trabalho...")

        for id_ag, nome_ag, task_desc in agentes_jobs:
            if dict_sel[id_ag]:
                status_box.update(label=f"⚙️ {nome_ag} trabalhando...", state="running")
                st.session_state.status[id_ag] = "trabalhando"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_sel), height=400)

                ag = Agent(role=nome_ag, goal=task_desc, backstory="Expert Sênior focado em entregar resultados limpos.", llm=llm)
                ts = Task(description=f"{task_desc}\nContexto: {contexto}", expected_output="Um relatório profissional seguindo rigorosamente as instruções de formato.", agent=ag)
                res = Crew(agents=[ag], tasks=[ts]).kickoff()
                
                st.session_state.resultado_final += f"### {nome_ag.upper()}\n{res.raw}\n\n---\n"
                contexto += f"\n[{nome_ag}: {res.raw}]"

                if id_ag == "engenheiro":
                    st.session_state.prompt_limpo = clean_visual_prompt(res.raw)
                
                st.session_state.status[id_ag] = "concluido"
                with escritorio_container:
                    components.html(render_office(st.session_state.status, dict_sel), height=400)
                time.sleep(1)

        status_box.update(label="✅ Agência finalizou o projeto!", state="complete")

# ==========================================
# EXIBIÇÃO DE RESULTADOS
# ==========================================
if st.session_state.resultado_final:
    
    if st.session_state.prompt_limpo:
        st.divider()
        st.subheader("🎨 Conceito Visual Sugerido")
        
        with st.expander("🔍 Ver detalhes do Prompt Gerado"):
            st.code(st.session_state.prompt_limpo, language="text")
            
        if st.button("🖼️ Gerar Amostra Visual agora"):
            with st.spinner("Conectando ao motor de renderização..."):
                encoded_prompt = urllib.parse.quote(st.session_state.prompt_limpo)
                # Adicionado seed aleatório para garantir que a imagem mude se o prompt mudar
                seed = int(time.time())
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&model=flux&seed={seed}"
                
                # Container para a imagem com tratamento de erro visual
                st.image(img_url, caption="Identidade Visual Gerada pela IA", use_container_width=True)
                st.info("💡 Dica: Se a imagem não aparecer, tente clicar novamente. O servidor do Pollinations pode levar alguns segundos para processar.")
        st.divider()

    st.markdown("### 📄 Relatório Estratégico")
    st.info(st.session_state.resultado_final)
    
    c1, c2 = st.columns(2)
    with c1: st.download_button("⬇️ Baixar TXT", st.session_state.resultado_final, "campanha.txt")
    with c2:
        try:
            pdf_data = gerar_pdf(st.session_state.resultado_final)
            st.download_button("⬇️ Baixar PDF", bytes(pdf_data), "campanha.pdf", "application/pdf")
        except: st.warning("Erro ao gerar o PDF.")
