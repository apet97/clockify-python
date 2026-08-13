"""Public-method wiring: tags (5 operations)."""

import pydantic
import pytest

from clockify.errors import ClockifyResponseValidationError
from clockify.models import TagCreate, TagDto

from ._harness import assert_wired, make_client

COVERED = {
    "postWorkspacesWorkspaceIdTags",
    "deleteWorkspacesWorkspaceIdTagsTagId",
    "getWorkspacesWorkspaceIdTagsTagId",
    "getWorkspacesWorkspaceIdTags",
    "putWorkspacesWorkspaceIdTagsTagId",
}

TAG_JSON = {"id": "t1", "name": "billing", "workspaceId": "w1", "archived": False}


async def test_create() -> None:
    client, capture = make_client(status=201, json=TAG_JSON)
    tag = await client.tags.create(TagCreate(name="billing"), workspace_id="w1")
    assert_wired(
        capture,
        resource="tags",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/tags",
    )
    assert capture.sent_json() == {"name": "billing"}
    assert isinstance(tag, TagDto)
    assert tag.id == "t1"


async def test_create_accepts_mapping_and_default_workspace() -> None:
    client, capture = make_client(status=201, json=TAG_JSON)
    await client.tags.create({"name": "billing"})
    assert "/workspaces/w-default/tags" in str(capture.request.url)


async def test_delete_returns_deleted_entity() -> None:
    client, capture = make_client(json=TAG_JSON)
    tag = await client.tags.delete("t1", workspace_id="w1")
    assert_wired(
        capture,
        resource="tags",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/tags/t1",
    )
    assert tag.name == "billing"


async def test_get() -> None:
    client, capture = make_client(json=TAG_JSON)
    await client.tags.get("t1", workspace_id="w1")
    assert_wired(
        capture,
        resource="tags",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/tags/t1",
    )


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[TAG_JSON])
    tags = await client.tags.list(
        workspace_id="w1",
        name="bil",
        strict_name_search=True,
        excluded_ids="a,b",
        archived=False,
        page=2,
        page_size=10,
    )
    assert_wired(
        capture,
        resource="tags",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/tags",
        query={
            "name": ["bil"],
            "strict-name-search": ["true"],
            "excluded-ids": ["a,b"],
            "archived": ["false"],
            "page": ["2"],
            "page-size": ["10"],
        },
    )
    assert [t.id for t in tags] == ["t1"]


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=TAG_JSON)
    await client.tags.update("t1", {"name": "billing", "archived": True}, workspace_id="w1")
    assert_wired(
        capture,
        resource="tags",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/tags/t1",
    )
    assert capture.sent_json() == {"name": "billing", "archived": True}


async def test_update_requires_archived_before_transport() -> None:
    client, capture = make_client(json=TAG_JSON)

    with pytest.raises(pydantic.ValidationError):
        await client.tags.update("t1", {"name": "billing"}, workspace_id="w1")

    assert capture.requests == []


async def test_update_rejects_unknown_field_before_transport() -> None:
    client, capture = make_client(json=TAG_JSON)

    with pytest.raises(pydantic.ValidationError):
        await client.tags.update(
            "t1",
            {"name": "billing", "archived": True, "archive": False},
            workspace_id="w1",
        )

    assert capture.requests == []


async def test_response_validation_error_exposes_only_controlled_metadata() -> None:
    secret = "private-upstream-value"
    client, _capture = make_client(json={"archived": secret})

    with pytest.raises(ClockifyResponseValidationError) as info:
        await client.tags.get("t1", workspace_id="w1")

    message = str(info.value)
    assert message == (
        "getWorkspacesWorkspaceIdTagsTagId: response validation failed with 1 error(s)"
    )
    assert secret not in message
    assert "input_value" not in message
    assert info.value.operation_id == "getWorkspacesWorkspaceIdTagsTagId"
    assert info.value.__cause__ is None
    assert info.value.__context__ is None
    traceback = info.value.__traceback__
    while traceback is not None:
        if "/src/clockify/" in traceback.tb_frame.f_code.co_filename:
            assert all(secret not in repr(value) for value in traceback.tb_frame.f_locals.values())
        traceback = traceback.tb_next
