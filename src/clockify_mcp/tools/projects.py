# pyright: reportUnusedFunction=false
"""Raw read tools: projects (2 reads)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_projects_get", annotations=READ_ANNOTATIONS)
    async def clockify_projects_get(
        project_id: str,
        workspace_id: str | None = None,
        hydrated: bool | None = None,
        custom_field_entity_type: str | None = None,
        expense_limit: int | None = None,
        expense_date: str | None = None,
    ) -> ReadResult:
        """Get one project by ID. Deleted, never-existing, and foreign IDs all
        return the same 400 (code 501) body, never a 404."""
        return await raw_read(
            client,
            "getProjectById",
            path={"workspaceId": workspace_of(client, workspace_id), "projectId": project_id},
            query={
                "hydrated": hydrated,
                "custom_field_entity_type": custom_field_entity_type,
                "expense_limit": expense_limit,
                "expense_date": expense_date,
            },
        )

    @server.tool(name="clockify_projects_list", annotations=READ_ANNOTATIONS)
    async def clockify_projects_list(
        workspace_id: str | None = None,
        name: str | None = None,
        strict_name_search: bool | None = None,
        archived: bool | None = None,
        billable: bool | None = None,
        clients: list[str] | None = None,
        contains_client: bool | None = None,
        client_status: str | None = None,
        users: list[str] | None = None,
        contains_user: bool | None = None,
        user_status: str | None = None,
        is_template: bool | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        hydrated: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        access: str | None = None,
        expense_limit: int | None = None,
        expense_date: str | None = None,
        user_groups: list[str] | None = None,
        contains_group: bool | None = None,
    ) -> ReadResult:
        """List workspace projects. Omitting `archived` returns archived AND active
        projects; only archived=false restricts to active."""
        return await raw_read(
            client,
            "getWorkspaceProjects",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "name": name,
                "strict_name_search": strict_name_search,
                "archived": archived,
                "billable": billable,
                "clients": clients,
                "contains_client": contains_client,
                "client_status": client_status,
                "users": users,
                "contains_user": contains_user,
                "user_status": user_status,
                "is_template": is_template,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "hydrated": hydrated,
                "page": page,
                "page_size": page_size,
                "access": access,
                "expense_limit": expense_limit,
                "expense_date": expense_date,
                "user_groups": user_groups,
                "contains_group": contains_group,
            },
        )
