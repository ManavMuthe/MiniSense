from app.agents.data_agent import DataAgent
from app.schemas import TaskSpec


agent = DataAgent("data/survey_responses.json")

task = TaskSpec(
    task_type="metrics",
    question="Analyze customer satisfaction for June 2026.",
    start_date="2026-06-01",
    end_date="2026-06-30",
    metrics=[
        "response_count",
        "csat",
        "average_rating",
        "top_themes",
    ],
)

result = agent.run(task)

print("\n--- MiniSense DataAgent Results ---")
print(result.model_dump_json(indent=2))