import json
import logging
import os

# Configuração de Logging para Auditoria (Requisito 3. Segurança e validação)
logging.basicConfig(
    filename='docs/audit_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class HospitalDatabase:
    def __init__(self, file_path='data/patients_mock.json'):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        """Carrega os dados dos prontuários anonimizados."""
        if not os.path.exists(self.file_path):
            logging.error(f"Arquivo de banco de dados não encontrado: {self.file_path}")
            return {"patients": []}

        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_patient_by_id(self, patient_id):
        """Busca dados completos de um paciente pelo ID."""
        logging.info(f"Consulta realizada: Busca de paciente ID {patient_id}")

        patient = next((p for p in self.data['patients'] if p['id'] == str(patient_id)), None)

        if patient:
            logging.info(f"Paciente {patient_id} encontrado com sucesso.")
            return patient
        else:
            logging.warning(f"Tentativa de busca falhou: Paciente {patient_id} não localizado.")
            return None

    def check_pending_exams(self, patient_id):
        """Verifica especificamente se há exames pendentes (Requisito do fluxo LangGraph)."""
        patient = self.get_patient_by_id(patient_id)
        if patient:
            exams = patient.get('pending_exams', [])
            logging.info(f"Verificação de exames para ID {patient_id}: {len(exams)} pendentes.")
            return exams
        return None


# Exemplo simples para teste local
if __name__ == "__main__":
    db = HospitalDatabase()
    print(db.get_patient_by_id("12345"))