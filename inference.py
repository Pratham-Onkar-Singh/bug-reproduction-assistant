from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

from server.env import BugReproEnv
from server.models import Action
from server.grader import grade_easy, grade_medium, grade_hard

import json
import time

import http.server
import socketserver

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b:groq")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

if not API_BASE_URL or not MODEL_NAME or not API_KEY:
    raise ValueError(
        "Missing environment variables. Set:\n"
        "  - API_BASE_URL\n"
        "  - MODEL_NAME\n"
        "  - OPENAI_API_KEY or HF_TOKEN"
    )

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)

def log_start(task):
    print(f"[START] task={task} env=bug_reproduction model={MODEL_NAME}", flush=True)


def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={done_val} error={error_val}",
        flush=True
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True
    )


def heuristic_action(env, obs):
    state = env.state()
    steps = state.steps_taken
    params = state.parameters
    difficulty = env.difficulty

    # EASY TASK
    if difficulty == "easy":
        if "file_size" not in params:
            return {
                "action_type": "change_parameter",
                "parameter": "file_size",
                "value": "100MB"
            }

        if "open_upload_page" not in steps:
            return {"action_type": "run_step", "step": "open_upload_page"}

        if not obs.crash_triggered:
            return {"action_type": "run_step", "step": "upload_file"}

        return {"action_type": "confirm_bug"}

    # MEDIUM TASK
    if difficulty == "medium":
        if "login" not in steps:
            return {"action_type": "run_step", "step": "login"}

        if "file_size" not in params:
            return {
                "action_type": "change_parameter",
                "parameter": "file_size",
                "value": "100MB"
            }

        if "open_upload_page" not in steps:
            return {"action_type": "run_step", "step": "open_upload_page"}

        if not obs.crash_triggered:
            return {"action_type": "run_step", "step": "upload_file"}

        return {"action_type": "confirm_bug"}

    # HARD TASK
    if difficulty == "hard":
        if "login" not in steps:
            return {"action_type": "run_step", "step": "login"}

        if "set_role_admin" not in steps:
            return {"action_type": "run_step", "step": "set_role_admin"}

        if "file_type" not in params:
            return {
                "action_type": "change_parameter",
                "parameter": "file_type",
                "value": "csv"
            }

        if "file_size" not in params:
            return {
                "action_type": "change_parameter",
                "parameter": "file_size",
                "value": "100MB"
            }

        if "open_upload_page" not in steps:
            return {"action_type": "run_step", "step": "open_upload_page"}

        if not obs.crash_triggered:
            return {"action_type": "run_step", "step": "upload_file"}

        return {"action_type": "confirm_bug"}


def run_task(difficulty, grader):
    try:
        env = BugReproEnv(difficulty)
    except Exception as e:
        print(f"[ERROR] Failed to initialize environment: {str(e)}", flush=True)
        raise
    
    try:
        obs = env.reset()
    except Exception as e:
        print(f"[ERROR] Failed to reset environment: {str(e)}", flush=True)
        raise

    log_start(difficulty)

    step_count = 0
    done = False
    rewards = []

    while not done:
        step_count += 1
        error_msg = None

        prompt = f"""
You are a QA engineer reproducing a software bug.

Bug description:
{obs.description}

Steps already taken:
{obs.steps_taken}

Allowed actions:
- run_step
- change_parameter
- confirm_bug
- request_info

Allowed steps:
- login
- set_role_admin
- open_upload_page
- upload_file

Allowed parameters and valid values:
- file_size: "100MB"
- file_type: "csv"
- role: "admin"

Rules:
- Use correct parameter values
- Trigger crash before confirm_bug
- Choose minimal steps
- Output JSON only

Format:
{{
  "action_type": "...",
  "step": "...",
  "parameter": "...",
  "value": "..."
}}
"""

        action_dict = None
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            text = response.choices[0].message.content
            parsed = json.loads(text)

            if isinstance(parsed, list):
                parsed = parsed[0]

            if isinstance(parsed, dict):
                action_dict = parsed
                action_dict["step"] = action_dict.get("step") or None
                action_dict["parameter"] = action_dict.get("parameter") or None
                action_dict["value"] = action_dict.get("value") or None

        except Exception as e:
            error_msg = str(e)

        if action_dict is None:
            if not obs.crash_triggered:
                if "open_upload_page" not in obs.steps_taken:
                    action_dict = {"action_type": "run_step", "step": "open_upload_page"}
                elif "file_size" not in env.state().parameters:
                    action_dict = {
                        "action_type": "change_parameter",
                        "parameter": "file_size",
                        "value": "100MB"
                    }
                else:
                    action_dict = {"action_type": "run_step", "step": "upload_file"}
            else:
                action_dict = {"action_type": "confirm_bug"}

        try:
            action = Action(**action_dict)
        except Exception as e:
            print(f"[ERROR] Failed to create Action: {str(e)}", flush=True)
            error_msg = str(e)
            action_dict = {"action_type": "confirm_bug"}
            action = Action(**action_dict)

        try:
            obs, reward, done, _ = env.step(action)
        except Exception as e:
            print(f"[ERROR] Failed to execute step: {str(e)}", flush=True)
            raise

        rewards.append(reward.score)

        log_step(
            step_count,
            action_dict,
            reward.score,
            done,
            error_msg
        )

    try:
        state = env.state()
    except Exception as e:
        print(f"[ERROR] Failed to get environment state: {str(e)}", flush=True)
        raise
    
    try:
        score = grader(state)
    except Exception as e:
        print(f"[ERROR] Failed to grade task: {str(e)}", flush=True)
        raise
    
    success = score >= 0.5

    log_end(success, step_count, score, rewards)
    return score


def main():
    try:
        scores = {}

        scores["easy"] = run_task("easy", grade_easy)
        scores["medium"] = run_task("medium", grade_medium)
        scores["hard"] = run_task("hard", grade_hard)
    except Exception as e:
        print(f"[FATAL] Inference failed: {str(e)}", flush=True)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL] Main execution failed: {str(e)}", flush=True)
        exit(1)
    
    print("Finished baseline run. Starting keep-alive server...")

    PORT = 7860
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()