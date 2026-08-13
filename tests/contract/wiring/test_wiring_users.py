"""Public-method wiring: users (12 operations)."""

from clockify.models import RoleAssignmentDtoV1, UserDtoV1, Workspace

from ._harness import assert_wired, make_client

COVERED = {
    "addLimitedUsersWithInfo",
    "addUserToWorkspace",
    "filterWorkspaceUsers",
    "giveUserManagerRole",
    "findWorkspaceUsers",
    "findUserTeamManagers",
    "getCurrentUser",
    "removeUserManagerRole",
    "updateUserCostRate",
    "updateUserCustomFieldValue",
    "updateUserHourlyRate",
    "updateUserStatus",
}

USER_JSON = {"id": "u1", "email": "a@b.c", "name": "Ada", "status": "ACTIVE"}
WORKSPACE_JSON = {"id": "w1", "name": "Acme"}


async def test_add_limited_to_workspace_returns_raw() -> None:
    client, capture = make_client(status=201, json={"invited": ["a@b.c"]})
    result = await client.users.add_limited_to_workspace(
        {"users": [{"name": "Ada"}]}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="users",
        method="add_limited_to_workspace",
        url="https://api.clockify.me/api/v1/workspaces/w1/limited-users",
    )
    assert capture.sent_json() == {"users": [{"name": "Ada"}]}
    assert result == {"invited": ["a@b.c"]}


async def test_add_to_workspace_send_email_wire_name() -> None:
    client, capture = make_client(status=201, json=WORKSPACE_JSON)
    workspace = await client.users.add_to_workspace(
        {"email": "a@b.c"}, workspace_id="w1", send_email="false"
    )
    assert_wired(
        capture,
        resource="users",
        method="add_to_workspace",
        url="https://api.clockify.me/api/v1/workspaces/w1/users",
        query={"send-email": ["false"]},
    )
    assert capture.sent_json() == {"email": "a@b.c"}
    assert isinstance(workspace, Workspace)


async def test_add_to_workspace_sends_documented_default() -> None:
    client, capture = make_client(status=201, json=WORKSPACE_JSON)
    await client.users.add_to_workspace({"email": "a@b.c"}, workspace_id="w1")
    assert_wired(
        capture,
        resource="users",
        method="add_to_workspace",
        url="https://api.clockify.me/api/v1/workspaces/w1/users",
        query={"send-email": ["true"]},
    )


async def test_filter_is_post_read() -> None:
    client, capture = make_client(json=[USER_JSON])
    users = await client.users.filter({"name": "Ada"}, workspace_id="w1")
    assert_wired(
        capture,
        resource="users",
        method="filter",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/info",
    )
    assert capture.request.method == "POST"
    assert isinstance(users[0], UserDtoV1)


async def test_grant_manager_role() -> None:
    client, capture = make_client(status=201, json=[{"id": "ra1"}])
    roles = await client.users.grant_manager_role(
        "u1", {"entityId": "g1", "role": "TEAM_MANAGER"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="users",
        method="grant_manager_role",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/u1/roles",
    )
    assert capture.sent_json() == {"entityId": "g1", "role": "TEAM_MANAGER"}
    assert isinstance(roles[0], RoleAssignmentDtoV1)


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[USER_JSON])
    users = await client.users.list(
        workspace_id="w1",
        email="a@b.c",
        project_id="pr1",
        status="ACTIVE",
        account_statuses="ACTIVE",
        name="Ada",
        sort_column="NAME",
        sort_order="ASCENDING",
        page=1,
        page_size=50,
        memberships="ALL",
        include_roles=True,
    )
    assert_wired(
        capture,
        resource="users",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/users",
        query={
            "email": ["a@b.c"],
            "project-id": ["pr1"],
            "status": ["ACTIVE"],
            "account-statuses": ["ACTIVE"],
            "name": ["Ada"],
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
            "page": ["1"],
            "page-size": ["50"],
            "memberships": ["ALL"],
            "include-roles": ["true"],
        },
    )
    assert isinstance(users[0], UserDtoV1)


async def test_list_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.users.list()
    assert_wired(
        capture,
        resource="users",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w-default/users",
        query={"include-roles": ["false"]},
    )


async def test_list_managers_query_wire_names() -> None:
    client, capture = make_client(json=[USER_JSON])
    managers = await client.users.list_managers(
        "u1", workspace_id="w1", sort_column="NAME", sort_order="ASCENDING", page=1, page_size=10
    )
    assert_wired(
        capture,
        resource="users",
        method="list_managers",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/u1/managers",
        query={
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
            "page": ["1"],
            "page-size": ["10"],
        },
    )
    assert isinstance(managers[0], UserDtoV1)


async def test_me_has_no_workspace_segment() -> None:
    client, capture = make_client(json=USER_JSON)
    user = await client.users.me(include_memberships=True)
    assert_wired(
        capture,
        resource="users",
        method="me",
        url="https://api.clockify.me/api/v1/user",
        query={"include-memberships": ["true"]},
    )
    assert isinstance(user, UserDtoV1)


async def test_revoke_manager_role_delete_with_body() -> None:
    client, capture = make_client(status=204)
    result = await client.users.revoke_manager_role(
        "u1", {"entityId": "g1", "role": "TEAM_MANAGER"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="users",
        method="revoke_manager_role",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/u1/roles",
    )
    assert capture.sent_json() == {"entityId": "g1", "role": "TEAM_MANAGER"}
    assert result is None


async def test_update_cost_rate() -> None:
    client, capture = make_client(json=WORKSPACE_JSON)
    workspace = await client.users.update_cost_rate("u1", {"amount": 1500}, workspace_id="w1")
    assert_wired(
        capture,
        resource="users",
        method="update_cost_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/u1/cost-rate",
    )
    assert capture.sent_json() == {"amount": 1500}
    assert isinstance(workspace, Workspace)


async def test_update_custom_field_value_returns_raw() -> None:
    client, capture = make_client(status=201, json={"customFieldId": "cf1", "value": "x"})
    result = await client.users.update_custom_field_value(
        "u1", "cf1", {"value": "x"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="users",
        method="update_custom_field_value",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/u1/custom-field/cf1/value",
    )
    assert capture.sent_json() == {"value": "x"}
    assert result == {"customFieldId": "cf1", "value": "x"}


async def test_update_hourly_rate() -> None:
    client, capture = make_client(json=WORKSPACE_JSON)
    workspace = await client.users.update_hourly_rate("u1", {"amount": 2500}, workspace_id="w1")
    assert_wired(
        capture,
        resource="users",
        method="update_hourly_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/u1/hourly-rate",
    )
    assert capture.sent_json() == {"amount": 2500}
    assert isinstance(workspace, Workspace)


async def test_update_status() -> None:
    client, capture = make_client(json=WORKSPACE_JSON)
    workspace = await client.users.update_status("u1", {"status": "INACTIVE"}, workspace_id="w1")
    assert_wired(
        capture,
        resource="users",
        method="update_status",
        url="https://api.clockify.me/api/v1/workspaces/w1/users/u1",
    )
    assert capture.sent_json() == {"status": "INACTIVE"}
    assert isinstance(workspace, Workspace)
