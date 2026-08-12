"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


class WebhookCollectionDtoV1(ClockifyResponseModel):
    webhooks: list[WebhookDtoV1] | None = None
    workspace_webhook_count: int | None = Field(default=None, alias="workspaceWebhookCount")


class WebhookDtoV1(ClockifyResponseModel):
    """Live webhook records do not return entityType, feature, payloadType, or validSourceTypes."""

    auth_token: str | None = Field(default=None, alias="authToken")
    delivery_enabled: bool | None = Field(default=None, alias="deliveryEnabled")
    enabled: bool | None = None
    id: str | None = None
    name: str | None = None
    plan_enabled: bool | None = Field(default=None, alias="planEnabled")
    trigger_source: list[str] | None = Field(default=None, alias="triggerSource")
    trigger_source_type: WebhookEventTriggerSourceType | None = Field(
        default=None, alias="triggerSourceType"
    )
    url: str | None = None
    user_id: str | None = Field(default=None, alias="userId")
    webhook_event: WebhookEventType | None = Field(default=None, alias="webhookEvent")
    workspace_id: str | None = Field(default=None, alias="workspaceId")


class WebhookEventStatusWithLatestLogDtoV1(ClockifyResponseModel):
    id: str | None = None
    request_body: str | None = Field(default=None, alias="requestBody")
    responded_at: str | None = Field(default=None, alias="respondedAt")
    response_body: str | None = Field(default=None, alias="responseBody")
    retry_count: int | None = Field(default=None, alias="retryCount")
    status: str | None = None
    status_code: int | None = Field(default=None, alias="statusCode")
    webhook_id: str | None = Field(default=None, alias="webhookId")
    webhook_log_id: str | None = Field(default=None, alias="webhookLogId")


WebhookEventTriggerSourceType = Literal[
    "PROJECT_ID", "USER_ID", "TAG_ID", "TASK_ID", "WORKSPACE_ID", "ASSIGNMENT_ID", "EXPENSE_ID"
]

WebhookEventType = Literal[
    "NEW_PROJECT",
    "NEW_TASK",
    "NEW_CLIENT",
    "NEW_TIMER_STARTED",
    "TIMER_STOPPED",
    "TIME_ENTRY_UPDATED",
    "TIME_ENTRY_DELETED",
    "TIME_ENTRY_SPLIT",
    "NEW_TIME_ENTRY",
    "TIME_ENTRY_RESTORED",
    "NEW_TAG",
    "USER_DELETED_FROM_WORKSPACE",
    "USER_JOINED_WORKSPACE",
    "USER_DEACTIVATED_ON_WORKSPACE",
    "USER_ACTIVATED_ON_WORKSPACE",
    "USER_EMAIL_CHANGED",
    "USER_UPDATED",
    "NEW_INVOICE",
    "INVOICE_UPDATED",
    "NEW_APPROVAL_REQUEST",
    "APPROVAL_REQUEST_STATUS_UPDATED",
    "TIME_OFF_REQUESTED",
    "TIME_OFF_REQUEST_UPDATED",
    "TIME_OFF_REQUEST_APPROVED",
    "TIME_OFF_REQUEST_REJECTED",
    "TIME_OFF_REQUEST_STARTED",
    "TIME_OFF_REQUEST_WITHDRAWN",
    "BALANCE_UPDATED",
    "TAG_UPDATED",
    "TAG_DELETED",
    "TASK_UPDATED",
    "CLIENT_UPDATED",
    "TASK_DELETED",
    "CLIENT_DELETED",
    "EXPENSE_RESTORED",
    "ASSIGNMENT_CREATED",
    "ASSIGNMENT_DELETED",
    "ASSIGNMENT_PUBLISHED",
    "ASSIGNMENT_UPDATED",
    "EXPENSE_CREATED",
    "EXPENSE_DELETED",
    "EXPENSE_UPDATED",
    "PROJECT_UPDATED",
    "PROJECT_DELETED",
    "USER_GROUP_CREATED",
    "USER_GROUP_UPDATED",
    "USER_GROUP_DELETED",
    "USERS_INVITED_TO_WORKSPACE",
    "LIMITED_USERS_ADDED_TO_WORKSPACE",
    "COST_RATE_UPDATED",
    "BILLABLE_RATE_UPDATED",
]


class WebhookLogDtoV1(ClockifyResponseModel):
    id: str | None = None
    request_body: str | None = Field(default=None, alias="requestBody")
    responded_at: str | None = Field(default=None, alias="respondedAt")
    response_body: str | None = Field(default=None, alias="responseBody")
    status_code: int | None = Field(default=None, alias="statusCode")
    webhook_event_status_id: str | None = Field(default=None, alias="webhookEventStatusId")
    webhook_id: str | None = Field(default=None, alias="webhookId")


class WebhookLogsRequest(ClockifyRequestModel):
    from_: str | None = Field(default=None, alias="from")
    sort_by_newest: bool | None = Field(default=None, alias="sortByNewest")
    status: Literal["ALL", "SUCCEEDED", "FAILED"] | None = None
    to: str | None = None


class WebhookRequest(ClockifyRequestModel):
    """For USER_EMAIL_CHANGED and USER_UPDATED, live Clockify requires triggerSourceType USER_ID and a nonempty triggerSource user id."""

    name: str
    trigger_source: list[str] = Field(alias="triggerSource")
    trigger_source_type: WebhookEventTriggerSourceType = Field(alias="triggerSourceType")
    url: str
    webhook_event: WebhookEventType = Field(alias="webhookEvent")


WebhookType = Literal["USER_CREATED", "SYSTEM", "ADDON"]


class WebhooksClockifyError(ClockifyResponseModel):
    code: int | None = None
    message: str | None = None


class WebhooksWebhook2(ClockifyResponseModel):
    auth_token: str | None = Field(default=None, alias="authToken")
    delivery_enabled: bool | None = Field(default=None, alias="deliveryEnabled")
    enabled: bool | None = None
    id: str | None = None
    name: str | None = None
    plan_enabled: bool | None = Field(default=None, alias="planEnabled")
    trigger_source: list[str] | None = Field(default=None, alias="triggerSource")
    trigger_source_type: str | None = Field(default=None, alias="triggerSourceType")
    url: str | None = None
    user_id: str | None = Field(default=None, alias="userId")
    webhook_event: str | None = Field(default=None, alias="webhookEvent")
    workspace_id: str | None = Field(default=None, alias="workspaceId")
