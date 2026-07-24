from __future__ import annotations

import json
from pathlib import Path

from .schemas import AgentTrace


def load_trace(path: str | Path) -> AgentTrace:
    trace_path = Path(path)
    try:
        data = json.loads(trace_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Trace file not found: {trace_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in trace file: {trace_path}") from exc

    return AgentTrace.from_dict(data)
