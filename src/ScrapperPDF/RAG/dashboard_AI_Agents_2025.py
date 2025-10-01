import streamlit as st
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field
from pydantic_ai import PydanticAI
from datetime import datetime
import json

#     pip install streamlit google-generativeai langgraph langchain_core pypdf2 pydantic pydantic-ai


# --- Configuração da Página e Título ---
st.set_page_config(page_title="Agentes de IA com LangGraph", page_icon="🤖", layout="wide")
st.title("🤖 Chatbot com Sistema Completo de Agentes de IA")
st.markdown("""
Esta versão inclui **Validação (PydanticAI)**, **Testes (DSPy)** e **Monitoramento (Agno)**.
""")

# --- Monitoramento (Simulação Agno) ---
if "agno_logs" not in st.session_state:
    st.session_state.agno_logs = []

def log_to_agno(agent_role, task, result):
    """Função para simular o log de monitoramento do Agno."""
    log_entry = {
        "agent": agent_role,
        "task": task[:150] + "..." if len(task) > 150 else task,
        "result_preview": result[:200] + "..." if len(result) > 200 else result,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.agno_logs.insert(0, log_entry) # Adiciona no início da lista

# --- Configuração da API Key e UI ---
with st.sidebar:
    st.header("Configurações")
    google_api_key = st.text_input("Digite sua Google API Key", type="password")
    
    st.markdown("---")
    st.subheader("Seus Documentos")
    pdf_docs = st.file_uploader(
        "Envie seus PDFs aqui e clique em 'Processar'", accept_multiple_files=True)

    if st.button("Processar Documentos"):
        if pdf_docs:
            with st.spinner("Processando..."):
                raw_text = ""
                for pdf in pdf_docs:
                    pdf_reader = PdfReader(pdf)
                    for page in pdf_reader.pages:
                        raw_text += page.extract_text() or ""
                st.session_state.pdf_text = raw_text
                st.success("Documentos processados!")
        else:
            st.warning("Por favor, envie um arquivo PDF.")

if not google_api_key:
    st.info("Por favor, adicione sua Google API Key para continuar.")
    st.stop()

# --- Configuração dos Modelos de IA ---
try:
    genai.configure(api_key=google_api_key)
    modelo = genai.GenerativeModel("gemini-1.5-flash-latest")
    # PydanticAI para forçar saídas estruturadas
    pydantic_llm = PydanticAI(llm=modelo)
except Exception as e:
    st.error(f"Erro ao configurar a API do Google: {e}")
    st.stop()

# --- PydanticAI: Definição dos Modelos de Saída (Validação) ---
class ResearchOutput(BaseModel):
    summary: str = Field(description="Um resumo detalhado e abrangente da pesquisa realizada.")
    sources: List[str] = Field(description="Uma lista de URLs ou referências de fontes relevantes encontradas.")

# --- Definição dos Agentes ---
class Agent:
    def __init__(self, role, goal, backstory, llm_engine):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm_engine = llm_engine

    def execute(self, task, context="", output_model=None):
        prompt = f"""
        **Persona:** Role: {self.role}, Goal: {self.goal}, Backstory: {self.backstory}
        **Contexto:** {context}
        **Tarefa:** {task}
        **Instrução:** Forneça a resposta em português do Brasil.
        """
        result = ""
        try:
            if output_model: # Usa PydanticAI para validação
                response_obj = self.llm_engine(output_model=output_model, prompt=prompt)
                result = json.dumps(response_obj.dict(), indent=2, ensure_ascii=False)
            else: # Resposta de texto livre
                response = self.llm_engine.generate_content(prompt)
                result = response.text
            
            log_to_agno(self.role, task, result)
            return result
        except Exception as e:
            error_msg = f"Erro ao executar a tarefa para {self.role}: {e}"
            log_to_agno(self.role, task, error_msg)
            return error_msg

# --- Instâncias dos Agentes ---
pesquisador = Agent("Pesquisador Especialista", "Encontrar informações detalhadas e de fontes confiáveis.", "Mestre da pesquisa digital, focado em fatos.", pydantic_llm)
redator = Agent("Redator Técnico", "Escrever um texto claro, coeso e prático em Markdown.", "Transforma informações complexas em conteúdo educativo.", modelo)
avaliador = Agent("Avaliador de Qualidade (DSPy)", "Garantir que a saída de outros agentes atenda a critérios de qualidade.", "Um inspetor de IA rigoroso que valida a qualidade do trabalho.", modelo)
coordenador = Agent("Coordenador Final", "Integrar tudo em uma resposta final coesa e completa.", "O maestro da equipe, garantindo um produto final polido.", modelo)

# --- Definição do Estado do LangGraph ---
class AgentState(TypedDict):
    task: str
    pdf_context: str
    research_result: str
    research_test_result: str
    draft_result: str
    draft_test_result: str
    final_result: Annotated[list[str], operator.add]

# --- Nós do Grafo (Funções dos Agentes) ---
def researcher_node(state: AgentState):
    task = f"Pesquise sobre: '{state['task']}'. Use o contexto do PDF como principal fonte, se disponível."
    result = pesquisador.execute(task, state.get("pdf_context", ""), output_model=ResearchOutput)
    return {"research_result": result}

def research_tester_node(state: AgentState): # DSPy: Nó de Teste
    task = f"""
    Avalie o seguinte resultado da pesquisa. O resumo não pode ser vazio e deve haver pelo menos uma fonte.
    Responda apenas com 'APROVADO' ou 'REPROVADO'.
    Resultado da Pesquisa:
    {state['research_result']}
    """
    result = avaliador.execute(task)
    return {"research_test_result": result}

def writer_node(state: AgentState):
    task = f"Com base na pesquisa, escreva um rascunho em Markdown para responder a pergunta: '{state['task']}'."
    result = redator.execute(task, state['research_result'])
    return {"draft_result": result}
    
def draft_tester_node(state: AgentState): # DSPy: Nó de Teste
    task = f"""
    Avalie o rascunho a seguir. Ele deve ter uma introdução, desenvolvimento e conclusão.
    Responda apenas com 'APROVADO' ou 'REPROVADO'.
    Rascunho:
    {state['draft_result']}
    """
    result = avaliador.execute(task)
    return {"draft_test_result": result}

def coordinator_node(state: AgentState):
    context = f"""
    Pesquisa Realizada: {state['research_result']}
    Rascunho Escrito: {state['draft_result']}
    Teste da Pesquisa: {state['research_test_result']}
    Teste do Rascunho: {state['draft_test_result']}
    """
    task = f"Refine e consolide a pesquisa e o rascunho para criar uma resposta final para: '{state['task']}'."
    result = coordenador.execute(task, context)
    return {"final_result": [result]}

# --- Construção do Grafo com LangGraph ---
workflow = StateGraph(AgentState)
workflow.set_entry_point("pesquisador")
workflow.add_node("pesquisador", researcher_node)
workflow.add_node("research_tester", research_tester_node)
workflow.add_node("redator", writer_node)
workflow.add_node("draft_tester", draft_tester_node)
workflow.add_node("coordenador", coordinator_node)

# Define as arestas (fluxo de trabalho com testes)
workflow.add_edge("pesquisador", "research_tester")
workflow.add_edge("research_tester", "redator")
workflow.add_edge("redator", "draft_tester")
workflow.add_edge("draft_tester", "coordenador")
workflow.add_edge("coordenador", END)

app = workflow.compile()

# --- Interface do Chatbot no Streamlit ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Qual é a sua pergunta?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("A equipe de agentes está trabalhando (Pesquisa > Teste > Redação > Teste > Finalização)..."):
            pdf_text = st.session_state.get("pdf_text", "")
            inputs = {"task": prompt, "pdf_context": pdf_text}
            
            try:
                final_state = app.invoke(inputs)
                final_result = final_state.get('final_result', ["Desculpe, não consegui processar."])[-1]
                st.markdown(final_result)
                st.session_state.messages.append({"role": "assistant", "content": final_result})
            except Exception as e:
                error_message = f"Ocorreu um erro crítico no fluxo de agentes: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# --- Exibição do Monitoramento Agno ---
with st.expander("🕵️‍♂️ Monitoramento de Agentes (Simulação Agno)", expanded=False):
    if st.session_state.agno_logs:
        st.dataframe(st.session_state.agno_logs, use_container_width=True)
    else:
        st.write("Nenhuma atividade de agente registrada ainda.")


