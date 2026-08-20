import httpx
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

url = "https://api.fireworks.ai/inference/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

models_to_test = [
    "accounts/fireworks/models/qwen2p5-72b-instruct",
    "accounts/fireworks/models/qwen2p5-32b-instruct",
    "accounts/fireworks/models/qwen2p5-14b-instruct",
    "accounts/fireworks/models/qwen2p5-7b-instruct",
    "accounts/fireworks/models/llama-v3p1-70b-instruct",
    "accounts/fireworks/models/llama-v3p1-8b-instruct"
]

for model in models_to_test:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello, respond with 3 words."}],
        "max_tokens": 15
    }
    r = httpx.post(url, json=payload, headers=headers, timeout=10.0)
    print(f"Model: {model} -> Status: {r.status_code}, Resp: {r.text[:100]}")
    if r.status_code == 200:
        print(f"SUCCESS! Working model found: {model}")
        break
