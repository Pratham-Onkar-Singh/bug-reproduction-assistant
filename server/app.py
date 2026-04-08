from fastapi import FastAPI
from server.env import BugReproEnv
from server.models import Action

app = FastAPI()

env = BugReproEnv("easy")


@app.post("/reset")
def reset():
    return env.reset()


@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state():
    return env.state()