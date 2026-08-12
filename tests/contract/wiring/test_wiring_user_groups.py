"""Public-method wiring: user_groups (6 operations)."""

from clockify.models import UserGroupDtoV1

from ._harness import assert_wired, make_client

COVERED = {
    "addUsersToGroup",
    "addNewGroup",
    "deleteGroup",
    "findAllGroupsOnWorkspace",
    "removeUserFromGroup",
    "updateGroup",
}

GROUP_JSON = {"id": "g1", "name": "Devs", "workspaceId": "w1", "userIds": ["u1"]}


async def test_add_members() -> None:
    client, capture = make_client(json=GROUP_JSON)
    group = await client.user_groups.add_members("g1", {"userId": "u1"}, workspace_id="w1")
    assert_wired(
        capture,
        resource="user_groups",
        method="add_members",
        url="https://api.clockify.me/api/v1/workspaces/w1/user-groups/g1/users",
    )
    assert capture.sent_json() == {"userId": "u1"}
    assert isinstance(group, UserGroupDtoV1)


async def test_create() -> None:
    client, capture = make_client(status=201, json=GROUP_JSON)
    group = await client.user_groups.create({"name": "Devs"}, workspace_id="w1")
    assert_wired(
        capture,
        resource="user_groups",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/user-groups",
    )
    assert capture.sent_json() == {"name": "Devs"}
    assert isinstance(group, UserGroupDtoV1)


async def test_delete_returns_deleted_group() -> None:
    client, capture = make_client(json=GROUP_JSON)
    group = await client.user_groups.delete("g1", workspace_id="w1")
    assert_wired(
        capture,
        resource="user_groups",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/user-groups/g1",
    )
    assert isinstance(group, UserGroupDtoV1)


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[GROUP_JSON])
    groups = await client.user_groups.list(
        workspace_id="w1",
        project_id="pr1",
        name="Dev",
        sort_column="NAME",
        sort_order="ASCENDING",
        page=1,
        page_size=50,
        include_team_managers=True,
    )
    assert_wired(
        capture,
        resource="user_groups",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/user-groups",
        query={
            "project-id": ["pr1"],
            "name": ["Dev"],
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
            "page": ["1"],
            "page-size": ["50"],
            "includeTeamManagers": ["true"],
        },
    )
    assert isinstance(groups[0], UserGroupDtoV1)


async def test_list_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.user_groups.list()
    assert "/workspaces/w-default/user-groups" in str(capture.request.url)


async def test_remove_member() -> None:
    client, capture = make_client(json=GROUP_JSON)
    group = await client.user_groups.remove_member("g1", "u1", workspace_id="w1")
    assert_wired(
        capture,
        resource="user_groups",
        method="remove_member",
        url="https://api.clockify.me/api/v1/workspaces/w1/user-groups/g1/users/u1",
    )
    assert isinstance(group, UserGroupDtoV1)


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=GROUP_JSON)
    await client.user_groups.update("g1", {"name": "Devs"}, workspace_id="w1")
    assert_wired(
        capture,
        resource="user_groups",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/user-groups/g1",
    )
    assert capture.sent_json() == {"name": "Devs"}
