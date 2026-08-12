"""Reports resource: explicit methods over the report-generation operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import (
    AttendanceReportRequest,
    AttendanceReportResponse,
    DetailedReportRequest,
    DetailedReportResponse,
    ExpenseDetailedReportDtoV1,
    ExpenseReportFilterV1,
    SummaryReportRequest,
    SummaryReportResponse,
    WeeklyReportRequest,
    WeeklyReportResponse,
)
from clockify.operations.reports import (
    REPORTS_ATTENDANCE,
    REPORTS_DETAILED,
    REPORTS_EXPENSE_DETAILS,
    REPORTS_SUMMARY,
    REPORTS_WEEKLY,
)
from clockify.resources._base import ResourceBase


class ReportsResource(ResourceBase):
    async def attendance(
        self,
        body: "AttendanceReportRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> AttendanceReportResponse:
        """Date range is wall-clock in the body's timeZone; timestamps come back in that zone."""
        validated = self._coerce(body, AttendanceReportRequest)
        response = await self._call(
            REPORTS_ATTENDANCE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(REPORTS_ATTENDANCE, response, AttendanceReportResponse)

    async def detailed(
        self,
        body: "DetailedReportRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> DetailedReportResponse:
        validated = self._coerce(body, DetailedReportRequest)
        response = await self._call(
            REPORTS_DETAILED,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(REPORTS_DETAILED, response, DetailedReportResponse)

    async def expense_details(
        self,
        body: "ExpenseReportFilterV1 | Mapping[str, Any] | None" = None,
        *,
        workspace_id: str | None = None,
    ) -> ExpenseDetailedReportDtoV1:
        """Money keeps upstream scaling: create amount is MAJOR units, response total MINOR."""
        validated = None if body is None else self._coerce(body, ExpenseReportFilterV1)
        response = await self._call(
            REPORTS_EXPENSE_DETAILS,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(REPORTS_EXPENSE_DETAILS, response, ExpenseDetailedReportDtoV1)

    async def summary(
        self,
        body: "SummaryReportRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> SummaryReportResponse:
        validated = self._coerce(body, SummaryReportRequest)
        response = await self._call(
            REPORTS_SUMMARY,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(REPORTS_SUMMARY, response, SummaryReportResponse)

    async def weekly(
        self,
        body: "WeeklyReportRequest | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> WeeklyReportResponse:
        """Requires an exact seven-day dateRangeStart..dateRangeEnd interval."""
        validated = self._coerce(body, WeeklyReportRequest)
        response = await self._call(
            REPORTS_WEEKLY,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(REPORTS_WEEKLY, response, WeeklyReportResponse)
