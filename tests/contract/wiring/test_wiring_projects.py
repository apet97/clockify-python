"""Public-method wiring: projects (12 operations)."""

from clockify.models import CreateProjectRequest, Project, RateRequest

from ._harness import assert_wired, make_client

COVERED = {
    "createProject",
    "createProjectFromTemplate",
    "deleteProject",
    "getProjectById",
    "getWorkspaceProjects",
    "assignOrRemoveProjectUsers",
    "updateProject",
    "updateProjectEstimate",
    "updateProjectMemberships",
    "updateProjectTemplate",
    "updateProjectUserCostRate",
    "updateProjectUserHourlyRate",
}

PROJECT_JSON = {
    "id": "p1",
    "name": "Website",
    "workspaceId": "w1",
    "archived": False,
    "billable": True,
    "color": "#FF0000",
    "public": True,
    "template": False,
}


async def test_create() -> None:
    client, capture = make_client(status=201, json=PROJECT_JSON)
    project = await client.projects.create(CreateProjectRequest(name="Website"), workspace_id="w1")
    assert_wired(
        capture,
        resource="projects",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects",
    )
    assert capture.sent_json() == {"name": "Website"}
    assert isinstance(project, Project)
    assert project.id == "p1"


async def test_create_from_template() -> None:
    client, capture = make_client(status=201, json=PROJECT_JSON)
    await client.projects.create_from_template(
        {"name": "Website", "templateProjectId": "tp1"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="projects",
        method="create_from_template",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/from-template",
    )
    assert capture.sent_json() == {"name": "Website", "templateProjectId": "tp1"}


async def test_delete_returns_project() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    project = await client.projects.delete("p1", workspace_id="w1")
    assert_wired(
        capture,
        resource="projects",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1",
    )
    assert isinstance(project, Project)


async def test_get_query_wire_names() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.get(
        "p1",
        workspace_id="w1",
        hydrated=True,
        custom_field_entity_type="PROJECT",
        expense_limit=5,
        expense_date="2026-08-01",
    )
    assert_wired(
        capture,
        resource="projects",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1",
        query={
            "hydrated": ["true"],
            "custom-field-entity-type": ["PROJECT"],
            "expense-limit": ["5"],
            "expense-date": ["2026-08-01"],
        },
    )


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[PROJECT_JSON])
    projects = await client.projects.list(
        workspace_id="w1",
        name="Web",
        strict_name_search=True,
        archived=False,
        billable=True,
        clients=["c1", "c2"],
        contains_client=True,
        client_status="ACTIVE",
        users=["u1", "u2"],
        contains_user=False,
        user_status="ACTIVE",
        is_template=False,
        sort_column="NAME",
        sort_order="ASCENDING",
        hydrated=True,
        page=2,
        page_size=25,
        access="PUBLIC",
        expense_limit=3,
        expense_date="2026-08-01",
        user_groups=["g1", "g2"],
        contains_group=True,
    )
    assert_wired(
        capture,
        resource="projects",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects",
        query={
            "name": ["Web"],
            "strict-name-search": ["true"],
            "archived": ["false"],
            "billable": ["true"],
            "clients": ["c1", "c2"],
            "contains-client": ["true"],
            "client-status": ["ACTIVE"],
            "users": ["u1", "u2"],
            "contains-user": ["false"],
            "user-status": ["ACTIVE"],
            "is-template": ["false"],
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
            "hydrated": ["true"],
            "page": ["2"],
            "page-size": ["25"],
            "access": ["PUBLIC"],
            "expense-limit": ["3"],
            "expense-date": ["2026-08-01"],
            "userGroups": ["g1", "g2"],
            "contains-group": ["true"],
        },
    )
    assert [p.id for p in projects] == ["p1"]


async def test_list_default_workspace() -> None:
    client, capture = make_client(json=[PROJECT_JSON])
    await client.projects.list()
    assert "/workspaces/w-default/projects" in str(capture.request.url)


async def test_set_members() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.set_members("p1", {"userIds": ["u1", "u2"]}, workspace_id="w1")
    assert_wired(
        capture,
        resource="projects",
        method="set_members",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/memberships",
    )
    assert capture.sent_json() == {"userIds": ["u1", "u2"]}


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.update(
        "p1", {"name": "Website", "billable": True, "isPublic": True}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="projects",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1",
    )
    assert capture.sent_json() == {"name": "Website", "billable": True, "isPublic": True}


async def test_update_estimate() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.update_estimate(
        "p1",
        {"timeEstimate": {"estimate": "PT10H", "type": "MANUAL", "active": True}},
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="projects",
        method="update_estimate",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/estimate",
    )
    assert capture.sent_json() == {
        "timeEstimate": {"estimate": "PT10H", "type": "MANUAL", "active": True}
    }


async def test_update_memberships() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.update_memberships(
        "p1", {"memberships": [{"userId": "u1"}]}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="projects",
        method="update_memberships",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/memberships",
    )
    assert capture.sent_json() == {"memberships": [{"userId": "u1"}]}


async def test_update_template() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.update_template("p1", {"isTemplate": True}, workspace_id="w1")
    assert_wired(
        capture,
        resource="projects",
        method="update_template",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/template",
    )
    assert capture.sent_json() == {"isTemplate": True}


async def test_update_user_cost_rate() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.update_user_cost_rate(
        "p1", "u1", RateRequest(amount=2500), workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="projects",
        method="update_user_cost_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/users/u1/cost-rate",
    )
    assert capture.sent_json() == {"amount": 2500}


async def test_update_user_hourly_rate() -> None:
    client, capture = make_client(json=PROJECT_JSON)
    await client.projects.update_user_hourly_rate("p1", "u1", {"amount": 5000}, workspace_id="w1")
    assert_wired(
        capture,
        resource="projects",
        method="update_user_hourly_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/users/u1/hourly-rate",
    )
    assert capture.sent_json() == {"amount": 5000}
