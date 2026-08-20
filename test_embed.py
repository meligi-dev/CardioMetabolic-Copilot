import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")

print(f"Testing embedding via OpenRouter ({base_url})...")
try:
    client = OpenAI(api_key=api_key, base_url=base_url)
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=["Recommendation 10.4: SGLT2 inhibitors and GLP-1 RA in T2D with ASCVD."]
    )
    vec = res.data[0].embedding
    print(f"Embedding Success via OpenRouter API! Vector length: {len(vec)}")
except Exception as e:
    print(f"OpenRouter embedding error: {e}")
    # Try testing fast local embedding
    try:
        print("Testing local sentence-transformers...")
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer("all-MiniLM-L6-v2")
        v = m.encode("test").tolist()
        print(f"Local embedding success! Vector length: {len(v)}")
    except Exception as e2:
        print(f"Local embedding error: {e2}")
