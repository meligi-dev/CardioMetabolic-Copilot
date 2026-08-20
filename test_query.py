import weaviate
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from backend.app.config import config
from backend.app.retrieval.weaviate_retriever import WeaviateRetriever

print("Connecting to Weaviate with configured timeouts...")
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=config.WEAVIATE_URL,
    auth_credentials=Auth.api_key(config.WEAVIATE_API_KEY),
    additional_config=AdditionalConfig(
        timeout=Timeout(init=45, query=45, insert=60)
    ),
    skip_init_checks=True
)

col = client.collections.get(config.COLLECTION_NAME)
count = len(col)
print(f"Total objects in Weaviate collection '{config.COLLECTION_NAME}': {count}")

# Test a hybrid search query
retriever = WeaviateRetriever()
results = retriever.hybrid_search("What is recommended for T2D with heart failure and reduced ejection fraction?")
print(f"\nRetrieved {len(results)} chunks for test query:")
for r in results[:3]:
    print(f"- [{r['guideline']}] {r['header_breadcrumb']} (Score: {r['score']:.4f})")
    print(f"  Rec ID: {r['recommendation_id']} | Evidence: {r['class_of_recommendation']}, {r['evidence_level']}")
    print(f"  Snippet: {r['content'][:140]}...")

retriever.close()
client.close()
