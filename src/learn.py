# File: src/learn.py
import json
from pathlib import Path
from datetime import datetime

class LearnTracker:
    def __init__(self, root="."):
        self.base = Path(root) / ".lec" / "learning"
        self.base.mkdir(parents=True, exist_ok=True)

    def log_completion(self, prompt, output, accepted=False):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "output": output,
            "accepted": accepted
        }
        self._append("completions.jsonl", entry)

    def log_correction(self, before, after, reason=""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "before": before,
            "after": after,
            "reason": reason
        }
        self._append("corrections.jsonl", entry)

    def log_test_feedback(self, file, passed, trace=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file,
            "result": "pass" if passed else "fail",
            "trace": trace
        }
        self._append("test_feedback.jsonl", entry)

    def _append(self, fname, obj):
        path = self.base / fname
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj) + "\n")
