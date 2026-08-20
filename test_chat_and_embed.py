import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")

client = OpenAI(api_key=api_key, base_url=base_url)

# Test chat completion first with Qwen 3.8
print("Testing Chat Completion with Qwen 3.8 on OpenRouter...")
try:
    resp = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": "Hello, answer in 5 words."}],
        max_tokens=20
    )
    print("Chat Completion Success:", resp.choices[0].message.content)
except Exception as e:
    print("Chat Completion Error:", e)

# Test embedding with OpenRouter models
print("\nTesting OpenRouter Embedding Models...")
for embed_m in ["text-embedding-3-small", "openai/text-embedding-3-small", "baai/bge-small-en-v1.5"]:
    try:
        res = client.embeddings.create(model=embed_m, input=["Hello world"])
        print(f"Embedding Success with {embed_m}! Dim: {len(res.data[0].embedding)}")
        break
    except Exception as e:
        print(f"Failed {embed_m}: {e}")
