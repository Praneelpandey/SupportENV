"""
grader.py — Deterministic grading function for SupportEnv.

Scoring rules per task:
  classify   → 1.0 if category correct, else 0.0
  prioritize → 0.5 × category_match + 0.5 × priority_match
  resolve    → 0.3 × category_match + 0.3 × priority_match
               + 0.4 × keyword_score  (penalty if reply empty / <10 words)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tasks import Ticket


def grade(
    action_category: str,
    action_priority: str,
    action_reply: str,
    ticket: "Ticket",
    task_name: str,
) -> tuple[float, dict]:
    """
    Return (score, breakdown) where score ∈ [0.0, 1.0].

    Parameters
    ----------
    action_category : str
        The category predicted by the agent.
    action_priority : str
        The priority predicted by the agent.
    action_reply : str
        The reply drafted by the agent.
    ticket : Ticket
        The ground-truth ticket being evaluated.
    task_name : str
        One of "classify", "prioritize", or "resolve".

    Returns
    -------
    tuple[float, dict]
        Final clamped score and detailed breakdown dict.
    """
    breakdown: dict[str, float] = {}

    category_match = 1.0 if action_category.strip().lower() == ticket.true_category.lower() else 0.0
    priority_match = 1.0 if action_priority.strip().lower() == ticket.true_priority.lower() else 0.0

    if task_name == "classify":
        breakdown["category"] = category_match
        score = category_match

    elif task_name == "prioritize":
        breakdown["category"] = category_match * 0.5
        breakdown["priority"] = priority_match * 0.5
        score = breakdown["category"] + breakdown["priority"]

    elif task_name == "resolve":
        breakdown["category"] = category_match * 0.3
        breakdown["priority"] = priority_match * 0.3

        # Reply quality — keyword overlap
        reply_lower = action_reply.strip().lower()
        keywords = ticket.ideal_reply_keywords
        if keywords:
            hits = sum(1 for kw in keywords if kw.lower() in reply_lower)
            keyword_ratio = hits / len(keywords)          # 0.0 – 1.0
        else:
            keyword_ratio = 0.0

        reply_quality = keyword_ratio * 0.4
        breakdown["reply_quality"] = reply_quality

        # Penalty for empty / very short reply
        word_count = len(action_reply.split())
        penalty = 0.0
        if not action_reply.strip() or word_count < 10:
            penalty = -0.1
            breakdown["reply_penalty"] = penalty

        score = breakdown["category"] + breakdown["priority"] + reply_quality + penalty

    else:
        raise ValueError(f"Unknown task: {task_name!r}")

    # Clamp to [0.0, 1.0]
    score = max(0.0, min(1.0, score))
    breakdown["total"] = score
    return score, breakdown
