from collections import Counter
from typing import Any


def compute_csat(responses: list[dict[str, Any]]) -> float:
    """
    Calculate CSAT as the percentage of responses
    with a rating of 4 or 5.
    """
    valid_responses = [
        response
        for response in responses
        if isinstance(response.get("rating"), int)
        and not isinstance(response.get("rating"), bool)
        and 1 <= response["rating"] <= 5
    ]

    if not valid_responses:
        return 0.0

    satisfied = sum(
        response["rating"] >= 4
        for response in valid_responses
    )

    return round(
        satisfied / len(valid_responses) * 100,
        2,
    )


def compute_average_rating(
    responses: list[dict[str, Any]],
) -> float:
    """Calculate the average of valid survey ratings."""
    valid_ratings = [
        response["rating"]
        for response in responses
        if isinstance(response.get("rating"), int)
        and not isinstance(response.get("rating"), bool)
        and 1 <= response["rating"] <= 5
    ]

    if not valid_ratings:
        return 0.0

    return round(sum(valid_ratings) / len(valid_ratings), 2)


def count_responses(
    responses: list[dict[str, Any]],
) -> int:
    """Count the number of records with valid ratings."""
    return sum(
        1
        for response in responses
        if isinstance(response.get("rating"), int)
        and not isinstance(response.get("rating"), bool)
        and 1 <= response["rating"] <= 5
    )


def identify_themes(
    responses: list[dict[str, Any]],
) -> dict[str, int]:
    """
    Identify themes using transparent keyword rules.

    This is a baseline classifier, not an LLM or
    a semantic text classifier.
    """
    theme_keywords = {
        "wait_time": [
            "wait",
            "waiting",
            "queue",
            "slow",
            "promptly",
            "quick",
        ],
        "food_quality": [
            "food",
            "meal",
            "ingredients",
            "flavor",
            "fresh",
            "taste",
        ],
        "staff_behavior": [
            "staff",
            "employee",
            "employees",
        ],
        "cleanliness": [
            "clean",
            "cleanliness",
            "hygiene",
            "dirty",
        ],
        "pricing": [
            "price",
            "pricing",
            "expensive",
            "value",
        ],
        "order_accuracy": [
            "order",
            "missing",
            "incorrect",
            "wrong",
        ],
    }

    theme_counts: Counter[str] = Counter()

    for response in responses:
        text = response.get("free_text", "").lower()

        matched_themes = [
            theme
            for theme, keywords in theme_keywords.items()
            if any(keyword in text for keyword in keywords)
        ]

        # Count each response once per matched theme.
        for theme in matched_themes:
            theme_counts[theme] += 1

    return dict(
        theme_counts.most_common()
    )