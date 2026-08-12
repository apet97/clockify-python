"""Public-method wiring: invoice_settings (2 operations)."""

from clockify.models import InvoiceSettingsResponse

from ._harness import assert_wired, make_client

COVERED = {
    "getInvoiceSettings",
    "updateInvoiceSettings",
}

LABELS = {
    "amount": "Amount",
    "billFrom": "Bill from",
    "billTo": "Bill to",
    "description": "Description",
    "discount": "Discount",
    "dueDate": "Due date",
    "issueDate": "Issue date",
    "itemType": "Item type",
    "notes": "Notes",
    "paid": "Paid",
    "quantity": "Quantity",
    "subtotal": "Subtotal",
    "tax": "Tax",
    "tax2": "Tax 2",
    "total": "Total",
    "totalAmountDue": "Total amount due",
    "unitPrice": "Unit price",
}


async def test_get() -> None:
    client, capture = make_client(json={"labels": {"amount": "Amount"}})
    settings = await client.invoice_settings.get(workspace_id="w1")
    assert_wired(
        capture,
        resource="invoice_settings",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/settings",
    )
    assert isinstance(settings, InvoiceSettingsResponse)
    assert settings.labels is not None and settings.labels.amount == "Amount"


async def test_get_default_workspace() -> None:
    client, capture = make_client(json={})
    await client.invoice_settings.get()
    assert "/workspaces/w-default/invoices/settings" in str(capture.request.url)


async def test_update_sends_exact_body_and_returns_none() -> None:
    client, capture = make_client(status=200, content=b"")
    result = await client.invoice_settings.update({"labels": LABELS}, workspace_id="w1")
    assert_wired(
        capture,
        resource="invoice_settings",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/invoices/settings",
    )
    assert capture.sent_json() == {"labels": LABELS}
    assert result is None
