import json

from app.agents.orchestrator import Orchestrator


def main():
    orchestrator = Orchestrator()

    question = (
        "Compare May and June customer satisfaction "
        "and explain what the business should investigate."
    )

    result = orchestrator.run(
        question=question,
    )

    print("\nMINISENSE ORCHESTRATOR RESULTS")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()