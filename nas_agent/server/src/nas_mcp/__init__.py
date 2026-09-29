"""nas-mcp: plan, submit, track and verify large dataset downloads onto a NAS."""

__version__ = "0.1.0"


class NasError(Exception):
    """Actionable error surfaced to the agent as a tool error."""
