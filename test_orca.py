import httpx
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

providers = [
    ("OpenRouter (with custom headers)", "https://openrouter.ai/api/v1/chat/completions", {"HTTP-Referer": "http://localhost:3000", "X-Title": "Medical RAG"}),
    ("Together AI", "https://api.together.xyz/v1/chat/completions", {}),
    ("Groq", "https://api.groq.com/openai/v1/chat/completions", {}),
    ("Fireworks", "https://api.fireworks.ai/inference/v1/chat/completions", {}),
    ("Hyperbolic", "https://api.hyperbolic.xyz/v1/chat/completions", {}),
    ("DeepInfra", "https://api.deepinfra.com/v1/openai/chat/completions", {}),
    ("SambaNova", "https://api.sambanova.ai/v1/chat/completions", {}),
]

for name, url, extra_headers in providers:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **extra_headers
    }
    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }
    try:
        r = httpx.post(url, json=payload, headers=headers, timeout=5.0)
        print(f"[{name}] status={r.status_code}, body={r.text[:120]}")
    except Exception as e:
        print(f"[{name}] error={e}")
