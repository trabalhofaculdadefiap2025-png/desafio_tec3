import os
import google.generativeai as genai
from src.database import HospitalDatabase


class MedicalAssistant:
    def __init__(self, model_path=None):
        """
        Inicializa o assistente configurando a API do Gemini.
        """
        self.db = HospitalDatabase()
        # Configuração da API Key (da sua imagem image_2430dc)
        genai.configure(api_key="AIzaSyALbsFZiVcaeXVwNlSztZ-OWk7-IR1XD8M")
        # Usamos o modelo Pro para máxima qualidade médica
        self.model = genai.GenerativeModel('gemini-2.5-pro')

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
        Envia a pergunta diretamente ao Gemini com o contexto do hospital.
        """
        print(f"🧠 [Assistant] Consultando Gemini 1.5 Pro para o paciente {patient_id}...")

        contexto = self._get_patient_context(patient_id)

        # Prompt estruturado para garantir a persona médica e segurança
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
            response = self.model.generate_content(prompt_final)
            return response.text
        except Exception as e:
            return f"Erro ao conectar com o cérebro da IA: {str(e)}"


if __name__ == "__main__":
    assistant = MedicalAssistant()
    resposta = assistant.process_query("12345", "Quais os cuidados para este paciente?")
    print(resposta)