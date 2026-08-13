"""Name resolution over the workflow read capability.

Each resolver accepts an id or an exact name; ambiguity raises
``AmbiguousNameError`` (the registration layer turns it into a clarification
receipt) and absence raises an actionable ``ToolError``.
"""

from typing import Any

from clockify_mcp.read_capability import WorkflowReadClient
from clockify_mcp.resolve import resolve_by_name

_PAGE_SIZE = 200


def _list_fetch(list_method: Any, **filters: Any):  # type: ignore[no-untyped-def]
    async def fetch(page: int) -> tuple[list[Any], bool | None]:
        items = await list_method(page=page, page_size=_PAGE_SIZE, **filters)
        return list(items), None

    return fetch


async def resolve_project(reads: WorkflowReadClient, value: str, workspace_id: str) -> str:
    return await resolve_by_name(
        value,
        label="project",
        fetch=_list_fetch(reads.projects.list, workspace_id=workspace_id),
    )


async def resolve_task(
    reads: WorkflowReadClient, value: str, project_id: str, workspace_id: str
) -> str:
    async def fetch(page: int) -> tuple[list[Any], bool | None]:
        items = await reads.tasks.list(
            project_id, workspace_id=workspace_id, page=page, page_size=_PAGE_SIZE
        )
        return list(items), None

    return await resolve_by_name(value, label="task", fetch=fetch)


async def resolve_tag(reads: WorkflowReadClient, value: str, workspace_id: str) -> str:
    return await resolve_by_name(
        value, label="tag", fetch=_list_fetch(reads.tags.list, workspace_id=workspace_id)
    )


async def resolve_client(reads: WorkflowReadClient, value: str, workspace_id: str) -> str:
    return await resolve_by_name(
        value,
        label="client",
        fetch=_list_fetch(reads.clients.list, workspace_id=workspace_id),
    )


async def resolve_category(reads: WorkflowReadClient, value: str, workspace_id: str) -> str:
    async def fetch(page: int) -> tuple[list[Any], bool | None]:
        response = await reads.expense_categories.list(
            workspace_id=workspace_id, page=page, page_size=_PAGE_SIZE
        )
        items = getattr(response, "categories", None) or []
        return list(items), None

    return await resolve_by_name(value, label="expense category", fetch=fetch)


async def resolve_policy(reads: WorkflowReadClient, value: str, workspace_id: str) -> str:
    async def fetch(page: int) -> tuple[list[Any], bool | None]:
        items = await reads.time_off_policies.list(
            workspace_id=workspace_id, page=str(page), page_size=_PAGE_SIZE
        )
        return list(items), None

    return await resolve_by_name(value, label="time-off policy", fetch=fetch)
