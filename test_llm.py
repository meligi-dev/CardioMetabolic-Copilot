import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLM_API_KEY")

endpoints_to_test = [
    ("Orca default", "https://api.orca.com/v1"),
    ("OpenRouter", "https://openrouter.ai/api/v1"),
    ("OpenAI Direct", "https://api.openai.com/v1"),
]

for name, base_url in endpoints_to_test:
    print(f"\nTesting endpoint: {name} ({base_url})")
    try:
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0)
        # Try listing models or simple completion
        models = client.models.list()
        print(f"Success! Found models: {[m.id for m in models.data[:5]]}")
        break
    except Exception as e:
        print(f"Failed with {name}: {e}")
