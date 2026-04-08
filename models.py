from pydantic import BaseModel
from typing import List, Optional, Dict


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
