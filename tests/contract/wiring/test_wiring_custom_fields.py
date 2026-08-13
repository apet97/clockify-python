"""Public-method wiring: custom_fields (7 operations)."""

from clockify.models import CreateCustomFieldRequest, CustomField

from ._harness import assert_wired, make_client

COVERED = {
    "createWorkspaceCustomField",
    "deleteWorkspaceCustomField",
    "listProjectCustomFields",
    "listWorkspaceCustomFields",
    "removeProjectCustomField",
    "updateProjectCustomField",
    "updateWorkspaceCustomField",
}

FIELD_JSON = {"id": "cf1", "name": "Severity", "type": "TXT", "workspaceId": "w1"}


async def test_create_for_workspace() -> None:
    client, capture = make_client(status=201, json=FIELD_JSON)
    field = await client.custom_fields.create_for_workspace(
        CreateCustomFieldRequest(name="Severity", type="TXT"), workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="custom_fields",
        method="create_for_workspace",
        url="https://api.clockify.me/api/v1/workspaces/w1/custom-fields",
    )
    assert capture.sent_json() == {"name": "Severity", "type": "TXT"}
    assert isinstance(field, CustomField)
    assert field.id == "cf1"


async def test_delete_for_workspace_returns_none() -> None:
    client, capture = make_client(status=204, content=b"")
    result = await client.custom_fields.delete_for_workspace("cf1", workspace_id="w1")
    assert_wired(
        capture,
        resource="custom_fields",
        method="delete_for_workspace",
        url="https://api.clockify.me/api/v1/workspaces/w1/custom-fields/cf1",
    )
    assert result is None


async def test_list_for_project_query_wire_names() -> None:
    client, capture = make_client(json=[FIELD_JSON])
    fields = await client.custom_fields.list_for_project(
        "p1",
        workspace_id="w1",
        status="VISIBLE",
        entity_type=["TIMEENTRY", "USER"],
        page=1,
        page_size=50,
    )
    assert_wired(
        capture,
        resource="custom_fields",
        method="list_for_project",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/custom-fields",
        query={
            "status": ["VISIBLE"],
            "entity-type": ["TIMEENTRY", "USER"],
            "page": ["1"],
            "page-size": ["50"],
        },
    )
    assert [f.id for f in fields] == ["cf1"]


async def test_list_for_workspace_query_wire_names_and_default_workspace() -> None:
    client, capture = make_client(json=[FIELD_JSON])
    await client.custom_fields.list_for_workspace(
        name="Sev", status="VISIBLE", entity_type=["USER"], page=2, page_size=100
    )
    assert_wired(
        capture,
        resource="custom_fields",
        method="list_for_workspace",
        url="https://api.clockify.me/api/v1/workspaces/w-default/custom-fields",
        query={
            "name": ["Sev"],
            "status": ["VISIBLE"],
            "entity-type": ["USER"],
            "page": ["2"],
            "page-size": ["100"],
        },
    )


async def test_remove_from_project() -> None:
    client, capture = make_client(json=FIELD_JSON)
    field = await client.custom_fields.remove_from_project("p1", "cf1", workspace_id="w1")
    assert_wired(
        capture,
        resource="custom_fields",
        method="remove_from_project",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/custom-fields/cf1",
    )
    assert isinstance(field, CustomField)


async def test_update_for_project_sends_exact_body() -> None:
    client, capture = make_client(json=FIELD_JSON)
    await client.custom_fields.update_for_project(
        "p1", "cf1", {"defaultValue": "high", "status": "VISIBLE"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="custom_fields",
        method="update_for_project",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/custom-fields/cf1",
    )
    assert capture.sent_json() == {"defaultValue": "high", "status": "VISIBLE"}


async def test_update_for_workspace_sends_exact_body() -> None:
    client, capture = make_client(json=FIELD_JSON)
    field = await client.custom_fields.update_for_workspace(
        "cf1", {"name": "Severity", "type": "TXT", "required": True}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="custom_fields",
        method="update_for_workspace",
        url="https://api.clockify.me/api/v1/workspaces/w1/custom-fields/cf1",
    )
    assert capture.sent_json() == {"name": "Severity", "type": "TXT", "required": True}
    assert field.name == "Severity"
