"""
server/app.py — OpenEnv-compatible FastAPI server entry point.

Uses openenv-core's create_fastapi_app to expose /reset, /step, /state endpoints.
"""

import sys
import os

# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openenv_core.env_server import create_fastapi_app
except ImportError:
    try:
        from openenv.core.env_server import create_fastapi_app
    except ImportError:
        create_fastapi_app = None

from environment import SupportEnv, Observation, Action
from tasks import TASKS

env = SupportEnv()

if create_fastapi_app is not None:
    app = create_fastapi_app(
        environment=env,
        action_model=Action,
        observation_model=Observation,
    )
else:
    # Fallback: create a minimal FastAPI app with the same endpoints
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="SupportEnv", version="1.0.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.post("/reset")
    async def reset(data: dict = {}):
        task_name = data.get("task_name")
        obs = env.reset(task_name=task_name)
        return {
            "observation": obs.model_dump(),
            "task_config": {
                "name": TASKS[obs.task_name].name,
                "difficulty": TASKS[obs.task_name].difficulty,
                "requires_category": TASKS[obs.task_name].requires_category,
                "requires_priority": TASKS[obs.task_name].requires_priority,
                "requires_reply": TASKS[obs.task_name].requires_reply,
            }
        }

    @app.post("/step")
    async def step(data: dict = {}):
        action = Action(
            category=data.get("category", "general"),
            priority=data.get("priority", "low"),
            reply=data.get("reply", ""),
        )
        obs, reward, done, info = env.step(action)
        ground_truth = {}
        if env._ticket:
            ground_truth = {
                "true_category": env._ticket.true_category,
                "true_priority": env._ticket.true_priority,
                "ideal_reply_keywords": env._ticket.ideal_reply_keywords,
            }
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info,
            "ground_truth": ground_truth,
            "action": action.model_dump(),
        }

    @app.get("/state")
    async def state():
        return env.state()


def main():
    """Entry point for the server script."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
