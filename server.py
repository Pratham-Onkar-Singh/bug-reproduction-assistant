from fastapi import FastAPI
from env import BugReproEnv
from models import Action

app = FastAPI()
env = BugReproEnv("easy")


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs


@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }


@app.get("/state")
def state():
    return env.state()