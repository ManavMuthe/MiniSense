import json

from app.agents.comparison_agent import ComparisonAgent


def main():
    agent = ComparisonAgent()

    result = agent.run(
        previous_start="2026-05-01",
        previous_end="2026-05-31",
        current_start="2026-06-01",
        current_end="2026-06-30",
    )

    print("\nMAY VS JUNE COMPARISON")
    print("=" * 60)

    print(
        json.dumps(
            result.model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()