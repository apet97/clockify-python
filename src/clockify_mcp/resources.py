"""Static guide resources served by the full server. No network access."""

from mcp.server import MCPServer

_AXIOMS = """\
# Clockify MCP axioms

1. One credential, one pinned workspace. Tools accept workspace_id only to
   override the pin.
2. Reads never mutate. The read boundary is enforced in code, not by hints.
3. Guarded writes show the user the exact bound request before anything is
   sent. The model never supplies the approval.
4. No write is ever retried automatically. An ambiguous transport failure
   reports outcome_unknown; read current state before retrying by hand.
5. Never test writes against a live customer workspace. Use a sacrificial
   workspace and prefixed names (DEMO-).
"""

_WORKFLOWS = """\
# Workflow tools

Daily tracking: clockify_start_work, clockify_stop_work, clockify_switch_work,
clockify_log_work, clockify_fix_entry.
Setup: clockify_create_work_package (client/project/task/tag upsert).
Business (approval required): clockify_invoice_client_work,
clockify_record_expense, clockify_request_time_off, clockify_schedule_work,
clockify_setup_webhook.
Demo data: clockify_demo_seed and clockify_demo_cleanup (prefix-scoped).
Reviews: clockify_review_day, clockify_review_week.
Orientation: clockify_tools_guide, clockify_plan_change,
clockify_operation_guide, clockify_sdk_snippet.
"""

_SAFETY = """\
# Write safety

Tiers: routine writes (personal time entries) execute directly, single
attempt. Guarded writes (business, external, privileged, destructive) pass a
sealed approval gate: deterministic preview of the exact wire request,
single-use confirmation bound to those bytes, byte-exact dispatch, optional
read-back. Argument drift after approval refuses the write.

PUT updates replace the whole entity. Deletes are not reversible; projects and
clients must be archived first, tasks must be DONE first.
"""

_AGENT_MODE = """\
# Agent guidance

Prefer workflows over raw tools. Chain ids from previous receipts. Read before
you write; preview warnings are part of the contract. If an approval is
rejected or expires, no request was sent - ask the user before trying again.
On outcome_unknown, list current state before any manual retry.
"""

_WHICH_TOOL = """\
# Which tool?

"What am I working on?" -> clockify_status
"Log 2h yesterday" -> clockify_log_work
"Start/stop the timer" -> clockify_start_work / clockify_stop_work
"What did I do this week?" -> clockify_review_week
"Set up client+project+task" -> clockify_create_work_package
"Invoice June for Acme" -> clockify_invoice_client_work
"Raw API access" -> clockify_operation_guide to find the exact tool
"""

_DOCTOR = """\
# Offline doctor

The clockify_doctor tool performs live checks. Without calling it:
1. Exactly one of CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN must be set.
2. CLOCKIFY_MCP_READ_ONLY=true serves only the 65 read tools.
3. stdout carries MCP protocol only; diagnostics go to stderr.
4. HTTP mode: clockify-mcp --http --host 127.0.0.1 --port 8000.
"""

_RESOURCES = {
    "clockify://guide/axioms": ("Clockify MCP axioms", _AXIOMS),
    "clockify://guide/workflows": ("Workflow tools", _WORKFLOWS),
    "clockify://guide/safety": ("Write safety", _SAFETY),
    "clockify://guide/agent-mode": ("Agent guidance", _AGENT_MODE),
    "clockify://guide/which-tool": ("Which tool?", _WHICH_TOOL),
    "clockify://mcp/doctor": ("Offline doctor", _DOCTOR),
}


def register_resources(server: MCPServer) -> None:
    for uri, (name, text) in _RESOURCES.items():

        def make_reader(content: str):  # type: ignore[no-untyped-def]
            def read() -> str:
                return content

            return read

        server.resource(uri, name=name, mime_type="text/markdown")(make_reader(text))
