from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from src.datasource.vector import ChromaClient

class SearchResult(BaseModel):
    entity_id: str
    metadata: dict
    score: float


class VectorRepository:
    def __init__(self, collection_name: str = None):
        self.client = ChromaClient()
        self.collection = self.client.get_or_create_collection(
            collection_name or "default_collection")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embedding(self, text: str) -> list:
        """Generate an embedding from a given text representation."""
        return self.embedding_model.encode(text).tolist()

    def add_vector(self, entity_id: str, entity_data: dict):
        """Add a new entity with an embedding to ChromaDB."""
        text_representation = " ".join(str(v) for v in entity_data.values())
        embedding = self.generate_embedding(text_representation)
        self.collection.add(ids=[entity_id], embeddings=[embedding], metadatas=[entity_data])

    def update_vector(self, entity_id: str, updated_data: dict):
        """Update an existing entity by replacing its vector and metadata."""
        # Step 1: Delete old entry if it exists
        existing = self.collection.get(ids=[entity_id])
        if existing and "ids" in existing and existing["ids"]:
            self.collection.delete(ids=[entity_id])

        # Step 2: Insert new updated data
        self.add_vector(entity_id, updated_data)

    def query_vectors(self, query_text: str, n_results: int = 1):
        """Search for similar vectors."""
        query_embedding = self.generate_embedding(query_text)
        return self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

    def query_vectors_v2(self, query_text: str, n_results: int = 1, min_score: float = 0.8) -> list[SearchResult]:
        query_embedding = self.generate_embedding(query_text)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

        # Convert results into SearchResult objects & filter by score
        search_results = []
        for i in range(len(results["ids"][0])):
            entity_id = results["ids"][0][i]
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            similarity_score = 1 - distance

            if similarity_score >= min_score:  # Filter by score
                search_results.append(SearchResult(
                    entity_id=entity_id,
                    metadata=metadata,
                    score=round(similarity_score, 4)
                ))

        return search_results
