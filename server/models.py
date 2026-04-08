from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Observation(BaseModel):
    bug_id: str
    description: str
    last_message: str
    crash_triggered: bool
    steps_taken: List[str]
    remaining_steps: int
    done: bool

class Action(BaseModel):
    action_type: str
    step: Optional[str] = None
    parameter: Optional[str] = None
    value: Optional[str] = None

class Reward(BaseModel):
    score: float
    reason: Optional[str] = None

class EnvironmentState(BaseModel):
    """Full internal environment state for debugging"""
    bug: Dict[str, Any]
    steps_taken: List[str]
    parameters: Dict[str, Any]
    crash_triggered: bool
    step_count: int
    done: bool

class TaskGrade(BaseModel):
    """Final episode grade"""
    task_id: str
    score: float
    success: bool
    steps_taken: int
    progress_ratio: float
