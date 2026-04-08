# fine-tune.py - Qwen LoRA Fine-Tuning Script
# Usage: python fine-tune.py

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer
import torch

# ===================== Configuration =====================
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
OUTPUT_DIR = "./qwen-finetuned"
DATASET_PATH = "./training_data.jsonl"
EPOCHS = 3
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 2048

# ===================== Load Model =====================
print(f"Loading model: {MODEL_NAME}")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto",
    load_in_4bit=True
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

# ===================== LoRA Config =====================
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"]
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ===================== Dataset =====================
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

# ===================== Training =====================
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION,
    learning_rate=LEARNING_RATE,
    lr_scheduler_type="cosine",
    num_train_epochs=EPOCHS,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,
    optim="paged_adamw_8bit",
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=True,
)

print("Starting training...")
trainer.train()
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")
