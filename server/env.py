from typing import Tuple, Dict, Any
from server.models import Observation, Action, Reward, EnvironmentState, TaskGrade
from server.tasks import TASKS
from server.grader import grade_easy, grade_medium, grade_hard

class BugReproEnv:

    def __init__(self, task_id: str = "easy"):
        self.max_steps = 6
        self.task_id = task_id
        self.graders = {
            "easy": grade_easy,
            "medium": grade_medium,
            "hard": grade_hard,
        }
        self.reset()

    def reset(self, task_id: str = None, seed: int = None) -> Observation:
        """Start a new episode"""
        if task_id is not None:
            self.task_id = task_id
        
        if self.task_id not in TASKS:
            raise ValueError(f"Unknown task_id: {self.task_id}")
        
        self.bug = TASKS[self.task_id]
        self.steps_taken = []
        self.parameters = {}
        self.crash_triggered = False
        self.step_count = 0
        self.done = False

        return self._get_observation("Environment reset")

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """Apply action"""

        if self.done:
            return self._get_observation("Episode already finished"), Reward(score=0.0), True, {}

        self.step_count += 1
        reward = 0.0
        message = "Action processed"

        # run step
        if action.action_type == "run_step" and action.step:
            self.steps_taken.append(action.step)

            if action.step in self.bug["correct_steps"]:
                reward += 0.2
                message = f"Step {action.step} executed"

            # trigger crash
            if action.step == self.bug["crash_step"] and \
               self.parameters.get("file_size") == self.bug["parameter"]["file_size"]:
                self.crash_triggered = True
                reward += 0.5
                message = "Crash triggered!"

        # change parameter
        elif action.action_type == "change_parameter":
            self.parameters[action.parameter] = action.value
            reward += 0.1
            message = f"Parameter {action.parameter} set to {action.value}"

        # confirm bug
        elif action.action_type == "confirm_bug":
            if self.crash_triggered:
                reward += 1.0
                message = "Bug successfully reproduced"
                self.done = True
            else:
                reward -= 0.5
                message = "Bug not reproduced"

        # invalid action
        else:
            reward -= 0.1
            message = "Invalid action"

        # step limit
        if self.step_count >= self.max_steps:
            self.done = True

        observation = self._get_observation(message)
        return observation, Reward(score=reward, reason=message), self.done, {}

    def state(self) -> EnvironmentState:
        """Return internal state"""
        return EnvironmentState(
            bug=self.bug,
            steps_taken=self.steps_taken,
            parameters=self.parameters,
            crash_triggered=self.crash_triggered,
            step_count=self.step_count,
            done=self.done
        )

    def grade(self) -> TaskGrade:
        """Grade the current episode"""
        grader = self.graders[self.task_id]
        state_dict = {
            "bug": self.bug,
            "steps_taken": self.steps_taken,
            "parameters": self.parameters,
            "crash_triggered": self.crash_triggered,
            "step_count": self.step_count,
            "done": self.done
        }
        score = grader(state_dict)
        progress = min(1.0, len(self.steps_taken) / len(self.bug["correct_steps"])) 
        return TaskGrade(
            task_id=self.task_id,
            score=score,
            success=score >= 0.75,
            steps_taken=self.step_count,
            progress_ratio=progress
        )

    def _get_observation(self, message: str) -> Observation:
        """Build observation"""
        return Observation(
            bug_id=self.bug["id"],
            description=self.bug["description"],
            last_message=message,
            crash_triggered=self.crash_triggered,
            steps_taken=self.steps_taken,
            remaining_steps=self.max_steps - self.step_count,
            done=self.done
        )