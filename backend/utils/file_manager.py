from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parents[1].parents[0] / "storage"


def save_code_file(task_id: int, version: str, filename: str, content: str) -> str:
    dest = BASE / "code" / str(task_id) / version
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def save_log_file(task_id: int, run_id: str, filename: str, content: str) -> str:
    dest = BASE / "logs" / str(task_id) / run_id
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def list_code_versions(task_id: int):
    dirpath = BASE / "code" / str(task_id)
    if not dirpath.exists():
        return []
    versions = []
    for v in sorted(dirpath.iterdir()):
        files = [f.name for f in v.iterdir() if f.is_file()]
        versions.append({"version": v.name, "files": files})
    return versions
