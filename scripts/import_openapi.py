"""One-shot importer: corrected Clockify OpenAPI -> static Pydantic v2 model modules.

Development tool only. It generates `src/clockify/models/<domain>.py` for every
component schema reachable from the 168 operations, grouped by the resource that
owns them (schemas used by several resources land in `common.py`). It never runs
at install or runtime; the repository works from the committed output alone.

Fails closed: any schema construct this script does not understand raises
UnsupportedSchema with the exact schema path instead of emitting a silent `Any`.

Usage:
    uv run python scripts/import_openapi.py ../clockify-ts-sdk/spec/corrected/clockify.corrected.openapi.yaml \
        --expect-sha256 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
"""

from __future__ import annotations

import argparse
import hashlib
import keyword
import re
import sys
from pathlib import Path
from typing import Any

import yaml

EXPECTED_ROOT_COUNT = 339

# Live-evidence leniency (2026-08-12, sacrificial workspace, getWorkspaceInfo):
# the live API returns plain strings where the corrected spec declares these
# schemas, and returns feature enum values missing from the spec's closed enum
# (e.g. WEEKLY_OVERTIME_CALCULATION_PERIOD). References to these schemas are
# rendered as `<Name> | str` so responses survive; the named types keep the
# documented shapes.
STR_UNION_REFS = {"EntityCreationPermission", "WorkspacesFeature"}

# Schemas known to be unreachable from the 168 operations; kept out of the output
# deliberately (see OPERATION_PORT_MANIFEST.md "Reconciliation findings").
KNOWN_UNREACHABLE = {
    "Feature",
    "LogBinDocumentDto",
    "PageableCollectionLogBinDocumentDto",
    "SummaryReportChartDto",
    "WebhookEntityType",
    "WebhookPayloadType",
}

# operationId -> owning resource/domain, transcribed from OPERATION_PORT_MANIFEST.md.
OPERATION_DOMAIN: dict[str, str] = {
    "createApprovalForOtherWithType": "approvals",
    "createApprrovalRequest_1": "approvals",
    "getApprovalRequests": "approvals",
    "resubmitEntriesForApproval": "approvals",
    "resubmitEntriesForApprovalForUser": "approvals",
    "submitApprovalRequest": "approvals",
    "submitApprovalRequestForUser": "approvals",
    "updateApprovalRequest": "approvals",
    "searchAuditLogs": "audit_log",
    "deleteWorkspacesWorkspaceIdClientsClientId": "clients",
    "getWorkspacesWorkspaceIdClients": "clients",
    "getWorkspacesWorkspaceIdClientsClientId": "clients",
    "postWorkspacesWorkspaceIdClients": "clients",
    "putWorkspacesWorkspaceIdClientsClientId": "clients",
    "createWorkspaceCustomField": "custom_fields",
    "deleteWorkspaceCustomField": "custom_fields",
    "listProjectCustomFields": "custom_fields",
    "listWorkspaceCustomFields": "custom_fields",
    "removeProjectCustomField": "custom_fields",
    "updateProjectCustomField": "custom_fields",
    "updateWorkspaceCustomField": "custom_fields",
    "getCreatedEntityInfo": "entity_changes",
    "getDeletedEntityInfo": "entity_changes",
    "getUpdatedEntityInfo": "entity_changes",
    "addExpenseCategory": "expense_categories",
    "archiveExpenseCategory": "expense_categories",
    "deleteExpenseCategory": "expense_categories",
    "getExpenseCategories": "expense_categories",
    "updateExpenseCategory": "expense_categories",
    "createExpense": "expenses",
    "deleteExpense": "expenses",
    "downloadExpenseReceipt": "expenses",
    "getExpenseById": "expenses",
    "getWorkspaceExpenses": "expenses",
    "updateExpense": "expenses",
    "uploadImage": "files",
    "createHoliday": "holidays",
    "deleteHoliday": "holidays",
    "getWorkspaceHolidays": "holidays",
    "getWorkspaceHolidaysInPeriod": "holidays",
    "updateHoliday": "holidays",
    "addInvoiceItem": "invoice_items",
    "deleteInvoiceItem": "invoice_items",
    "importInvoiceItems": "invoice_items",
    "addInvoicePayment": "invoice_payments",
    "deleteInvoicePayment": "invoice_payments",
    "getInvoicePayments": "invoice_payments",
    "getInvoiceSettings": "invoice_settings",
    "updateInvoiceSettings": "invoice_settings",
    "addInvoice": "invoices",
    "changeInvoiceStatus": "invoices",
    "deleteInvoice": "invoices",
    "duplicateInvoice": "invoices",
    "exportInvoice": "invoices",
    "filterInvoices": "invoices",
    "getInvoiceById": "invoices",
    "getWorkspaceInvoices": "invoices",
    "updateInvoice": "invoices",
    "getMemberProfile": "member_profiles",
    "updateMemberProfile": "member_profiles",
    "assignOrRemoveProjectUsers": "projects",
    "createProject": "projects",
    "createProjectFromTemplate": "projects",
    "deleteProject": "projects",
    "getProjectById": "projects",
    "getWorkspaceProjects": "projects",
    "updateProject": "projects",
    "updateProjectEstimate": "projects",
    "updateProjectMemberships": "projects",
    "updateProjectTemplate": "projects",
    "updateProjectUserCostRate": "projects",
    "updateProjectUserHourlyRate": "projects",
    "generateAttendanceReport": "reports",
    "generateDetailedReport": "reports",
    "generateDetailedReportV1": "reports",
    "generateSummaryReport": "reports",
    "generateWeeklyReport": "reports",
    "changeRecurringPeriod": "scheduling",
    "copyScheduledAssignment": "scheduling",
    "createRecurringAssignment": "scheduling",
    "deleteRecurringAssignment": "scheduling",
    "getAllSchedulingAssignments": "scheduling",
    "getScheduledAssignmentsOnProject": "scheduling",
    "getScheduledAssignmentsPerProject": "scheduling",
    "getUserCapacityTotal": "scheduling",
    "getUsersCapacityTotals": "scheduling",
    "publishAssignments": "scheduling",
    "updateRecurringAssignment": "scheduling",
    "deleteWorkspacesWorkspaceIdSharedReportsSharedReportId": "shared_reports",
    "getSharedReportsSharedReportId": "shared_reports",
    "getWorkspacesWorkspaceIdSharedReports": "shared_reports",
    "postWorkspacesWorkspaceIdSharedReports": "shared_reports",
    "putWorkspacesWorkspaceIdSharedReportsSharedReportId": "shared_reports",
    "deleteWorkspacesWorkspaceIdTagsTagId": "tags",
    "getWorkspacesWorkspaceIdTags": "tags",
    "getWorkspacesWorkspaceIdTagsTagId": "tags",
    "postWorkspacesWorkspaceIdTags": "tags",
    "putWorkspacesWorkspaceIdTagsTagId": "tags",
    "addTaskOnProject": "tasks",
    "deleteTaskFromProject": "tasks",
    "findTasksOnProject": "tasks",
    "getTaskById": "tasks",
    "updateTaskBillableRate": "tasks",
    "updateTaskCostRate": "tasks",
    "updateTaskOnProject": "tasks",
    "deleteMany": "time_entries",
    "deleteWorkspacesWorkspaceIdTimeEntriesTimeEntryId": "time_entries",
    "getMultipleTimeEntries": "time_entries",
    "getWorkspacesWorkspaceIdTimeEntriesStatusInProgress": "time_entries",
    "getWorkspacesWorkspaceIdTimeEntriesTimeEntryId": "time_entries",
    "getWorkspacesWorkspaceIdUserUserIdTimeEntries": "time_entries",
    "patchWorkspacesWorkspaceIdTimeEntriesInvoiced": "time_entries",
    "patchWorkspacesWorkspaceIdUserUserIdTimeEntries": "time_entries",
    "postWorkspacesWorkspaceIdTimeEntries": "time_entries",
    "postWorkspacesWorkspaceIdUserUserIdTimeEntries": "time_entries",
    "postWorkspacesWorkspaceIdUserUserIdTimeEntriesTimeEntryIdDuplicate": "time_entries",
    "putWorkspacesWorkspaceIdTimeEntriesTimeEntryId": "time_entries",
    "putWorkspacesWorkspaceIdUserUserIdTimeEntries": "time_entries",
    "createBalanceAssignment": "time_off_balance_assignments",
    "deleteBalanceAssignment": "time_off_balance_assignments",
    "getBalanceAssignmentsForUserAndPolicy": "time_off_balance_assignments",
    "updateBalanceAssignment": "time_off_balance_assignments",
    "getBalanceForUser": "time_off_balances",
    "getBalancesForPolicy": "time_off_balances",
    "updateBalance": "time_off_balances",
    "changeTimeOffPolicyStatus": "time_off_policies",
    "createTimeOffPolicy": "time_off_policies",
    "deleteTimeOffPolicy": "time_off_policies",
    "getTimeOffPolicies": "time_off_policies",
    "getTimeOffPolicy": "time_off_policies",
    "updateTimeOffPolicy": "time_off_policies",
    "changeTimeOffRequestStatus": "time_off_requests",
    "createTimeOffRequest": "time_off_requests",
    "createTimeOffRequestForUser": "time_off_requests",
    "deleteTimeOffRequest": "time_off_requests",
    "getAllTimeOffRequestsOnWorkspace": "time_off_requests",
    "addNewGroup": "user_groups",
    "addUsersToGroup": "user_groups",
    "deleteGroup": "user_groups",
    "findAllGroupsOnWorkspace": "user_groups",
    "removeUserFromGroup": "user_groups",
    "updateGroup": "user_groups",
    "addLimitedUsersWithInfo": "users",
    "addUserToWorkspace": "users",
    "filterWorkspaceUsers": "users",
    "findUserTeamManagers": "users",
    "findWorkspaceUsers": "users",
    "getCurrentUser": "users",
    "giveUserManagerRole": "users",
    "removeUserManagerRole": "users",
    "updateUserCostRate": "users",
    "updateUserCustomFieldValue": "users",
    "updateUserHourlyRate": "users",
    "updateUserStatus": "users",
    "createWebhook": "webhooks",
    "deleteWebhook": "webhooks",
    "getAddonWebhooksOnWorkspace": "webhooks",
    "getWebhookById": "webhooks",
    "getWebhookEventStatusesWithLatestLog": "webhooks",
    "getWebhookLogs": "webhooks",
    "getWebhooksOnWorkspace": "webhooks",
    "patchWorkspacesWorkspaceIdWebhooksWebhookIdToken": "webhooks",
    "updateWebhook": "webhooks",
    "addWorkspace": "workspaces",
    "getAllMyWorkspaces": "workspaces",
    "getWorkspaceInfo": "workspaces",
    "updateWorkspaceBillableRate": "workspaces",
    "updateWorkspaceCostRate": "workspaces",
}


class UnsupportedSchema(Exception):
    """Raised with the exact schema path when a construct is not understood."""


SCHEMA_REF = re.compile(r"^#/components/schemas/([^/]+)$")
# `#/components/schemas/X/properties/y` points inside a schema; X is the root
# (manifest reconciliation finding: this is why the root count is 339, not 340).
NESTED_SCHEMA_REF = re.compile(r"^#/components/schemas/([^/]+)/properties/([^/]+)$")
COMPONENT_REF = re.compile(r"^#/components/(parameters|responses|requestBodies)/([^/]+)$")


def snake(name: str) -> str:
    """camelCase / PascalCase / kebab-case wire name -> python snake_case."""
    out = re.sub(r"[-. ]", "_", name)
    out = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", out)
    out = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", out)
    out = out.lower()
    if out.startswith("_"):
        out = out.lstrip("_")
        if not out:
            raise UnsupportedSchema(f"cannot derive public identifier from wire name {name!r}")
        out += "_"
    if keyword.iskeyword(out):
        out += "_"
    if not out.isidentifier():
        raise UnsupportedSchema(f"cannot derive identifier from wire name {name!r}")
    return out


class Importer:
    def __init__(self, spec: dict[str, Any], source_sha: str) -> None:
        self.spec = spec
        self.schemas: dict[str, Any] = spec["components"]["schemas"]
        self.components: dict[str, Any] = spec["components"]
        self.source_sha = source_sha

    # ---------- reachability and grouping ----------

    def _collect_schema_refs(self, obj: Any, acc: set[str]) -> None:
        if isinstance(obj, dict):
            ref = obj.get("$ref")
            if isinstance(ref, str):
                m = SCHEMA_REF.match(ref)
                nested = NESTED_SCHEMA_REF.match(ref)
                if m:
                    acc.add(m.group(1))
                elif nested:
                    acc.add(nested.group(1))
                else:
                    m2 = COMPONENT_REF.match(ref)
                    if not m2:
                        raise UnsupportedSchema(f"unsupported $ref target {ref!r}")
                    self._collect_schema_refs(self.components[m2.group(1)][m2.group(2)], acc)
            for value in obj.values():
                self._collect_schema_refs(value, acc)
        elif isinstance(obj, list):
            for value in obj:
                self._collect_schema_refs(value, acc)

    def _closure(self, seed: set[str]) -> set[str]:
        out = set(seed)
        frontier = set(seed)
        while frontier:
            nxt: set[str] = set()
            for name in frontier:
                if name not in self.schemas:
                    raise UnsupportedSchema(f"$ref to unknown schema {name!r}")
                acc: set[str] = set()
                self._collect_schema_refs(self.schemas[name], acc)
                nxt |= acc - out
            out |= nxt
            frontier = nxt
        return out

    def group_schemas(self) -> tuple[dict[str, str], set[str]]:
        """Return ({schema: domain-or-common}, request_only_roots)."""
        per_domain: dict[str, set[str]] = {}
        request_side: set[str] = set()
        response_side: set[str] = set()
        seen_ops: set[str] = set()
        for item in self.spec["paths"].values():
            for verb in ("get", "post", "put", "patch", "delete"):
                if verb not in item:
                    continue
                op = item[verb]
                op_id = op["operationId"]
                seen_ops.add(op_id)
                domain = OPERATION_DOMAIN[op_id]
                direct: set[str] = set()
                self._collect_schema_refs(op, direct)
                per_domain.setdefault(domain, set()).update(self._closure(direct))
                req_refs: set[str] = set()
                if "requestBody" in op:
                    self._collect_schema_refs(op["requestBody"], req_refs)
                for parameter in op.get("parameters", []):
                    self._collect_schema_refs(parameter, req_refs)
                request_side |= self._closure(req_refs)
                resp_refs: set[str] = set()
                self._collect_schema_refs(op.get("responses", {}), resp_refs)
                response_side |= self._closure(resp_refs)
        missing = set(OPERATION_DOMAIN) - seen_ops
        if missing:
            raise UnsupportedSchema(f"operations in domain map but not spec: {sorted(missing)}")

        owner: dict[str, str] = {}
        for domain, names in per_domain.items():
            for name in names:
                if name in owner and owner[name] != domain:
                    owner[name] = "common"
                elif name not in owner:
                    owner[name] = domain
        reachable = set(owner)
        if len(reachable) != EXPECTED_ROOT_COUNT:
            raise UnsupportedSchema(
                f"reachable root count {len(reachable)} != {EXPECTED_ROOT_COUNT}"
            )
        unreachable = set(self.schemas) - reachable
        if unreachable != KNOWN_UNREACHABLE:
            raise UnsupportedSchema(f"unexpected unreachable set: {sorted(unreachable)}")
        return owner, request_side - response_side

    # ---------- type rendering ----------

    # Inline object schemas synthesize named classes (Parent + FieldPascal). They are
    # collected here while rendering a root and emitted before it.
    pending_inline: list[str]
    current_request_only: bool
    current_root: str

    def _inline_class(self, schema: dict[str, Any], path: str, field_hint: str) -> str:
        pascal = "".join(part.capitalize() for part in snake(field_hint).split("_"))
        name = f"{self.current_root}{pascal}"
        source = self._render_object_class(name, schema, path, self.current_request_only)
        self.pending_inline.append(source)
        return name

    def ref_name(self, ref: str, path: str) -> str:
        m = SCHEMA_REF.match(ref)
        if not m:
            raise UnsupportedSchema(f"{path}: non-schema $ref {ref!r}")
        name = m.group(1)
        if name in STR_UNION_REFS:
            return f"{name} | str"
        return name

    def render_type(self, schema: Any, path: str) -> str:
        """Render the Python annotation for a schema node (as a quoted-safe string)."""
        if not isinstance(schema, dict):
            raise UnsupportedSchema(f"{path}: schema node is not a mapping")
        if "$ref" in schema:
            extra_keys = set(schema) - {"$ref", "description", "example", "nullable"}
            if extra_keys:
                raise UnsupportedSchema(f"{path}: $ref with siblings {sorted(extra_keys)}")
            nested = NESTED_SCHEMA_REF.match(schema["$ref"])
            if nested:
                target = self.schemas[nested.group(1)]["properties"][nested.group(2)]
                rendered = self.render_type(target, f"{path}->({schema['$ref']})")
            else:
                rendered = self.ref_name(schema["$ref"], path)
            if schema.get("nullable"):
                rendered = f"{rendered} | None"
            return rendered

        nullable = bool(schema.get("nullable"))
        rendered = self._render_core(schema, path)
        if nullable:
            rendered = f"{rendered} | None"
        return rendered

    def _render_core(self, schema: dict[str, Any], path: str) -> str:
        if "allOf" in schema:
            parts = schema["allOf"]
            if len(parts) == 1 and "$ref" in parts[0]:
                return self.ref_name(parts[0]["$ref"], path)
            raise UnsupportedSchema(f"{path}: inline allOf composition needs a named class")
        if "oneOf" in schema or "anyOf" in schema:
            variants = schema.get("oneOf") or schema.get("anyOf") or []
            rendered = [self.render_type(v, f"{path}/oneOf[{i}]") for i, v in enumerate(variants)]
            return " | ".join(dict.fromkeys(rendered))
        if "enum" in schema:
            if schema.get("type") not in (None, "string"):
                raise UnsupportedSchema(f"{path}: non-string enum")
            values = schema["enum"]
            if not all(isinstance(v, str) for v in values):
                raise UnsupportedSchema(f"{path}: non-string enum values")
            joined = ", ".join(repr(v) for v in values)
            return f"Literal[{joined}]"
        t = schema.get("type")
        if t == "string":
            return "bytes" if schema.get("format") == "binary" else "str"
        if t == "integer":
            return "int"
        if t == "number":
            return "float"
        if t == "boolean":
            return "bool"
        if t == "array":
            items = schema.get("items")
            if items is None:
                raise UnsupportedSchema(f"{path}: array without items")
            return f"list[{self.render_type(items, path + '/items')}]"
        if t == "object" or "properties" in schema:
            if "properties" in schema:
                field_hint = path.rsplit("/", 1)[-1]
                if field_hint in ("items", "additionalProperties"):
                    field_hint = path.rsplit("/", 3)[-3] + "Item"
                return self._inline_class(schema, path, field_hint)
            unknown = set(schema) - {
                "type",
                "additionalProperties",
                "description",
                "example",
                "nullable",
                "default",
                "title",
            }
            if unknown:
                raise UnsupportedSchema(f"{path}: unsupported object keys {sorted(unknown)}")
            ap = schema.get("additionalProperties")
            if isinstance(ap, dict):
                return f"dict[str, {self.render_type(ap, path + '/additionalProperties')}]"
            return "dict[str, Any]"
        if t is None and set(schema) <= {"description", "example", "nullable", "default"}:
            # A bare `{description: ...}` node means "unconstrained value" in this spec.
            return "Any"
        raise UnsupportedSchema(f"{path}: unsupported construct keys={sorted(schema)}")

    # ---------- class rendering ----------

    def render_root(self, name: str, request_only: bool) -> tuple[str, bool]:
        """Render one component-schema root. Returns (source, is_model_class)."""
        schema = self.schemas[name]
        path = f"components/schemas/{name}"
        description = schema.get("description")
        self.pending_inline = []
        self.current_request_only = request_only
        self.current_root = name

        if "enum" in schema:
            body = self.render_type({k: v for k, v in schema.items() if k != "nullable"}, path)
            doc = f"\n# {' '.join(str(description).split())}" if description else ""
            return f"{doc}\n{name} = {body}\n", False

        if "allOf" in schema:
            return self._render_allof_class(name, schema, path, request_only), True

        if "oneOf" in schema:
            body = self.render_type(schema, path)
            return f"\n{name} = {body}\n", False

        t = schema.get("type")
        if t == "array":
            item = self.render_type(schema["items"], path + "/items")
            return f"\n{name} = list[{item}]\n", False
        if t == "string":
            return f"\n{name} = {self.render_type(schema, path)}\n", False
        if t == "object" or "properties" in schema:
            return self._render_object_class(name, schema, path, request_only), True
        raise UnsupportedSchema(f"{path}: unsupported root construct keys={sorted(schema)}")

    def _render_allof_class(
        self, name: str, schema: dict[str, Any], path: str, request_only: bool
    ) -> str:
        merged_props: dict[str, Any] = {}
        merged_required: set[str] = set()
        description = schema.get("description")
        for i, part in enumerate(schema["allOf"]):
            node = part
            if "$ref" in part:
                match = SCHEMA_REF.match(part["$ref"])
                if not match:
                    raise UnsupportedSchema(f"{path}: non-schema allOf $ref")
                node = self.schemas[match.group(1)]
            if not (node.get("type") == "object" or "properties" in node):
                raise UnsupportedSchema(f"{path}/allOf[{i}]: non-object allOf part")
            merged_props.update(node.get("properties", {}))
            merged_required.update(node.get("required", []))
        flat = {
            "type": "object",
            "properties": merged_props,
            "required": sorted(merged_required),
            "description": description,
            "additionalProperties": schema.get("additionalProperties"),
        }
        return self._render_object_class(name, flat, path, request_only)

    def _render_object_class(
        self, name: str, schema: dict[str, Any], path: str, request_only: bool
    ) -> str:
        base = "ClockifyRequestModel" if request_only else "ClockifyResponseModel"
        required = set(schema.get("required") or [])
        props: dict[str, Any] = schema.get("properties") or {}
        description = schema.get("description")

        lines = [f"\n\nclass {name}({base}):"]
        if description:
            doc = " ".join(str(description).split())
            lines.append(f'    """{doc}"""\n')
        if not props:
            if not description:
                lines.append("    pass")
            self._maybe_note_additional(schema, lines)
            return "\n".join(lines) + "\n"

        # The wire has one real case collision (`rtl` and `RTL`): an all-caps name
        # that collides after snake_case gets an `_upper` suffix.
        field_names: dict[str, str] = {}
        taken: set[str] = set()
        # All-caps wire names yield first so a colliding lowercase original keeps
        # the plain field name.
        for wire_name in sorted(props, key=lambda w: (w.isupper(), w)):
            field = snake(wire_name)
            if field in taken and wire_name.isupper():
                field = f"{field}_upper"
            if field in taken:
                raise UnsupportedSchema(
                    f"{path}: wire name {wire_name!r} collides on field {field!r}"
                )
            field_names[wire_name] = field
            taken.add(field)

        for wire_name, prop in props.items():
            field = field_names[wire_name]
            annotation = self.render_type(prop, f"{path}/properties/{wire_name}")
            is_required = wire_name in required
            needs_alias = field != wire_name
            if is_required:
                if needs_alias:
                    lines.append(f'    {field}: {annotation} = Field(alias="{wire_name}")')
                else:
                    lines.append(f"    {field}: {annotation}")
            else:
                if not annotation.endswith("| None"):
                    annotation = f"{annotation} | None"
                if needs_alias:
                    lines.append(
                        f'    {field}: {annotation} = Field(default=None, alias="{wire_name}")'
                    )
                else:
                    lines.append(f"    {field}: {annotation} = None")
        self._maybe_note_additional(schema, lines)
        return "\n".join(lines) + "\n"

    @staticmethod
    def _maybe_note_additional(schema: dict[str, Any], lines: list[str]) -> None:
        ap = schema.get("additionalProperties")
        if isinstance(ap, dict) and ap:
            lines.append("    # additionalProperties beyond declared fields land in model_extra")


MODULE_DOC = '''"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: {sha}
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

'''


def build_header(sha: str, body: str, external: dict[str, str]) -> str:
    """Emit only the imports the module body actually uses."""
    words = set(re.findall(r"\b\w+\b", body))
    header = MODULE_DOC.format(sha=sha)
    typing_names = [n for n in ("Any", "Literal") if n in words]
    if typing_names:
        header += f"from typing import {', '.join(typing_names)}\n\n"
    if "Field" in words:
        header += "from pydantic import Field\n\n"
    base_names = [n for n in ("ClockifyRequestModel", "ClockifyResponseModel") if n in words]
    if base_names:
        header += f"from clockify.models.base import {', '.join(base_names)}\n"
    used_external = sorted(n for n in external if n in words)
    by_module: dict[str, list[str]] = {}
    for name in used_external:
        by_module.setdefault(external[name], []).append(name)
    for module in sorted(by_module):
        names = ", ".join(by_module[module])
        header += f"from clockify.models.{module} import {names}\n"
    return header


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec_path", type=Path)
    parser.add_argument("--expect-sha256")
    parser.add_argument("--out", type=Path, default=Path("src/clockify/models"))
    args = parser.parse_args()

    raw = args.spec_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if args.expect_sha256 and sha != args.expect_sha256:
        print(f"source SHA mismatch: {sha}", file=sys.stderr)
        return 1

    spec = yaml.safe_load(raw)
    importer = Importer(spec, sha)
    owner, request_only = importer.group_schemas()

    modules: dict[str, list[str]] = {}
    for name in sorted(owner):
        source, _ = importer.render_root(name, request_only=name in request_only)
        # Inline nested classes are emitted immediately before their root.
        for inline_source in importer.pending_inline:
            modules.setdefault(owner[name], []).append(inline_source)
        modules.setdefault(owner[name], []).append(source)

    args.out.mkdir(parents=True, exist_ok=True)
    bodies = {domain: "".join(sources) for domain, sources in modules.items()}
    defined: dict[str, list[str]] = {
        domain: re.findall(r"^(?:class (\w+)\(|(\w+) = )", body, re.M)
        for domain, body in bodies.items()
    }
    names_by_module = {domain: [a or b for a, b in pairs] for domain, pairs in defined.items()}
    home: dict[str, str] = {}
    for domain, names in names_by_module.items():
        for name in names:
            if name in home:
                raise UnsupportedSchema(f"class {name!r} defined in two modules")
            home[name] = domain

    for domain, body in bodies.items():
        external = {n: m for n, m in home.items() if m != domain}
        header = build_header(sha, body, external)
        (args.out / f"{domain}.py").write_text(header + body + "\n")

    import_lines: list[str] = []
    all_names = ["ClockifyRequestModel", "ClockifyResponseModel"]
    for domain in sorted(names_by_module):
        names = sorted(names_by_module[domain])
        import_lines.append(
            f"from clockify.models.{domain} import (\n"
            + "".join(f"    {n},\n" for n in names)
            + ")"
        )
        all_names.extend(names)
    joined_imports = "\n".join(import_lines)
    all_block = "__all__ = [\n" + "".join(f'    "{n}",\n' for n in sorted(all_names)) + "]"
    (args.out / "__init__.py").write_text(
        f'''"""Static Clockify models generated from the corrected OpenAPI.

Source SHA-256: {sha}
Regenerate with scripts/import_openapi.py.
"""

from pydantic import BaseModel

from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel

{joined_imports}

{all_block}

for _name in __all__:
    _value = globals()[_name]
    if isinstance(_value, type) and issubclass(_value, BaseModel):
        _value.model_rebuild()
'''
    )
    print(f"wrote {len(bodies)} domain modules + __init__.py; {len(owner)} roots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
