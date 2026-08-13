"""Public-method wiring: invoice_items (3 operations)."""

import pytest

from clockify.errors import ClockifyConfigurationError
from clockify.models import InvoiceDtoFull

from ._harness import assert_wired, make_client

COVERED = {
    "addInvoiceItem",
    "deleteInvoiceItem",
    "importInvoiceItems",
}

INVOICE_JSON = {"id": "i1", "number": "INV-001", "amount": 5000, "currency": "USD"}


async def test_create_returns_full_invoice() -> None:
    client, capture = make_client(status=201, json=INVOICE_JSON)
    invoice = await client.invoice_items.create(
        "i1",
        {
            "applyTaxes": "NONE",
            "description": "Work",
            "itemType": "SERVICE",
            "quantity": 2,
            "unitPrice": 250000,
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="invoice_items",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/items",
    )
    assert capture.sent_json() == {
        "applyTaxes": "NONE",
        "description": "Work",
        "itemType": "SERVICE",
        "quantity": 2,
        "unitPrice": 250000,
    }
    assert isinstance(invoice, InvoiceDtoFull)
    assert invoice.id == "i1"


async def test_delete_by_order_returns_full_invoice() -> None:
    client, capture = make_client(json=INVOICE_JSON)
    invoice = await client.invoice_items.delete("i1", 1, workspace_id="w1")
    assert_wired(
        capture,
        resource="invoice_items",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/items/1",
    )
    assert isinstance(invoice, InvoiceDtoFull)


async def test_delete_rejects_non_positive_order_before_transport() -> None:
    client, capture = make_client(json=INVOICE_JSON)

    with pytest.raises(ClockifyConfigurationError, match="order must be at least 1"):
        await client.invoice_items.delete("i1", 0, workspace_id="w1")

    assert capture.requests == []


async def test_import_items_default_workspace() -> None:
    client, capture = make_client(json=INVOICE_JSON)
    body = {
        "from": "2026-01-01T00:00:00Z",
        "to": "2026-01-31T23:59:59Z",
        "importExpenses": False,
        "projectFilter": {"contains": "CONTAINS", "ids": ["p1"], "status": "ALL"},
        "timeEntryGroupType": "GROUPED",
    }
    invoice = await client.invoice_items.import_items("i1", body)
    assert_wired(
        capture,
        resource="invoice_items",
        method="import_items",
        url="https://api.clockify.me/api/v1/workspaces/w-default/invoices/i1/items/import",
    )
    assert capture.sent_json() == body
    assert isinstance(invoice, InvoiceDtoFull)
