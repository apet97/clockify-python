"""Public-method wiring: expenses (6 operations)."""

from clockify.files import Upload
from clockify.models import ExpenseCreateRequest, ExpenseDtoV1, WorkspaceExpensesDtoV1
from clockify.response import BinaryResponse

from ._harness import assert_wired, make_client

COVERED = {
    "createExpense",
    "deleteExpense",
    "downloadExpenseReceipt",
    "getExpenseById",
    "getWorkspaceExpenses",
    "updateExpense",
}

EXPENSE_JSON = {"id": "e1", "workspaceId": "w1", "userId": "u1", "total": 1250}


async def test_create_multipart_with_file() -> None:
    client, capture = make_client(status=201, json=EXPENSE_JSON)
    expense = await client.expenses.create(
        ExpenseCreateRequest(amount=12.5, categoryId="c1", date="2026-08-12", userId="u1"),
        file=Upload(filename="receipt.pdf", content=b"%PDF"),
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="expenses",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses",
    )
    content_type = capture.request.headers["Content-Type"]
    assert content_type.startswith("multipart/form-data")
    body = capture.request.content
    assert b'name="amount"' in body and b"12.5" in body
    assert b'name="categoryId"' in body
    assert b'name="userId"' in body
    assert b'name="file"; filename="receipt.pdf"' in body
    assert b"%PDF" in body
    assert isinstance(expense, ExpenseDtoV1)
    assert expense.total == 1250


async def test_create_mapping_without_file_and_default_workspace() -> None:
    client, capture = make_client(status=201, json=EXPENSE_JSON)
    await client.expenses.create(
        {"amount": 3, "categoryId": "c1", "date": "2026-08-12", "userId": "u1"}
    )
    assert "/workspaces/w-default/expenses" in str(capture.request.url)


async def test_delete_returns_none() -> None:
    client, capture = make_client(status=200, content=b"")
    result = await client.expenses.delete("e1", workspace_id="w1")
    assert_wired(
        capture,
        resource="expenses",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/e1",
    )
    assert result is None


async def test_download_receipt_binary() -> None:
    client, capture = make_client(content=b"%PDF-1.4", content_type="application/pdf")
    receipt = await client.expenses.download_receipt("e1", "f1", workspace_id="w1")
    assert_wired(
        capture,
        resource="expenses",
        method="download_receipt",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/e1/files/f1",
    )
    assert isinstance(receipt, BinaryResponse)
    assert receipt.content == b"%PDF-1.4"


async def test_get() -> None:
    client, capture = make_client(json=EXPENSE_JSON)
    expense = await client.expenses.get("e1", workspace_id="w1")
    assert_wired(
        capture,
        resource="expenses",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/e1",
    )
    assert expense.id == "e1"


async def test_list_envelope_and_query_wire_names() -> None:
    client, capture = make_client(
        json={
            "expenses": {"count": 1, "expenses": [{"id": "e1", "total": 1250}]},
            "dailyTotals": [],
            "weeklyTotals": [],
        }
    )
    envelope = await client.expenses.list(workspace_id="w1", page=1, page_size=50, user_id="u1")
    assert_wired(
        capture,
        resource="expenses",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses",
        query={"page": ["1"], "page-size": ["50"], "user-id": ["u1"]},
    )
    assert isinstance(envelope, WorkspaceExpensesDtoV1)
    assert envelope.expenses is not None
    assert envelope.expenses.expenses is not None
    assert envelope.expenses.expenses[0].id == "e1"


async def test_update_multipart_sends_change_fields() -> None:
    client, capture = make_client(json=EXPENSE_JSON)
    await client.expenses.update(
        "e1",
        {
            "amount": 20,
            "categoryId": "c1",
            "changeFields": ["AMOUNT"],
            "date": "2026-08-12",
            "userId": "u1",
        },
        workspace_id="w1",
    )
    assert_wired(
        capture,
        resource="expenses",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/e1",
    )
    # Form fields ride as filename-less multipart parts even with no file attached.
    assert capture.request.headers["Content-Type"].startswith("multipart/form-data")
    body = capture.request.content
    assert b'name="changeFields"' in body
    assert b'name="amount"' in body and b"20" in body
