from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

from server.models import Observation, Action, Reward, EnvironmentState, TaskGrade
from server.env import BugReproEnv
from server.tasks import TASKS
import uvicorn

app = FastAPI(title="Bug Reproduction Assistant")

env = BugReproEnv()

@app.get("/")
async def root():
    return {"message": "Bug Reproduction Assistant is running", "status": "200"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reset")
async def reset(task_id: str = "easy", seed: int = None):
    """Resets the environment to a specific task state."""
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail=f"Unknown task_id '{task_id}'")
    observation = env.reset(task_id=task_id, seed=seed)
    return observation


@app.post("/step")
async def step(action: Action):
    """Executes one action and returns the new observation and reward."""
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/tasks")
async def get_tasks():
    """Returns list of tasks and the action schema."""
    return {
        "tasks": [
            {
                "id": task_key,
                "description": TASKS[task_key]["description"],
                "difficulty": task_key,
            }
            for task_key in TASKS.keys()
        ],
        "action_schema": Action.model_json_schema(),
        "observation_schema": Observation.model_json_schema(),
        "reward_schema": Reward.model_json_schema(),
        "state_schema": EnvironmentState.model_json_schema(),
        "grader_schema": TaskGrade.model_json_schema(),
    }


@app.get("/grader")
async def get_grader():
    """Returns the final score (0.0-1.0) after an episode."""
    return env.grade()


@app.get("/state")
async def get_state():
    """Returns the current environment state for debugging and validation."""
    return env.state()


@app.post("/baseline")
async def run_baseline():
    """Triggers the baseline inference script."""
    try:
        from scripts.baseline import run_all_tasks
        results = await run_in_threadpool(run_all_tasks)
        return {"results": results}
    except ImportError:
        raise HTTPException(status_code=500, detail="Baseline script not found. Run inference.py directly.")


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()