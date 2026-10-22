import pytest

from app.agents.summary_agent import SummaryAgent


@pytest.fixture
def agent():
    return SummaryAgent()


def make_evidence(faq_text):
    return {
        "metrics": {
            "response_count": 100,
            "csat_percentage": 75.0,
            "average_rating": 3.8,
            "top_themes": [],
        },
        "retrieval": {
            "retrieved_chunks": [
                {
                    "text": faq_text,
                    "source": "product_faq.txt",
                    "chunk_index": 0,
                    "distance": 0.3,
                }
            ]
        },
    }


def test_complaint_escalation_answer(agent):
    evidence = make_evidence(
        "Complaints requiring escalation should be "
        "escalated within 15 minutes."
    )

    result = agent.run(
        "How quickly must a customer complaint be escalated?",
        evidence,
    )

    assert result["policy_answered"] is True
    assert "15 minutes" in result["answer"]


def test_peak_waiting_time_answer(agent):
    evidence = make_evidence(
        "During peak periods, the expected waiting time "
        "is approximately 15–20 minutes."
    )

    result = agent.run(
        "What waiting times should customers expect during busy periods?",
        evidence,
    )

    assert result["policy_answered"] is True
    assert "15–20 minutes" in result["answer"]


def test_csat_root_cause_threshold(agent):
    evidence = make_evidence(
        "Scores below 4.0 trigger a root-cause review. "
        "The target customer satisfaction score is 4.5 or higher."
    )

    result = agent.run(
        "What CSAT score triggers a root-cause review?",
        evidence,
    )

    assert result["policy_answered"] is True
    assert "below 4.0" in result["answer"]
    assert "4.5 or higher" in result["answer"]


def test_empty_question_is_rejected(agent):
    with pytest.raises(ValueError):
        agent.run("", make_evidence("Some FAQ content."))