"""Demo-data cleanup: discovery and the multi-step destructive plan.

Only entities whose names carry an allowed demo prefix are ever selected.
The prefix rule is enforced twice: at discovery (only matching entities enter
the plan) and at revalidation of the consumed plan (only cleanup operations
are allowed to dispatch). The whole cleanup is ONE plan under ONE approval;
a mid-plan failure reports exactly which steps applied.
"""

import json
import re
from typing import Any

from clockify_mcp.errors import ToolError
from clockify_mcp.paging import collect_paged
from clockify_mcp.read_capability import WorkflowReadClient
from clockify_mcp.writes.plan import PreviewField, ReconciliationPlan, WritePlan, WriteStep
from clockify_mcp.writes.plans import build_step

DEMO_PREFIX_PATTERN = re.compile(r"^(DEMO-|sdk-demo-)")

_CLEANUP_OPERATIONS = frozenset(
    {
        "deleteWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
        "updateTaskOnProject",
        "deleteTaskFromProject",
        "updateProject",
        "deleteProject",
        "deleteWorkspacesWorkspaceIdTagsTagId",
        "putWorkspacesWorkspaceIdClientsClientId",
        "deleteWorkspacesWorkspaceIdClientsClientId",
    }
)


def assert_demo_prefix(prefix: str) -> None:
    if not DEMO_PREFIX_PATTERN.match(prefix):
        raise ToolError("prefix must start with DEMO- or sdk-demo-")


def revalidate_cleanup(plan: WritePlan) -> None:
    """Consumed-plan check: every step must be a known cleanup operation."""
    for step in plan.steps:
        if step.operation_id not in _CLEANUP_OPERATIONS:
            raise ValueError(f"{step.operation_id} is not a cleanup operation")
        if step.body_json is not None:
            body = json.loads(step.body_json)
            if not isinstance(body, dict):
                raise ValueError("cleanup step body must be an object")


async def _paged(list_method: Any, **filters: Any) -> list[Any]:
    async def fetch(page: int) -> tuple[list[Any], bool | None]:
        items = await list_method(page=page, page_size=200, **filters)
        return list(items), None

    return await collect_paged(fetch)


async def discover_cleanup_steps(
    reads: WorkflowReadClient, workspace_id: str, prefix: str
) -> tuple[tuple[WriteStep, ...], tuple[PreviewField, ...]]:
    """Walk every page of every entity type; select only prefixed names."""
    assert_demo_prefix(prefix)
    steps: list[WriteStep] = []
    preview: list[PreviewField] = []

    def matches(name: str | None) -> bool:
        return bool(name and name.startswith(prefix))

    me = await reads.users.me()

    def list_entries(**kwargs: Any) -> Any:
        return reads.time_entries.list_for_user(
            me.id, workspace_id=workspace_id, description=prefix, **kwargs
        )

    entries = await _paged(list_entries)
    for entry in entries:
        if matches(entry.description):
            steps.append(
                build_step(
                    "deleteWorkspacesWorkspaceIdTimeEntriesTimeEntryId",
                    path_args={"workspaceId": workspace_id, "timeEntryId": entry.id},
                )
            )
            preview.append(PreviewField("delete time_entry", f"{entry.id} {entry.description}"))

    projects = await _paged(reads.projects.list, workspace_id=workspace_id, name=prefix)
    for project in projects:
        if not matches(project.name):
            continue

        def list_project_tasks(*, project_id: str = project.id, **kwargs: Any) -> Any:
            return reads.tasks.list(project_id, workspace_id=workspace_id, **kwargs)

        tasks = await _paged(list_project_tasks)
        for task in tasks:
            if matches(task.name):
                steps.append(
                    build_step(
                        "updateTaskOnProject",
                        path_args={
                            "workspaceId": workspace_id,
                            "projectId": project.id,
                            "taskId": task.id,
                        },
                        body={"name": task.name, "status": "DONE"},
                    )
                )
                steps.append(
                    build_step(
                        "deleteTaskFromProject",
                        path_args={
                            "workspaceId": workspace_id,
                            "projectId": project.id,
                            "taskId": task.id,
                        },
                    )
                )
                preview.append(PreviewField("delete task", f"{task.id} {task.name}"))
        steps.append(
            build_step(
                "updateProject",
                path_args={"workspaceId": workspace_id, "projectId": project.id},
                body={"name": project.name, "archived": True},
            )
        )
        steps.append(
            build_step(
                "deleteProject",
                path_args={"workspaceId": workspace_id, "projectId": project.id},
            )
        )
        preview.append(PreviewField("delete project", f"{project.id} {project.name}"))

    tags = await _paged(reads.tags.list, workspace_id=workspace_id, name=prefix)
    for tag in tags:
        if matches(tag.name):
            steps.append(
                build_step(
                    "deleteWorkspacesWorkspaceIdTagsTagId",
                    path_args={"workspaceId": workspace_id, "tagId": tag.id},
                )
            )
            preview.append(PreviewField("delete tag", f"{tag.id} {tag.name}"))

    clients = await _paged(reads.clients.list, workspace_id=workspace_id, name=prefix)
    for client in clients:
        if matches(client.name):
            steps.append(
                build_step(
                    "putWorkspacesWorkspaceIdClientsClientId",
                    path_args={"workspaceId": workspace_id, "clientId": client.id},
                    body={"name": client.name, "archived": True},
                )
            )
            steps.append(
                build_step(
                    "deleteWorkspacesWorkspaceIdClientsClientId",
                    path_args={"workspaceId": workspace_id, "clientId": client.id},
                )
            )
            preview.append(PreviewField("delete client", f"{client.id} {client.name}"))

    return tuple(steps), tuple(preview)


def cleanup_plan(
    workspace_id: str,
    prefix: str,
    steps: tuple[WriteStep, ...],
    preview: tuple[PreviewField, ...],
) -> WritePlan:
    return WritePlan(
        version=1,
        title="Delete demo data",
        summary=(
            f"Delete every {prefix}* entity in workspace {workspace_id}: "
            f"{len(steps)} ordered steps (archive/DONE prerequisites included)"
        ),
        effect="delete",
        scope=f"{len(preview)} entities",
        sensitivity=(),
        reversibility="NOT reversible",
        steps=steps,
        preview_fields=preview,
        warnings=("every listed entity will be permanently deleted",),
        reconciliation=ReconciliationPlan(
            kind="none", description="verify by re-listing with the prefix afterwards"
        ),
    )
