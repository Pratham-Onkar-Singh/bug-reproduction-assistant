"""
Standard client for the Bug Reproduction Assistant environment.
"""

import requests
from typing import Any, Dict, Optional


class BugReproClient:
    def __init__(self, url: str = "http://localhost:7860"):
        """
        Initialize the client.
        
        Args:
            url: Base URL of the environment server (default: http://localhost:7860)
        """
        self.url = url.rstrip("/")
        self.session = requests.Session()
    
    def health(self) -> Dict[str, Any]:
        """Check if the server is healthy."""
        response = self.session.get(f"{self.url}/health")
        response.raise_for_status()
        return response.json()
    
    def reset(self, task_id: str = "easy", seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Reset the environment to a specific task.
        """
        params = {"task_id": task_id}
        if seed is not None:
            params["seed"] = seed
        response = self.session.post(f"{self.url}/reset", params=params)
        response.raise_for_status()
        return response.json()
    
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one action in the environment.
        """
        response = self.session.post(f"{self.url}/step", json=action)
        response.raise_for_status()
        return response.json()
    
    def state(self) -> Dict[str, Any]:
        """
        Get the current environment state.
        """
        response = self.session.get(f"{self.url}/state")
        response.raise_for_status()
        return response.json()
    
    def get_tasks(self) -> Dict[str, Any]:
        """
        Get list of available tasks and all model schemas.
        """
        response = self.session.get(f"{self.url}/tasks")
        response.raise_for_status()
        return response.json()
    
    def get_grader(self) -> Dict[str, Any]:
        """
        Get the final grade for the current episode.
        """
        response = self.session.get(f"{self.url}/grader")
        response.raise_for_status()
        return response.json()
    
    def run_baseline(self) -> Dict[str, Any]:
        """
        Trigger the baseline inference scrip
        """
        response = self.session.post(f"{self.url}/baseline")
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    # Example usage
    client = BugReproClient()
    
    print("🔍 Checking server health...")
    health = client.health()
    print(f"✅ Server: {health}")
    
    print("\n📋 Available tasks:")
    tasks = client.get_tasks()
    for task in tasks["tasks"]:
        print(f"  - {task['id']}: {task['description']}")
    
    print("\n🎮 Running easy task...")
    obs = client.reset(task_id="easy")
    print(f"Initial: bug_id={obs['bug_id']}, remaining={obs['remaining_steps']}")
    
    print("\n⚙️ Setting file_size parameter...")
    action = {
        "action_type": "change_parameter",
        "parameter": "file_size",
        "value": "100MB"
    }
    result = client.step(action)
    print(f"Reward: {result['reward']['score']}")
    
    print("\n📊 Episode grade:")
    grade = client.get_grader()
    print(f"  Score: {grade['score']}")
    print(f"  Success: {grade['success']}")
