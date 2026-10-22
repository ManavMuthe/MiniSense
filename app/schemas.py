from typing import Literal

from pydantic import BaseModel, Field


class TaskSpec(BaseModel):
    """Structured instruction sent to an agent."""

    task_type: Literal[
        "metrics",
        "comparison",
        "retrieval",
        "summary",
    ]

    question: str

    start_date: str | None = None
    end_date: str | None = None

    business_id: str | None = None

    metrics: list[str] = Field(
        default_factory=lambda: [
            "response_count",
            "csat",
            "average_rating",
            "top_themes",
        ]
    )


class ThemeCount(BaseModel):
    """Count for one identified feedback theme."""

    theme: str
    count: int


class DataMetrics(BaseModel):
    """Structured output returned by the DataAgent."""

    response_count: int

    csat_percentage: float

    average_rating: float

    top_themes: list[ThemeCount]

    period_start: str | None = None
    period_end: str | None = None

    business_id: str | None = None