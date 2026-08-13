"""Public-method wiring: tasks (7 operations)."""

from clockify.models import Task, TaskCreateRequest

from ._harness import assert_wired, make_client

COVERED = {
    "addTaskOnProject",
    "deleteTaskFromProject",
    "getTaskById",
    "findTasksOnProject",
    "updateTaskOnProject",
    "updateTaskBillableRate",
    "updateTaskCostRate",
}

TASK_JSON = {
    "id": "tk1",
    "name": "Design",
    "projectId": "p1",
    "billable": True,
    "status": "ACTIVE",
}


async def test_create_with_query() -> None:
    client, capture = make_client(status=201, json=TASK_JSON)
    task = await client.tasks.create(
        "p1",
        TaskCreateRequest(name="Design"),
        workspace_id="w1",
        contains_assignee=True,
    )
    assert_wired(
        capture,
        resource="tasks",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/tasks",
        query={"contains-assignee": ["true"]},
    )
    assert capture.sent_json() == {"name": "Design"}
    assert isinstance(task, Task)


async def test_create_mapping_default_workspace() -> None:
    client, capture = make_client(status=201, json=TASK_JSON)
    await client.tasks.create("p1", {"name": "Design"})
    assert "/workspaces/w-default/projects/p1/tasks" in str(capture.request.url)


async def test_delete_returns_deleted_task() -> None:
    client, capture = make_client(json={**TASK_JSON, "status": "DONE"})
    task = await client.tasks.delete("p1", "tk1", workspace_id="w1")
    assert_wired(
        capture,
        resource="tasks",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/tasks/tk1",
    )
    assert task.id == "tk1"


async def test_get() -> None:
    client, capture = make_client(json=TASK_JSON)
    await client.tasks.get("p1", "tk1", workspace_id="w1")
    assert_wired(
        capture,
        resource="tasks",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/tasks/tk1",
    )


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[TASK_JSON])
    tasks = await client.tasks.list(
        "p1",
        workspace_id="w1",
        name="Des",
        strict_name_search=True,
        is_active=True,
        page=2,
        page_size=10,
        sort_column="NAME",
        sort_order="ASCENDING",
    )
    assert_wired(
        capture,
        resource="tasks",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/tasks",
        query={
            "name": ["Des"],
            "strict-name-search": ["true"],
            "is-active": ["true"],
            "page": ["2"],
            "page-size": ["10"],
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
        },
    )
    assert [t.id for t in tasks] == ["tk1"]


async def test_update_sends_exact_body_and_query() -> None:
    client, capture = make_client(json=TASK_JSON)
    await client.tasks.update(
        "p1",
        "tk1",
        {"name": "Design", "status": "DONE"},
        workspace_id="w1",
        contains_assignee=False,
        membership_status="ACTIVE",
    )
    assert_wired(
        capture,
        resource="tasks",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/tasks/tk1",
        query={"contains-assignee": ["false"], "membership-status": ["ACTIVE"]},
    )
    sent = capture.sent_json()
    assert sent["name"] == "Design"
    assert sent["status"] == "DONE"


async def test_update_billable_rate() -> None:
    client, capture = make_client(json=TASK_JSON)
    task = await client.tasks.update_billable_rate("p1", "tk1", {"amount": 2500}, workspace_id="w1")
    assert_wired(
        capture,
        resource="tasks",
        method="update_billable_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/tasks/tk1/hourly-rate",
    )
    assert capture.sent_json() == {"amount": 2500}
    assert isinstance(task, Task)


async def test_update_cost_rate() -> None:
    client, capture = make_client(json=TASK_JSON)
    task = await client.tasks.update_cost_rate("p1", "tk1", {"amount": 1500}, workspace_id="w1")
    assert_wired(
        capture,
        resource="tasks",
        method="update_cost_rate",
        url="https://api.clockify.me/api/v1/workspaces/w1/projects/p1/tasks/tk1/cost-rate",
    )
    assert capture.sent_json() == {"amount": 1500}
    assert isinstance(task, Task)
