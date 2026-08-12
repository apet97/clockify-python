"""The public async Clockify client."""

from types import TracebackType

import httpx

from clockify._transport.auth import Credential
from clockify._transport.executor import HttpExecutor, ReadOnlyExecutor
from clockify.config import DEFAULT_TIMEOUT, ReadRetryPolicy
from clockify.operations.model import Service
from clockify.raw import RawOperations
from clockify.resources.approvals import ApprovalsResource
from clockify.resources.audit_log import AuditLogResource
from clockify.resources.clients import ClientsResource
from clockify.resources.custom_fields import CustomFieldsResource
from clockify.resources.entity_changes import EntityChangesResource
from clockify.resources.expense_categories import ExpenseCategoriesResource
from clockify.resources.expenses import ExpensesResource
from clockify.resources.files import FilesResource
from clockify.resources.holidays import HolidaysResource
from clockify.resources.invoice_items import InvoiceItemsResource
from clockify.resources.invoice_payments import InvoicePaymentsResource
from clockify.resources.invoice_settings import InvoiceSettingsResource
from clockify.resources.invoices import InvoicesResource
from clockify.resources.member_profiles import MemberProfilesResource
from clockify.resources.projects import ProjectsResource
from clockify.resources.reports import ReportsResource
from clockify.resources.scheduling import SchedulingResource
from clockify.resources.shared_reports import SharedReportsResource
from clockify.resources.tags import TagsResource
from clockify.resources.tasks import TasksResource
from clockify.resources.time_entries import TimeEntriesResource
from clockify.resources.time_off_balance_assignments import (
    TimeOffBalanceAssignmentsResource,
)
from clockify.resources.time_off_balances import TimeOffBalancesResource
from clockify.resources.time_off_policies import TimeOffPoliciesResource
from clockify.resources.time_off_requests import TimeOffRequestsResource
from clockify.resources.user_groups import UserGroupsResource
from clockify.resources.users import UsersResource
from clockify.resources.webhooks import WebhooksResource
from clockify.resources.workspaces import WorkspacesResource


class ClockifyClient:
    """Async Clockify API client with 29 typed resource attributes.

    Exactly one credential must be given. One `httpx.AsyncClient` is created
    and reused; when a caller injects `http_client`, the caller keeps ownership
    and this class never closes it.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        addon_token: str | None = None,
        workspace_id: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout: httpx.Timeout | None = None,
        service_urls: dict[Service, str] | None = None,
        allow_custom_hosts: bool = False,
        retry_policy: ReadRetryPolicy | None = None,
        _executor: "HttpExecutor | ReadOnlyExecutor | None" = None,
    ) -> None:
        self.workspace_id = workspace_id
        if _executor is not None:
            # Embedding callers (the MCP server) supply a prebuilt executor. If they
            # also pass the executor's http_client, this client owns and closes it.
            self._owns_http_client = http_client is not None
            self._http_client = http_client
            self._executor: HttpExecutor | ReadOnlyExecutor = _executor
        else:
            credential = Credential(api_key=api_key, addon_token=addon_token)
            self._owns_http_client = http_client is None
            self._http_client = http_client or httpx.AsyncClient(
                timeout=timeout if timeout is not None else DEFAULT_TIMEOUT
            )
            self._executor = HttpExecutor(
                client=self._http_client,
                credential=credential,
                service_urls=service_urls,
                allow_custom_hosts=allow_custom_hosts,
                retry_policy=retry_policy,
            )

        executor = self._executor
        self.raw = RawOperations(executor)
        self.approvals = ApprovalsResource(executor, workspace_id)
        self.audit_log = AuditLogResource(executor, workspace_id)
        self.clients = ClientsResource(executor, workspace_id)
        self.custom_fields = CustomFieldsResource(executor, workspace_id)
        self.entity_changes = EntityChangesResource(executor, workspace_id)
        self.expense_categories = ExpenseCategoriesResource(executor, workspace_id)
        self.expenses = ExpensesResource(executor, workspace_id)
        self.files = FilesResource(executor, workspace_id)
        self.holidays = HolidaysResource(executor, workspace_id)
        self.invoice_items = InvoiceItemsResource(executor, workspace_id)
        self.invoice_payments = InvoicePaymentsResource(executor, workspace_id)
        self.invoice_settings = InvoiceSettingsResource(executor, workspace_id)
        self.invoices = InvoicesResource(executor, workspace_id)
        self.member_profiles = MemberProfilesResource(executor, workspace_id)
        self.projects = ProjectsResource(executor, workspace_id)
        self.reports = ReportsResource(executor, workspace_id)
        self.scheduling = SchedulingResource(executor, workspace_id)
        self.shared_reports = SharedReportsResource(executor, workspace_id)
        self.tags = TagsResource(executor, workspace_id)
        self.tasks = TasksResource(executor, workspace_id)
        self.time_entries = TimeEntriesResource(executor, workspace_id)
        self.time_off_balance_assignments = TimeOffBalanceAssignmentsResource(
            executor, workspace_id
        )
        self.time_off_balances = TimeOffBalancesResource(executor, workspace_id)
        self.time_off_policies = TimeOffPoliciesResource(executor, workspace_id)
        self.time_off_requests = TimeOffRequestsResource(executor, workspace_id)
        self.user_groups = UserGroupsResource(executor, workspace_id)
        self.users = UsersResource(executor, workspace_id)
        self.webhooks = WebhooksResource(executor, workspace_id)
        self.workspaces = WorkspacesResource(executor, workspace_id)

    async def aclose(self) -> None:
        """Close the owned HTTP client. Injected clients stay open."""
        if self._owns_http_client and self._http_client is not None:
            await self._http_client.aclose()

    async def __aenter__(self) -> "ClockifyClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()
