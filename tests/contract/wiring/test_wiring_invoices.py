"""Public-method wiring: invoices (9 operations)."""

from clockify.models import (
    InvoiceCreateRequest,
    InvoiceCreateResponse,
    InvoiceDtoFull,
    InvoiceInfoListResponse,
    InvoiceListResponse,
    InvoiceStatusRequest,
)
from clockify.response import BinaryResponse

from ._harness import assert_wired, make_client

COVERED = {
    "addInvoice",
    "deleteInvoice",
    "duplicateInvoice",
    "exportInvoice",
    "filterInvoices",
    "getInvoiceById",
    "getWorkspaceInvoices",
    "updateInvoice",
    "changeInvoiceStatus",
}

INVOICE_FULL_JSON = {"id": "i1", "number": "INV-001", "currency": "USD", "amount": 12500}


async def test_create() -> None:
    client, capture = make_client(status=201, json={"id": "i1", "number": "INV-001"})
    invoice = await client.invoices.create(
        InvoiceCreateRequest(
            clientId="c1",
            currency="USD",
            dueDate="2026-09-01T00:00:00Z",
            issuedDate="2026-08-01T00:00:00Z",
            number="INV-001",
        ),
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="invoices",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices",
    )
    assert capture.sent_json() == {
        "clientId": "c1",
        "currency": "USD",
        "dueDate": "2026-09-01T00:00:00Z",
        "issuedDate": "2026-08-01T00:00:00Z",
        "number": "INV-001",
    }
    assert isinstance(invoice, InvoiceCreateResponse)
    assert invoice.id == "i1"


async def test_delete_returns_none() -> None:
    client, capture = make_client(status=204)
    result = await client.invoices.delete("i1", workspace_id="w1")
    assert_wired(
        capture,
        resource="invoices",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1",
    )
    assert result is None


async def test_duplicate() -> None:
    client, capture = make_client(status=201, json=INVOICE_FULL_JSON)
    invoice = await client.invoices.duplicate("i1", workspace_id="w1")
    assert_wired(
        capture,
        resource="invoices",
        method="duplicate",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/duplicate",
    )
    assert isinstance(invoice, InvoiceDtoFull)
    assert invoice.id == "i1"


async def test_export_returns_binary() -> None:
    client, capture = make_client(content=b"%PDF-1.7", content_type="application/pdf")
    result = await client.invoices.export("i1", workspace_id="w1", user_locale="en-US")
    assert_wired(
        capture,
        resource="invoices",
        method="export",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/export",
        query={"userLocale": ["en-US"]},
    )
    assert isinstance(result, BinaryResponse)
    assert result.content == b"%PDF-1.7"


async def test_export_sends_documented_locale_default() -> None:
    client, capture = make_client(content=b"%PDF-1.7", content_type="application/pdf")
    await client.invoices.export("i1", workspace_id="w1")
    assert_wired(
        capture,
        resource="invoices",
        method="export",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/export",
        query={"userLocale": ["en-US"]},
    )


async def test_filter_is_post_read_returning_envelope() -> None:
    client, capture = make_client(
        json={"invoices": [{"id": "i1", "number": "INV-001"}], "total": 1}
    )
    result = await client.invoices.filter({"invoiceNumber": "INV-001"}, workspace_id="w1")
    assert_wired(
        capture,
        resource="invoices",
        method="filter",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/info",
    )
    assert capture.sent_json() == {"invoiceNumber": "INV-001"}
    assert isinstance(result, InvoiceInfoListResponse)
    assert result.total == 1
    assert result.invoices is not None and result.invoices[0].id == "i1"


async def test_get() -> None:
    client, capture = make_client(json=INVOICE_FULL_JSON)
    invoice = await client.invoices.get("i1", workspace_id="w1")
    assert_wired(
        capture,
        resource="invoices",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1",
    )
    assert isinstance(invoice, InvoiceDtoFull)


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json={"invoices": [{"id": "i1"}], "total": 1})
    result = await client.invoices.list(
        workspace_id="w1",
        page=2,
        page_size=10,
        statuses=["UNSENT", "PAID"],
        sort_column="ID",
        sort_order="ASCENDING",
    )
    assert_wired(
        capture,
        resource="invoices",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices",
        query={
            "page": ["2"],
            "page-size": ["10"],
            "statuses": ["UNSENT", "PAID"],
            "sort-column": ["ID"],
            "sort-order": ["ASCENDING"],
        },
    )
    assert isinstance(result, InvoiceListResponse)
    assert result.invoices is not None and result.invoices[0].id == "i1"


async def test_list_default_workspace() -> None:
    client, capture = make_client(json={"invoices": [], "total": 0})
    await client.invoices.list()
    assert "/workspaces/w-default/invoices" in str(capture.request.url)


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=INVOICE_FULL_JSON)
    await client.invoices.update(
        "i1",
        {
            "currency": "USD",
            "discountPercent": 10.0,
            "dueDate": "2026-09-01T00:00:00Z",
            "issuedDate": "2026-08-01T00:00:00Z",
            "number": "INV-001",
            "taxPercent": 5.0,
            "tax2Percent": 0.0,
            "note": "kept",
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="invoices",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1",
    )
    assert capture.sent_json() == {
        "currency": "USD",
        "discountPercent": 10.0,
        "dueDate": "2026-09-01T00:00:00Z",
        "issuedDate": "2026-08-01T00:00:00Z",
        "number": "INV-001",
        "taxPercent": 5.0,
        "tax2Percent": 0.0,
        "note": "kept",
    }


async def test_update_status_returns_none() -> None:
    client, capture = make_client(status=204)
    result = await client.invoices.update_status(
        "i1", InvoiceStatusRequest(invoiceStatus="SENT"), workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="invoices",
        method="update_status",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/status",
    )
    assert capture.sent_json() == {"invoiceStatus": "SENT"}
    assert result is None
