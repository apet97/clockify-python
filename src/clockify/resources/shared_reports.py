"""Shared reports resource: explicit methods over the shared-report operations."""

from collections.abc import Mapping
from typing import Any

from clockify.models import SharedReport, SharedReportCreate, SharedReportListEnvelope
from clockify.operations.shared_reports import (
    SHARED_REPORTS_CREATE,
    SHARED_REPORTS_DELETE,
    SHARED_REPORTS_LIST,
    SHARED_REPORTS_UPDATE,
    SHARED_REPORTS_VIEW_PUBLIC,
)
from clockify.resources._base import ResourceBase


class SharedReportsResource(ResourceBase):
    async def create(
        self,
        body: "SharedReportCreate | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> SharedReport:
        validated = self._coerce(body, SharedReportCreate)
        response = await self._call(
            SHARED_REPORTS_CREATE,
            path={"workspaceId": self._workspace(workspace_id)},
            body=validated,
        )
        return self._adapt(SHARED_REPORTS_CREATE, response, SharedReport)

    async def delete(self, shared_report_id: str, *, workspace_id: str | None = None) -> None:
        await self._call(
            SHARED_REPORTS_DELETE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "sharedReportId": shared_report_id,
            },
        )
        return None

    async def list(
        self,
        *,
        workspace_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        shared_reports_filter: str | None = None,
    ) -> SharedReportListEnvelope:
        response = await self._call(
            SHARED_REPORTS_LIST,
            path={"workspaceId": self._workspace(workspace_id)},
            query={
                "page": page,
                "page_size": page_size,
                "shared_reports_filter": shared_reports_filter,
            },
        )
        return self._adapt(SHARED_REPORTS_LIST, response, SharedReportListEnvelope)

    async def update(
        self,
        shared_report_id: str,
        body: "SharedReportCreate | Mapping[str, Any]",
        *,
        workspace_id: str | None = None,
    ) -> SharedReport:
        """PUT with documented MERGE semantics, not a full replace."""
        validated = self._coerce(body, SharedReportCreate)
        response = await self._call(
            SHARED_REPORTS_UPDATE,
            path={
                "workspaceId": self._workspace(workspace_id),
                "sharedReportId": shared_report_id,
            },
            body=validated,
        )
        return self._adapt(SHARED_REPORTS_UPDATE, response, SharedReport)

    async def view_public(
        self,
        shared_report_id: str,
        *,
        export_type: str | None = None,
        date_range_start: str | None = None,
        date_range_end: str | None = None,
        sort_column: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:
        """Content-negotiated: JSON dict (rendered report), CSV text, or PDF/XLSX bytes
        by exportType. No workspaceId; the link token is the only auth."""
        response = await self._call(
            SHARED_REPORTS_VIEW_PUBLIC,
            path={"sharedReportId": shared_report_id},
            query={
                "export_type": export_type,
                "date_range_start": date_range_start,
                "date_range_end": date_range_end,
                "sort_column": sort_column,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            },
        )
        return response.data
