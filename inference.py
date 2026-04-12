"""
inference.py — Run a baseline LLM agent through all SupportEnv tasks.

Configuration (via environment variables):
  API_BASE_URL  – OpenAI-compatible endpoint
                  (default: https://router.huggingface.co/v1)
  MODEL_NAME    – Model to query
                  (default: Qwen/Qwen2.5-72B-Instruct)
  HF_TOKEN      – Bearer / API token
"""

from __future__ import annotations

import json
import os
import sys

from openai import OpenAI

from environment import Action, SupportEnv
from tasks import TASKS

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "")

EPISODES_PER_TASK = 3
TASKS_TO_RUN = ["classify", "prioritize", "resolve"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_prompt(task_name: str, ticket_text: str, ticket_id: str) -> tuple[str, str]:
    """Construct the system + user prompt for the LLM."""
    task_cfg = TASKS[task_name]

    instructions_parts: list[str] = [
        "You are a customer support triage assistant.",
        "Respond ONLY with a JSON object with the following keys: category, priority, reply.",
        "",
        "Rules:",
        '- "category" must be one of: "billing", "technical", "general".',
        '- "priority" must be one of: "low", "medium", "high", "urgent".',
    ]

    if task_cfg.requires_reply:
        instructions_parts.append(
            '- "reply" should be a helpful, empathetic response to the customer (at least 10 words).'
        )
    else:
        instructions_parts.append(
            '- "reply" can be an empty string "".'
        )

    instructions_parts += [
        "",
        "Do NOT include any text outside the JSON object.",
    ]

    system_msg = "\n".join(instructions_parts)

    user_msg = (
        f"Ticket ID: {ticket_id}\n"
        f"Ticket Text: {ticket_text}\n\n"
        f"Task: {task_name}\n"
        "Respond with JSON only."
    )

    return system_msg, user_msg


def parse_action(raw: str) -> Action:
    """
    Parse the LLM's raw text output into an Action.
    Attempts to extract JSON even if surrounded by markdown fences.
    """
    text = raw.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        # Remove first and last fence lines
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    data = json.loads(text)
    return Action(
        category=data.get("category", "general"),
        priority=data.get("priority", "low"),
        reply=data.get("reply", ""),
    )


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN, timeout=60.0)
    env = SupportEnv()

    for task_name in TASKS_TO_RUN:
        for ep in range(EPISODES_PER_TASK):
            obs = env.reset(task_name=task_name)
            rewards: list[float] = []
            step_count = 0
            success = False

            print(f"[START] task={task_name} env=supportenv model={MODEL_NAME}")

            # --- single-step episode ---
            system_msg, user_msg = build_prompt(
                task_name=obs.task_name,
                ticket_text=obs.ticket_text,
                ticket_id=obs.ticket_id,
            )

            try:
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.0,
                    max_tokens=512,
                )
                raw_response = completion.choices[0].message.content or ""
                action = parse_action(raw_response)
                error_str = "null"
            except Exception as exc:
                # Fallback action on error
                action = Action(category="general", priority="low", reply="")
                error_str = str(exc).replace("\n", " ")[:120]

            obs, reward, done, info = env.step(action)
            step_count += 1
            rewards.append(reward.score)

            print(
                f"[STEP] step={step_count} "
                f"action={action.category} "
                f"reward={reward.score:.2f} "
                f"done={str(done).lower()} "
                f"error={error_str}"
            )

            success = done and reward.score > 0.0
            rewards_str = ",".join(f"{r:.2f}" for r in rewards)
            print(
                f"[END] success={str(success).lower()} "
                f"steps={step_count} "
                f"score={reward.score:.2f} "
                f"rewards={rewards_str}"
            )
            print()  # blank line between episodes


if __name__ == "__main__":
    main()
