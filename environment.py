"""
environment.py — SupportEnv: an OpenEnv-compatible environment for
customer-support ticket triage.

Exports:
  Observation, Action, Reward  — Pydantic v2 models
  SupportEnv                   — the environment class
"""

from __future__ import annotations

import random
from typing import Any

from pydantic import BaseModel, Field

from grader import grade
from tasks import TASKS, TICKETS, Ticket


# ---------------------------------------------------------------------------
# Pydantic v2 data models
# ---------------------------------------------------------------------------

class Observation(BaseModel):
    """What the agent sees at each step."""
    ticket_id: str
    ticket_text: str
    task_name: str
    step_number: int


class Action(BaseModel):
    """What the agent submits."""
    category: str
    priority: str
    reply: str = ""


class Reward(BaseModel):
    """Grading result returned to the agent."""
    score: float
    breakdown: dict[str, float] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

VALID_CATEGORIES = ["billing", "technical", "general"]
VALID_PRIORITIES = ["low", "medium", "high", "urgent"]


class SupportEnv:
    """OpenEnv-compatible customer-support environment."""

    def __init__(self) -> None:
        self._task_name: str = ""
        self._ticket: Ticket | None = None
        self._step: int = 0
        self._done: bool = True

    # ---- public API -------------------------------------------------------

    def reset(self, task_name: str | None = None) -> Observation:
        """
        Start a new episode.

        Parameters
        ----------
        task_name : str, optional
            One of "classify", "prioritize", "resolve".
            If *None*, a task is chosen at random.

        Returns
        -------
        Observation
        """
        if task_name is None:
            task_name = random.choice(list(TASKS.keys()))
        if task_name not in TASKS:
            raise ValueError(
                f"Unknown task {task_name!r}. Choose from {list(TASKS.keys())}"
            )

        self._task_name = task_name
        self._ticket = random.choice(TICKETS[task_name])
        self._step = 0
        self._done = False

        return self._make_observation()

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict[str, Any]]:
        """
        Execute one action and return (observation, reward, done, info).
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() first.")

        info: dict[str, Any] = {}
        assert self._ticket is not None

        # Validate action values
        errors: list[str] = []
        if action.category.strip().lower() not in VALID_CATEGORIES:
            errors.append(
                f"Invalid category {action.category!r}. Must be one of {VALID_CATEGORIES}"
            )
        if action.priority.strip().lower() not in VALID_PRIORITIES:
            errors.append(
                f"Invalid priority {action.priority!r}. Must be one of {VALID_PRIORITIES}"
            )
        if errors:
            info["errors"] = errors

        self._step += 1

        score, breakdown = grade(
            action_category=action.category,
            action_priority=action.priority,
            action_reply=action.reply,
            ticket=self._ticket,
            task_name=self._task_name,
        )

        reward = Reward(score=score, breakdown=breakdown)

        # Each episode is a single step in this environment.
        self._done = True

        obs = self._make_observation()
        return obs, reward, self._done, info

    def state(self) -> dict[str, Any]:
        """Return the current internal state of the environment."""
        return {
            "task_name": self._task_name,
            "ticket": {
                "ticket_id": self._ticket.ticket_id if self._ticket else None,
                "ticket_text": self._ticket.ticket_text if self._ticket else None,
            },
            "step_number": self._step,
        }

    # ---- helpers ----------------------------------------------------------

    def _make_observation(self) -> Observation:
        assert self._ticket is not None
        return Observation(
            ticket_id=self._ticket.ticket_id,
            ticket_text=self._ticket.ticket_text,
            task_name=self._task_name,
            step_number=self._step,
        )
