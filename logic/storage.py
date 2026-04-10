from __future__ import annotations

import json
from pathlib import Path

from logic.models import Project


class ProjectStorage:
    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, project: Project, file_path: str | None = None) -> Path:
        path = Path(file_path) if file_path else self.base_dir / "last_project.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(project.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load(self, file_path: str) -> Project:
        path = Path(file_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return Project.from_dict(payload)
