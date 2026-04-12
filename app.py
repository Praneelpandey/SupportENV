"""
app.py — Flask web server for SupportEnv frontend.

Provides REST API endpoints and serves the web UI.
"""

from __future__ import annotations

import json
from flask import Flask, jsonify, request, render_template, send_from_directory

from environment import SupportEnv, Action, Observation, Reward
from tasks import TASKS, TICKETS

app = Flask(__name__, static_folder="static", template_folder="templates")

# Global environment instance
env = SupportEnv()
episode_history: list[dict] = []


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Return all available tasks and their configs."""
    tasks_data = []
    for name, cfg in TASKS.items():
        tasks_data.append({
            "name": cfg.name,
            "difficulty": cfg.difficulty,
            "requires_category": cfg.requires_category,
            "requires_priority": cfg.requires_priority,
            "requires_reply": cfg.requires_reply,
            "ticket_count": len(TICKETS.get(name, [])),
        })
    return jsonify({"tasks": tasks_data})


@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    """Return all tickets grouped by task."""
    result = {}
    for task_name, ticket_list in TICKETS.items():
        result[task_name] = [
            {
                "ticket_id": t.ticket_id,
                "ticket_text": t.ticket_text,
                "true_category": t.true_category,
                "true_priority": t.true_priority,
                "ideal_reply_keywords": t.ideal_reply_keywords,
            }
            for t in ticket_list
        ]
    return jsonify(result)


@app.route("/api/reset", methods=["POST"])
def reset_env():
    """Reset the environment with an optional task_name."""
    data = request.get_json(silent=True) or {}
    task_name = data.get("task_name")
    ticket_id = data.get("ticket_id")  # optional: pick specific ticket

    try:
        obs = env.reset(task_name=task_name)

        # If a specific ticket was requested, keep resetting until we get it
        # (or just override internally)
        if ticket_id:
            from tasks import TICKETS as _T
            for t in _T.get(task_name, []):
                if t.ticket_id == ticket_id:
                    env._ticket = t
                    obs = env._make_observation()
                    break

        return jsonify({
            "observation": obs.model_dump(),
            "task_config": {
                "name": TASKS[obs.task_name].name,
                "difficulty": TASKS[obs.task_name].difficulty,
                "requires_category": TASKS[obs.task_name].requires_category,
                "requires_priority": TASKS[obs.task_name].requires_priority,
                "requires_reply": TASKS[obs.task_name].requires_reply,
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/step", methods=["POST"])
def step_env():
    """Submit an action and get the result."""
    data = request.get_json(silent=True) or {}

    try:
        action = Action(
            category=data.get("category", "general"),
            priority=data.get("priority", "low"),
            reply=data.get("reply", ""),
        )

        obs, reward, done, info = env.step(action)

        # Get the ground truth for display
        ground_truth = {}
        if env._ticket:
            ground_truth = {
                "true_category": env._ticket.true_category,
                "true_priority": env._ticket.true_priority,
                "ideal_reply_keywords": env._ticket.ideal_reply_keywords,
            }

        result = {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info,
            "ground_truth": ground_truth,
            "action": action.model_dump(),
        }

        # Save to history
        episode_history.append(result)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/state", methods=["GET"])
def get_state():
    """Return current environment state."""
    return jsonify(env.state())


@app.route("/api/history", methods=["GET"])
def get_history():
    """Return episode history."""
    return jsonify({"history": episode_history})


@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    """Clear episode history."""
    episode_history.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=7860)
