import json
from pathlib import Path

from src.analyzer import EXT_LANGUAGE_MAP
from .project_metadata import ProjectMetadata

class SmartContextBuilder:
    def __init__(self, root="."):
        self.root = Path(root)
        self.metadata = ProjectMetadata(root).load()
        self.context_map = self._load_context_map()
        self.ignore = set(self.metadata.get("ignore_paths", []))

    def _load_context_map(self):
        context_file = self.root / ".lec" / "context_map.json"
        if context_file.exists():
            return json.loads(context_file.read_text())
        return {}

    def build_for(self, filepath, max_chars=1500):
        return self._build_trimmed_context(filepath, max_chars)

    def _build_trimmed_context(self, filepath, max_chars):
        buffer = []
        seen = set()
        files = self._rank_files_by_relevance(filepath)

        for f in files:
            if f in seen:
                continue
            if any(p in Path(f).parts for p in self.ignore):
                continue
            try:
                with open(f, "r", encoding="utf-8") as src:
                    code = src.read()
                    if len(code) > 800:
                        code = code[:800] + "\n# ...trimmed...\n"
                    buffer.append(f"# File: {f}\n{code}")
                    seen.add(f)
            except:
                continue
            if sum(len(x) for x in buffer) > max_chars:
                break

        return "\n\n".join(buffer)


    def _rank_files_by_relevance(self, filepath):
        ranked = [str(Path(filepath).resolve())]

        entry_points = self.metadata.get("entry_points", [])
        structure = self.metadata.get("structure", {})

        # Add entry points first
        for ep in entry_points:
            ep_path = self.root / ep
            if ep_path.exists():
                ranked.append(str(ep_path.resolve()))

        # Prioritize folders like 'routes', 'models', 'core', etc.
        priority_folders = ["routes", "core", "models", "src"]
        for folder in priority_folders:
            folder_path = self.root / folder
            if folder_path.exists():
                for file in folder_path.rglob("*"):
                    if file.is_file() and file.suffix in EXT_LANGUAGE_MAP:
                        ranked.append(str(file.resolve()))

        return ranked

