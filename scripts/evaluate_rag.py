import json
from pathlib import Path

from app.agents.orchestrator import Orchestrator


QUESTIONS = [
    "How quickly must a customer complaint be escalated?",
    "What waiting times should customers expect during busy periods?",
    "What CSAT score triggers a root-cause review?",
]


def main():
    orchestrator = Orchestrator()
    evaluation_results = []

    for question in QUESTIONS:
        print("\n" + "=" * 90)
        print(f"QUESTION: {question}")
        print("=" * 90)

        result = orchestrator.run(question=question)

        retrieval = result.get("retrieval", {})
        chunks = retrieval.get("retrieved_chunks", [])

        print("\nRETRIEVED FAQ CHUNKS")
        print("-" * 90)

        for index, chunk in enumerate(chunks, start=1):
            print(f"\nChunk {index}")
            print(f"Source: {chunk.get('source')}")
            print(f"Chunk index: {chunk.get('chunk_index')}")
            print(f"Cosine distance: {chunk.get('distance')}")
            print(f"Text:\n{chunk.get('text')}")

        summary = result.get("summary", {})
        final_answer = summary.get("answer", "")

        print("\nFINAL ANSWER")
        print("-" * 90)
        print(final_answer)

        evaluation_results.append(
            {
                "question": question,
                "retrieved_chunks": chunks,
                "final_answer": final_answer,
            }
        )

    output_path = Path("data/rag_evaluation_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(
            evaluation_results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 90)
    print(f"Evaluation results saved to: {output_path.resolve()}")
    print(f"Questions evaluated: {len(evaluation_results)}")


if __name__ == "__main__":
    main()