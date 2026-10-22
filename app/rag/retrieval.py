import chromadb
from sentence_transformers import SentenceTransformer

from app.rag.ingestion import (
    COLLECTION_NAME,
    DEFAULT_MODEL,
)


class FAQRetriever:
    """Retrieve semantically relevant FAQ chunks."""

    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        model_name: str = DEFAULT_MODEL,
    ):
        self.model = SentenceTransformer(model_name)

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_collection(
            name=COLLECTION_NAME
        )

    def retrieve(
        self,
        question: str,
        top_k: int = 3,
    ) -> list[dict]:
        """Return the most relevant FAQ chunks for a question."""

        if not question.strip():
            raise ValueError("Question cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        collection_size = self.collection.count()

        if collection_size == 0:
            return []

        query_embedding = self.model.encode(
            question,
            normalize_embeddings=True,
        )

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(top_k, collection_size),
            include=["documents", "metadatas", "distances"],
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved_chunks = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved_chunks.append(
                {
                    "text": document,
                    "source": metadata.get("source", "unknown"),
                    "chunk_index": metadata.get("chunk_index"),
                    "distance": float(distance),
                }
            )

        return retrieved_chunks