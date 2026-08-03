"""
Structured audit logging for tool lifecycle events.
"""

import json
from datetime import datetime, timezone
from typing import Any


def log_event(
    event_type: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    """Create and display one structured audit event."""

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "details": details,
    }

    print("\nAUDIT EVENT")
    print(json.dumps(event, indent=2))

    return event