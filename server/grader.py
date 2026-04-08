from typing import Union, Dict
from .models import EnvironmentState


def _get_value(state: Union[EnvironmentState, Dict], key: str, default=None):
    """Get value from either EnvironmentState or dict."""
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)


def grade_easy(state: Union[EnvironmentState, Dict]) -> float:
    score = 0.0

    if _get_value(state, "crash_triggered", False):
        score += 0.5

    steps = _get_value(state, "steps_taken", [])
    correct_steps = ["open_upload_page", "upload_file"]
    step_matches = len(set(steps) & set(correct_steps))
    score += 0.3 * (step_matches / len(correct_steps))

    params = _get_value(state, "parameters", {})
    if params.get("file_size") == "100MB":
        score += 0.2

    return round(score, 3)


def grade_medium(state: Union[EnvironmentState, Dict]) -> float:
    score = 0.0

    if _get_value(state, "crash_triggered", False):
        score += 0.4

    steps = _get_value(state, "steps_taken", [])
    correct_steps = ["login", "open_upload_page", "upload_file"]
    step_matches = len(set(steps) & set(correct_steps))
    score += 0.3 * (step_matches / len(correct_steps))

    params = _get_value(state, "parameters", {})
    if params.get("file_type") == "csv":
        score += 0.1
    if params.get("file_size") == "100MB":
        score += 0.1

    step_count = _get_value(state, "step_count", 0)
    efficiency = max(0, 1 - step_count / 6)
    score += 0.1 * efficiency

    return round(score, 3)


def grade_hard(state: Union[EnvironmentState, Dict]) -> float:
    score = 0.0

    if _get_value(state, "crash_triggered", False):
        score += 0.4

    steps = _get_value(state, "steps_taken", [])
    correct_steps = [
        "login",
        "set_role_admin",
        "open_upload_page",
        "upload_file"
    ]

    step_matches = len(set(steps) & set(correct_steps))
    score += 0.3 * (step_matches / len(correct_steps))

    params = _get_value(state, "parameters", {})

    if params.get("file_type") == "csv":
        score += 0.05
    if params.get("file_size") == "100MB":
        score += 0.05
    if params.get("role") == "admin":
        score += 0.1

    step_count = _get_value(state, "step_count", 0)
    efficiency = max(0, 1 - step_count / 6)
    score += 0.1 * efficiency

    return round(score, 3)