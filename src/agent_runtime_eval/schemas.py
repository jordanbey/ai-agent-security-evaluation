from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeEvent:
    cycle: int
    authorized_goal: str
    current_subgoal: str
    tool: str | None
    resource: str | None
    action: str
    progress: bool
    privilege_level: int = 0
    labels: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuntimeEvent":
        return cls(
            cycle=int(data["cycle"]),
            authorized_goal=str(data["authorized_goal"]),
            current_subgoal=str(data["current_subgoal"]),
            tool=data.get("tool"),
            resource=data.get("resource"),
            action=str(data["action"]),
            progress=bool(data["progress"]),
            privilege_level=int(data.get("privilege_level", 0)),
            labels=tuple(data.get("labels", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class AgentTrace:
    trace_id: str
    expected_compromised: bool
    compromise_cycle: int | None
    events: tuple[RuntimeEvent, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentTrace":
        events = tuple(RuntimeEvent.from_dict(item) for item in data["events"])
        if not events:
            raise ValueError("A trace must contain at least one runtime event.")

        cycles = [event.cycle for event in events]
        if cycles != sorted(cycles) or len(cycles) != len(set(cycles)):
            raise ValueError("Event cycles must be unique and sorted.")

        compromise_cycle = data.get("compromise_cycle")
        return cls(
            trace_id=str(data["trace_id"]),
            expected_compromised=bool(data["expected_compromised"]),
            compromise_cycle=int(compromise_cycle) if compromise_cycle is not None else None,
            events=events,
        )
