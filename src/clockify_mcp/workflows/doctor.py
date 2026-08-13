"""`clockify_doctor`: configuration and connectivity diagnosis. Read-only."""

from typing import Any

from clockify.errors import (
    ClockifyAPIError,
    ClockifyAuthenticationError,
    ClockifyError,
)
from clockify_mcp.context import ServerConfig
from clockify_mcp.errors import to_tool_error
from clockify_mcp.read_capability import WorkflowReadClient
from clockify_mcp.workflows._workspace import resolve_workspace_id


async def doctor(client: WorkflowReadClient, config: ServerConfig) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": ok, "detail": detail})

    credential_kind = (
        "api_key" if config.api_key else "addon_token" if config.addon_token else "missing"
    )
    both = bool(config.api_key) and bool(config.addon_token)
    record(
        "credential configured",
        credential_kind != "missing" and not both,
        "exactly one credential set"
        if credential_kind != "missing" and not both
        else "set exactly one of CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN",
    )
    me = None
    try:
        me = await client.users.me()
        record("credential works", True, f"authenticated as user {me.id}")
    except ClockifyAuthenticationError:
        record("credential works", False, "Clockify rejected the credential (401)")
    except ClockifyError as exc:
        record("credential works", False, str(to_tool_error(exc)))

    workspace_id, workspace_source = resolve_workspace_id(
        config.workspace_id,
        me.default_workspace if me else None,
        me.active_workspace if me else None,
    )
    record(
        "workspace resolved",
        workspace_id is not None,
        f"using {workspace_source} workspace {workspace_id}"
        if workspace_id
        else "set CLOCKIFY_WORKSPACE_ID or select a default or active workspace",
    )

    if me and workspace_id:
        try:
            workspace = await client.workspaces.get(workspace_id=workspace_id)
            record(
                "workspace reachable",
                True,
                f"workspace {workspace.id} ({workspace.name}) is accessible",
            )
        except ClockifyAPIError as exc:
            record(
                "workspace reachable",
                False,
                f"HTTP {exc.status_code}: the credential cannot access this workspace",
            )
        except ClockifyError as exc:
            record("workspace reachable", False, str(to_tool_error(exc)))

    healthy = all(c["ok"] for c in checks)
    return {"healthy": healthy, "checks": checks}
