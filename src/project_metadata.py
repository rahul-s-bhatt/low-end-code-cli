# File: src/project_metadata.py
import yaml
from pathlib import Path

METADATA_FILE = "PROJECT_METADATA.lec"

class ProjectMetadata:
    def __init__(self, root_path="."):
        self.root = Path(root_path)
        self.path = self.root / METADATA_FILE
        self.data = {}

    def exists(self):
        return self.path.exists()

    def load(self):
        if self.exists():
            with open(self.path, "r") as f:
                self.data = yaml.safe_load(f) or {}
        return self.data

    def save(self, data):
        with open(self.path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def generate_from_context(self, context_map):
        languages = list(set(v.get("language", "") for v in context_map.values() if isinstance(v, dict)))
        structure = context_map.get("__structure__", {})
        generated_summary = self._summarize_context_map(context_map)

        generated = {
            "project_name": self.root.name,
            "language": languages[0] if languages else "unknown",
            "entry_points": [],
            "test_paths": ["tests/"],
            "ignore_paths": ["venv", ".venv", "__pycache__", ".git", "node_modules"],
            "description": "",
            "generated_summary": generated_summary,
            "structure": structure 
        }
        self.save(generated)
        return generated

    def _summarize_context_map(self, context_map):
        summary = {"functions": 0, "classes": 0, "modules": 0, "score": 0}
        for file, data in context_map.items():
            if file == "__structure__":
                continue
            summary["modules"] += 1
            summary["functions"] += len(data.get("functions", []))
            summary["classes"] += len(data.get("classes", []))
        return summary