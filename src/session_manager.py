# File: src/session_manager.py
import hashlib
import json
from pathlib import Path
from datetime import datetime

class SessionManager:
    def __init__(self, root="."):
        self.root = Path(root)
        self.sessions_dir = self.root / ".lec" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_path = self.root / ".lec" / "active_session"

    def get_project_hash(self, path):
        return hashlib.sha256(str(Path(path).resolve()).encode()).hexdigest()[:8]

    def get_session_path(self, path):
        return self.sessions_dir / self.get_project_hash(path)

    def set_active(self, path):
        session_path = self.get_session_path(path)
        session_path.mkdir(parents=True, exist_ok=True)
        with open(self.active_path, 'w') as f:
            f.write(str(session_path))

    def get_active(self):
        if self.active_path.exists():
            return Path(self.active_path.read_text().strip())
        return None

    def list_sessions(self):
        return [p for p in self.sessions_dir.iterdir() if p.is_dir()]

    def save_session_metadata(self, session_path, metadata):
        with open(session_path / "PROJECT_METADATA.lec", "w") as f:
            json.dump(metadata, f, indent=2)
        with open(session_path / "last_scanned.txt", "w") as f:
            f.write(datetime.now().isoformat())

    def load_session_metadata(self, session_path):
        meta_path = session_path / "PROJECT_METADATA.lec"
        if meta_path.exists():
            return json.loads(meta_path.read_text())
        return {}
