"""One-shot uplink scheduling, independent of Home Assistant and device type."""
from dataclasses import dataclass
from datetime import datetime, timedelta

DEFAULTS = {"mode": "disabled", "lead_seconds": 20, "delay_seconds": 580,
            "minimum_seconds": 30}


@dataclass
class UplinkSchedule:
    """Filter bursts against the accepted anchor, never against a follow-up."""

    anchor: datetime | None = None

    def observe(self, now: datetime, settings: dict) -> dict | None:
        """Return a new plan for an accepted uplink, or ignore a burst."""
        if settings["mode"] == "disabled":
            return None
        interval = (now - self.anchor).total_seconds() if self.anchor else None
        if interval is not None and interval < settings["minimum_seconds"]:
            return None
        self.anchor = now
        automatic = settings["mode"] == "automatic"
        expected = now + timedelta(seconds=interval) if automatic and interval is not None else None
        offset = -settings["lead_seconds"] if automatic else settings["delay_seconds"]
        scheduled = expected + timedelta(seconds=offset) if expected else (
            None if automatic else now + timedelta(seconds=offset)
        )
        # A lead >= interval cannot predict a future window. Do not fire late.
        if scheduled is not None and scheduled <= now:
            scheduled = None
        return {"mode": settings["mode"], "interval_seconds": interval,
                "offset_seconds": offset, "last_uplink": now,
                "expected_next_uplink": expected, "scheduled_for": scheduled}
