import streamlit as st
import time
import sys
import os

# Ajuste de caminho para garantir que o Python encontre a pasta 'src'
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.database import HospitalDatabase
from src.graph import app_graph  # Importando nosso fluxo LangGraph completo

# 1. Configuração da Página do Streamlit
st.set_page_config(
    page_title="Assistente Médico - Tech Challenge",
    page_icon="🏥",
    layout="wide"
)

# Estilo para o título e divisor
st.title("🏥 Assistente Virtual Médico Inteligente")
st.markdown("---")

# --- 2. BARRA LATERAL (Contexto em tempo real do Prontuário) ---
st.sidebar.header("📋 Prontuário Eletrônico")

# Inicialização do banco de dados mockado
db = HospitalDatabase()
patient_id = st.sidebar.text_input("ID do Paciente:", value="12345")

# Busca ativa dos dados do paciente para exibir na lateral
patient = db.get_patient_by_id(patient_id)

if patient:
    st.sidebar.success(f"Paciente: {patient['name']}")
    st.sidebar.markdown(f"**Idade:** {patient['age']} anos")
    st.sidebar.markdown(f"**Histórico:** {patient['history']}")

    # Exibição de Risco: Destaque visual se houver pendências
    if patient['pending_exams']:
        st.sidebar.warning(f"⚠️ **Exames Pendentes:** {', '.join(patient['pending_exams'])}")
    else:
        st.sidebar.info("✅ Sem pendências críticas.")
else:
    st.sidebar.error("Paciente não localizado no sistema.")

# --- 3. ÁREA DE CHAT (Interface de Interação) ---

# Inicializa o histórico de mensagens na sessão do navegador
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens do histórico visualmente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura de entrada do Médico
if prompt := st.chat_input("Digite sua dúvida clínica ou consulta sobre dados..."):
    # Adiciona a pergunta do médico ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # PROCESSAMENTO DA RESPOSTA (Lógica de 3 Níveis via LangGraph)
    if patient:
        with st.chat_message("assistant"):
            # Feedback visual dos níveis de processamento para o utilizador
            with st.status("🕵️ Analisando solicitação...", expanded=False) as status:
                st.write("🚦 Nível 0: Validando protocolos de segurança...")

                # Execução do Grafo: Checa Segurança -> Decide Nível 1 ou 2/3 -> Responde
                try:
                    result = app_graph.invoke({
                        "patient_id": patient_id,
                        "question": prompt,
                        "pending_exams": [],
                        "response": ""
                    })

                    st.write("✅ Fluxo de segurança processado.")
                    status.update(label="💉 Resposta Pronta!", state="complete", expanded=False)

                    response_text = result.get("response", "Erro: O sistema não retornou uma resposta válida.")

                except Exception as e:
                    response_text = f"🚨 Falha no motor de decisão: {str(e)}"
                    status.update(label="❌ Erro no Processamento", state="error", expanded=True)

            # Efeito de Digitação (UX para simular inteligência em tempo real)
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response_text.split():
                full_response += chunk + " "
                time.sleep(0.04)  # Velocidade da digitação
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

            # Armazena a resposta final no histórico da sessão
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.error("Erro: Selecione um paciente válido para habilitar a consulta.")