from fastapi import FastAPI
import uvicorn

from server.env import BugReproEnv
from server.models import Action

app = FastAPI()
env = BugReproEnv("easy")

@app.get("/")
async def root():
    return {"message": "Bug Resproduction Assistant is running", "status": "200"}


@app.get("/health")
async def health():
    return {"status": "ok"}


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


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()