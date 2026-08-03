"""
Controlled execution for security-focused tools.
"""

from typing import Any

from audit_logger import log_event
from tools import TOOL_FUNCTIONS
from validation import validate_tool_request


def run_tool(
    tool_name: str,
    arguments: dict[str, Any],
    allowed_tool_names: set[str],
) -> dict[str, Any]:
    """Validate, authorize, execute, and log one tool request."""

    log_event(
        "tool_requested",
        {
            "tool_name": tool_name,
            "arguments": arguments,
        },
    )

    is_valid, reason = validate_tool_request(
        tool_name=tool_name,
        arguments=arguments,
        allowed_tool_names=allowed_tool_names,
    )

    if not is_valid:
        log_event(
            "tool_blocked",
            {
                "tool_name": tool_name,
                "reason": reason,
            },
        )

        return {
            "success": False,
            "error": reason,
        }

    tool_function = TOOL_FUNCTIONS.get(tool_name)

    if tool_function is None:
        reason = f"No implementation exists for '{tool_name}'."

        log_event(
            "tool_failed",
            {
                "tool_name": tool_name,
                "reason": reason,
            },
        )

        return {
            "success": False,
            "error": reason,
        }

    try:
        result = tool_function(**arguments)

    except Exception as exc:
        log_event(
            "tool_failed",
            {
                "tool_name": tool_name,
                "reason": str(exc),
            },
        )

        return {
            "success": False,
            "error": str(exc),
        }

    log_event(
        "tool_executed",
        {
            "tool_name": tool_name,
            "result": result,
        },
    )

    return {
        "success": True,
        "tool_name": tool_name,
        "result": result,
    }