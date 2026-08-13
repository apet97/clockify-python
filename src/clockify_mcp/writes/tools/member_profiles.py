# pyright: reportUnusedFunction=false
"""Guarded write tools: member profiles."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve

from clockify.models import MemberProfileUpdateRequest
from clockify_mcp.writes.plan import PreparedWrite
from clockify_mcp.writes.runner import WriteApproval, WriteDeps, elicit_approval
from clockify_mcp.writes.state import WriteResult
from clockify_mcp.writes.tools._shared import GuardedOp, tool_annotations


def register(server: MCPServer, deps: WriteDeps) -> None:

    update = GuardedOp(
        deps,
        tool_name="clockify_member_profiles_update",
        title="Update member profile",
        operation_id="updateMemberProfile",
        body_model=MemberProfileUpdateRequest,
    )

    async def prepare_update(
        user_id: str, body: MemberProfileUpdateRequest, workspace_id: str | None = None
    ) -> PreparedWrite:
        return await update.prepare(
            arguments={"user_id": user_id, "body": body, "workspace_id": workspace_id},
            path_args={"workspaceId": update.workspace(workspace_id), "userId": user_id},
            body=body,
        )

    def ask_update(
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
    ) -> Elicit[WriteApproval]:
        return elicit_approval(prepared)

    @server.tool(
        name="clockify_member_profiles_update",
        annotations=tool_annotations("clockify_member_profiles_update"),
    )
    async def clockify_member_profiles_update(
        user_id: str,
        body: MemberProfileUpdateRequest,
        workspace_id: str | None = None,
        *,
        prepared: Annotated[PreparedWrite, Resolve(prepare_update)],
        approval: Annotated[ElicitationResult[WriteApproval], Resolve(ask_update)],
    ) -> WriteResult:
        """Update a member's profile fields (PATCH)."""
        return await update.run(prepared, approval)
