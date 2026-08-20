import os
import glob
from typing import List, Dict, Any
import weaviate
from weaviate.classes.init import Auth
import weaviate.classes.config as wvc
from backend.app.config import config
from backend.app.ingestion.hierarchical_chunker import HierarchicalChunker
from backend.app.ingestion.fast_embedder import FastGuidelineEmbedder

class WeaviateIndexer:
    def __init__(self):
        print(f"Connecting to Weaviate Cloud: {config.WEAVIATE_URL}...")
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=config.WEAVIATE_URL,
            auth_credentials=Auth.api_key(config.WEAVIATE_API_KEY)
        )
        print("Weaviate connected successfully.")
        self.embedder = FastGuidelineEmbedder(dim=384)
        self.chunker = HierarchicalChunker()

    def create_schema(self, recreate: bool = True):
        collection_name = config.COLLECTION_NAME
        
        # Check existing collections on free cluster (limit is 1 collection)
        existing = list(self.client.collections.list_all().keys())
        print(f"Current collections on Weaviate Cloud: {existing}")
        
        if recreate:
            for old_col in existing:
                print(f"Deleting previous collection '{old_col}' to free quota slot...")
                self.client.collections.delete(old_col)

        print(f"Creating collection: {collection_name}")
        self.client.collections.create(
            name=collection_name,
            inverted_index_config=wvc.Configure.inverted_index(
                bm25_b=0.75,
                bm25_k1=1.2,
                index_null_state=True
            ),
            properties=[
                wvc.Property(name="content", data_type=wvc.DataType.TEXT, index_searchable=True),
                wvc.Property(name="header_breadcrumb", data_type=wvc.DataType.TEXT, index_searchable=True),
                wvc.Property(name="guideline", data_type=wvc.DataType.TEXT, index_filterable=True),
                wvc.Property(name="year", data_type=wvc.DataType.INT, index_filterable=True),
                wvc.Property(name="chapter_num", data_type=wvc.DataType.INT, index_filterable=True),
                wvc.Property(name="chapter_title", data_type=wvc.DataType.TEXT),
                wvc.Property(name="section_title", data_type=wvc.DataType.TEXT),
                wvc.Property(name="recommendation_id", data_type=wvc.DataType.TEXT, index_filterable=True),
                wvc.Property(name="evidence_level", data_type=wvc.DataType.TEXT, index_filterable=True),
                wvc.Property(name="class_of_recommendation", data_type=wvc.DataType.TEXT, index_filterable=True),
                wvc.Property(name="target_conditions", data_type=wvc.DataType.TEXT_ARRAY, index_filterable=True),
                wvc.Property(name="parent_id", data_type=wvc.DataType.TEXT),
                wvc.Property(name="parent_content", data_type=wvc.DataType.TEXT),
                wvc.Property(name="is_table", data_type=wvc.DataType.BOOL, index_filterable=True)
            ]
        )
        print(f"Collection '{collection_name}' created successfully on Weaviate Cloud.")

    def index_guidelines(self, data_dir: str):
        md_files = glob.glob(os.path.join(data_dir, "*.md"))
        print(f"Found {len(md_files)} guideline files to index: {[os.path.basename(f) for f in md_files]}")

        all_chunks: List[Dict[str, Any]] = []
        for file in md_files:
            chunks = self.chunker.parse_file(file)
            print(f"Parsed {len(chunks)} chunks from {os.path.basename(file)}")
            all_chunks.extend(chunks)

        print(f"Total chunks extracted: {len(all_chunks)}. Generating embeddings...")
        texts_to_embed = [chunk["content"] for chunk in all_chunks]
        vectors = self.embedder.encode(texts_to_embed)

        collection = self.client.collections.get(config.COLLECTION_NAME)
        print("Ingesting objects into Weaviate...")
        with collection.batch.dynamic() as batch:
            for chunk, vector in zip(all_chunks, vectors):
                batch.add_object(
                    properties=chunk,
                    vector=vector
                )

        print(f"\nSUCCESS! {len(all_chunks)} guideline recommendation units indexed into Weaviate Cloud.")

    def close(self):
        self.client.close()

if __name__ == "__main__":
    indexer = WeaviateIndexer()
    try:
        indexer.create_schema(recreate=True)
        indexer.index_guidelines("data/raw_guidelines")
    finally:
        indexer.close()
