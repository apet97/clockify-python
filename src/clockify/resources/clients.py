"""Clients resource: explicit methods over the client operations."""

import builtins
from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from clockify.models import Client, ClientCreate, ClientUpdate
from clockify.operations.clients import (
    CLIENTS_CREATE,
    CLIENTS_DELETE,
    CLIENTS_GET,
    CLIENTS_LIST,
    CLIENTS_UPDATE,
)
from clockify.resources._base import ResourceBase

_CLIENT_LIST = TypeAdapter(list[Client])


class ClientsResource(ResourceBase):
    async def create(
        self, body: "ClientCreate | Mapping[str, Any]", *, workspace_id: str | None = None
    ) -> Client:
        """ccEmails and currencyId are silently ignored on create; only update persists them."""
        validated = self._coerce(body, ClientCreate)
        response = await self._call(
            CLIENTS_CREATE, path={"workspaceId": self._workspace(workspace_id)}, body=validated
        )
        return self._adapt(CLIENTS_CREATE, response, Client)

    async def delete(self, client_id: str, *, workspace_id: str | None = None) -> Client:
        """Client must be archived first; Clockify answers 200 with the deleted entity."""
        response = await self._call(
            CLIENTS_DELETE,
            path={"workspaceId": self._workspace(workspace_id), "clientId": client_id},
        )
        return self._adapt(CLIENTS_DELETE, response, Client)

    async def get(self, client_id: str, *, workspace_id: str | None = None) -> Client:
        response = await self._call(
            CLIENTS_GET,
            path={"workspaceId": self._workspace(workspace_id), "clientId": client_id},
        )
        return self._adapt(CLIENTS_GET, response, Client)

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        name: str | None = None,
        archived: bool | None = None,
        address: str | None = None,
        note: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> builtins.list[Client]:
        """Omitting archived returns archived AND active rows; archived=false restricts to active."""
        response = await self._call(
            CLIENTS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "name": name,
                "archived": archived,
                "address": address,
                "note": note,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )
        return self._adapt(CLIENTS_LIST, response, _CLIENT_LIST)

    async def update(
        self,
        client_id: str,
        body: "ClientUpdate | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
        archive_projects: bool | None = None,
        mark_tasks_as_done: bool | None = None,
    ) -> Client:
        """Full replacement: an omitted ccEmails clears stored addresses — resend name and ccEmails."""
        validated = self._coerce(body, ClientUpdate)
        response = await self._call(
            CLIENTS_UPDATE,
            path={"workspaceId": self._workspace(workspace_id), "clientId": client_id},
            query={
                "archive_projects": archive_projects,
                "mark_tasks_as_done": mark_tasks_as_done,
            },
            body=validated,
        )
        return self._adapt(CLIENTS_UPDATE, response, Client)
