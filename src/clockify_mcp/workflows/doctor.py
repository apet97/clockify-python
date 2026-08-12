"""`clockify_doctor`: configuration and connectivity diagnosis. Read-only."""

from typing import Any

from clockify.client import ClockifyClient
from clockify.errors import (
    ClockifyAPIError,
    ClockifyAuthenticationError,
    ClockifyError,
)
from clockify_mcp.context import ServerConfig


async def doctor(client: ClockifyClient, config: ServerConfig) -> dict[str, Any]:
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
    record(
        "workspace configured",
        bool(config.workspace_id),
        "CLOCKIFY_WORKSPACE_ID set"
        if config.workspace_id
        else "not set; tools fall back to the user's default workspace",
    )

    user_id: str | None = None
    try:
        me = await client.users.me()
        user_id = me.id
        record("credential works", True, f"authenticated as user {me.id}")
    except ClockifyAuthenticationError:
        record("credential works", False, "Clockify rejected the credential (401)")
    except ClockifyError as exc:
        record("credential works", False, f"could not reach Clockify: {exc}")

    if user_id and config.workspace_id:
        try:
            workspace = await client.workspaces.get(workspace_id=config.workspace_id)
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
            record("workspace reachable", False, str(exc))

    healthy = all(c["ok"] for c in checks)
    return {"healthy": healthy, "checks": checks}
