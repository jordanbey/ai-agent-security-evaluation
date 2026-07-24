import pytest

from agent_runtime_eval.schemas import AgentTrace


def test_rejects_empty_trace() -> None:
    with pytest.raises(ValueError, match="at least one"):
        AgentTrace.from_dict(
            {
                "trace_id": "empty",
                "expected_compromised": False,
                "compromise_cycle": None,
                "events": [],
            }
        )


def test_rejects_unsorted_cycles() -> None:
    with pytest.raises(ValueError, match="unique and sorted"):
        AgentTrace.from_dict(
            {
                "trace_id": "unsorted",
                "expected_compromised": False,
                "compromise_cycle": None,
                "events": [
                    {
                        "cycle": 2,
                        "authorized_goal": "Analyze reports",
                        "current_subgoal": "Write report",
                        "tool": None,
                        "resource": None,
                        "action": "Write",
                        "progress": True,
                    },
                    {
                        "cycle": 1,
                        "authorized_goal": "Analyze reports",
                        "current_subgoal": "Read reports",
                        "tool": None,
                        "resource": None,
                        "action": "Read",
                        "progress": True,
                    },
                ],
            }
        )
