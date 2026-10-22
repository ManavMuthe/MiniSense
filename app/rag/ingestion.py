from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "minisense_faq"


def split_into_chunks(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[str]:
    """Split text into overlapping character-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def ingest_faq(
    faq_path: str = "data/product_faq.txt",
    persist_directory: str = "data/chroma_db",
    model_name: str = DEFAULT_MODEL,
) -> int:
    """Load the FAQ, generate embeddings, and store them in ChromaDB."""

    faq_file = Path(faq_path)

    if not faq_file.exists():
        raise FileNotFoundError(
            f"FAQ file not found: {faq_file.resolve()}"
        )

    text = faq_file.read_text(encoding="utf-8")
    chunks = split_into_chunks(text)

    if not chunks:
        raise ValueError("The FAQ file contains no usable text")

    model = SentenceTransformer(model_name)

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    client = chromadb.PersistentClient(
        path=persist_directory
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Upsert makes repeated ingestion safe for unchanged chunk IDs.
    collection.upsert(
        ids=[f"faq_chunk_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "source": faq_file.name,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ],
    )

    print(f"FAQ source: {faq_file.resolve()}")
    print(f"Chunks processed: {len(chunks)}")
    print(f"ChromaDB directory: {Path(persist_directory).resolve()}")

    return len(chunks)