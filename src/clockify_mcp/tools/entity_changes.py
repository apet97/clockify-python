# pyright: reportUnusedFunction=false
"""Raw read tools: entity_changes (3 reads).


Experimental endpoints: `type` is required (repeated key of
ChangeTrackerDocumentType values); `page`/`limit` are string-typed on the wire
(defaults '0'/'50') and there is no Last-Page header. Omitted start/end default
to a 30-day window anchored on the provided bound (or the current date).
"""

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.result import ReadResult
from clockify_mcp.tools._shared import READ_ANNOTATIONS, raw_read, workspace_of


def register(server: MCPServer, client: ClockifyClient) -> None:
    @server.tool(name="clockify_entity_changes_list_created", annotations=READ_ANNOTATIONS)
    async def clockify_entity_changes_list_created(
        type: list[str],
        workspace_id: str | None = None,
        start: str | None = None,
        end: str | None = None,
        page: str | None = None,
        limit: str | None = None,
    ) -> ReadResult:
        """List entities created in a period (experimental). `type` is required;
        `page`/`limit` are strings on the wire; no Last-Page header."""
        return await raw_read(
            client,
            "getCreatedEntityInfo",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"type": type, "start": start, "end": end, "page": page, "limit": limit},
        )

    @server.tool(name="clockify_entity_changes_list_deleted", annotations=READ_ANNOTATIONS)
    async def clockify_entity_changes_list_deleted(
        type: list[str],
        workspace_id: str | None = None,
        start: str | None = None,
        end: str | None = None,
        page: str | None = None,
        limit: str | None = None,
    ) -> ReadResult:
        """List entities deleted in a period (experimental). `type` is required;
        `page`/`limit` are strings on the wire; no Last-Page header."""
        return await raw_read(
            client,
            "getDeletedEntityInfo",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"type": type, "start": start, "end": end, "page": page, "limit": limit},
        )

    @server.tool(name="clockify_entity_changes_list_updated", annotations=READ_ANNOTATIONS)
    async def clockify_entity_changes_list_updated(
        type: list[str],
        workspace_id: str | None = None,
        start: str | None = None,
        end: str | None = None,
        page: str | None = None,
        limit: str | None = None,
    ) -> ReadResult:
        """List entities updated in a period (experimental). `type` is required;
        `page`/`limit` are strings on the wire; no Last-Page header."""
        return await raw_read(
            client,
            "getUpdatedEntityInfo",
            path={"workspaceId": workspace_of(client, workspace_id)},
            query={"type": type, "start": start, "end": end, "page": page, "limit": limit},
        )
