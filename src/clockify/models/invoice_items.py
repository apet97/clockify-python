"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clockify.models.base import ClockifyRequestModel
from clockify.models.common import ApplyTaxes, ContainsArchivedFilterRequest


class AddInvoiceItemRequest(ClockifyRequestModel):
    apply_taxes: ApplyTaxes = Field(alias="applyTaxes")
    description: str
    item_type: str = Field(alias="itemType")
    quantity: int
    unit_price: int = Field(alias="unitPrice")


ExpenseFieldsForDetailedGroup = Literal["PROJECT", "TASK", "CATEGORY", "NOTE", "DATE", "USER"]

ExpensesGroupBy = Literal["CATEGORY", "PROJECT", "USER"]

ExpensesGroupType = Literal["GROUPED", "DETAILED"]


class ImportInvoiceItemsRequest(ClockifyRequestModel):
    expense_fields_for_detailed_group: list[ExpenseFieldsForDetailedGroup] | None = Field(
        default=None, alias="expenseFieldsForDetailedGroup"
    )
    expenses_group_by: ExpensesGroupBy | None = Field(default=None, alias="expensesGroupBy")
    expenses_group_type: ExpensesGroupType | None = Field(default=None, alias="expensesGroupType")
    from_: str = Field(alias="from")
    import_expenses: bool = Field(alias="importExpenses")
    project_filter: ContainsArchivedFilterRequest = Field(alias="projectFilter")
    round_time_entry_duration: bool | None = Field(default=None, alias="roundTimeEntryDuration")
    time_entry_fields_for_detailed_group: list[TimeEntryFieldsForDetailedGroup] | None = Field(
        default=None, alias="timeEntryFieldsForDetailedGroup"
    )
    time_entry_group_type: TimeEntryGroupType = Field(alias="timeEntryGroupType")
    time_entry_primary_group_by: TimeEntryPrimaryGroupBy | None = Field(
        default=None, alias="timeEntryPrimaryGroupBy"
    )
    time_entry_secondary_group_by: TimeEntrySecondaryGroupBy | None = Field(
        default=None, alias="timeEntrySecondaryGroupBy"
    )
    to: str


TimeEntryFieldsForDetailedGroup = Literal["PROJECT", "TASK", "TAGS", "DESCRIPTION", "DATE", "USER"]

TimeEntryGroupType = Literal["SINGLE_ITEM", "GROUPED", "DETAILED"]

TimeEntryPrimaryGroupBy = Literal["USER", "PROJECT", "DATE"]

TimeEntrySecondaryGroupBy = Literal["PROJECT", "USER", "TASK", "DATE", "DESCRIPTION", "NONE"]
