from typing import Dict

def grade_easy(state: Dict) -> float:
    score = 0.0

    if state["crash_triggered"]:
        score += 0.5

    correct_steps = ["open_upload_page", "upload_file"]
    step_matches = len(set(state["steps_taken"]) & set(correct_steps))
    score += 0.3 * (step_matches / len(correct_steps))

    if state["parameters"].get("file_size") == "100MB":
        score += 0.2

    return round(score, 3)


def grade_medium(state: Dict) -> float:
    score = 0.0

    if state["crash_triggered"]:
        score += 0.4

    correct_steps = ["login", "open_upload_page", "upload_file"]
    step_matches = len(set(state["steps_taken"]) & set(correct_steps))
    score += 0.3 * (step_matches / len(correct_steps))

    params = state["parameters"]
    if params.get("file_type") == "csv":
        score += 0.1
    if params.get("file_size") == "100MB":
        score += 0.1

    efficiency = max(0, 1 - state["step_count"] / 6)
    score += 0.1 * efficiency

    return round(score, 3)


def grade_hard(state: Dict) -> float:
    score = 0.0

    if state["crash_triggered"]:
        score += 0.4

    correct_steps = [
        "login",
        "set_role_admin",
        "open_upload_page",
        "upload_file"
    ]

    step_matches = len(set(state["steps_taken"]) & set(correct_steps))
    score += 0.3 * (step_matches / len(correct_steps))

    params = state["parameters"]

    if params.get("file_type") == "csv":
        score += 0.05
    if params.get("file_size") == "100MB":
        score += 0.05
    if params.get("role") == "admin":
        score += 0.1

    efficiency = max(0, 1 - state["step_count"] / 6)
    score += 0.1 * efficiency

    return round(score, 3)