"""`clockify_workspace_overview`: identity plus concise entity counts."""

from typing import Any

from clockify.errors import ClockifyError
from clockify_mcp.errors import ToolError, to_tool_error
from clockify_mcp.read_capability import WorkflowReadClient

_SAMPLE_PAGE_SIZE = 50  # bounded: one page per entity type, never a full crawl


async def workspace_overview(
    client: WorkflowReadClient, workspace_id: str | None = None
) -> dict[str, Any]:
    resolved = workspace_id or client.workspace_id
    try:
        if not resolved:
            me = await client.users.me()
            resolved = me.default_workspace or me.active_workspace
        if not resolved:
            raise ToolError("no workspace_id configured and the user has no default workspace")
        workspace = await client.workspaces.get(workspace_id=resolved)
        users = await client.users.list(workspace_id=resolved, page=1, page_size=_SAMPLE_PAGE_SIZE)
        projects = await client.projects.list(
            workspace_id=resolved, page=1, page_size=_SAMPLE_PAGE_SIZE
        )
        tags = await client.tags.list(workspace_id=resolved, page=1, page_size=_SAMPLE_PAGE_SIZE)
    except ClockifyError as exc:
        raise to_tool_error(exc) from exc

    def count_of(items: list[Any]) -> dict[str, Any]:
        exact = len(items) < _SAMPLE_PAGE_SIZE
        return {"count": len(items), "exact": exact}

    settings = workspace.workspace_settings
    return {
        "workspace": {"id": workspace.id, "name": workspace.name},
        "users": count_of(users),
        "projects": count_of(projects),
        "tags": count_of(tags),
        "settings": {
            "onlyAdminsCreateProject": getattr(settings, "only_admins_create_project", None),
            "onlyAdminsSeeAllTimeEntries": getattr(
                settings, "only_admins_see_all_time_entries", None
            ),
            "forceProjects": getattr(settings, "force_projects", None),
            "forceTasks": getattr(settings, "force_tasks", None),
        }
        if settings is not None
        else None,
        "note": f"counts sample the first page (size {_SAMPLE_PAGE_SIZE}); "
        "exact=false means more may exist",
    }
