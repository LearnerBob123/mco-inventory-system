from __future__ import annotations

from datetime import datetime
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
WORKFLOW_LOG = LOG_DIR / "workflow_audit.log"


def log_workflow_event(action: str, message: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    with WORKFLOW_LOG.open("a", encoding="utf-8") as file_handle:
        file_handle.write(f"{timestamp} | {action} | {message}\n")
