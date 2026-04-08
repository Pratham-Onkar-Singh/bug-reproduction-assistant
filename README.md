---
title: Bug Reproduction Assistant
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Bug Reproduction Assistant (OpenEnv)

## Overview

This project implements a real-world QA bug reproduction environment where an AI agent attempts to reproduce software bugs by executing steps, adjusting parameters, and confirming crash behavior.

The environment follows the OpenEnv specification and provides multiple tasks with deterministic grading.

---

## Real-World Motivation

Software QA engineers frequently reproduce bugs from incomplete reports. This environment simulates that workflow, allowing AI agents to learn structured debugging and reproduction strategies.

---

## Environment Design

### Actions

The agent can perform the following actions:

* `run_step` — execute a reproduction step
* `change_parameter` — modify environment parameter
* `confirm_bug` — confirm reproduction
* `request_info` — request additional info

Action schema:

```
{
  "action_type": str,
  "step": Optional[str],
  "parameter": Optional[str],
  "value": Optional[str]
}
```

---

### Observation Space

```
{
  "bug_id": str,
  "description": str,
  "last_message": str,
  "crash_triggered": bool,
  "steps_taken": List[str],
  "remaining_steps": int,
  "done": bool
}
```

---

## Tasks

### Easy

Simple bug reproduction requiring minimal steps.

### Medium

Bug requiring login and parameter configuration.

### Hard

Multi-step reproduction requiring role assignment and parameter tuning.

---

## Reward Structure

Rewards are given for:

* executing correct steps
* triggering crash
* confirming reproduction
* penalizing incorrect actions

Final grading is deterministic and produces scores between 0.0 and 1.0.

---

## Setup

Install dependencies:

```
pip install -r requirements.txt
```

Set environment variables:

```
API_BASE_URL=...
MODEL_NAME=...
HF_TOKEN=...
```

---

## Running Baseline

```
python inference.py
```

This runs the agent across all tasks and prints structured logs.

---

## Docker

Build:

```
docker build -t bug-env .
```

Run:

```
docker run bug-env
```

---

## Project Structure

```
.
├── env.py
├── tasks.py
├── grader.py
├── models.py
├── inference.py
├── openenv.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Baseline Scores

Example baseline performance:

| Task   | Score |
| ------ | ----- |
| Easy   | ~0.8  |
| Medium | ~0.6  |
| Hard   | ~0.4  |

---

## OpenEnv Compliance

* Typed Pydantic models
* step/reset/state API
* 3 tasks with graders
* deterministic scoring
* Dockerized execution
* inference baseline

---

## License

MIT
