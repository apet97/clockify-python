# pyright: reportUnusedFunction=false
"""Raw read tools: users (4 reads)."""

from typing import Any

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_users_filter", annotations=READ_ANNOTATIONS)
    async def clockify_users_filter(
        workspace_id: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> ReadResult:
        """Filter workspace users (non-mutating POST). `body` is a UserFilterRequest."""
        return await raw_read(
            client,
            "filterWorkspaceUsers",
            path={"workspaceId": workspace_of(client, workspace_id)},
            body=body,
        )

    @server.tool(name="clockify_users_list", annotations=READ_ANNOTATIONS)
    async def clockify_users_list(
        workspace_id: str | None = None,
        email: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        account_statuses: str | None = None,
        name: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        memberships: str | None = None,
        include_roles: bool | None = None,
    ) -> ReadResult:
        """List workspace users with filters. `include_roles` is a required query
        parameter on the API side."""
        return await raw_read(
            client,
            "findWorkspaceUsers",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={
                "email": email,
                "project_id": project_id,
                "status": status,
                "account_statuses": account_statuses,
                "name": name,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "memberships": memberships,
                "include_roles": include_roles,
            },
        )

    @server.tool(name="clockify_users_list_managers", annotations=READ_ANNOTATIONS)
    async def clockify_users_list_managers(
        user_id: str,
        workspace_id: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ReadResult:
        """List the team managers of one user."""
        return await raw_read(
            client,
            "findUserTeamManagers",
            path={
                "workspaceId": workspace_of(client, workspace_id),
                "userId": user_id,
            },
            query={
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )

    @server.tool(name="clockify_users_me", annotations=READ_ANNOTATIONS)
    async def clockify_users_me(include_memberships: str | None = None) -> ReadResult:
        """Get the current (token-owning) user. No workspace scope."""
        return await raw_read(
            client,
            "getCurrentUser",
            query={"include_memberships": include_memberships},
        )
