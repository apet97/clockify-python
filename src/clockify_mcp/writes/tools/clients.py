# pyright: reportUnusedFunction=false
"""Guarded write tools: clients."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import ClientCreate, ClientUpdate
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:
    create = GuardedOp(
        deps,
        tool_name="clockify_clients_create",
        title="Create client",
        operation_id="postWorkspacesWorkspaceIdClients",
        body_model=ClientCreate,
    )

    async def prepare_create(body: ClientCreate, workspace_id: str | None = None) -> PreparedWrite:
        return await create.prepare(
            arguments={"body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": create.workspace(workspace_id)},
            body=body,
        )

    def ask_create(
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_clients_create", annotations=tool_annotations("clockify_clients_create")
    )
    async def clockify_clients_create(
        body: ClientCreate,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_create)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_create)],
    ) -> WriteResult:
        """Create a client."""
        return await create.run(prepared, approval)

    update = GuardedOp(
        deps,
        tool_name="clockify_clients_update",
        title="Update client",
        operation_id="putWorkspacesWorkspaceIdClientsClientId",
        body_model=ClientUpdate,
    )

    async def prepare_update(
        client_id: str,
        body: ClientUpdate,
        archive_projects: bool | None = None,
        mark_tasks_as_done: bool | None = None,
        workspace_id: str | None = None,
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={
                "client_id": client_id,
                "body": body,
                "archive_projects": archive_projects,
                "mark_tasks_as_done": mark_tasks_as_done,
                "workspace_id": workspace_id,
            },
            path_args={"workspaceId": update.workspace(workspace_id), "clientId": client_id},
            body=body,
            query={
                "archive_projects": archive_projects,
                "mark_tasks_as_done": mark_tasks_as_done,
            },
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_clients_update", annotations=tool_annotations("clockify_clients_update")
    )
    async def clockify_clients_update(
        client_id: str,
        body: ClientUpdate,
        archive_projects: bool | None = None,
        mark_tasks_as_done: bool | None = None,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Replace a client (PUT: send every field you want to keep)."""
        return await update.run(prepared, approval)

    delete = GuardedOp(
        deps,
        tool_name="clockify_clients_delete",
        title="Delete client",
        operation_id="deleteWorkspacesWorkspaceIdClientsClientId",
    )

    async def prepare_delete(client_id: str, workspace_id: str | None = None) -> PreparedWrite:
        return await delete.prepare(
            arguments={"client_id": client_id, "workspace_id": workspace_id},
            path_args={"workspaceId": delete.workspace(workspace_id), "clientId": client_id},
        )

    def ask_delete(
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_clients_delete", annotations=tool_annotations("clockify_clients_delete")
    )
    async def clockify_clients_delete(
        client_id: str,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_delete)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_delete)],
    ) -> WriteResult:
        """Delete a client. NOT reversible; archive it first."""
        return await delete.run(prepared, approval)
