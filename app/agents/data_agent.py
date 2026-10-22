import json
from pathlib import Path

from app.schemas import DataMetrics, TaskSpec, ThemeCount
from app.tools.metrics import (
    compute_csat,
    compute_average_rating,
    count_responses,
    identify_themes,
)


class DataAgent:
    """Analyze survey data and return validated metrics."""

    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self.responses = self._load_data()

    def _load_data(self) -> list[dict]:
        """Load the survey dataset once when initializing."""
        with self.data_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        responses = data.get("responses")

        if not isinstance(responses, list):
            raise ValueError(
                "Dataset must contain a 'responses' list."
            )

        return responses

    def _filter_responses(
        self,
        task: TaskSpec,
    ) -> list[dict]:
        """Filter records using the structured task."""

        filtered = self.responses

        if task.start_date:
            filtered = [
                response
                for response in filtered
                if response["date"] >= task.start_date
            ]

        if task.end_date:
            filtered = [
                response
                for response in filtered
                if response["date"] <= task.end_date
            ]

        if task.business_id:
            filtered = [
                response
                for response in filtered
                if response["business_id"] == task.business_id
            ]

        return filtered

    def run(self, task: TaskSpec) -> DataMetrics:
        """Execute the requested analysis."""

        if task.task_type != "metrics":
            raise ValueError(
                "DataAgent only supports metrics tasks."
            )

        responses = self._filter_responses(task)

        requested = set(task.metrics)

        response_count = (
            count_responses(responses)
            if "response_count" in requested
            else 0
        )

        csat = (
            compute_csat(responses)
            if "csat" in requested
            else 0.0
        )

        average_rating = (
            compute_average_rating(responses)
            if "average_rating" in requested
            else 0.0
        )

        theme_counts = (
            identify_themes(responses)
            if "top_themes" in requested
            else {}
        )

        top_themes = [
            ThemeCount(
                theme=theme,
                count=count,
            )
            for theme, count in list(theme_counts.items())[:5]
        ]

        return DataMetrics(
            response_count=response_count,
            csat_percentage=csat,
            average_rating=average_rating,
            top_themes=top_themes,
            period_start=task.start_date,
            period_end=task.end_date,
            business_id=task.business_id,
        )