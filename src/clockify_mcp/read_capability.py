"""Smallest readable capability handed to the five workflows (review finding F3).

Workflow implementations receive a `WorkflowReadClient`, never a full
`ClockifyClient`. Its ordinary API exposes only the read calls the workflows
use: no `raw.call`, no mutating resource methods, no direct executor
attribute, and no general dispatch. The exposed attributes are bound resource
methods, so private reach-through (`method.__self__._executor`, and its
`_inner`) is still possible for trusted in-process code; only ordinary use is
narrowed. The `ReadOnlyExecutor` wrapped inside the server's client remains
the final runtime enforcement boundary for ordinary dispatch. Python cannot
stop deliberate rewriting of trusted package source — this is a capability
discipline plus a tested tripwire, not a sandbox.
"""

from clockify.client import ClockifyClient


class _UsersReads:
    __slots__ = ("list", "me")

    def __init__(self, client: ClockifyClient) -> None:
        self.me = client.users.me
        self.list = client.users.list


class _ClientsReads:
    __slots__ = ("list",)

    def __init__(self, client: ClockifyClient) -> None:
        self.list = client.clients.list


class _TasksReads:
    __slots__ = ("list",)

    def __init__(self, client: ClockifyClient) -> None:
        self.list = client.tasks.list


class _ExpenseCategoriesReads:
    __slots__ = ("list",)

    def __init__(self, client: ClockifyClient) -> None:
        self.list = client.expense_categories.list


class _TimeOffPoliciesReads:
    __slots__ = ("list",)

    def __init__(self, client: ClockifyClient) -> None:
        self.list = client.time_off_policies.list


class _WorkspacesReads:
    __slots__ = ("get",)

    def __init__(self, client: ClockifyClient) -> None:
        self.get = client.workspaces.get


class _TimeEntriesReads:
    __slots__ = ("get", "list_for_user", "list_in_progress")

    def __init__(self, client: ClockifyClient) -> None:
        self.list_in_progress = client.time_entries.list_in_progress
        self.list_for_user = client.time_entries.list_for_user
        self.get = client.time_entries.get


class _ProjectsReads:
    __slots__ = ("get", "list")

    def __init__(self, client: ClockifyClient) -> None:
        self.list = client.projects.list
        self.get = client.projects.get


class _TagsReads:
    __slots__ = ("list",)

    def __init__(self, client: ClockifyClient) -> None:
        self.list = client.tags.list


class _ReportsReads:
    __slots__ = ("weekly",)

    def __init__(self, client: ClockifyClient) -> None:
        self.weekly = client.reports.weekly


class WorkflowReadClient:
    """Read-only facade over exactly the calls the workflows require."""

    __slots__ = (
        "clients",
        "expense_categories",
        "projects",
        "reports",
        "tags",
        "tasks",
        "time_entries",
        "time_off_policies",
        "users",
        "workspace_id",
        "workspaces",
    )

    def __init__(self, client: ClockifyClient) -> None:
        self.workspace_id = client.workspace_id
        self.users = _UsersReads(client)
        self.workspaces = _WorkspacesReads(client)
        self.time_entries = _TimeEntriesReads(client)
        self.projects = _ProjectsReads(client)
        self.tags = _TagsReads(client)
        self.reports = _ReportsReads(client)
        self.clients = _ClientsReads(client)
        self.tasks = _TasksReads(client)
        self.expense_categories = _ExpenseCategoriesReads(client)
        self.time_off_policies = _TimeOffPoliciesReads(client)
