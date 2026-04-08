from typing import Tuple, Dict, Any
from server.models import Observation, Action, Reward
from server.tasks import TASKS

class BugReproEnv:

    def __init__(self, difficulty="easy"):
        self.max_steps = 6
        self.difficulty = difficulty
        self.reset()

    def reset(self) -> Observation:
        """Start a new episode"""

        self.bug = TASKS[self.difficulty]

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

    def state(self) -> Dict[str, Any]:
        """Return internal state"""
        return {
            "bug": self.bug,
            "steps_taken": self.steps_taken,
            "parameters": self.parameters,
            "crash_triggered": self.crash_triggered,
            "step_count": self.step_count,
            "done": self.done
        }

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