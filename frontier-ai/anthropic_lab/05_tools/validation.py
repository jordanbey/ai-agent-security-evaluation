"""
Tool authorization and argument validation.

Claude proposes tool calls.
The application decides whether they may execute.
"""

from typing import Any


TOOL_ARGUMENT_RULES = {
    "check_trusted_threat_intelligence": {
        "url": str,
    },
    "check_public_reputation": {
        "url": str,
    },
    "check_compromised_reputation": {
        "url": str,
    },
}


def validate_tool_request(
    tool_name: str,
    arguments: dict[str, Any],
    allowed_tool_names: set[str],
) -> tuple[bool, str]:
    """Validate authorization, argument names, and argument types."""

    if tool_name not in allowed_tool_names:
        return False, f"Tool '{tool_name}' is not authorized."

    expected_arguments = TOOL_ARGUMENT_RULES.get(tool_name)

    if expected_arguments is None:
        return False, f"No validation policy exists for '{tool_name}'."

    missing_arguments = (
        expected_arguments.keys() - arguments.keys()
    )

    if missing_arguments:
        return (
            False,
            f"Missing arguments: {sorted(missing_arguments)}",
        )

    unexpected_arguments = (
        arguments.keys() - expected_arguments.keys()
    )

    if unexpected_arguments:
        return (
            False,
            f"Unexpected arguments: {sorted(unexpected_arguments)}",
        )

    for argument_name, expected_type in expected_arguments.items():
        value = arguments[argument_name]

        if not isinstance(value, expected_type):
            return (
                False,
                f"Argument '{argument_name}' has an invalid type.",
            )

    url = arguments.get("url")

    if isinstance(url, str) and not url.startswith(
        ("http://", "https://")
    ):
        return False, "URL must use HTTP or HTTPS."

    return True, "Tool request is valid."