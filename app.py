import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM

st.set_page_config(page_title="Agência de Marketing IA", page_icon="🤖", layout="wide")

st.title("🤖 Agência de Marketing com IA")
st.markdown("Configure e acione seus agentes sem precisar mexer no código!")

with st.sidebar:
    st.header("⚙️ Configurações")
    groq_api_key = st.text_input("🔑 Sua chave da API Groq", type="password")
    st.markdown("---")
    st.header("🎯 Tema da Campanha")
    tema = st.text_area(
        "Descreva o tema da sua campanha:",
        placeholder="Ex: Lançamento de curso de fotografia para iniciantes...",
        height=120
    )
    st.markdown("---")
    st.header("👥 Agentes Ativos")
    usar_pesquisador = st.checkbox("🔍 Pesquisador de Mercado", value=True)
    usar_diretor = st.checkbox("🎨 Diretor Criativo", value=True)
    usar_copywriter = st.checkbox("✍️ Copywriter", value=True)
    usar_engenheiro = st.checkbox("🖼️ Engenheiro de Prompts", value=True)
    usar_social = st.checkbox("📱 Social Media", value=True)

iniciar = st.button("🚀 Iniciar Agência", type="primary", use_container_width=True)

if iniciar:
    if not groq_api_key:
        st.error("⚠️ Por favor, insira sua chave da API Groq na barra lateral!")
        st.stop()
    if not tema.strip():
        st.error("⚠️ Por favor, descreva o tema da campanha!")
        st.stop()

    meu_llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.7,
        max_tokens=1024
    )

    agentes = []
    tarefas = []

    with st.status("⏳ Agência trabalhando...", expanded=True) as status:

        if usar_pesquisador:
            st.write("🔍 Pesquisador analisando o mercado...")
            pesquisador = Agent(
                role='Pesquisador de Mercado e Tendências',
                goal=f'Analisar o mercado atual para: {tema}',
                backstory='Analista obcecado por tendências e comportamento do consumidor.',
                verbose=False,
                llm=meu_llm
            )
            t1 = Task(
                description=f'Pesquise tendências para: {tema}. Entregue 3 parágrafos com insights.',
                expected_output='Resumo de mercado com principais insights.',
                agent=pesquisador
            )
            agentes.append(pesquisador)
            tarefas.append(t1)

        if usar_diretor:
            st.write("🎨 Diretor Criativo desenvolvendo o conceito...")
            diretor = Agent(
                role='Diretor Criativo Sênior',
                goal='Criar o conceito central da campanha com base na pesquisa',
                backstory='Premiado diretor que define tom de voz e estética visual.',
                verbose=False,
                llm=meu_llm
            )
            t2 = Task(
                description='Crie o conceito da campanha: Slogan, Tom de Voz e Estética Visual.',
                expected_output='Diretrizes criativas da campanha.',
                agent=diretor
            )
            agentes.append(diretor)
            tarefas.append(t2)

        if usar_copywriter:
            st.write("✍️ Copywriter redigindo os textos...")
            copywriter = Agent(
                role='Copywriter de Conversão',
                goal='Escrever textos persuasivos seguindo o conceito da campanha',
                backstory='Mestre das palavras e especialista em gatilhos mentais.',
                verbose=False,
                llm=meu_llm
            )
            t3 = Task(
                description='Escreva 3 legendas para Instagram: topo, meio e fundo de funil.',
                expected_output='Três textos completos com emojis e hashtags.',
                agent=copywriter
            )
            agentes.append(copywriter)
            tarefas.append(t3)

        if usar_engenheiro:
            st.write("🖼️ Engenheiro criando prompts visuais...")
            engenheiro = Agent(
                role='Engenheiro de Prompts Visuais',
                goal='Criar prompts detalhados para IA geradora de imagens',
                backstory='Especialista em Midjourney e geração de imagens com IA.',
                verbose=False,
                llm=meu_llm
            )
            t4 = Task(
                description='Escreva 3 prompts em inglês ultra-detalhados para gerar as imagens dos posts.',
                expected_output='Três prompts descrevendo sujeito, cenário e estilo.',
                agent=engenheiro
            )
            agentes.append(engenheiro)
            tarefas.append(t4)

        if usar_social:
            st.write("📱 Social Media montando o cronograma...")
            social = Agent(
                role='Estrategista de Social Media',
                goal='Organizar tudo em um cronograma pronto para uso',
                backstory='Expert em algoritmos e engajamento nas redes sociais.',
                verbose=False,
                llm=meu_llm
            )
            t5 = Task(
                description='Monte um documento final organizado com textos e prompts de cada post.',
                expected_output='Cronograma final pronto para o cliente.',
                agent=social
            )
            agentes.append(social)
            tarefas.append(t5)

        crew = Crew(
            agents=agentes,
            tasks=tarefas,
            process=Process.sequential,
            max_rpm=20
        )

        resultado = crew.kickoff()
        status.update(label="✅ Campanha concluída!", state="complete")

    st.markdown("---")
    st.header("📋 Resultado Final da Agência")
    st.markdown(str(resultado))
    st.download_button(
        label="⬇️ Baixar Resultado",
        data=str(resultado),
        file_name="campanha.txt",
        mime="text/plain"
)
