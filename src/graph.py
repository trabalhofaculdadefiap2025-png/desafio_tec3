from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from src.database import HospitalDatabase
from src.assistant import MedicalAssistant


# 1. Estado do Grafo
class AgentState(TypedDict):
    patient_id: str
    question: str
    pending_exams: List[str]
    response: str


db = HospitalDatabase()
assistant = MedicalAssistant()

def check_safety_node(state: AgentState):
    """Verifica se há exames pendentes."""
    print("🚦 [Graph] Verificando segurança...")
    exams = db.check_pending_exams(state['patient_id'])
    return {"pending_exams": exams if exams else []}


def query_data_node(state: AgentState):
    """Nível 1: Responde dados diretos sem IA."""
    print("📊 [Graph] Nível 1: Consulta Direta ao Banco...")
    patient = db.get_patient_by_id(state['patient_id'])
    q = state['question'].lower()

    if "idade" in q:
        res = f"O paciente {patient['name']} tem {patient['age']} anos."
    elif "histórico" in q or "historico" in q:
        res = f"Histórico: {patient['history']}"
    elif "exames" in q:
        ex = ", ".join(patient['pending_exams']) if patient['pending_exams'] else "Nenhum"
        res = f"Exames pendentes para {patient['name']}: {ex}"
    else:
        res = f"Informação básica de {patient['name']} localizada no sistema."
    return {"response": res}


def alert_node(state: AgentState):
    """Nó de Bloqueio."""
    print("🚨 [Graph] Bloqueio de segurança ativado!")
    exams = ", ".join(state['pending_exams'])
    return {"response": f"⚠️ ALERTA: O paciente possui exames pendentes ({exams}). Alta não recomendada."}


def assistant_node(state: AgentState):
    """Nível 2 e 3: IA Especialista ou Fallback."""
    print("🧠 [Graph] Nível 2/3: Acionando IA...")
    response = assistant.process_query(state['patient_id'], state['question'])
    return {"response": response}


# --- 3. Lógica de Roteamento ---

def decide_next_step(state: AgentState):
    # Regra 1: Bloqueio Total se houver pendência
    if state['pending_exams']:
        return "alert"

    # Regra 2: Consulta Direta (Nível 1)
    q = state['question'].lower()
    palavras_simples = ["idade", "histórico", "historico", "exames", "nome"]
    if any(word in q for word in palavras_simples):
        return "query_data"

    # Regra 3: IA (Nível 2/3)
    return "assistant"


# --- 4. Construção do Grafo ---

workflow = StateGraph(AgentState)

workflow.add_node("check_safety", check_safety_node)
workflow.add_node("alert", alert_node)
workflow.add_node("query_data", query_data_node)
workflow.add_node("assistant", assistant_node)

workflow.set_entry_point("check_safety")

workflow.add_conditional_edges(
    "check_safety",
    decide_next_step,
    {
        "alert": "alert",
        "query_data": "query_data",
        "assistant": "assistant"
    }
)

workflow.add_edge("alert", END)
workflow.add_edge("query_data", END)
workflow.add_edge("assistant", END)

app_graph = workflow.compile()