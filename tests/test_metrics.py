import pytest

from app.tools.metrics import (
    compute_csat,
    compute_average_rating,
    count_responses,
)


@pytest.fixture
def sample_responses():
    return [
        {"rating": 1, "free_text": "Very bad"},
        {"rating": 2, "free_text": "Not good"},
        {"rating": 3, "free_text": "Average"},
        {"rating": 4, "free_text": "Good"},
        {"rating": 5, "free_text": "Excellent"},
    ]


def test_compute_csat(sample_responses):
    assert compute_csat(sample_responses) == 40.0


def test_compute_average_rating(sample_responses):
    assert compute_average_rating(sample_responses) == 3.0


def test_count_responses(sample_responses):
    assert count_responses(sample_responses) == 5


def test_empty_responses():
    assert compute_csat([]) == 0.0
    assert compute_average_rating([]) == 0.0
    assert count_responses([]) == 0


def test_invalid_ratings_are_ignored():
    responses = [
        {"rating": 5},
        {"rating": 3},
        {"rating": 0},
        {"rating": 6},
        {"rating": "5"},
        {"rating": True},
    ]

    assert compute_csat(responses) == 50.0
    assert compute_average_rating(responses) == 4.0
    assert count_responses(responses) == 2