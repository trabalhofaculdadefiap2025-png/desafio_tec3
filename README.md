🏥 Assistente Médico Virtual - Tech Challenge Fase 3
Este projeto consiste em um Assistente Virtual Médico Inteligente desenvolvido para o Hospital Tech Challenge. O sistema utiliza uma arquitetura híbrida para auxiliar médicos em condutas clínicas, responder dúvidas sobre protocolos internos e consultar dados de prontuários com segurança garantida via LangGraph.

📂 Estrutura do Projeto
data/: Contém as bases de dados do sistema, incluindo o prontuário mockado (patients_mock.json), protocolos institucionais sintéticos (internal_protocols.json) e os datasets preparados para treino (train.jsonl, autotrain_dataset.csv).

docs/: Armazena a documentação de suporte e o log de auditoria (audit_log.log), essencial para o rastreamento de decisões do sistema.

finetuning/: Contém os scripts de pré-processamento para anonimização (preprocess.py) e o pipeline de treinamento (train.py) utilizando a biblioteca Unsloth.

src/: Núcleo da aplicação:

app.py: Interface do usuário desenvolvida em Streamlit.

assistant.py: Lógica de integração com o motor de IA (Vertex AI/Gemini).

database.py: Camada de acesso aos dados estruturados.

graph.py: Definição do fluxo de estados e segurança via LangGraph.

requirements.txt: Lista de dependências necessárias para a execução do projeto.

credenciais.json: Arquivo de Service Account para autenticação no Google Cloud (não incluído no controle de versão por segurança).

🧠 Arquitetura de Inteligência e Decisão
O assistente opera sob uma Arquitetura de 3 Níveis coordenada pelo LangGraph para garantir máxima segurança e eficiência:

Nível 0 - Segurança (LangGraph Check): O sistema verifica automaticamente se o paciente possui exames críticos pendentes no prontuário. Se houver pendências (ex: Carlos Silva - ID 12345), o fluxo de IA é bloqueado e um alerta de risco é emitido.

Nível 1 - Eficiência (Consulta Direta): Perguntas sobre dados estruturados (idade, histórico, nome) são respondidas via busca direta no banco de dados, sem custo de processamento de LLM.

Nível 2/3 - Inteligência e Fallback (Vertex AI): Respostas clínicas complexas são processadas pelo motor de IA (Gemini 1.5 Pro) configurado com temperature=0.2 para garantir precisão técnica e evitar alucinações.

⚙️ Fine-Tuning e Processamento de Dados
Modelo Base: Llama-3-8B quantizado em 4-bit para otimização de recursos.

Técnica: Fine-tuning via LoRA (Low-Rank Adaptation) com a biblioteca Unsloth.

Dataset: Composto por dados científicos do PubMedQA e protocolos sintéticos do hospital.

Anonimização: Todos os dados passaram por um processo de limpeza via Regex no script preprocess.py para remover nomes e identificadores reais (PII), garantindo a privacidade dos dados.

🚀 Como Executar
Pré-requisitos
Python 3.10+

Arquivo credenciais.json (Service Account do Google Cloud) na raiz do projeto.
Clone o repositório,
Crie e ative um ambiente virtual,
Instale as dependências,
Inicie a interface do assistente.

🧪 Exemplos de Teste
Bloqueio de Segurança: Selecione o ID 12345 e pergunte: "O paciente pode receber alta?". O sistema bloqueará a resposta devido aos exames pendentes.

Consulta de Dados: Selecione o ID 67890 e pergunte: "Qual a idade da paciente?".

Protocolo Clínico: Selecione o ID 67890 e pergunte: "Qual o protocolo para suspeita de Sepse?".
