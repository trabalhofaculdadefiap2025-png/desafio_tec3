from src.graph import app_graph

def test_system(patient_id, question):
    print(f"\n--- TESTANDO: {question} ---")
    state = {"patient_id": patient_id, "question": question, "pending_exams": [], "response": ""}
    result = app_graph.invoke(state)
    print(f"RESPOSTA FINAL: {result['response']}")

# 1. Teste de Bloqueio (Carlos tem pendências)
test_system("12345", "O paciente pode receber alta?")

# 2. Teste de Consulta Direta (Ana não tem pendências)
test_system("67890", "Qual a idade da paciente?")

# 3. Teste de IA (Ana não tem pendências)
test_system("67890", "Qual o protocolo para dor abdominal?")