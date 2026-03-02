import pandas as pd

# Carregar o ficheiro de treino atual
df = pd.read_json('data/train.jsonl', lines=True)

# Função para juntar tudo numa única coluna de texto
def formatar_prompt(row):
    prompt = f"### Instrução:\n{row['instruction']}\n\n"
    if row.get('input'):
        prompt += f"### Contexto:\n{row['input']}\n\n"
    prompt += f"### Resposta:\n{row['output']}"
    return prompt

# Aplicar a função
df['text'] = df.apply(formatar_prompt, axis=1)

# Guardar o novo ficheiro CSV apenas com a coluna 'text'
df[['text']].to_csv('data/autotrain_dataset.csv', index=False)
print("✅ Ficheiro 'autotrain_dataset.csv' gerado com sucesso na pasta data!")