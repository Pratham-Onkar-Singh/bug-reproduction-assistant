import subprocess
import sys
import json


def run_all_tasks():
    try:
        result = subprocess.run(
            [sys.executable, "inference.py"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
            cwd="."
        )
        
        if result.returncode != 0:
            return {
                "status": "error",
                "error": result.stderr,
                "stdout": result.stdout,
            }
        
        # Parse output logs
        lines = result.stdout.strip().split("\n")
        results = {
            "status": "success",
            "logs": lines,
            "raw_output": result.stdout,
        }
        
        return results
    
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Baseline script exceeded 10 minute timeout",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
