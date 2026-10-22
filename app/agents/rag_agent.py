from app.rag.retrieval import FAQRetriever


class RAGAgent:
    """Agent responsible for retrieving business FAQ information."""

    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
    ):
        self.retriever = FAQRetriever(
            persist_directory=persist_directory
        )

    def run(
        self,
        question: str,
        top_k: int = 3,
    ) -> dict:
        """Return structured retrieval results."""

        chunks = self.retriever.retrieve(
            question=question,
            top_k=top_k,
        )

        return {
            "agent": "RAGAgent",
            "question": question,
            "retrieved_chunks": chunks,
            "retrieval_count": len(chunks),
        }