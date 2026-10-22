import json

from app.agents.rag_agent import RAGAgent


def main():
    agent = RAGAgent()

    questions = [
        "How quickly must a customer complaint be escalated?",
        "What waiting times should customers expect during busy periods?",
        "What CSAT score triggers a root-cause review?",
    ]

    for question in questions:
        result = agent.run(question, top_k=3)

        print("\n" + "=" * 80)
        print(f"QUESTION: {question}")
        print("=" * 80)

        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()