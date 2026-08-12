"""`clockify_status`: who am I, which workspace, what is running."""

from typing import Any

from clockify.client import ClockifyClient
from clockify.errors import ClockifyError
from clockify_mcp.errors import to_tool_error


async def status(client: ClockifyClient) -> dict[str, Any]:
    try:
        me = await client.users.me()
        workspace_id = client.workspace_id or me.default_workspace or me.active_workspace
        running: list[dict[str, Any]] = []
        workspace: dict[str, Any] | None = None
        if workspace_id:
            workspace_model = await client.workspaces.get(workspace_id=workspace_id)
            workspace = {
                "id": workspace_model.id,
                "name": workspace_model.name,
            }
            in_progress = await client.time_entries.list_in_progress(
                workspace_id=workspace_id, page=1, page_size=25
            )
            running = [
                {
                    "id": entry.id,
                    "userId": entry.user_id,
                    "description": entry.description,
                    "projectId": entry.project_id,
                    "start": entry.time_interval.start if entry.time_interval else None,
                }
                for entry in in_progress
            ]
    except ClockifyError as exc:
        raise to_tool_error(exc) from exc
    return {
        "user": {"id": me.id, "name": me.name, "email": me.email},
        "workspace": workspace,
        "workspace_source": "configured" if client.workspace_id else "user default",
        "running_entries": running,
    }
