#!/usr/bin/env python3
"""
Qwen Chat - Free API access via various providers
Works on Termux/Android with no ML dependencies
"""

import sys
import json
import httpx

PROVIDERS = {
    "1": {"name": "DashScope",     "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", "models": ["qwen-turbo", "qwen-plus", "qwen-max"]},
    "2": {"name": "OpenRouter",    "url": "https://openrouter.ai/api/v1/chat/completions",                     "models": ["qwen/qwen-2.5-72b-instruct"]},
    "3": {"name": "Groq",          "url": "https://api.groq.com/openai/v1/chat/completions",                    "models": ["llama-3.1-70b", "mixtral-8x7b"]},
    "4": {"name": "Custom",        "url": "", "models": []},
}

def get_api_key():
    import os
    # Try common env vars
    for key in ["DASHSCOPE_API_KEY", "OPENROUTER_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY"]:
        if os.environ.get(key):
            return os.environ[key]
    # Try git config for stored key
    return input("\nEnter API key: ").strip()

def chat(provider, messages, api_key, model, max_tokens=2048, temperature=0.7):
    url = provider["url"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    try:
        resp = httpx.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except httpx.HTTPError as e:
        return f"\n[HTTP Error {resp.status_code}]: {resp.text}"
    except Exception as e:
        return f"\nError: {e}"

def main():
    print("\n" + "="*50)
    print("  Qwen Chat - API Runner (No ML Needed)")
    print("="*50)
    
    print("\nChoose provider:")
    for k, v in PROVIDERS.items():
        print(f"  {k}. {v['name']}")
    
    choice = input("\nProvider (1-4) [1]: ").strip() or "1"
    provider = PROVIDERS.get(choice, PROVIDERS["1"])
    
    api_key = get_api_key()
    if not api_key:
        print("No API key. Exiting.")
        sys.exit(1)
    
    model = provider["models"][0] if provider["models"] else input("Model name: ")
    
    print(f"\n  Provider: {provider['name']}")
    print(f"  Model:    {model}")
    print("="*50)
    print("  Type 'quit' to exit, 'clear' to reset chat\n")
    
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
        response = chat(provider, messages, api_key, model)
        print(response)
        messages.append({"role": "assistant", "content": response})
        print()

if __name__ == "__main__":
    main()
