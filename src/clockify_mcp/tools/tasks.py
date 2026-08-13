# pyright: reportUnusedFunction=false
"""Raw read tools: tasks (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_tasks_get", annotations=READ_ANNOTATIONS)
    async def clockify_tasks_get(
        project_id: str, task_id: str, workspace_id: str | None = None
    ) -> ReadResult:
        """Get one task by ID on a project."""
        return await raw_read(
            client,
            "getTaskById",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "projectId": project_id,
                "taskId": task_id,
            },
        )

    @server.tool(name="clockify_tasks_list", annotations=READ_ANNOTATIONS)
    async def clockify_tasks_list(
        project_id: str,
        workspace_id: str | None = None,
        name: str | None = None,
        strict_name_search: bool | None = None,
        is_active: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
    ) -> ReadResult:
        """List tasks on a project; filter by `name` or `is_active`."""
        return await raw_read(
            client,
            "findTasksOnProject",
            path={"workspaceId": workspace_of(client, workspace_id), "projectId": project_id},
            query={
                "name": name,
                "strict_name_search": strict_name_search,
                "is_active": is_active,
                "page": page,
                "page_size": page_size,
                "sort_column": sort_column,
                "sort_order": sort_order,
            },
        )
