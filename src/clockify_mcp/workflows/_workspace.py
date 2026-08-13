"""Shared workspace selection for workflows that read the current user."""

from typing import Literal

WorkspaceSource = Literal["configured", "user default", "user active", "unresolved"]


def resolve_workspace_id(
    configured: str | None,
    default: str | None,
    active: str | None,
) -> tuple[str | None, WorkspaceSource]:
    """Select one workspace and report the source without overstating it."""
    if configured:
        return configured, "configured"
    if default:
        return default, "user default"
    if active:
        return active, "user active"
    return None, "unresolved"
