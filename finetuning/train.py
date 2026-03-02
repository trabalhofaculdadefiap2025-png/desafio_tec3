import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline
)
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from trl import SFTTrainer

# 1. Configurações
# Usaremos o Llama-3-8B ou um modelo menor como o TinyLlama para testes rápidos
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
dataset_path = "data/train.jsonl"
output_dir = "./med_llm_finetuned"

# 2. Carregar Dataset gerado pelo preprocess.py
dataset = load_dataset('json', data_files=dataset_path, split='train')

# 3. Configuração de Quantização (Para rodar em GPUs mais simples)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

# 4. Carregar Modelo e Tokenizer
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

# 5. Configuração do LoRA (Fine-tuning eficiente)
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 6. Parâmetros de Treino
training_arguments = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    learning_rate=2e-4,
    max_steps=100, # Ajuste conforme necessário
    logging_steps=10,
    fp16=True
)

# 7. Inicializar o Trainer (SFT)
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=peft_config,
    dataset_text_field="instruction", # O preprocess.py gerou este campo
    max_seq_length=512,
    tokenizer=tokenizer,
    args=training_arguments,
)

# 8. Treinar e Salvar
print("🚀 Iniciando Fine-tuning...")
trainer.train()
trainer.save_model(output_dir)
print(f"✅ Modelo salvo em: {output_dir}")