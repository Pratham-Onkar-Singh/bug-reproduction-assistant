---

title: Bug Reproduction Assistant
emoji: 🐞
colorFrom: blue
colorTo: purple
sdk: docker
tags:
    - openenv
    - qa
    - bug-reproduction
    - evaluation
pinned: false

---

# Bug Reproduction Assistant

Bug Reproduction Assistant is a real-world OpenEnv benchmark that simulates how QA engineers reproduce software bugs from incomplete reports. The agent must interpret bug descriptions, execute reproduction steps, configure parameters, and confirm crashes while minimizing unnecessary actions.

This environment models the workflow of manual bug triage commonly performed in software testing and quality assurance.

---

# Why This Benchmark Matters

Bug reproduction is a common and time-consuming engineering task:

* bug reports are often incomplete
* reproduction requires ordered steps
* configuration matters
* incorrect actions waste time
* partial progress should be rewarded

This benchmark captures those dynamics in a deterministic OpenEnv environment suitable for evaluating agent reasoning and sequential decision-making.

---

# Hackathon Requirement Coverage

This submission satisfies all Round 1 requirements:

* real-world task simulation (QA bug reproduction)
* full OpenEnv interface (`step`, `reset`, `state`)
* typed Pydantic models
* 3 tasks (easy → medium → hard)
* deterministic graders (0.0–1.0 scoring)
* meaningful reward shaping
* reproducible baseline inference
* Docker container deployment
* Hugging Face Spaces runtime
* structured stdout logs

---

# Environment Overview

The agent receives a bug report and must reproduce it using available actions.

Typical workflow:

1. open required UI
2. set configuration parameters
3. perform reproduction action
4. trigger crash
5. confirm bug

Incorrect ordering results in penalties.

---

# OpenEnv Interface

The environment implements:

* `reset()` → returns initial observation
* `step(action)` → returns observation, reward, done, info
* `state()` → returns full environment state

Metadata defined in:

* `openenv.yaml`

---

# Action Space

Typed model: `Action`

| Field       | Type          | Description         |
| ----------- | ------------- | ------------------- |
| action_type | str           | Action to execute   |
| step        | Optional[str] | UI step to run      |
| parameter   | Optional[str] | Configuration key   |
| value       | Optional[str] | Configuration value |

Supported actions:

* `run_step`
* `change_parameter`
* `confirm_bug`
* `request_info`

Supported steps:

* `login`
* `set_role_admin`
* `open_upload_page`
* `upload_file`

---

# Observation Space

Typed model: `Observation`

| Field           | Type      | Description            |
| --------------- | --------- | ---------------------- |
| bug_id          | str       | Unique bug identifier  |
| description     | str       | Bug report text        |
| last_message    | str       | Last system message    |
| crash_triggered | bool      | Whether crash occurred |
| steps_taken     | List[str] | Steps executed so far  |
| remaining_steps | int       | Remaining budget       |
| done            | bool      | Episode finished       |

---

# Reward Design

The grading function provides deterministic scores between 0.0 and 1.0.

### Easy Task

| Component         | Weight |
| ----------------- | ------ |
| Crash triggered   | 0.5    |
| Correct steps     | 0.3    |
| Correct parameter | 0.2    |

### Medium Task

| Component             | Weight |
| --------------------- | ------ |
| Crash triggered       | 0.4    |
| Correct steps         | 0.3    |
| Parameter correctness | 0.2    |
| Efficiency            | 0.1    |

### Hard Task

| Component             | Weight |
| --------------------- | ------ |
| Crash triggered       | 0.4    |
| Correct steps         | 0.3    |
| Parameter correctness | 0.2    |
| Efficiency            | 0.1    |

Efficiency rewards fewer steps and penalizes redundant actions.

All graders are deterministic and return scores in the range [0.0, 1.0].


---

# Task Suite

Three deterministic tasks are included.

| Task   | Difficulty | Objective                                       |
| ------ | ---------- | ----------------------------------------------- |
| easy   | Easy       | Set file size and upload file                   |
| medium | Medium     | Login, configure parameter, reproduce crash     |
| hard   | Hard       | Set role, configure parameters, reproduce crash |

Difficulty increases by:

* more required steps
* stricter ordering
* additional parameters

---

# Graders

Each task has deterministic scoring:

* `grade_easy`
* `grade_medium`
* `grade_hard`

All graders return:

* score (0.0–1.0)
* success flag
* steps taken
* progress ratio

---

# Baseline Inference

The root-level `inference.py`:

* uses OpenAI client
* reads environment variables
* produces deterministic baseline
* emits structured logs

Required environment variables:

```
API_BASE_URL           # LLM API endpoint
MODEL_NAME             # Model identifier
HF_TOKEN               # Hugging Face API key (or OPENAI_API_KEY as fallback)
```

Example with HuggingFace:

```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct"
export HF_TOKEN="hf_..."
```

Example with OpenAI:

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4-turbo"
export OPENAI_API_KEY="sk-..."
```

---

# Example Output

```
[START] task=easy env=bug_reproduction model=gpt-4-turbo
[STEP] step=1 action={'action_type': 'change_parameter', 'parameter': 'file_size', 'value': '100MB'} reward=0.10 done=false error=null
[STEP] step=2 action={'action_type': 'run_step', 'step': 'open_upload_page'} reward=0.20 done=false error=null
[STEP] step=3 action={'action_type': 'run_step', 'step': 'upload_file'} reward=0.70 done=true error=null
[END] success=true steps=3 score=1.000 rewards=0.10,0.20,0.70
```

---

# Baseline Scores

Typical deterministic baseline:

| Task   | Score |
| ------ | ----- |
| easy   | 1.0   |
| medium | ~0.9  |
| hard   | ~0.75 |

---

# Setup

## Local

```
pip install -r requirements.txt
python inference.py
```

## Docker

```
docker build -t bug-reproduction .
docker run bug-reproduction
```

---

# Hugging Face Space

Live runtime:

https://huggingface.co/spaces/CodeArtisan09/bug-reproduction-assistant

The Space runs the baseline and exposes a lightweight HTTP server for health checks.

---

# Project Structure

```
.
├── server/
│   ├── app.py              # FastAPI server
│   ├── env.py              # BugReproEnv class
│   ├── models.py           # Pydantic models (Observation, Action, Reward)
│   ├── tasks.py            # Task definitions
│   └── grader.py           # Grading functions
├── tests/
│   ├── test_graders.py     # Unit tests (27 tests, all passing)
│   └── __init__.py
├── inference.py            # Baseline inference script
├── openenv.yaml            # OpenEnv specification
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── pytest.ini              # Pytest configuration
└── README.md
```

---

# Real-World Use Cases

This benchmark evaluates whether an agent can:

* follow ordered procedures
* configure environment parameters
* avoid redundant actions
* reason about state transitions
* confirm task completion

---

# Summary

Bug Reproduction Assistant is a realistic QA automation benchmark that:

* models real bug reproduction workflows
* rewards partial progress
* penalizes incorrect ordering
* supports deterministic grading
* provides reproducible baselines

It is designed specifically for evaluating agent reasoning in structured debugging environments.
