from datetime import date

from app.agents.summary_agent import SummaryAgent
from app.agents.comparison_agent import ComparisonAgent
from app.agents.data_agent import DataAgent
from app.agents.rag_agent import RAGAgent
from app.schemas import TaskSpec


class Orchestrator:
    """
    Plans and coordinates the survey-analysis agents.

    This initial implementation uses deterministic routing rules.
    """

    def __init__(
        self,
        data_path="data/survey_responses.json",
        persist_directory="data/chroma_db",
    ):
        self.data_agent = DataAgent(data_path=data_path)
        self.summary_agent = SummaryAgent()
        self.comparison_agent = ComparisonAgent(data_path=data_path)
        self.rag_agent = RAGAgent(
            persist_directory=persist_directory
        )

    def run(
        self,
        question: str,
        business_id: str | None = None,
        start_date: str = "2026-05-01",
        end_date: str = "2026-06-30",
    ) -> dict:
        """
        Route a business question to the appropriate agents.
        """

        if not question.strip():
            raise ValueError("Question cannot be empty")

        # Validate the supplied date range.
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        if start > end:
            raise ValueError("start_date must be before end_date")

        question_lower = question.lower()

        # Step 1: Determine whether the question requests
        # a comparison between two months.
        comparison_keywords = (
            "compare",
            "comparison",
            "versus",
            "vs",
            "change",
            "decline",
            "improve",
            "trend",
        )

        needs_comparison = any(
            keyword in question_lower
            for keyword in comparison_keywords
        )

        # Step 2: Always calculate metrics for the requested range.
        metrics_result = self.data_agent.run(
            TaskSpec(
                task_type="metrics",
                question=question,
                start_date=start_date,
                end_date=end_date,
                business_id=business_id,
                metrics=[
                    "response_count",
                    "csat",
                    "average_rating",
                    "top_themes",
                ],
            )
        )

        results = {
            "question": question,
            "business_id": business_id,
            "metrics": metrics_result.model_dump(),
        }

        # Step 3: Run the comparison agent when appropriate.
        if needs_comparison:
            comparison_result = self.comparison_agent.run(
                previous_start="2026-05-01",
                previous_end="2026-05-31",
                current_start="2026-06-01",
                current_end="2026-06-30",
                business_id=business_id,
            )

            results["comparison"] = comparison_result.model_dump()

        # Step 4: Retrieve business policy and FAQ context.
        rag_result = self.rag_agent.run(
            question=question,
            top_k=3,
        )

        results["retrieval"] = rag_result

        # Synthesize the collected evidence into a business answer.
        summary_result = self.summary_agent.run(
            question=question,
            evidence=results,
        )

        results["summary"] = summary_result

        return results

        