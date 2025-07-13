# File: src/context.py
import os
from pathlib import Path
import json
from datetime import datetime
import hashlib

class FilesystemContext:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.cache_dir = self.project_root / ".lec" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_hash_key(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def cache_result(self, key, result):
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump({"result": result}, f)

    def load_cached_result(self, key):
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f).get("result")
        return None

    def get_context(self, current_file, max_chars=1000):
        context_parts = []

        if os.path.exists(current_file):
            with open(current_file, 'r') as f:
                context_parts.append(f"# Current file: {current_file}\n" + f.read())

        current_dir = Path(current_file).parent
        for py_file in current_dir.glob("*.py"):
            if py_file.name != Path(current_file).name:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()[:500]
                        context_parts.append(f"# {py_file.name}\n{content}")
                except:
                    pass

        return "\n\n".join(context_parts)[:max_chars]

    def init_project(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        config = {
            "initialized": datetime.now().isoformat(),
            "project_root": str(self.project_root)
        }
        with open(self.cache_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
