# Qwen Fine-Tuning on Google Colab

## Quick Start

1. Go to: https://colab.research.google.com/
2. Click **File > Upload Notebook** (or start new)
3. Upload or paste the code from `colab-finetune.ipynb`
4. Connect to a GPU: **Runtime > Change runtime type > T4 GPU**
5. Run all cells

## Steps Overview

| Step | Description |
|------|-------------|
| 1 | Install dependencies |
| 2 | Upload training data |
| 3 | Run fine-tuning (LoRA) |
| 4 | Test the model |
| 5 | Download or push to Hugging Face |

## Upload Training Data

In Colab, upload `training_data.jsonl`:
```python
from google.colab import files
uploaded = files.upload()  # Select your file
```

Or use the sample data included in this guide.

## Hugging Face Integration (Optional)

To save to Hugging Face Hub:
```python
from huggingface_hub import login
login(token="your-hf-token")

model.push_to_hub("your-username/qwen-finetuned")
tokenizer.push_to_hub("your-username/qwen-finetuned")
```

## Estimated Times (T4 GPU)
- 7B model (LoRA, 4-bit): ~2-4 hours for 3 epochs
- 14B model (LoRA, 4-bit): ~4-6 hours for 3 epochs
