from typing import List, Dict, Any, Optional
import weaviate
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from weaviate.classes.query import MetadataQuery
from backend.app.config import config
from backend.app.ingestion.fast_embedder import FastGuidelineEmbedder

class WeaviateRetriever:
    def __init__(self):
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=config.WEAVIATE_URL,
            auth_credentials=Auth.api_key(config.WEAVIATE_API_KEY),
            additional_config=AdditionalConfig(
                timeout=Timeout(init=45, query=45, insert=60)
            ),
            skip_init_checks=True
        )
        self.embedder = FastGuidelineEmbedder(dim=384)
        self.collection_name = config.COLLECTION_NAME

    def hybrid_search(
        self,
        query: str,
        alpha: float = 0.65,
        limit: int = 6,
        include_parent_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Executes native hybrid search (BM25 + Vector) in Weaviate Cloud.
        Small-to-Big Retrieval: Returns child matches enriched with parent context.
        """
        collection = self.client.collections.get(self.collection_name)
        query_vector = self.embedder.encode(query)[0]

        response = collection.query.hybrid(
            query=query,
            vector=query_vector,
            alpha=alpha,
            limit=limit,
            return_metadata=MetadataQuery(score=True, explain_score=True)
        )

        results = []
        for obj in response.objects:
            props = obj.properties
            score = obj.metadata.score if obj.metadata else 0.0
            
            chunk_data = {
                "id": str(obj.uuid),
                "score": score,
                "content": props.get("content", ""),
                "header_breadcrumb": props.get("header_breadcrumb", ""),
                "guideline": props.get("guideline", ""),
                "year": props.get("year", 2024),
                "chapter_num": props.get("chapter_num", 0),
                "chapter_title": props.get("chapter_title", ""),
                "section_title": props.get("section_title", ""),
                "recommendation_id": props.get("recommendation_id", ""),
                "evidence_level": props.get("evidence_level", ""),
                "class_of_recommendation": props.get("class_of_recommendation", ""),
                "target_conditions": props.get("target_conditions", []),
                "parent_id": props.get("parent_id", ""),
                "is_table": props.get("is_table", False),
            }

            if include_parent_context and props.get("parent_content"):
                chunk_data["parent_context"] = props.get("parent_content")
            else:
                chunk_data["parent_context"] = props.get("content", "")

            results.append(chunk_data)

        return results

    def close(self):
        self.client.close()
