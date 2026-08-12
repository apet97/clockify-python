"""Public-method wiring: expense_categories (5 operations)."""

from clockify.models import (
    ExpenseCategoriesDtoV1,
    ExpenseCategoryDtoV1,
    ExpenseCategoryRequest,
    ExpenseCategoryStatusRequest,
)

from ._harness import assert_wired, make_client

COVERED = {
    "addExpenseCategory",
    "deleteExpenseCategory",
    "getExpenseCategories",
    "updateExpenseCategory",
    "archiveExpenseCategory",
}

CATEGORY_JSON = {"id": "c1", "name": "Travel", "workspaceId": "w1", "archived": False}


async def test_create() -> None:
    client, capture = make_client(status=201, json=CATEGORY_JSON)
    category = await client.expense_categories.create(
        ExpenseCategoryRequest(name="Travel"), workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="expense_categories",
        method="create",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/categories",
    )
    assert capture.sent_json() == {"name": "Travel"}
    assert isinstance(category, ExpenseCategoryDtoV1)
    assert category.id == "c1"


async def test_delete_returns_none() -> None:
    client, capture = make_client(status=204, content=b"")
    result = await client.expense_categories.delete("c1", workspace_id="w1")
    assert_wired(
        capture,
        resource="expense_categories",
        method="delete",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/categories/c1",
    )
    assert result is None


async def test_list_envelope_and_query_wire_names() -> None:
    client, capture = make_client(json={"categories": [CATEGORY_JSON], "count": 1})
    envelope = await client.expense_categories.list(
        workspace_id="w1",
        sort_column="NAME",
        sort_order="ASCENDING",
        page=2,
        page_size=10,
        archived=False,
        name="Tra",
    )
    assert_wired(
        capture,
        resource="expense_categories",
        method="list",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/categories",
        query={
            "sort-column": ["NAME"],
            "sort-order": ["ASCENDING"],
            "page": ["2"],
            "page-size": ["10"],
            "archived": ["false"],
            "name": ["Tra"],
        },
    )
    assert isinstance(envelope, ExpenseCategoriesDtoV1)
    assert envelope.categories is not None and envelope.categories[0].id == "c1"


async def test_list_default_workspace() -> None:
    client, capture = make_client(json={"categories": [], "count": 0})
    await client.expense_categories.list()
    assert "/workspaces/w-default/expenses/categories" in str(capture.request.url)


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=CATEGORY_JSON)
    await client.expense_categories.update(
        "c1", {"name": "Travel", "unit": "km"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="expense_categories",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/categories/c1",
    )
    assert capture.sent_json() == {"name": "Travel", "unit": "km"}


async def test_update_status() -> None:
    client, capture = make_client(json={**CATEGORY_JSON, "archived": True})
    category = await client.expense_categories.update_status(
        "c1", ExpenseCategoryStatusRequest(archived=True), workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="expense_categories",
        method="update_status",
        url="https://api.clockify.me/api/v1/workspaces/w1/expenses/categories/c1/status",
    )
    assert capture.sent_json() == {"archived": True}
    assert category.archived is True
