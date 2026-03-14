import json
import re
import pandas as pd
from datasets import load_dataset
from sklearn.model_selection import train_test_split


def anonymize_text(text):
    """
    Remove menções a nomes próprios ou padrões que pareçam PII (Simulação).
    Atende ao requisito de anonimização do desafio.
    """
    # Exemplo: Substitui padrões de nomes comuns ou IDs por [ANONIMIZADO]
    text = re.sub(r'\b(Dr\.|Dra\.)\s[A-Z][a-z]+', '[MEDICO_ANONIMIZADO]', text)
    text = re.sub(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', '[NOME_ANONIMIZADO]', text)
    return text


def prepare_data():
    print("🚀 Iniciando a preparação dos dados...")

    # 1. Carregar PubMedQA (Conhecimento Médico Geral)
    # Usaremos a partição 'pqa_labeled' que contém perguntas e respostas reais
    print("📚 Carregando PubMedQA...")
    pubmed = load_dataset("pubmed_qa", "pqa_labeled", split='train')

    pubmed_formatted = []
    for item in pubmed:
        pubmed_formatted.append({
            "instruction": item['question'],
            "input": item['context']['contexts'][0] if item['context']['contexts'] else "",
            "output": item['long_answer']
        })

    # 2. Carregar Protocolos Internos (Dados Sintéticos que criamos)
    print("🏥 Carregando protocolos do hospital...")
    with open('data/internal_protocols.json', 'r', encoding='utf-8') as f:
        hospital_data = json.load(f)

    # 3. Mesclar e Anonimizar
    full_dataset = pubmed_formatted + hospital_data

    for item in full_dataset:
        item['instruction'] = anonymize_text(item['instruction'])
        item['output'] = anonymize_text(item['output'])

    # 4. Divisão em Treino, Validação e Teste
    # Cumpre a necessidade de avaliação técnica posterior
    df = pd.DataFrame(full_dataset)
    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

    # 5. Salvar os arquivos processados na pasta data/
    train_df.to_json('data/train.jsonl', orient='records', lines=True, force_ascii=False)
    val_df.to_json('data/val.jsonl', orient='records', lines=True, force_ascii=False)
    test_df.to_json('data/test.jsonl', orient='records', lines=True, force_ascii=False)

    print(f"✅ Sucesso! {len(train_df)} exemplos para treino, {len(val_df)} para validação e {len(test_df)} para teste.")


if __name__ == "__main__":
    prepare_data()