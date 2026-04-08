# Complete Qwen Tuning Guide

## Table of Contents
1. [Model Fine-Tuning](#1-model-fine-tuning)
2. [Qwen Code CLI Settings](#2-qwen-code-cli-settings)
3. [System Prompt / Persona Tuning](#3-system-prompt--persona-tuning)
4. [Parameter Tuning](#4-parameter-tuning)

---

## 1. Model Fine-Tuning

Fine-tuning adapts Qwen to your specific domain or use case.

### Prerequisites
- Python 3.10+
- PyTorch
- Transformers library
- PEFT (Parameter-Efficient Fine-Tuning) / LoRA
- A GPU (recommended) or cloud compute (Colab, RunPod)

### Setup Environment
```bash
pip install torch transformers peft accelerate datasets trl bitsandbytes
```

### Method A: LoRA Fine-Tuning (Recommended for limited resources)

```python
# fine-tune.py
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

# Configuration
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"  # Choose model size
OUTPUT_DIR = "./qwen-finetuned"
DATASET_PATH = "./training_data.json"  # Your dataset

# Load model & tokenizer
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto",
    load_in_4bit=True  # Quantization for memory efficiency
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# LoRA configuration
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

# Prepare dataset
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,
    optim="paged_adamw_8bit",
)

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=2048,
    packing=True,
)
trainer.train()
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
```

### Training Data Format (JSON)
```json
[
  {"text": "### Instruction:\nWrite a function to sort a list.\n\n### Response:\n```python\ndef sort_list(lst):\n    return sorted(lst)\n```"},
  {"text": "### Instruction:\nExplain recursion.\n\n### Response:\nRecursion is a technique where a function calls itself..."}
]
```

### Method B: Full Fine-Tuning (Requires significant GPU memory)
- Use `TrainingArguments` without LoRA
- Requires 40GB+ VRAM for 7B model
- Recommended: Use cloud GPUs or distributed training

---

## 2. Qwen Code CLI Settings

### Locate Settings File
Settings are stored in: `~/.qwen/settings.json`

### Key Configuration Options
```json
{
  "model": {
    "provider": "dashscope",
    "model": "qwen-coder-plus",
    "api_key": "your-api-key"
  },
  "context": {
    "max_tokens": 8192,
    "temperature": 0.7,
    "top_p": 0.95
  },
  "behavior": {
    "auto_run": false,
    "verbose": true,
    "output_language": "en"
  },
  "approval": {
    "mode": "default"
  }
}
```

### Edit Settings via CLI
Use `/qc-helper` command to view/modify settings:
- `/qc-helper how do I configure MCP servers?`
- `/qc-helper change approval mode to yolo`

### Environment Variables
```bash
export DASHSCOPE_API_KEY="your-key"
export QWEN_MODEL="qwen-coder-plus"
```

---

## 3. System Prompt / Persona Tuning

### Global System Prompt
Create/edit `~/.qwen/system-prompt.md`:

```markdown
You are an expert software engineer with deep knowledge of:
- Python, JavaScript/TypeScript, Go, Rust
- System architecture and design patterns
- DevOps, CI/CD, and cloud infrastructure

Guidelines:
- Always write clean, well-documented code
- Follow best practices and design patterns
- Be concise and direct in responses
- Include security considerations
- Optimize for readability and maintainability
```

### Project-Specific Prompts
Create `QWEN.md` in your project root:

```markdown
# Project Context

## Tech Stack
- Frontend: React + TypeScript + Tailwind
- Backend: Node.js + Express
- Database: PostgreSQL

## Coding Standards
- Use functional components
- Prefer async/await over callbacks
- Write unit tests for all business logic
- Follow SOLID principles

## Conventions
- File naming: kebab-case
- Variables: camelCase
- Constants: UPPER_SNAKE_CASE
- All functions should have JSDoc comments
```

### QWEN.md in Home Directory
Create `~/.qwen/QWEN.md` for global preferences:

```markdown
# Global Preferences

## Communication
- Be direct and concise
- Use technical language
- Skip pleasantries

## Code Style
- Modern syntax (ES2022+, Python 3.11+)
- Type hints required
- No unnecessary comments
- DRY principle

## Output Language
- Always respond in English
- Technical terms remain unchanged
```

---

## 4. Parameter Tuning

### Key Parameters Explained

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `temperature` | 0.0-2.0 | 0.7 | Creativity vs determinism |
| `top_p` | 0.0-1.0 | 0.95 | Nucleus sampling threshold |
| `top_k` | 1-100 | 40 | Number of tokens to consider |
| `max_tokens` | 1-32768 | 2048 | Maximum response length |
| `frequency_penalty` | -2.0-2.0 | 0.0 | Reduce repetition |
| `presence_penalty` | -2.0-2.0 | 0.0 | Encourage new topics |

### Recommended Settings by Task

#### Code Generation
```json
{
  "temperature": 0.2,
  "top_p": 0.95,
  "top_k": 40,
  "max_tokens": 4096,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

#### Creative Writing
```json
{
  "temperature": 0.8,
  "top_p": 0.9,
  "top_k": 50,
  "max_tokens": 8192,
  "frequency_penalty": 0.3,
  "presence_penalty": 0.3
}
```

#### Analysis / Reasoning
```json
{
  "temperature": 0.1,
  "top_p": 0.9,
  "top_k": 20,
  "max_tokens": 4096,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

#### Q&A / Factual
```json
{
  "temperature": 0.0,
  "top_p": 1.0,
  "top_k": 1,
  "max_tokens": 2048,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

### Context Window Tuning

| Model | Max Context | Max Output |
|-------|-------------|------------|
| Qwen2.5-0.5B | 32K tokens | 8K |
| Qwen2.5-7B | 128K tokens | 8K |
| Qwen2.5-14B | 128K tokens | 8K |
| Qwen2.5-72B | 128K tokens | 8K |

### Optimization Tips

1. **Lower temperature (0.1-0.3)**: Deterministic code generation
2. **Higher temperature (0.7-1.0)**: Brainstorming, creative tasks
3. **Increase max_tokens**: For long-form outputs
4. **Use top_p < 1.0**: For more focused responses
5. **Enable repetition penalties**: When model repeats itself

---

## Quick Start Checklist

- [ ] Install fine-tuning dependencies: `pip install transformers peft trl`
- [ ] Prepare training dataset in JSON format
- [ ] Run fine-tuning script with LoRA (low memory)
- [ ] Configure `~/.qwen/settings.json`
- [ ] Create `~/.qwen/QWEN.md` with global preferences
- [ ] Create project-specific `QWEN.md` in each project
- [ ] Tune parameters based on your use case
- [ ] Test and iterate

---

## Resources

- **Qwen Documentation**: https://qwenlm.github.io/
- **Hugging Face Models**: https://huggingface.co/Qwen
- **PEFT Library**: https://huggingface.co/docs/peft
- **Transformers Docs**: https://huggingface.co/docs/transformers
