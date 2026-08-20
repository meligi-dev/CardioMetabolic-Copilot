import os
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv

load_dotenv()

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

print(f"Connecting to Weaviate: {weaviate_url}")

try:
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key)
    )
    is_ready = client.is_ready()
    print(f"Weaviate Connection Success! Is Ready: {is_ready}")
    print("Existing Collections:", [c for c in client.collections.list_all().keys()])
    client.close()
except Exception as e:
    print(f"Connection failed: {e}")
