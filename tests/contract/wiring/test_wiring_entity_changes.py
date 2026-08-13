"""Public-method wiring: entity_changes (3 operations)."""

import pytest

from clockify.errors import ClockifyConfigurationError
from clockify.models import EntityChangeDocument

from ._harness import assert_wired, make_client

COVERED = {
    "getCreatedEntityInfo",
    "getDeletedEntityInfo",
    "getUpdatedEntityInfo",
}

DOC_JSON = {
    "id": "d1",
    "documentCode": "TAGS",
    "auditMetadata": {"createdAt": "2026-08-01T00:00:00Z"},
}


async def test_list_created_query_wire_names() -> None:
    client, capture = make_client(json=[DOC_JSON])
    docs = await client.entity_changes.list_created(
        workspace_id="w1",
        type=["TAGS", "CLIENTS"],
        start="2026-08-01T00:00:00Z",
        end="2026-08-12T00:00:00Z",
        page="0",
        limit="50",
    )
    assert_wired(
        capture,
        resource="entity_changes",
        method="list_created",
        url="https://api.clockify.me/api/v1/workspaces/w1/entities/created",
        query={
            "type": ["TAGS", "CLIENTS"],
            "start": ["2026-08-01T00:00:00Z"],
            "end": ["2026-08-12T00:00:00Z"],
            "page": ["0"],
            "limit": ["50"],
        },
    )
    assert isinstance(docs[0], EntityChangeDocument)
    assert docs[0].document_code == "TAGS"


async def test_list_deleted() -> None:
    client, capture = make_client(json=[DOC_JSON])
    await client.entity_changes.list_deleted(
        workspace_id="w1", type=["TIME_ENTRY"], page="1", limit="25"
    )
    assert_wired(
        capture,
        resource="entity_changes",
        method="list_deleted",
        url="https://api.clockify.me/api/v1/workspaces/w1/entities/deleted",
        query={"type": ["TIME_ENTRY"], "page": ["1"], "limit": ["25"]},
    )


async def test_list_updated_default_workspace() -> None:
    client, capture = make_client(json=[])
    docs = await client.entity_changes.list_updated(type=["PROJECTS"])
    assert_wired(
        capture,
        resource="entity_changes",
        method="list_updated",
        url="https://api.clockify.me/api/v1/workspaces/w-default/entities/updated",
        query={"type": ["PROJECTS"]},
    )
    assert docs == []


async def test_required_type_rejects_none_before_transport() -> None:
    client, capture = make_client(json=[])

    with pytest.raises(ClockifyConfigurationError, match="required query parameter 'type'"):
        await client.entity_changes.list_created(type=None)  # type: ignore[arg-type]

    assert capture.requests == []
