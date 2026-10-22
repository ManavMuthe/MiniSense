from pydantic import BaseModel

from app.agents.data_agent import DataAgent
from app.schemas import TaskSpec


class MetricComparison(BaseModel):
    metric: str
    previous_value: float
    current_value: float
    change: float
    interpretation: str


class ComparisonResult(BaseModel):
    agent: str
    previous_period: str
    current_period: str
    business_id: str | None
    comparisons: list[MetricComparison]


class ComparisonAgent:
    """
    Compares survey metrics across two time periods.

    Uses DataAgent to calculate the metrics for each period,
    then calculates the changes between those results.
    """

    def __init__(self, data_path="data/survey_responses.json"):
        self.data_agent = DataAgent(data_path=data_path)

    def run(
        self,
        previous_start: str,
        previous_end: str,
        current_start: str,
        current_end: str,
        business_id: str | None = None,
    ) -> ComparisonResult:

        metrics_to_calculate = [
            "response_count",
            "csat",
            "average_rating",
        ]

        # Step 1: Calculate metrics for the previous period.
        previous_metrics = self.data_agent.run(
            TaskSpec(
                task_type="metrics",
                question="Calculate survey metrics for the previous period.",
                start_date=previous_start,
                end_date=previous_end,
                business_id=business_id,
                metrics=metrics_to_calculate,
            )
        )

        # Step 2: Calculate metrics for the current period.
        current_metrics = self.data_agent.run(
            TaskSpec(
                task_type="metrics",
                question="Calculate survey metrics for the current period.",
                start_date=current_start,
                end_date=current_end,
                business_id=business_id,
                metrics=metrics_to_calculate,
            )
        )

        # Step 3: Compare the two periods.
        comparisons = []

        metric_definitions = [
            ("response_count", "Response count"),
            ("csat_percentage", "CSAT"),
            ("average_rating", "Average rating"),
        ]

        for field, label in metric_definitions:
            previous_value = float(getattr(previous_metrics, field))
            current_value = float(getattr(current_metrics, field))

            change = round(current_value - previous_value, 2)

            if change > 0:
                interpretation = "increased"
            elif change < 0:
                interpretation = "decreased"
            else:
                interpretation = "remained unchanged"

            comparisons.append(
                MetricComparison(
                    metric=label,
                    previous_value=round(previous_value, 2),
                    current_value=round(current_value, 2),
                    change=change,
                    interpretation=interpretation,
                )
            )

        return ComparisonResult(
            agent="ComparisonAgent",
            previous_period=f"{previous_start} to {previous_end}",
            current_period=f"{current_start} to {current_end}",
            business_id=business_id,
            comparisons=comparisons,
        )