#!/usr/bin/env python3
"""
Qwen Chat - Groq Provider
No ML, no compilation, works on Termux/Android
"""

import sys
import json
import httpx

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Groq has no Qwen, but has powerful alternatives
MODELS = {
    "1": "llama-3.1-70b-versatile",
    "2": "mixtral-8x7b-32768",
    "3": "llama-3.3-70b-specdec",
    "4": "gemma2-9b-it",
}

def chat(api_key, messages, model, max_tokens=2048, temperature=0.7):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    try:
        resp = httpx.post(API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def get_key():
    import os
    for k in ["GROQ_API_KEY", "OPENAI_API_KEY"]:
        v = os.environ.get(k)
        if v:
            return v
    return ""

print("\n" + "="*50)
print("  Qwen/Groq Chat - No ML Needed")
print("="*50)

print("\nChoose model:")
for k, v in MODELS.items():
    print(f"  {k}. {v}")
choice = input("\nModel (1-4) [1]: ").strip() or "1"
model = MODELS.get(choice, MODELS["1"])

key = get_key()
if not key:
    key = input("\nEnter your Groq API key: ").strip()
    if key:
        print("  (Save for later: export GROQ_API_KEY=your-key)")

if not key:
    print("\nNo API key. Get one FREE at: https://console.groq.com/keys")
    sys.exit(1)

print(f"\n  Model: {model}")
print("="*50)
print("  Type 'quit' to exit, 'clear' to reset\n")

messages = []
while True:
    try:
        prompt = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")
        break
    
    if prompt.lower() in ("quit", "exit", "q"):
        break
    if prompt.lower() == "clear":
        messages = []
        print("Chat cleared.")
        continue
    if not prompt:
        continue
    
    messages.append({"role": "user", "content": prompt})
    print(f"\nAI: ", end="", flush=True)
    response = chat(key, messages, model)
    print(response)
    messages.append({"role": "assistant", "content": response})
    print()
