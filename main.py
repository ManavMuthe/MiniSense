from app.agents.orchestrator import Orchestrator


def main():
    print("=" * 70)
    print("MiniSense - Multi-Agent Survey Analysis System")
    print("=" * 70)

    question = input(
        "\nEnter your business question: "
    ).strip()

    if not question:
        print("Error: Please enter a business question.")
        return

    try:
        orchestrator = Orchestrator()
        result = orchestrator.run(question)

        print("\n" + "=" * 70)
        print("FINAL BUSINESS ANSWER")
        print("=" * 70)
        summary = result["summary"]

        if isinstance(summary, dict):
            print(summary.get("answer", summary))
        else:
            print(summary)

        print("\n" + "=" * 70)
        print("SUPPORTING METRICS")
        print("=" * 70)

        metrics = result["metrics"]

        print(f"Responses: {metrics['response_count']}")
        print(f"CSAT: {metrics['csat_percentage']:.2f}%")
        print(f"Average rating: {metrics['average_rating']:.2f}/5")

        print("\nTop feedback themes:")
        for theme in metrics["top_themes"]:
            print(f"  - {theme['theme']}: {theme['count']}")

        if "comparison" in result:
            print("\nPeriod comparison:")
            for comparison in result["comparison"]["comparisons"]:
                print(
                    f"  - {comparison['metric']}: "
                    f"{comparison['previous_value']} -> "
                    f"{comparison['current_value']} "
                    f"(change: {comparison['change']})"
                )

        retrieval = result.get("retrieval", {})
        chunks = retrieval.get("retrieved_chunks", [])

        print(f"\nFAQ chunks retrieved: {len(chunks)}")

    except Exception as exc:
        print(f"\nError while analyzing the survey: {exc}")


if __name__ == "__main__":
    main()