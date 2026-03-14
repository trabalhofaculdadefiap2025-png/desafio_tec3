import os
import json
from google.cloud import aiplatform
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel
import vertexai
from src.database import HospitalDatabase


class MedicalAssistant:
    def __init__(self, credentials_path="credenciais.json"):
        """
        Inicializa o assistente usando Service Account para acessar o Vertex AI (Gemini).
        """
        self.db = HospitalDatabase()

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")

        with open(credentials_path, 'r') as f:
            credentials_info = json.load(f)

        credentials = service_account.Credentials.from_service_account_info(credentials_info)

        vertexai.init(
            project=credentials_info["project_id"],
            location="us-central1",
            credentials=credentials
        )

        self.model = GenerativeModel("gemini-2.5-pro")

    def _get_patient_context(self, patient_id):
        """Busca dados estruturados no banco de dados."""
        patient = self.db.get_patient_by_id(patient_id)
        if not patient:
            return "Paciente não encontrado na base de dados."

        context_str = (
            f"Nome: {patient['name']}\n"
            f"Idade: {patient['age']}\n"
            f"Histórico: {patient['history']}\n"
            f"Exames Pendentes: {', '.join(patient['pending_exams']) if patient['pending_exams'] else 'Nenhum'}"
        )
        return context_str

    def process_query(self, patient_id, question):
        """
        Envia a pergunta ao Gemini via Vertex AI com o contexto do hospital.
        """
        print(f"🧠 [Assistant] Consultando Gemini via Vertex AI para o paciente {patient_id}...")

        contexto = self._get_patient_context(patient_id)

        prompt_final = f"""
        Você é o Assistente Médico Virtual do Hospital Tech Challenge.
        Sua função é auxiliar médicos com base em protocolos internos.

        REGRAS:
        1. Responda de forma profissional e baseada em evidências.
        2. Nunca prescreva medicamentos diretamente, sugira condutas.
        3. Se o contexto indicar exames pendentes, reforce que a conduta depende desses resultados.

        CONTEXTO DO PACIENTE:
        {contexto}

        PERGUNTA DO MÉDICO:
        {question}

        RESPOSTA:
        """

        try:
            # A chamada no Vertex AI é similar
            response = self.model.generate_content(prompt_final)
            return response.text
        except Exception as e:
            return f"Erro na conexão Vertex AI: {str(e)}"


if __name__ == "__main__":
    assistant = MedicalAssistant()
    resposta = assistant.process_query("67890", "Qual o protocolo para dor abdominal?")
    print(resposta)