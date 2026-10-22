import json
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


# -----------------------------
# Configuration
# -----------------------------

NUM_RESPONSES = 50_000
RANDOM_SEED = 42

START_DATE = date(2026, 5, 1)
END_DATE = date(2026, 6, 30)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "survey_responses.json"
)

random.seed(RANDOM_SEED)


# -----------------------------
# Synthetic business data
# -----------------------------

BUSINESSES = [
    {
        "business_id": "b01",
        "business_name": "GreenLeaf Bistro",
    },
    {
        "business_id": "b02",
        "business_name": "Urban Spoon Cafe",
    },
    {
        "business_id": "b03",
        "business_name": "FreshFork Kitchen",
    },
]

SURVEYS = [
    {
        "survey_id": "s01",
        "survey_name": "Customer Experience",
    },
    {
        "survey_id": "s02",
        "survey_name": "Food Quality",
    },
    {
        "survey_id": "s03",
        "survey_name": "Service Satisfaction",
    },
]

CHANNELS = [
    "mobile",
    "web",
    "email",
    "in_store",
]

# Theme-specific feedback helps us validate our analysis.
FEEDBACK = {
    "food_quality": {
        "positive": [
            "The food was fresh and delicious.",
            "The meal tasted excellent and was well prepared.",
            "Loved the quality and presentation of the food.",
            "The ingredients tasted fresh and flavorful.",
        ],
        "neutral": [
            "The food was average and could be improved.",
            "The meal was okay but nothing special.",
            "The food quality was acceptable.",
        ],
        "negative": [
            "The food was cold when it arrived.",
            "The meal tasted stale and lacked flavor.",
            "The food quality was disappointing.",
            "My order was poorly prepared.",
        ],
    },
    "wait_time": {
        "positive": [
            "The service was quick and there was almost no wait.",
            "My order arrived promptly.",
            "The waiting time was shorter than expected.",
        ],
        "neutral": [
            "The wait was reasonable but could be shorter.",
            "The service took a little longer than expected.",
        ],
        "negative": [
            "The waiting time was too long.",
            "I waited a long time for my order.",
            "Service was extremely slow during the visit.",
            "The queue was long and the order took forever.",
        ],
    },
    "staff_behavior": {
        "positive": [
            "The staff were friendly and helpful.",
            "The employees were polite and attentive.",
            "The staff made the experience enjoyable.",
        ],
        "neutral": [
            "The staff were okay but not particularly attentive.",
            "The service was acceptable.",
        ],
        "negative": [
            "The staff were rude and unhelpful.",
            "Employees ignored my request.",
            "The staff could have been more professional.",
        ],
    },
    "cleanliness": {
        "positive": [
            "The restaurant was clean and comfortable.",
            "The dining area was spotless.",
        ],
        "neutral": [
            "The cleanliness was acceptable.",
            "The dining area could be maintained better.",
        ],
        "negative": [
            "The table was dirty when I arrived.",
            "The dining area was not properly cleaned.",
            "The restaurant needed better hygiene.",
        ],
    },
    "pricing": {
        "positive": [
            "The prices were reasonable for the quality.",
            "Great value for money.",
        ],
        "neutral": [
            "The pricing was fair but could be better.",
            "The prices were average.",
        ],
        "negative": [
            "The prices were too expensive.",
            "The meal was not worth the price.",
            "I expected better value for money.",
        ],
    },
    "order_accuracy": {
        "positive": [
            "My order was accurate and complete.",
            "Everything I ordered arrived correctly.",
        ],
        "neutral": [
            "One small detail in the order could be improved.",
            "The order was mostly correct.",
        ],
        "negative": [
            "My order was incorrect.",
            "Several items were missing from my order.",
            "I received the wrong meal.",
        ],
    },
}

# Probability distributions by theme.
# These are synthetic assumptions, not real customer measurements.
BASE_THEME_WEIGHTS = {
    "food_quality": 0.25,
    "wait_time": 0.20,
    "staff_behavior": 0.18,
    "cleanliness": 0.12,
    "pricing": 0.13,
    "order_accuracy": 0.12,
}

RATING_WEIGHTS = {
    "positive": [0.02, 0.03, 0.10, 0.35, 0.50],
    "neutral": [0.03, 0.12, 0.50, 0.25, 0.10],
    "negative": [0.45, 0.30, 0.15, 0.07, 0.03],
}


# -----------------------------
# Helper functions
# -----------------------------

def get_dates():
    """Return every date in the configured inclusive date range."""
    days = (END_DATE - START_DATE).days

    return [
        START_DATE + timedelta(days=offset)
        for offset in range(days + 1)
    ]


def choose_theme(response_date):
    """
    Select a feedback theme.

    Waiting-time complaints are deliberately more common in June.
    """
    weights = BASE_THEME_WEIGHTS.copy()

    if response_date.month == 6:
        weights["wait_time"] += 0.15

        # Keep probabilities normalized.
        total = sum(weights.values())
        weights = {
            theme: weight / total
            for theme, weight in weights.items()
        }

    themes = list(weights.keys())
    probabilities = list(weights.values())

    return random.choices(
        themes,
        weights=probabilities,
        k=1,
    )[0]


def choose_sentiment(theme):
    """Select a sentiment using a theme-specific distribution."""
    # Negative feedback is more common for wait times,
    # while food quality has a stronger positive distribution.
    if theme == "wait_time":
        sentiment_weights = [0.45, 0.20, 0.35]
    elif theme == "food_quality":
        sentiment_weights = [0.25, 0.15, 0.60]
    else:
        sentiment_weights = [0.30, 0.20, 0.50]

    sentiments = ["negative", "neutral", "positive"]

    return random.choices(
        sentiments,
        weights=sentiment_weights,
        k=1,
    )[0]


def generate_response(index, dates):
    """Generate one synthetic survey response."""
    response_date = random.choice(dates)
    business = random.choice(BUSINESSES)
    survey = random.choice(SURVEYS)
    channel = random.choice(CHANNELS)

    theme = choose_theme(response_date)
    sentiment = choose_sentiment(theme)

    free_text = random.choice(
        FEEDBACK[theme][sentiment]
    )

    rating = random.choices(
        population=[1, 2, 3, 4, 5],
        weights=RATING_WEIGHTS[sentiment],
        k=1,
    )[0]

    return {
        "response_id": f"r{index:06d}",
        "date": response_date.isoformat(),
        "business_id": business["business_id"],
        "business_name": business["business_name"],
        "survey_id": survey["survey_id"],
        "survey_name": survey["survey_name"],
        "rating": rating,
        "response_channel": channel,
        "free_text": free_text,
        "synthetic_theme": theme,
    }


def validate_responses(responses):
    """Check important dataset invariants before saving."""
    assert len(responses) == NUM_RESPONSES

    response_ids = {
        response["response_id"]
        for response in responses
    }

    assert len(response_ids) == len(responses)

    for response in responses:
        assert 1 <= response["rating"] <= 5

        response_date = date.fromisoformat(
            response["date"]
        )

        assert START_DATE <= response_date <= END_DATE

        assert response["free_text"].strip()


# -----------------------------
# Main generation pipeline
# -----------------------------

def main():
    dates = get_dates()

    responses = [
        generate_response(index, dates)
        for index in range(1, NUM_RESPONSES + 1)
    ]

    validate_responses(responses)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {"responses": responses},
            file,
            indent=2,
            ensure_ascii=False,
        )

    # theme_counts = Counter(
    #     choose_theme_for_existing_response(response)
    #     for response in responses
    # )

    print("Dataset generated successfully.")
    print(f"Total responses: {len(responses)}")
    print(f"Date range: {START_DATE} to {END_DATE}")
    print(f"Output file: {OUTPUT_PATH}")
    print(f"File size: {OUTPUT_PATH.stat().st_size / 1_000_000:.2f} MB")


def choose_theme_for_existing_response(response):
    """
    Infer a theme from the generated text for basic diagnostics.
    """
    text = response["free_text"].lower()

    keywords = {
        "food_quality": ["food", "meal", "ingredients"],
        "wait_time": ["wait", "queue", "slow", "promptly", "quick"],
        "staff_behavior": ["staff", "employees"],
        "cleanliness": ["clean", "hygiene", "table", "dining area"],
        "pricing": ["price", "pricing", "value"],
        "order_accuracy": ["order", "items", "meal"],
    }

    for theme, terms in keywords.items():
        if any(term in text for term in terms):
            return theme

    return "other"


if __name__ == "__main__":
    main()