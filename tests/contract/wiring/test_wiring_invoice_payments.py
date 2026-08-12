"""Public-method wiring: invoice_payments (3 operations)."""

from clockify.models import AddInvoicePaymentRequest, InvoiceDtoFull, InvoicePaymentDto

from ._harness import assert_wired, make_client

COVERED = {
    "addInvoicePayment",
    "deleteInvoicePayment",
    "getInvoicePayments",
}

INVOICE_JSON = {"id": "i1", "number": "INV-001", "paid": 100, "balance": 400}
PAYMENT_JSON = {"id": "pay1", "amount": 100, "author": "u1", "date": "2026-08-12T00:00:00Z"}


async def test_create_returns_updated_invoice() -> None:
    client, capture = make_client(status=201, json=INVOICE_JSON)
    invoice = await client.invoice_payments.create(
        "i1",
        AddInvoicePaymentRequest(amount=100, paymentDate="2026-08-12T00:00:00Z"),
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="invoice_payments",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/payments",
    )
    assert capture.sent_json() == {"amount": 100, "paymentDate": "2026-08-12T00:00:00Z"}
    assert isinstance(invoice, InvoiceDtoFull)
    assert invoice.paid == 100


async def test_delete_returns_updated_invoice() -> None:
    client, capture = make_client(json=INVOICE_JSON)
    invoice = await client.invoice_payments.delete("i1", "pay1", workspace_id="w1")
    assert_wired(
        capture,
        resource="invoice_payments",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/payments/pay1",
    )
    assert isinstance(invoice, InvoiceDtoFull)


async def test_list_query_wire_names() -> None:
    client, capture = make_client(json=[PAYMENT_JSON])
    payments = await client.invoice_payments.list("i1", workspace_id="w1", page=1, page_size=50)
    assert_wired(
        capture,
        resource="invoice_payments",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/i1/payments",
        query={"page": ["1"], "page-size": ["50"]},
    )
    assert isinstance(payments[0], InvoicePaymentDto)
    assert payments[0].id == "pay1"


async def test_list_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.invoice_payments.list("i1")
    assert "/workspaces/w-default/invoices/i1/payments" in str(capture.request.url)
