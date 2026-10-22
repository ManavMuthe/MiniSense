from app.rag.ingestion import ingest_faq


if __name__ == "__main__":
    chunk_count = ingest_faq()

    print(f"\nFAQ ingestion completed: {chunk_count} chunks indexed.")