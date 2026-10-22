import re


class SummaryAgent:
    """
    Produces evidence-grounded business answers from survey metrics,
    period comparisons, and retrieved FAQ content.

    This implementation uses deterministic rules rather than an LLM.
    """

    def run(self, question: str, evidence: dict) -> dict:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        metrics = evidence.get("metrics") or {}
        comparison = evidence.get("comparison") or {}
        retrieval = evidence.get("retrieval") or {}

        chunks = retrieval.get("retrieved_chunks", [])

        faq_context = "\n".join(
            chunk.get("text", "")
            for chunk in chunks
            if chunk.get("text")
        )

        question_lower = question.lower()
        context_lower = faq_context.lower()

        answer_parts = []
        policy_answered = False

        # 1. Summarize available period comparisons.
        comparisons = comparison.get("comparisons", [])

        if comparisons:
            previous_period = comparison.get(
                "previous_period", "previous period"
            )
            current_period = comparison.get(
                "current_period", "current period"
            )

            answer_parts.append(
                f"Comparison of {previous_period} and "
                f"{current_period}:"
            )

            for item in comparisons:
                metric = item.get("metric", "Metric")
                previous = item.get("previous_value")
                current = item.get("current_value")
                change = item.get("change")

                if previous is None or current is None:
                    continue

                if metric.lower() == "csat":
                    answer_parts.append(
                        f"CSAT changed from {previous:.2f}% "
                        f"to {current:.2f}%, a change of "
                        f"{change:+.2f} percentage points."
                    )

                elif metric.lower() == "average rating":
                    answer_parts.append(
                        f"Average rating changed from "
                        f"{previous:.2f} to {current:.2f} "
                        f"out of 5, a change of {change:+.2f}."
                    )

                elif metric.lower() == "response count":
                    answer_parts.append(
                        f"Response count changed from "
                        f"{previous:,.0f} to {current:,.0f}, "
                        f"a change of {change:+,.0f}."
                    )

            csat_comparison = next(
                (
                    item
                    for item in comparisons
                    if item.get("metric", "").lower() == "csat"
                ),
                None,
            )

            if csat_comparison:
                if csat_comparison.get("change", 0) < 0:
                    answer_parts.append(
                        "Customer satisfaction declined during "
                        "the current period and warrants further "
                        "investigation. The comparison alone does "
                        "not establish the cause."
                    )
                elif csat_comparison.get("change", 0) > 0:
                    answer_parts.append(
                        "Customer satisfaction improved during "
                        "the current period. The business should "
                        "identify which changes may have contributed "
                        "to the improvement."
                    )
                else:
                    answer_parts.append(
                        "Customer satisfaction remained unchanged "
                        "between the two periods."
                    )

        # 2. Include general metrics when no comparison is available.
        elif metrics:
            response_count = metrics.get("response_count", 0)
            csat = metrics.get("csat_percentage", 0.0)
            average_rating = metrics.get("average_rating", 0.0)

            answer_parts.append(
                f"The analyzed period contains {response_count:,} "
                f"survey responses. CSAT is {csat:.2f}%, and the "
                f"average rating is {average_rating:.2f} out of 5."
            )

        # 3. Recommend investigations supported by the FAQ.
        asks_for_investigation = any(
            term in question_lower
            for term in (
                "investigate",
                "investigation",
                "root cause",
                "root-cause",
                "why",
                "recommend",
                "should",
                "improve",
            )
        )

        if asks_for_investigation and faq_context:
            investigation_pattern = (
                r"survey feedback should be analyzed for recurring "
                r"themes.*?operational decision-making"
            )

            if re.search(
                investigation_pattern,
                context_lower,
                flags=re.DOTALL,
            ):
                answer_parts.append(
                    "Recommended investigation: examine recurring "
                    "complaints about waiting time, food quality, "
                    "staff behavior, cleanliness, pricing, and order "
                    "accuracy. Compare these themes across both "
                    "periods and investigate relevant business "
                    "locations, survey types, response channels, "
                    "staffing, and preparation workflows. Treat these "
                    "as investigation areas rather than proven causes."
                )
                # 4. Answer complaint escalation questions.
        if any(
            term in question_lower
            for term in ("complaint", "escalation", "escalated")
        ):
            if re.search(
                r"complaints requiring escalation should be "
                r"escalated within 15 minutes",
                context_lower,
            ):
                answer_parts.append(
                    "Complaints requiring escalation must be "
                    "escalated within 15 minutes. Staff should "
                    "record the complaint, action taken, and "
                    "any required follow-up."
                )
                policy_answered = True

        # 5. Answer waiting-time questions.
        if (
            "waiting" in question_lower
            or "wait time" in question_lower
            or "wait times" in question_lower
        ):
            if any(
                term in question_lower
                for term in ("peak", "busy", "busy periods")
            ):
                peak_wait_found = re.search(
                    r"during peak periods, the expected waiting "
                    r"time is approximately 15\s*[–-]\s*20 minutes",
                    context_lower,
                )

                if peak_wait_found:
                    answer_parts.append(
                        "During peak periods, the expected waiting "
                        "time is approximately 15–20 minutes. "
                        "Actual waiting times may vary with order "
                        "volume and operational conditions."
                    )
                    policy_answered = True

            elif re.search(
                r"below 10 minutes during off-peak periods",
                context_lower,
            ):
                answer_parts.append(
                    "GreenLeaf Bistro aims to keep waiting times "
                    "below 10 minutes during off-peak periods."
                )
                policy_answered = True
        # 4. Include relevant CSAT policy when the question concerns
        # satisfaction, its thresholds, or a root-cause review.
        asks_about_csat_policy = any(
            term in question_lower
            for term in (
                "csat",
                "customer satisfaction",
                "root cause",
                "root-cause",
                "satisfaction score",
            )
        )

        if asks_about_csat_policy and faq_context:
            threshold_found = re.search(
                r"scores below 4\.0 trigger a root-cause review",
                context_lower,
            )

            target_found = re.search(
                r"target customer satisfaction score is 4\.5 or higher",
                context_lower,
            )

            if threshold_found or target_found:
                policy_parts = []

                if threshold_found:
                    policy_parts.append(
                        "Scores below 4.0 on the five-point rating "
                        "scale trigger a root-cause review."
                    )

                if target_found:
                    policy_parts.append(
                        "The business's target customer satisfaction "
                        "score is 4.5 or higher."
                    )

                answer_parts.extend(policy_parts)
                policy_answered = True

        if not answer_parts:
            answer_parts.append(
                "The available evidence does not support a "
                "specific answer to this question. Retrieve "
                "relevant survey metrics or FAQ information "
                "before making a recommendation."
            )

        return {
            "agent": "SummaryAgent",
            "question": question,
            "answer": " ".join(answer_parts),
            "faq_chunks_used": len(chunks),
            "policy_answered": policy_answered,
        }