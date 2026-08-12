"""Public-method wiring: audit_log (1 operation)."""

from clockify.models import AuditLogEntry, AuditLogRequest

from ._harness import assert_wired, make_client

COVERED = {"searchAuditLogs"}

ENTRY_JSON = {"action": "CREATE_TAG", "userId": "u1", "workspaceId": "w1"}
SEARCH_BODY = {
    "actions": ["CREATE_TAG"],
    "authors": {"authorIds": ["u1"], "contains": "CONTAINS"},
    "start": "2026-08-01T00:00:00Z",
    "end": "2026-08-12T00:00:00Z",
}


async def test_search_hits_audit_log_service() -> None:
    client, capture = make_client(json=[ENTRY_JSON])
    entries = await client.audit_log.search(SEARCH_BODY, workspace_id="w1")
    assert_wired(
        capture,
        resource="audit_log",
        method="search",
        url="https://auditlog-api.api.clockify.me/v1/workspaces/w1/audit-log",
    )
    assert capture.sent_json() == SEARCH_BODY
    assert isinstance(entries[0], AuditLogEntry)
    assert entries[0].action == "CREATE_TAG"


async def test_search_model_body_and_default_workspace() -> None:
    client, capture = make_client(json=[])
    await client.audit_log.search(AuditLogRequest.model_validate(SEARCH_BODY))
    assert "/workspaces/w-default/audit-log" in str(capture.request.url)
    assert capture.sent_json() == SEARCH_BODY
