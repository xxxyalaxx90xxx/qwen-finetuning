#!/usr/bin/env python3
"""
Qwen Chat - OpenRouter Provider
No ML, no compilation, works on Termux/Android
"""

import sys
import os
import httpx

API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "1": "qwen/qwen-2.5-72b-instruct",
    "2": "qwen/qwen-2.5-coder-32b-instruct",
    "3": "qwen/qwen-max",
    "4": "qwen/qwen-plus",
}

def chat(api_key, messages, model, max_tokens=2048, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://termux.com",
        "X-Title": "Termux Qwen Chat",
    }
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    try:
        resp = httpx.post(API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

print("\n" + "="*50)
print("  Qwen Chat - OpenRouter")
print("="*50)

print("\nChoose model:")
for k, v in MODELS.items():
    print(f"  {k}. {v}")
choice = input("\nModel (1-4) [1]: ").strip() or "1"
model = MODELS.get(choice, MODELS["1"])

api_key = os.environ.get("OPENROUTER_API_KEY", "")
if not api_key:
    print("\nGet a FREE key at: https://openrouter.ai/keys")
    api_key = input("Enter OpenRouter API key: ").strip()
    if api_key:
        print("  (Save: export OPENROUTER_API_KEY=your-key)")

if not api_key:
    print("\nNo API key. Exiting.")
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
    print(f"\nQwen: ", end="", flush=True)
    response = chat(api_key, messages, model)
    print(response)
    messages.append({"role": "assistant", "content": response})
    print()
