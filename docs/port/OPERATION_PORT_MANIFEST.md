# Clockify Python Operation Port Manifest

**Status:** authoritative for endpoint mappings. The per-operation MCP
`Eligibility:` stamps (`WRITE-DEFERRED` and similar) are historical: since
0.2.0 the full server registers 104 write tools through the sealed gate
described in `MCP_WRITE_SAFETY_PLAN.md`.

| Source | Value |
|---|---|
| TypeScript repository snapshot | `apet97/clockify-ts-sdk@d7091a44a1b95d4918fa17a7f9b174bf668a9136` |
| Corrected OpenAPI | `clockify.corrected.openapi.yaml` · SHA-256 `38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94` |
| Discrepancy ledger | `spec/evidence/discrepancies.md` · SHA-256 `2b4a6c48a5e071e21b77ce76d1401b19c1206dab5b536f6bc290d5ab1b856bd8` |
| Generated on | `2026-08-12` |

## Epistemic key

- **FACT** means the corrected OpenAPI, repository source, committed fixture, or live-evidence ledger directly supports the statement.
- **INFERENCE** means the statement follows from those facts but is not itself asserted by a source.
- **PROPOSAL** means the Python design choice to implement.
- **UNRESOLVED** means the sources do not prove the behavior strongly enough to make it a hidden requirement.

## Reconciled surface

| Classification | Count | Basis |
|---|---:|---|
| Total operations | **168** | Exact count from the corrected OpenAPI paths |
| Non-mutating operations | **62** | 49 `GET` + 13 semantic read/search/report `POST` operations |
| Mutating operations | **106** | Classified by actual behavior, not HTTP verb alone |
| Raw MCP read tools proposed | **60** | 62 reads minus two binary-only operations |
| Conditional MCP read tool | **1 of the 60** | Public shared-report view is limited to JSON/CSV in MCP; PDF/XLSX stay SDK-only |
| SDK-only read operations | **2** | Receipt download and invoice export return binary payloads |
| Reachable component schemas | **339** | Transitive closure of component-schema roots from all operation parameters, bodies, and responses |

The 13 non-mutating `POST` operations are:

- `filterInvoices` → `invoices.filter()` — `POST /workspaces/{workspaceId}/invoices/info`
- `filterWorkspaceUsers` → `users.filter()` — `POST /workspaces/{workspaceId}/users/info`
- `generateAttendanceReport` → `reports.attendance()` — `POST /workspaces/{workspaceId}/reports/attendance`
- `generateDetailedReport` → `reports.detailed()` — `POST /workspaces/{workspaceId}/reports/detailed`
- `generateDetailedReportV1` → `reports.expense_details()` — `POST /workspaces/{workspaceId}/reports/expenses/detailed`
- `generateSummaryReport` → `reports.summary()` — `POST /workspaces/{workspaceId}/reports/summary`
- `generateWeeklyReport` → `reports.weekly()` — `POST /workspaces/{workspaceId}/reports/weekly`
- `getAllTimeOffRequestsOnWorkspace` → `time_off_requests.list()` — `POST /workspaces/{workspaceId}/time-off/requests`
- `getMultipleTimeEntries` → `time_entries.get_many()` — `POST /workspaces/{workspaceId}/time-entries/batch`
- `getScheduledAssignmentsPerProject` → `scheduling.list_project_totals()` — `POST /workspaces/{workspaceId}/scheduling/assignments/projects/totals`
- `getUsersCapacityTotals` → `scheduling.get_filtered_user_capacity()` — `POST /workspaces/{workspaceId}/scheduling/assignments/user-filter/totals`
- `getWebhookLogs` → `webhooks.search_logs()` — `POST /workspaces/{workspaceId}/webhooks/{webhookId}/logs`
- `searchAuditLogs` → `audit_log.search()` — `POST /workspaces/{workspaceId}/audit-log`

### Reconciliation findings that change the build

1. `x-clockify-risk` cannot be used as the read/write authority. Twelve of the thirteen semantic `POST` reads are currently tagged as writes in the corrected OpenAPI metadata. The Python manifest therefore owns an explicit, tested semantic classification.
2. The current TypeScript SDK names are useful evidence, not the Python API. Nineteen operations lack an explicit SDK group/method stamp, user-admin operations are split between `users`, `roles`, and `workspaces`, and the three user-scoped time-entry verbs are semantically misnamed. The mapping below resolves all collisions and Python keywords.
3. No per-operation data-cache TTL survives. MCP `ttlMs`/`cacheScope` describe protocol list/resource cacheability, not Clockify API response freshness.
4. All operations use the same configured Clockify credential invariant in the current contract: exactly one of API key or add-on token. Authentication is therefore a client/executor invariant, not repeated runtime metadata on every `Operation`.
5. PUT is not classified as full replacement by verb alone. Each operation records proven, mixed, or conservative replacement risk.
6. The transitive component-schema root count is 339, not 340. The larger draft count treated `#/components/schemas/SharedReportCreate/properties/type` as if it named a component schema. Six component schemas are unreachable from the 168 operations: `Feature`, `LogBinDocumentDto`, `PageableCollectionLogBinDocumentDto`, `SummaryReportChartDto`, `WebhookEntityType`, and `WebhookPayloadType`.

## Proposed Python resource map

| Resource attribute | Methods |
|---|---|
| `clockify.approvals` | `list()`, `resubmit()`, `resubmit_for_user()`, `submit()`, `submit_for_user()`, `submit_for_user_with_type()`, `submit_with_type()`, `update_status()` |
| `clockify.audit_log` | `search()` |
| `clockify.clients` | `create()`, `delete()`, `get()`, `list()`, `update()` |
| `clockify.custom_fields` | `create_for_workspace()`, `delete_for_workspace()`, `list_for_project()`, `list_for_workspace()`, `remove_from_project()`, `update_for_project()`, `update_for_workspace()` |
| `clockify.entity_changes` | `list_created()`, `list_deleted()`, `list_updated()` |
| `clockify.expense_categories` | `create()`, `delete()`, `list()`, `update()`, `update_status()` |
| `clockify.expenses` | `create()`, `delete()`, `download_receipt()`, `get()`, `list()`, `update()` |
| `clockify.files` | `upload_image()` |
| `clockify.holidays` | `create()`, `delete()`, `list()`, `list_in_period()`, `update()` |
| `clockify.invoice_items` | `create()`, `delete()`, `import_items()` |
| `clockify.invoice_payments` | `create()`, `delete()`, `list()` |
| `clockify.invoice_settings` | `get()`, `update()` |
| `clockify.invoices` | `create()`, `delete()`, `duplicate()`, `export()`, `filter()`, `get()`, `list()`, `update()`, `update_status()` |
| `clockify.member_profiles` | `get()`, `update()` |
| `clockify.projects` | `create()`, `create_from_template()`, `delete()`, `get()`, `list()`, `set_members()`, `update()`, `update_estimate()`, `update_memberships()`, `update_template()`, `update_user_cost_rate()`, `update_user_hourly_rate()` |
| `clockify.reports` | `attendance()`, `detailed()`, `expense_details()`, `summary()`, `weekly()` |
| `clockify.scheduling` | `change_recurring_period()`, `copy_assignment()`, `create_recurring()`, `delete_recurring()`, `get_filtered_user_capacity()`, `get_project_totals()`, `get_user_capacity()`, `list_assignments()`, `list_project_totals()`, `publish_assignments()`, `update_recurring()` |
| `clockify.shared_reports` | `create()`, `delete()`, `list()`, `update()`, `view_public()` |
| `clockify.tags` | `create()`, `delete()`, `get()`, `list()`, `update()` |
| `clockify.tasks` | `create()`, `delete()`, `get()`, `list()`, `update()`, `update_billable_rate()`, `update_cost_rate()` |
| `clockify.time_entries` | `bulk_update_for_user()`, `create()`, `create_for_user()`, `delete()`, `delete_all_for_user()`, `duplicate()`, `get()`, `get_many()`, `list_for_user()`, `list_in_progress()`, `mark_invoiced()`, `stop_timer_for_user()`, `update()` |
| `clockify.time_off_balance_assignments` | `create()`, `delete()`, `get_for_user_and_policy()`, `update()` |
| `clockify.time_off_balances` | `list_for_policy()`, `list_for_user()`, `update_for_policy()` |
| `clockify.time_off_policies` | `create()`, `delete()`, `get()`, `list()`, `update()`, `update_status()` |
| `clockify.time_off_requests` | `list()`, `submit()`, `submit_for_user()`, `update_status()`, `withdraw()` |
| `clockify.user_groups` | `add_members()`, `create()`, `delete()`, `list()`, `remove_member()`, `update()` |
| `clockify.users` | `add_limited_to_workspace()`, `add_to_workspace()`, `filter()`, `grant_manager_role()`, `list()`, `list_managers()`, `me()`, `revoke_manager_role()`, `update_cost_rate()`, `update_custom_field_value()`, `update_hourly_rate()`, `update_status()` |
| `clockify.webhooks` | `create()`, `delete()`, `get()`, `list()`, `list_event_statuses()`, `list_for_addon()`, `rotate_token()`, `search_logs()`, `update()` |
| `clockify.workspaces` | `create()`, `get()`, `list()`, `update_billable_rate()`, `update_cost_rate()` |

## Operation records

Parameter names under **Python** are the proposed public keyword names. Wire names remain exact. A `*` inside a schema shape marks a required property; `?` marks optional.

## Resource: `approvals`

### `approvals.list()` — `getApprovalRequests`

| Field | Reconciled value |
|---|---|
| Behavior | Get approval requests |
| HTTP | `GET /workspaces/{workspaceId}/approval-requests` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `status` | `status` | `query` | no | [`ApprovalRequestFilterState`](#schema-approvalrequestfilterstate)<br>Filters results based on the provided approval state. | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | [`ApprovalRequestSortColumn`](#schema-approvalrequestsortcolumn)<br>Column name to use as sorting criteria. | single query value; omit only when `None` |
| `types` | `types` | `query` | no | array[[`ApprovalRequestType`](#schema-approvalrequesttype)]<br>Filters results to the listed approval-request types. | repeated query key |
| `sort_order` | `sort-order` | `query` | no | [`SortOrder`](#schema-sortorder)<br>Represents the sorting order. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`ApprovalRequestListItem`](#schema-approvalrequestlistitem)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `types`:**

```yaml
default:
- TIMESHEET
- TIMESHEET_AND_EXPENSE
- EXPENSE
items:
  $ref: '#/components/schemas/ApprovalRequestType'
type: array
uniqueItems: true
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/ApprovalRequestListItem'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — `params.dropped-by-source-shadowing`:** `compensated-in-corrected-spec`.
- **FACT — `approvals.list.userid-and-date-params-ignored`:** **ignored.** A request carrying a `userId` that matches no request's owner, plus a `start`/`end` window with zero overlap with any request's `dateRange`, still returned the one real request unfiltered. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `approvals.resubmit()` — `resubmitEntriesForApproval`

| Field | Reconciled value |
|---|---|
| Behavior | Submit non pending/approved entries/expenses for approval to an existing approval request |
| HTTP | `POST /workspaces/{workspaceId}/approval-requests/resubmit-entries-for-approval` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `documented` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`SubmitApprovalRequestRequest`](#schema-submitapprovalrequestrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ApprovalRequestDtoV1`](#schema-approvalrequestdtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_resubmit`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`action`; blast radius=`multi-entity`; sensitivity=`financial, time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **LOW-MEDIUM**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `real-openapi`.
- **UNRESOLVED:** Operation success is not in the `live-success` bucket (`documented`); keep the SDK method but do not expose an MCP write until a controlled success probe exists.

### `approvals.resubmit_for_user()` — `resubmitEntriesForApprovalForUser`

| Field | Reconciled value |
|---|---|
| Behavior | Re-submit rejected/withdrawn entries/expenses for an approval of a user |
| HTTP | `POST /workspaces/{workspaceId}/approval-requests/users/{userId}/resubmit-entries-for-approval` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `probe-documented` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`SubmitApprovalRequestRequest`](#schema-submitapprovalrequestrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ApprovalRequestDtoV1`](#schema-approvalrequestdtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_resubmit_for_user`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`action`; blast radius=`multi-entity`; sensitivity=`financial, time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **MEDIUM**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** Operation success is not in the `live-success` bucket (`probe-documented`); keep the SDK method but do not expose an MCP write until a controlled success probe exists.

### `approvals.submit()` — `submitApprovalRequest`

| Field | Reconciled value |
|---|---|
| Behavior | Submit approval request |
| HTTP | `POST /workspaces/{workspaceId}/approval-requests` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`SubmitApprovalRequestRequest`](#schema-submitapprovalrequestrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`ApprovalRequestDtoV1`](#schema-approvalrequestdtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_submit`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`multi-entity`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `approvals.submit_for_user()` — `submitApprovalRequestForUser`

| Field | Reconciled value |
|---|---|
| Behavior | Submit an approval request for a user |
| HTTP | `POST /workspaces/{workspaceId}/approval-requests/users/{userId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`SubmitApprovalRequestRequest`](#schema-submitapprovalrequestrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`ApprovalRequestDtoV1`](#schema-approvalrequestdtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_submit_for_user`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`multi-entity`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `approvals.submit_for_user_with_type()` — `createApprovalForOtherWithType`

| Field | Reconciled value |
|---|---|
| Behavior | Submit approval request for user with type |
| HTTP | `POST /workspaces/{workspaceId}/approval-requests/users/{userId}/{type}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `probe-documented` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents user identifier across the system. | path segment; percent-encode once |
| `type` | `type` | `path` | yes | string enum["TIMESHEET", "EXPENSE", "TIMESHEET_AND_EXPENSE"]<br>Represents approval request type. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateApprovalRequestNoType`](#schema-createapprovalrequestnotype) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`ApprovalRequestDtoV1`](#schema-approvalrequestdtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: dd087fe2dd087fe2dd087fe2
type: string
```

**parameter path `userId`:**

```yaml
description: Represents user identifier across the system.
example: ff9ef6ffff9ef6ffff9ef6ff
type: string
```

**parameter path `type`:**

```yaml
enum:
- TIMESHEET
- EXPENSE
- TIMESHEET_AND_EXPENSE
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `approval-requests.balance-assignment.official-spec-surface-add-2026-08-05`:** a live fetch of the official public spec (`https://docs.clockify.me/openapi.json`, `openapi: 3.0.1`, `info.version: v1`, fetched 2026-08-05) diffed against the canonical 161-operation inventory (path-parameter names normalized to `{}` before comparison, to avoid false positives from e.g. `{id}` vs `{clientId}` naming) surfaced 14 raw additions, 7 of which the official spec itself marks `deprecated: true` (a new `templates` resource: `getTemplates`/`getTemplate`/ `createMany`/`update`/`delete_1`; plus `getProjectTotals`; plus `removeMember` — see the correction above). The remaining 7 are current, non-deprecated, and were independently corr…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_submit_for_user_with_type`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`multi-entity`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **MEDIUM**.
- Source evidence classes: `probe-fragment`.
- **UNRESOLVED:** Operation success is not in the `live-success` bucket (`probe-documented`); keep the SDK method but do not expose an MCP write until a controlled success probe exists.

### `approvals.submit_with_type()` — `createApprrovalRequest_1`

| Field | Reconciled value |
|---|---|
| Behavior | Submit approval request with type |
| HTTP | `POST /workspaces/{workspaceId}/approval-requests/{approvalRequestId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `probe-documented` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |
| `approval_request_id` | `approvalRequestId` | `path` | yes | string enum["TIMESHEET", "EXPENSE"]<br>Represents approval request type. Named approvalRequestId (not type) because this path position collides, at the HTTP routing level, with PATCH .../approval-requests/{approvalRequestId} (updateApprovalStatus) -- Clockify's own server cannot distinguish the two by name, only by position. GOCLMCP's ca… | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateApprovalRequestNoType`](#schema-createapprovalrequestnotype) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`ApprovalRequestDtoV1`](#schema-approvalrequestdtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: dd087fe2dd087fe2dd087fe2
type: string
```

**parameter path `approvalRequestId`:**

```yaml
enum:
- TIMESHEET
- EXPENSE
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `approval-requests.balance-assignment.official-spec-surface-add-2026-08-05`:** a live fetch of the official public spec (`https://docs.clockify.me/openapi.json`, `openapi: 3.0.1`, `info.version: v1`, fetched 2026-08-05) diffed against the canonical 161-operation inventory (path-parameter names normalized to `{}` before comparison, to avoid false positives from e.g. `{id}` vs `{clientId}` naming) surfaced 14 raw additions, 7 of which the official spec itself marks `deprecated: true` (a new `templates` resource: `getTemplates`/`getTemplate`/ `createMany`/`update`/`delete_1`; plus `getProjectTotals`; plus `removeMember` — see the correction above). The remaining 7 are current, non-deprecated, and were independently corr…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_submit_with_type`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`multi-entity`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **MEDIUM**.
- Source evidence classes: `probe-fragment`.
- **UNRESOLVED:** Operation success is not in the `live-success` bucket (`probe-documented`); keep the SDK method but do not expose an MCP write until a controlled success probe exists.

### `approvals.update_status()` — `updateApprovalRequest`

| Field | Reconciled value |
|---|---|
| Behavior | Update an approval request |
| HTTP | `PATCH /workspaces/{workspaceId}/approval-requests/{approvalRequestId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `approval_request_id` | `approvalRequestId` | `path` | yes | string<br>Represents an approval request identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateApprovalRequestRequest`](#schema-updateapprovalrequestrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ApprovalRequestDtoV1`](#schema-approvalrequestdtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `approvalRequestId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_approvals_update_status`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `audit_log`

### `audit_log.search()` — `searchAuditLogs`

| Field | Reconciled value |
|---|---|
| Behavior | Generate an audit log report using the audit-log /v1 API |
| HTTP | `POST /workspaces/{workspaceId}/audit-log` |
| Service | `AUDIT_LOG` · `https://auditlog-api.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Clockify workspace identifier. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AuditLogRequest`](#schema-auditlogrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`AuditLogResponse`](#schema-auditlogresponse) | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `audit-log.actions.closed-enum`:** the audit-log service accepts a closed action vocabulary; an invented action fails the request rather than acting as an open filter. `fixed-in-canonical-generator`. GOCLMCP's source fragment now owns `AuditLogAction`, a Go test compares it exactly with the tool enum, and the generated SDK exports `AUDIT_LOG_ACTIONS` plus `AuditLogAction` for local CLI/MCP validation.
- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_audit_log_search`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `har-capture`, `live-success`, `official-json`, `probe-fragment`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `clients`

### `clients.create()` — `postWorkspacesWorkspaceIdClients`

| Field | Reconciled value |
|---|---|
| Behavior | Create client |
| HTTP | `POST /workspaces/{workspaceId}/clients` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ClientCreate`](#schema-clientcreate) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`Client`](#schema-client) | object envelope; item arrays: `ccEmails` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `clients.create.cc-emails-and-currency-id-dropped`:** `POST /workspaces/{ws}/clients` with `ccEmails` and `currencyId` returns 201 and ignores both: `ccEmails` comes back `null` and `currencyId` falls back to the workspace default currency. `PUT` on the same client accepts both and they persist. The reporting repository's "only name+email stick" is too strong — `note` sticks on create as well. `fixed-in-canonical-source`.
- **FACT — `clients.write.currency-code-is-inert`:** Clockify ignores `currencyCode` on **both** verbs, with no error. The only field that sets a client's currency is `currencyId`, which no request type declares, and it works only on `PUT`. `fixed-in-canonical-source`.
- **FACT — `entity.name-reserved-after-delete.cross-repo-2026-06-09`:** a project / tag / client NAME stays reserved even after the entity is archived and then deleted. Re-creating with the same name returns `... with this name already exists` (e.g. `"Project with this name already exists"`) even though the name no longer appears in any list — so a "list, then reuse the name" recovery never surfaces it. The only fix is a distinct name. `documented; ts-side-hint-pending`. Recommend the TS MCP `clockify_*_create` tools (and the SDK `create` docstrings) warn that a previously deleted name may report "already exists" and to retry with a distinct name. No spec change — a platform behavior, not a shape divergence.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_clients_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `clients.delete()` — `deleteWorkspacesWorkspaceIdClientsClientId`

| Field | Reconciled value |
|---|---|
| Behavior | Delete client |
| HTTP | `DELETE /workspaces/{workspaceId}/clients/{clientId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `client_id` | `clientId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Client`](#schema-client) | object envelope; item arrays: `ccEmails` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `clientId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** archive or complete before delete.
- **FACT — lifecycle:** client must be archived before delete.
- **FACT — `deletes.archive-first`:** Clockify rejects DELETE of an ACTIVE entity. Projects/clients/expense-categories must be archived first; tasks marked DONE first. `compensated-in-tool-layer` for expense categories (2026-06-14) — `clockify_expenses_categories_delete` now `expenseCategories.archive({archived:true})` (the dedicated PATCH `/status`, no replace risk) before delete. Test: `mcp/tests/sweep-fixes.test.ts`. Projects/tasks compensated 2026-06-15 and clients 2026-06-17 (see the sub-entries below) — each archives via GET-then-PUT (carry the entity's fields, overlay `archived:true`/`status:"DONE"`) then DELETE, because their archive is a **replace-PUT** (`*.update`) w…
- **FACT — `deletes.archive-first.clients-blocked`:** `compensated-in-tool-layer` (2026-06-17). `clockify_clients_delete` GET-then-PUT (body envelope `{name, archived:true}`) to archive, then DELETE, after the confirm gate — mirroring `clockify_projects_delete`. Carries the client `name` the replace-PUT requires; errors clearly if the fetched client has no name. Order pinned by `mcp/tests/archive-then-delete.test.ts`. The upstream cleanup (type `archived` into `UpdateClientsRequestBody` so the cast isn't needed) remains a nice-to-have in `../GOCLMCP/` / `spec/corrected`, not a blocker.
- **FACT — `deletes.clients-tags.response-body-dropped`:** both DELETEs answer 200 with the full deleted entity. `deleteExpense` really is empty-bodied, so the contrast is what makes the finding narrow rather than a blanket rule. 200 with no content.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_clients_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `clients.get()` — `getWorkspacesWorkspaceIdClientsClientId`

| Field | Reconciled value |
|---|---|
| Behavior | Get client |
| HTTP | `GET /workspaces/{workspaceId}/clients/{clientId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `client_id` | `clientId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Client`](#schema-client) | object envelope; item arrays: `ccEmails` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `clientId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_clients_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `clients.list()` — `getWorkspacesWorkspaceIdClients`

| Field | Reconciled value |
|---|---|
| Behavior | List clients |
| HTTP | `GET /workspaces/{workspaceId}/clients` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `name` | `name` | `query` | no | string | single query value; omit only when `None` |
| `archived` | `archived` | `query` | no | boolean | single query value; omit only when `None` |
| `address` | `address` | `query` | no | string | single query value; omit only when `None` |
| `note` | `note` | `query` | no | string | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | string enum["NAME", "EMAIL", "NOTE"] | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"] | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<br>Hyphenated `page-size` is the documented spelling for v1 listing endpoints. Note: shared-reports uses `pageSize` (camelCase); the hyphenated form is silently ignored there. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`Client`](#schema-client)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter query `name`:**

```yaml
type: string
```

**parameter query `archived`:**

```yaml
type: boolean
```

**parameter query `address`:**

```yaml
type: string
```

**parameter query `note`:**

```yaml
type: string
```

**parameter query `sort-column`:**

```yaml
enum:
- NAME
- EMAIL
- NOTE
type: string
```

**parameter query `sort-order`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**parameter query `page`:**

```yaml
default: 1
minimum: 1
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/Client'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `list.archived-default-returns-both`:** omitting `archived` returns archived **and** active rows. Only `archived=false` restricts the result to active rows. `documented`.
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_clients_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `clients.update()` — `putWorkspacesWorkspaceIdClientsClientId`

| Field | Reconciled value |
|---|---|
| Behavior | Update client |
| HTTP | `PUT /workspaces/{workspaceId}/clients/{clientId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `client_id` | `clientId` | `path` | yes | string | path segment; percent-encode once |
| `archive_projects` | `archive-projects` | `query` | no | boolean | single query value; omit only when `None` |
| `mark_tasks_as_done` | `mark-tasks-as-done` | `query` | no | boolean | single query value; omit only when `None` |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ClientUpdate`](#schema-clientupdate) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Client`](#schema-client) | object envelope; item arrays: `ccEmails` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `clientId`:**

```yaml
type: string
```

**parameter query `archive-projects`:**

```yaml
default: false
type: boolean
```

**parameter query `mark-tasks-as-done`:**

```yaml
default: false
type: boolean
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** replacement update; omitted ccEmails clears stored addresses.
- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- **FACT — `clients.update.archived-missing-from-canonical-request`:** `fixed-in-canonical-source`. This was first recorded as pending in downstream ledger commit `90fefb7`. GOCLMCP test commit `b6d4560` locked the composed `ClientUpdate` shape and source commit `a4e72bb` added the optional `archived` field, refreshed the manifest, and regenerated the green canonical document. That document was copied byte-for-byte downstream at SHA-256 `0a1eeb34f6f8e7693b92d3edfb5841e512e6fa1b402b3ea49c82be70fd5565e7`; `make sdk-codegen` then regenerated the SDK and resource docs.
- **FACT — `clients.update.cc-emails-cleared-by-replacing-put`:** a client update is a replacing `PUT`, and `ccEmails` is not sticky under omission the way the currency is — omitting it clears it. Because no client request type declared the field, `clientUpdateBody` could not re-send it, so **every** `clockify_clients_update` call destroyed the client's CC email list as a side effect of changing something else. `fixed-in-canonical-source`.
- **FACT — `clients.write.currency-code-is-inert`:** Clockify ignores `currencyCode` on **both** verbs, with no error. The only field that sets a client's currency is `currencyId`, which no request type declares, and it works only on `PUT`. `fixed-in-canonical-source`.
- **FACT — `fern.sdk.clients-update-body-vs-projects-update-top-level`:** Clockify accepts client archive updates only with the nested client body shape (`body: { name, archived: true }`). Sending client update fields at the top level returns "Required request body is missing". Project archive updates, by contrast, accept the generated top-level project fields (`{ name, archived: true }`) and do not use a nested `body` wrapper in the generated SDK surface. The `archive` helper routes for both clients and projects returned 404 in this live cleanup path, so archive+delete cleanup must use the update methods first. accepted local SDK shape split. Keep client update fields nested under `body`; keep project update fi…
- **FACT — `params.dropped-by-source-shadowing`:** `compensated-in-corrected-spec`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_clients_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `custom_fields`

### `custom_fields.create_for_workspace()` — `createWorkspaceCustomField`

| Field | Reconciled value |
|---|---|
| Behavior | Create custom field on a workspace |
| HTTP | `POST /workspaces/{workspaceId}/custom-fields` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateCustomFieldRequest`](#schema-createcustomfieldrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`CustomField`](#schema-customfield) | object envelope; item arrays: `allowedValues`, `projectDefaultValues` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `custom-fields.create.required-missing-from-request`:** `fixed-in-canonical-source`. This was first recorded as pending in downstream ledger commit `90fefb7`. GOCLMCP test commit `b6d4560` locked optional boolean `required` and the explicit `false` example; source commit `a4e72bb` corrected the create schema, refreshed the manifest, and regenerated the green canonical document. The downstream byte-for-byte copy has SHA-256 `0a1eeb34f6f8e7693b92d3edfb5841e512e6fa1b402b3ea49c82be70fd5565e7`, after which `make sdk-codegen` regenerated the request type and docs.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_custom_fields_create_for_workspace`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `custom_fields.delete_for_workspace()` — `deleteWorkspaceCustomField`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a custom field |
| HTTP | `DELETE /workspaces/{workspaceId}/custom-fields/{customFieldId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `custom_field_id` | `customFieldId` | `path` | yes | string<br>Represents a custom field identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `204` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `customFieldId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_custom_fields_delete_for_workspace`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `custom_fields.list_for_project()` — `listProjectCustomFields`

| Field | Reconciled value |
|---|---|
| Behavior | Get custom fields on a project |
| HTTP | `GET /workspaces/{workspaceId}/projects/{projectId}/custom-fields` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `status` | `status` | `query` | no | [`CustomFieldStatus`](#schema-customfieldstatus)<br>Filters custom fields by custom field status. | single query value; omit only when `None` |
| `entity_type` | `entity-type` | `query` | no | array[[`CustomFieldEntityType`](#schema-customfieldentitytype)]<br>Filters custom fields by custom field entity type. Use repeated query parameters for more than one value, for example entity-type=TIMEENTRY&entity-type=USER. | repeated query key |
| `page` | `page` | `query` | no | integer<int32><br>1-based page index. Default 1. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size (number of items per page). Default 50; maximum 200. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`CustomField`](#schema-customfield)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

**parameter query `entity-type`:**

```yaml
items:
  $ref: '#/components/schemas/CustomFieldEntityType'
type: array
```

**parameter query `page`:**

```yaml
default: 1
format: int32
minimum: 1
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
maximum: 200
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/CustomField'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `pagination.iter-known-set.envelope-and-unpaginated`:** each endpoint was probed with `?page=1&page-size=2` (results-available) and the paginated endpoints additionally with `?page=999&page-size=2` (results- exhausted). Result: `audited-and-shipped`. Two changes ship in this session: 1. **Generator (GOCLMCP):** new `LAST_PAGE_HEADER_OPS` set (15 entries) + `stamp_last_page_header!` function called in the per-op finalization loop. The canonical YAML now carries `x-clockify-last-page-header: true` on each of the 15 audited-emitting operations. 2. **Wrapper (this repo):** `iterPages` now feature-detects `.withRawResponse()` on the fetcher's return, reads the `Last-Page` response header via the cas…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_custom_fields_list_for_project`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `custom_fields.list_for_workspace()` — `listWorkspaceCustomFields`

| Field | Reconciled value |
|---|---|
| Behavior | Get custom fields on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/custom-fields` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `name` | `name` | `query` | no | string<br>Filters custom fields by a string contained in the custom field name. | single query value; omit only when `None` |
| `status` | `status` | `query` | no | [`CustomFieldStatus`](#schema-customfieldstatus)<br>Filters custom fields by custom field status. | single query value; omit only when `None` |
| `entity_type` | `entity-type` | `query` | no | array[[`CustomFieldEntityType`](#schema-customfieldentitytype)]<br>Filters custom fields by custom field entity type. Use repeated query parameters for more than one value, for example entity-type=TIMEENTRY&entity-type=USER. | repeated query key |
| `page` | `page` | `query` | no | integer<int32><br>1-based page index. Default 1. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size (number of items per page). Default 50; maximum 200. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`CustomField`](#schema-customfield)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `name`:**

```yaml
type: string
```

**parameter query `entity-type`:**

```yaml
items:
  $ref: '#/components/schemas/CustomFieldEntityType'
type: array
```

**parameter query `page`:**

```yaml
default: 1
format: int32
minimum: 1
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
maximum: 200
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/CustomField'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `pagination.iter-known-set.envelope-and-unpaginated`:** each endpoint was probed with `?page=1&page-size=2` (results-available) and the paginated endpoints additionally with `?page=999&page-size=2` (results- exhausted). Result: `audited-and-shipped`. Two changes ship in this session: 1. **Generator (GOCLMCP):** new `LAST_PAGE_HEADER_OPS` set (15 entries) + `stamp_last_page_header!` function called in the per-op finalization loop. The canonical YAML now carries `x-clockify-last-page-header: true` on each of the 15 audited-emitting operations. 2. **Wrapper (this repo):** `iterPages` now feature-detects `.withRawResponse()` on the fetcher's return, reads the `Last-Page` response header via the cas…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_custom_fields_list_for_workspace`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `custom_fields.remove_from_project()` — `removeProjectCustomField`

| Field | Reconciled value |
|---|---|
| Behavior | Remove custom field from a project |
| HTTP | `DELETE /workspaces/{workspaceId}/projects/{projectId}/custom-fields/{customFieldId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `custom_field_id` | `customFieldId` | `path` | yes | string<br>Represents a custom field identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`CustomField`](#schema-customfield) | object envelope; item arrays: `allowedValues`, `projectDefaultValues` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

**parameter path `customFieldId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_custom_fields_remove_from_project`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `custom_fields.update_for_project()` — `updateProjectCustomField`

| Field | Reconciled value |
|---|---|
| Behavior | Update custom field on a project |
| HTTP | `PATCH /workspaces/{workspaceId}/projects/{projectId}/custom-fields/{customFieldId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `custom_field_id` | `customFieldId` | `path` | yes | string<br>Represents a custom field identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateProjectCustomFieldRequest`](#schema-updateprojectcustomfieldrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`CustomField`](#schema-customfield) | object envelope; item arrays: `allowedValues`, `projectDefaultValues` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

**parameter path `customFieldId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_custom_fields_update_for_project`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `custom_fields.update_for_workspace()` — `updateWorkspaceCustomField`

| Field | Reconciled value |
|---|---|
| Behavior | Update custom field on workspace |
| HTTP | `PUT /workspaces/{workspaceId}/custom-fields/{customFieldId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `custom_field_id` | `customFieldId` | `path` | yes | string<br>Represents a custom field identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateCustomFieldRequest`](#schema-updatecustomfieldrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`CustomField`](#schema-customfield) | object envelope; item arrays: `allowedValues`, `projectDefaultValues` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `customFieldId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_custom_fields_update_for_workspace`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `entity_changes`

### `entity_changes.list_created()` — `getCreatedEntityInfo`

| Field | Reconciled value |
|---|---|
| Behavior | Created entities (Experimental) |
| HTTP | `GET /workspaces/{workspaceId}/entities/created` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |
| `type` | `type` | `query` | yes | array[[`ChangeTrackerDocumentType`](#schema-changetrackerdocumenttype)]<br>Entity-change document type. Accepted values: APPROVAL_REQUESTS, BALANCE, CLIENTS, CUSTOM_FIELDS, HOLIDAYS, INVOICES, PROJECTS, PTO_POLICY, SCHEDULED_ASSIGNMENT, TAGS, TASKS, TIME_ENTRY, TIME_ENTRY_CUSTOM_FIELD_VALUE, TIME_ENTRY_RATE, TIME_OFF_REQUEST, USER, USER_GROUPS. | repeated query key |
| `start` | `start` | `query` | no | string<br>Represents the start date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no start date is provided, the application will set a default start date that matches the end date to create a date range of 30 days. If the end date is not specified either, the default behavior will apply from… | single query value; omit only when `None` |
| `end` | `end` | `query` | no | string<br>Represents the end date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no end date is provided, the application will set a default end date that matches the start date to create a date range of 30 days. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | string | single query value; omit only when `None` |
| `limit` | `limit` | `query` | no | string | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`EntityChangeDocument`](#schema-entitychangedocument)] | bare array |

**Pagination:** page=`page`; page size=`limit`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter query `type`:**

```yaml
type: array
description: 'Entity-change document type. Accepted values: APPROVAL_REQUESTS, BALANCE, CLIENTS, CUSTOM_FIELDS,
  HOLIDAYS, INVOICES, PROJECTS, PTO_POLICY, SCHEDULED_ASSIGNMENT, TAGS, TASKS, TIME_ENTRY, TIME_ENTRY_CUSTOM_FIELD_VALUE,
  TIME_ENTRY_RATE, TIME_OFF_REQUEST, USER, USER_GROUPS.'
example: TIME_ENTRY
items:
  $ref: '#/components/schemas/ChangeTrackerDocumentType'
```

**parameter query `start`:**

```yaml
description: Represents the start date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no start date
  is provided, the application will set a default start date that matches the end date to create a date range of
  30 days. If the end date is not specified either, the default behavior will apply from the current date.
example: '2024-10-29T10:00:00Z'
type: string
```

**parameter query `end`:**

```yaml
description: Represents the end date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no end date
  is provided, the application will set a default end date that matches the start date to create a date range of
  30 days.
example: '2024-11-28T10:00:00Z'
type: string
```

**parameter query `page`:**

```yaml
default: '0'
type: string
```

**parameter query `limit`:**

```yaml
default: '50'
type: string
```

**response `200` `application/json`:**

```yaml
type: array
items:
  $ref: '#/components/schemas/EntityChangeDocument'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_entity_changes_list_created`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`.
- No operation-specific unresolved item blocks the raw SDK method.

### `entity_changes.list_deleted()` — `getDeletedEntityInfo`

| Field | Reconciled value |
|---|---|
| Behavior | Deleted entities (Experimental) |
| HTTP | `GET /workspaces/{workspaceId}/entities/deleted` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system (Experimental) | path segment; percent-encode once |
| `type` | `type` | `query` | yes | array[[`ChangeTrackerDocumentType`](#schema-changetrackerdocumenttype)]<br>Entity-change document type. Accepted values: APPROVAL_REQUESTS, BALANCE, CLIENTS, CUSTOM_FIELDS, HOLIDAYS, INVOICES, PROJECTS, PTO_POLICY, SCHEDULED_ASSIGNMENT, TAGS, TASKS, TIME_ENTRY, TIME_ENTRY_CUSTOM_FIELD_VALUE, TIME_ENTRY_RATE, TIME_OFF_REQUEST, USER, USER_GROUPS. | repeated query key |
| `start` | `start` | `query` | no | string<br>Represents the start date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no start date is provided, the application will set a default start date that matches the end date to create a date range of 30 days. If the end date is not specified either, the default behavior will apply from… | single query value; omit only when `None` |
| `end` | `end` | `query` | no | string<br>Represents the end date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no end date is provided, the application will set a default end date that matches the start date to create a date range of 30 days. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | string | single query value; omit only when `None` |
| `limit` | `limit` | `query` | no | string | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`EntityChangeDocument`](#schema-entitychangedocument)] | bare array |

**Pagination:** page=`page`; page size=`limit`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: 'Represents workspace identifier across the system (Experimental) '
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter query `type`:**

```yaml
type: array
description: 'Entity-change document type. Accepted values: APPROVAL_REQUESTS, BALANCE, CLIENTS, CUSTOM_FIELDS,
  HOLIDAYS, INVOICES, PROJECTS, PTO_POLICY, SCHEDULED_ASSIGNMENT, TAGS, TASKS, TIME_ENTRY, TIME_ENTRY_CUSTOM_FIELD_VALUE,
  TIME_ENTRY_RATE, TIME_OFF_REQUEST, USER, USER_GROUPS.'
example: TIME_ENTRY
items:
  $ref: '#/components/schemas/ChangeTrackerDocumentType'
```

**parameter query `start`:**

```yaml
description: Represents the start date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no start date
  is provided, the application will set a default start date that matches the end date to create a date range of
  30 days. If the end date is not specified either, the default behavior will apply from the current date.
example: '2024-10-29T10:00:00Z'
type: string
```

**parameter query `end`:**

```yaml
description: Represents the end date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no end date
  is provided, the application will set a default end date that matches the start date to create a date range of
  30 days.
example: '2024-11-28T10:00:00Z'
type: string
```

**parameter query `page`:**

```yaml
default: '0'
type: string
```

**parameter query `limit`:**

```yaml
default: '50'
type: string
```

**response `200` `application/json`:**

```yaml
type: array
items:
  $ref: '#/components/schemas/EntityChangeDocument'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_entity_changes_list_deleted`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`.
- No operation-specific unresolved item blocks the raw SDK method.

### `entity_changes.list_updated()` — `getUpdatedEntityInfo`

| Field | Reconciled value |
|---|---|
| Behavior | Updated entities (Experimental) |
| HTTP | `GET /workspaces/{workspaceId}/entities/updated` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |
| `type` | `type` | `query` | yes | array[[`ChangeTrackerDocumentType`](#schema-changetrackerdocumenttype)]<br>Entity-change document type. Accepted values: APPROVAL_REQUESTS, BALANCE, CLIENTS, CUSTOM_FIELDS, HOLIDAYS, INVOICES, PROJECTS, PTO_POLICY, SCHEDULED_ASSIGNMENT, TAGS, TASKS, TIME_ENTRY, TIME_ENTRY_CUSTOM_FIELD_VALUE, TIME_ENTRY_RATE, TIME_OFF_REQUEST, USER, USER_GROUPS. | repeated query key |
| `start` | `start` | `query` | no | string<br>Represents the start date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no start date is provided, the application will set a default start date that matches the end date to create a date range of 30 days. If the end date is not specified either, the default behavior will apply from… | single query value; omit only when `None` |
| `end` | `end` | `query` | no | string<br>Represents the end date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no end date is provided, the application will set a default end date that matches the start date to create a date range of 30 days. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | string | single query value; omit only when `None` |
| `limit` | `limit` | `query` | no | string | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`EntityChangeDocument`](#schema-entitychangedocument)] | bare array |

**Pagination:** page=`page`; page size=`limit`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter query `type`:**

```yaml
type: array
description: 'Entity-change document type. Accepted values: APPROVAL_REQUESTS, BALANCE, CLIENTS, CUSTOM_FIELDS,
  HOLIDAYS, INVOICES, PROJECTS, PTO_POLICY, SCHEDULED_ASSIGNMENT, TAGS, TASKS, TIME_ENTRY, TIME_ENTRY_CUSTOM_FIELD_VALUE,
  TIME_ENTRY_RATE, TIME_OFF_REQUEST, USER, USER_GROUPS.'
example: TIME_ENTRY
items:
  $ref: '#/components/schemas/ChangeTrackerDocumentType'
```

**parameter query `start`:**

```yaml
description: Represents the start date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no start date
  is provided, the application will set a default start date that matches the end date to create a date range of
  30 days. If the end date is not specified either, the default behavior will apply from the current date.
example: '2024-10-29T10:00:00Z'
type: string
```

**parameter query `end`:**

```yaml
description: Represents the end date in yyyy-MM-ddThh:mm:ssZ format. This parameter is optional; if no end date
  is provided, the application will set a default end date that matches the start date to create a date range of
  30 days.
example: '2024-11-28T10:00:00Z'
type: string
```

**parameter query `page`:**

```yaml
default: '0'
type: string
```

**parameter query `limit`:**

```yaml
default: '50'
type: string
```

**response `200` `application/json`:**

```yaml
type: array
items:
  $ref: '#/components/schemas/EntityChangeDocument'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_entity_changes_list_updated`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `expense_categories`

### `expense_categories.create()` — `addExpenseCategory`

| Field | Reconciled value |
|---|---|
| Behavior | Add an expense category |
| HTTP | `POST /workspaces/{workspaceId}/expenses/categories` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ExpenseCategoryRequest`](#schema-expensecategoryrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`ExpenseCategoryDtoV1`](#schema-expensecategorydtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expense_categories_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expense_categories.delete()` — `deleteExpenseCategory`

| Field | Reconciled value |
|---|---|
| Behavior | Delete an expense category |
| HTTP | `DELETE /workspaces/{workspaceId}/expenses/categories/{categoryId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `category_id` | `categoryId` | `path` | yes | string<br>Represents a category identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `204` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `categoryId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** archive or complete before delete.
- **FACT — `deletes.archive-first`:** Clockify rejects DELETE of an ACTIVE entity. Projects/clients/expense-categories must be archived first; tasks marked DONE first. `compensated-in-tool-layer` for expense categories (2026-06-14) — `clockify_expenses_categories_delete` now `expenseCategories.archive({archived:true})` (the dedicated PATCH `/status`, no replace risk) before delete. Test: `mcp/tests/sweep-fixes.test.ts`. Projects/tasks compensated 2026-06-15 and clients 2026-06-17 (see the sub-entries below) — each archives via GET-then-PUT (carry the entity's fields, overlay `archived:true`/`status:"DONE"`) then DELETE, because their archive is a **replace-PUT** (`*.update`) w…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expense_categories_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expense_categories.list()` — `getExpenseCategories`

| Field | Reconciled value |
|---|---|
| Behavior | Get all expense categories |
| HTTP | `GET /workspaces/{workspaceId}/expenses/categories` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `sort_column` | `sort-column` | `query` | no | string enum["NAME"]<br>Column name to be used as sorting criteria. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"]<br>Sorting order. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `archived` | `archived` | `query` | no | boolean<br>Filters results based on whether the category is archived. | single query value; omit only when `None` |
| `name` | `name` | `query` | no | string<br>Filters expense categories by a string matched against their name. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ExpenseCategoriesDtoV1`](#schema-expensecategoriesdtov1) | object envelope; item arrays: `categories` |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; object envelope; item arrays: `categories`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter query `sort-column`:**

```yaml
enum:
- NAME
type: string
```

**parameter query `sort-order`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `archived`:**

```yaml
default: false
type: boolean
```

**parameter query `name`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expense_categories_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expense_categories.update()` — `updateExpenseCategory`

| Field | Reconciled value |
|---|---|
| Behavior | Update an expense category |
| HTTP | `PUT /workspaces/{workspaceId}/expenses/categories/{categoryId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `category_id` | `categoryId` | `path` | yes | string<br>Represents a category identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ExpenseCategoryRequest`](#schema-expensecategoryrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ExpenseCategoryDtoV1`](#schema-expensecategorydtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `categoryId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expense_categories_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expense_categories.update_status()` — `archiveExpenseCategory`

| Field | Reconciled value |
|---|---|
| Behavior | Archive an expense category |
| HTTP | `PATCH /workspaces/{workspaceId}/expenses/categories/{categoryId}/status` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `category_id` | `categoryId` | `path` | yes | string<br>Represents a category identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ExpenseCategoryStatusRequest`](#schema-expensecategorystatusrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ExpenseCategoryDtoV1`](#schema-expensecategorydtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `categoryId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expense_categories_update_status`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`transition`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `expenses`

### `expenses.create()` — `createExpense`

| Field | Reconciled value |
|---|---|
| Behavior | Create an expense |
| HTTP | `POST /workspaces/{workspaceId}/expenses` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `multipart/form-data` | [`ExpenseCreateRequest`](#schema-expensecreaterequest) | `file` content type `application/octet-stream` |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`ExpenseDtoV1`](#schema-expensedtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expenses_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expenses.delete()` — `deleteExpense`

| Field | Reconciled value |
|---|---|
| Behavior | Delete an expense |
| HTTP | `DELETE /workspaces/{workspaceId}/expenses/{expenseId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `expense_id` | `expenseId` | `path` | yes | string<br>Represents an expense identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `expenseId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expenses_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expenses.download_receipt()` — `downloadExpenseReceipt`

| Field | Reconciled value |
|---|---|
| Behavior | Download a receipt |
| HTTP | `GET /workspaces/{workspaceId}/expenses/{expenseId}/files/{fileId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `expense_id` | `expenseId` | `path` | yes | string<br>Represents an expense identifier across the system. | path segment; percent-encode once |
| `file_id` | `fileId` | `path` | yes | string<br>Represents a file identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/octet-stream` | `bytes` | string<byte> | string |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `expenseId`:**

```yaml
default: '##default'
type: string
```

**parameter path `fileId`:**

```yaml
default: '##default'
type: string
```

**response `200` `application/octet-stream`:**

```yaml
format: byte
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `expenses.download-receipt.bytes-available-on-supported-runtimes`:** present and correct on the tested runtime. No divergence reproduced. `documented`.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expenses_download_receipt`.
- Eligibility: **SDK-ONLY (binary response)**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-fragment`, `probe-supplement`, `real-openapi`.
- **UNRESOLVED:** Binary payload has no context-safe raw MCP representation in v1; keep it SDK-only unless a bounded resource/download contract is designed.

### `expenses.get()` — `getExpenseById`

| Field | Reconciled value |
|---|---|
| Behavior | Get an expense by ID |
| HTTP | `GET /workspaces/{workspaceId}/expenses/{expenseId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `expense_id` | `expenseId` | `path` | yes | string<br>Represents an expense identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ExpenseDtoV1`](#schema-expensedtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `expenseId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expenses_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expenses.list()` — `getWorkspaceExpenses`

| Field | Reconciled value |
|---|---|
| Behavior | Get all expenses on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/expenses` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `user_id` | `user-id` | `query` | no | string<br>Filters expenses by the user ID linked to the expense. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`WorkspaceExpensesDtoV1`](#schema-workspaceexpensesdtov1) | object envelope; item arrays: `dailyTotals`, `weeklyTotals` |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; object envelope; item arrays: `dailyTotals`, `weeklyTotals`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `user-id`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `expenses.list.expanded-category-and-project-dropped`:** the live wire returns **fully expanded objects** alongside those ids. Observed field names (values never captured): `expenses.expenses[].category` with `.id`, `.name`, `.priceInCents`, `.unit`, `.hasUnitPrice`, `.archived`, `.workspaceId`; `expenses.expenses[].project` with `.id`, `.name`, `.clientId`, `.clientName`, `.color`; plus `expenses.expenses[].task` and `expenses.expenses[].fileName`. **RESOLVED 2026-07-29.** `apply_live_overrides!` in `../GOCLMCP/scripts/gen-clockify-openapi` now replaces `ExpenseHydratedDtoV1` with the 14 live-observed properties (`category` → `$ref ExpenseCategoryDto`, `project` → `$ref ProjectInfoDto`, `task`…
- **FACT — `expenses.list.start-end-ignored-client-filtered`:** `compensated-in-sdk`. The typed double-nested response envelope remains canonical. One exported helper now scans pages, applies inclusive date-only/ISO bounds client-side, honors `Last-Page`, falls back to bounded page-length termination, distinguishes total limit from page size, and returns an explicit warning plus lossless page/filtered-offset continuation metadata. User bounds accept only valid date-only or RFC3339 values with an explicit `Z`/offset. CLI and MCP both use the helper and no longer cast the expense-list response.
- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expenses_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `expenses.update()` — `updateExpense`

| Field | Reconciled value |
|---|---|
| Behavior | Update an expense |
| HTTP | `PUT /workspaces/{workspaceId}/expenses/{expenseId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `expense_id` | `expenseId` | `path` | yes | string<br>Represents an expense identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `multipart/form-data` | [`ExpenseUpdateRequest`](#schema-expenseupdaterequest) | `file` content type `application/octet-stream` |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ExpenseDtoV1`](#schema-expensedtov1) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `expenseId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_expenses_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `files`

### `files.upload_image()` — `uploadImage`

| Field | Reconciled value |
|---|---|
| Behavior | Add a photo |
| HTTP | `POST /file/image` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

None.

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `multipart/form-data` | {`file*`: string<binary>} | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ImageUploadResponse`](#schema-imageuploadresponse) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**request `multipart/form-data`:**

```yaml
properties:
  file:
    description: Image to be uploaded
    format: binary
    type: string
required:
- file
type: object
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_files_upload_image`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `holidays`

### `holidays.create()` — `createHoliday`

| Field | Reconciled value |
|---|---|
| Behavior | Create a holiday |
| HTTP | `POST /workspaces/{workspaceId}/holidays` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateHolidayRequest`](#schema-createholidayrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`HolidayDto`](#schema-holidaydto) | object envelope; item arrays: `userGroupIds`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** replacement update; preserve required fields and assignment scope.
- **FACT — `holidays.update.replace-and-scope-filter`:** `PUT /holidays/{id}` **replaces** the document (omitted fields 400 "must not be null"), there is **no single-GET route** (must list-scan), and the assignment round-trips asymmetrically — GET echoes it FLAT as `userIds`/`userGroupIds`, but POST/PUT want it as a `{contains:"CONTAINS", ids, status}` filter under `users`/ `userGroups`. A holiday with no resolvable assignment is rejected. `compensated-in-tool-layer`. `clockify_holidays_update` now list-scans, rebuilds the full body, reconstructs the flat assignment into the CONTAINS filter, and errors clearly when no assignment can be preserved; create accepts `userIds`/`userGroupIds`. Tests: `…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_holidays_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `holidays.delete()` — `deleteHoliday`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a holiday |
| HTTP | `DELETE /workspaces/{workspaceId}/holidays/{holidayId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `holiday_id` | `holidayId` | `path` | yes | string<br>Represents a holiday identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`HolidayDetailsDto`](#schema-holidaydetailsdto) | object envelope; item arrays: `userGroupIds`, `userGroups`, `userIds`, `users` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `holidayId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_holidays_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `holidays.list()` — `getWorkspaceHolidays`

| Field | Reconciled value |
|---|---|
| Behavior | Get holidays on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/holidays` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `assigned_to` | `assigned-to` | `query` | no | string<br>If provided, returns a filtered list of holidays assigned to the user. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>1-based page index. Default 1. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size (number of items per page). Default 50; maximum 200. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`HolidayDto`](#schema-holidaydto)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `assigned-to`:**

```yaml
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
minimum: 1
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
maximum: 200
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/HolidayDto'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `pagination.iter-known-set.envelope-and-unpaginated`:** each endpoint was probed with `?page=1&page-size=2` (results-available) and the paginated endpoints additionally with `?page=999&page-size=2` (results- exhausted). Result: `audited-and-shipped`. Two changes ship in this session: 1. **Generator (GOCLMCP):** new `LAST_PAGE_HEADER_OPS` set (15 entries) + `stamp_last_page_header!` function called in the per-op finalization loop. The canonical YAML now carries `x-clockify-last-page-header: true` on each of the 15 audited-emitting operations. 2. **Wrapper (this repo):** `iterPages` now feature-detects `.withRawResponse()` on the fetcher's return, reads the `Last-Page` response header via the cas…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_holidays_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `holidays.list_in_period()` — `getWorkspaceHolidaysInPeriod`

| Field | Reconciled value |
|---|---|
| Behavior | Get holidays in a specific period |
| HTTP | `GET /workspaces/{workspaceId}/holidays/in-period` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `assigned_to` | `assigned-to` | `query` | yes | string<br>Filter list of holidays assigned to user. This value is a user ID; user-group IDs are not supported and may produce a misleading 403. Required by live Clockify for in-period holiday lookup. | single query value; omit only when `None` |
| `start` | `start` | `query` | yes | string<date-time><br>Filter list of holidays starting from start date. Expected date format yyyy-MM-ddThh:mm:ssZ. | single query value; omit only when `None` |
| `end` | `end` | `query` | yes | string<date-time><br>Filter list of holidays ending by end date. Expected date format yyyy-MM-ddThh:mm:ssZ. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`HolidayDto`](#schema-holidaydto)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `assigned-to`:**

```yaml
type: string
```

**parameter query `start`:**

```yaml
format: date-time
type: string
```

**parameter query `end`:**

```yaml
format: date-time
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/HolidayDto'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `deferred-list-endpoints.not-paginated-or-not-live`:** 1. `GET /workspaces?page=1&page-size=1` returned **all 28** records (200 102 bytes). Also tried `?per_page=1`, `?size=1`, `?limit=1`, `?pageSize=1` — every variant returned the full 28-record list unchanged. The endpoint is a collection enumerator with no server-side paging. 2. `GET /workspaces/{wsId}/balance?policyId=<real>` returned `HTTP 404 {"message":"No static resource v1/workspaces/{wsId}/balance.","code":3000}`. The bare `/balance` route does not exist on the live API. The granular routes `/workspaces/{wsId}/time-off/balance/policy/{policyId}` and `/workspaces/{wsId}/time-off/balance/user/{userId}` are the live equivalents and are…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_holidays_list_in_period`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `holidays.update()` — `updateHoliday`

| Field | Reconciled value |
|---|---|
| Behavior | Update a holiday |
| HTTP | `PUT /workspaces/{workspaceId}/holidays/{holidayId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `holiday_id` | `holidayId` | `path` | yes | string<br>Represents a holiday identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateHolidayRequest`](#schema-updateholidayrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`HolidayDto`](#schema-holidaydto) | object envelope; item arrays: `userGroupIds`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `holidayId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** replacement update; preserve required fields and assignment scope.
- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- **FACT — `holidays.update.replace-and-scope-filter`:** `PUT /holidays/{id}` **replaces** the document (omitted fields 400 "must not be null"), there is **no single-GET route** (must list-scan), and the assignment round-trips asymmetrically — GET echoes it FLAT as `userIds`/`userGroupIds`, but POST/PUT want it as a `{contains:"CONTAINS", ids, status}` filter under `users`/ `userGroups`. A holiday with no resolvable assignment is rejected. `compensated-in-tool-layer`. `clockify_holidays_update` now list-scans, rebuilds the full body, reconstructs the flat assignment into the CONTAINS filter, and errors clearly when no assignment can be preserved; create accepts `userIds`/`userGroupIds`. Tests: `…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_holidays_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `invoice_items`

### `invoice_items.create()` — `addInvoiceItem`

| Field | Reconciled value |
|---|---|
| Behavior | Add item to an invoice |
| HTTP | `POST /workspaces/{workspaceId}/invoices/{invoiceId}/items` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AddInvoiceItemRequest`](#schema-addinvoiceitemrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `invoices.items-unit-price-scale`:** `compensated` (2026-08-09). `clockify_invoices_items_add` scales the price, `mcp/tests/backlog-tools.test.ts` pins `15000 -> 1500000` plus the RangeError refusal above the exact-integer envelope, and the repaired tripwire reds if a future item-add site drops the call.
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_items_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoice_items.delete()` — `deleteInvoiceItem`

| Field | Reconciled value |
|---|---|
| Behavior | Delete item from an invoice |
| HTTP | `DELETE /workspaces/{workspaceId}/invoices/{invoiceId}/items/{order}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |
| `order` | `order` | `path` | yes | integer<int32><br>Represents an invoice item order. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `order`:**

```yaml
format: int32
minimum: 1
type: integer
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `invoices.items.order-path-param-typed-string`:** `order` binds to a Java `int`. `abc` returns `Failed to convert value of type 'java.lang.String' to required type 'int'` and `0` returns `must be greater than or equal to 1`. `compensated-in-corrected-spec`.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_items_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoice_items.import_items()` — `importInvoiceItems`

| Field | Reconciled value |
|---|---|
| Behavior | Import time entries and expenses to an invoice |
| HTTP | `POST /workspaces/{workspaceId}/invoices/{invoiceId}/items/import` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ImportInvoiceItemsRequest`](#schema-importinvoiceitemsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `invoices.items-unit-price-scale`:** `compensated` (2026-08-09). `clockify_invoices_items_add` scales the price, `mcp/tests/backlog-tools.test.ts` pins `15000 -> 1500000` plus the RangeError refusal above the exact-integer envelope, and the repaired tripwire reds if a future item-add site drops the call.
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_items_import_items`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `invoice_payments`

### `invoice_payments.create()` — `addInvoicePayment`

| Field | Reconciled value |
|---|---|
| Behavior | Add payment to an invoice |
| HTTP | `POST /workspaces/{workspaceId}/invoices/{invoiceId}/payments` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AddInvoicePaymentRequest`](#schema-addinvoicepaymentrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `invoices.payments.post-returns-invoice`:** the POST returns **`201` with the updated INVOICE document** (`InvoiceDtoFull`: `balance`/`clientId`/`number`/`status`/…), NOT the created payment. To recover the new payment id, GET `…/payments` before and after the POST and take the new id by set-difference (list items carry `id`/`amount`/`author`/`date`/`note`). Field-name asymmetry: the request body uses **`paymentDate`** (RFC3339, non-millisecond) while the payments-list item uses **`date`**; `amount` is an int64 in **minor units** (`minimum: 1`). `compensated-in-corrected-spec` (2026-06-22; tool-side list-diff recovery landed 2026-08-09). `x-clockify-live-status` stays `probe-documen…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_payments_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoice_payments.delete()` — `deleteInvoicePayment`

| Field | Reconciled value |
|---|---|
| Behavior | Delete payment from an invoice |
| HTTP | `DELETE /workspaces/{workspaceId}/invoices/{invoiceId}/payments/{paymentId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |
| `payment_id` | `paymentId` | `path` | yes | string<br>Represents a payment identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `paymentId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_payments_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoice_payments.list()` — `getInvoicePayments`

| Field | Reconciled value |
|---|---|
| Behavior | Get payments for an invoice |
| HTTP | `GET /workspaces/{workspaceId}/invoices/{invoiceId}/payments` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`InvoicePaymentDto`](#schema-invoicepaymentdto)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/InvoicePaymentDto'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_payments_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `invoice_settings`

### `invoice_settings.get()` — `getInvoiceSettings`

| Field | Reconciled value |
|---|---|
| Behavior | Get invoice settings |
| HTTP | `GET /workspaces/{workspaceId}/invoices/settings` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceSettingsResponse`](#schema-invoicesettingsresponse) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_settings_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoice_settings.update()` — `updateInvoiceSettings`

| Field | Reconciled value |
|---|---|
| Behavior | Change an invoice language |
| HTTP | `PUT /workspaces/{workspaceId}/invoices/settings` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`InvoiceSettingsRequest`](#schema-invoicesettingsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoice_settings_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`workspace-wide configuration`; sensitivity=`financial`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `invoices`

### `invoices.create()` — `addInvoice`

| Field | Reconciled value |
|---|---|
| Behavior | Add an invoice |
| HTTP | `POST /workspaces/{workspaceId}/invoices` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`InvoiceCreateRequest`](#schema-invoicecreaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`InvoiceCreateResponse`](#schema-invoicecreateresponse) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `invoices.create.note-subject-dropped`:** POST accepts ONLY `CreateInvoiceRequest` fields (clientId/currency/dueDate/issuedDate/number); `note`/`subject` are **silently dropped** — POST + a follow-up GET both echo the workspace placeholder ("INPUT BILL INFO HERE"), never the supplied text. `compensated-in-tool-layer` (fail closed). `clockify_invoices_create` rejects note/subject during guarded preview, issues no token, and directs the caller to create the draft first and then use guarded `clockify_invoices_update`. This keeps execution bound to the exact stored create request instead of building an unpreviewable replacement request around a future invoice ID. - Re-verified 2026-06…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoices.delete()` — `deleteInvoice`

| Field | Reconciled value |
|---|---|
| Behavior | Delete an invoice |
| HTTP | `DELETE /workspaces/{workspaceId}/invoices/{invoiceId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoices.duplicate()` — `duplicateInvoice`

| Field | Reconciled value |
|---|---|
| Behavior | Duplicate an invoice |
| HTTP | `POST /workspaces/{workspaceId}/invoices/{invoiceId}/duplicate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_duplicate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`action`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoices.export()` — `exportInvoice`

| Field | Reconciled value |
|---|---|
| Behavior | Export an invoice |
| HTTP | `GET /workspaces/{workspaceId}/invoices/{invoiceId}/export` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |
| `user_locale` | `userLocale` | `query` | yes | string<br>Required by live Clockify invoice export; the MCP defaults it to en-US. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `*/*` | `bytes` | string<byte> | string |
| `200` | `application/octet-stream` | `bytes` | string<binary> | string |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter query `userLocale`:**

```yaml
type: string
default: en-US
```

**response `200` `*/*`:**

```yaml
format: byte
type: string
```

**response `200` `application/octet-stream`:**

```yaml
format: binary
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_export`.
- Eligibility: **SDK-ONLY (binary response)**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- **UNRESOLVED:** Binary payload has no context-safe raw MCP representation in v1; keep it SDK-only unless a bounded resource/download contract is designed.

### `invoices.filter()` — `filterInvoices`

| Field | Reconciled value |
|---|---|
| Behavior | Filter out invoices |
| HTTP | `POST /workspaces/{workspaceId}/invoices/info` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`InvoiceFilterRequest`](#schema-invoicefilterrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceInfoListResponse`](#schema-invoiceinfolistresponse) | object envelope; item arrays: `invoices` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_filter`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoices.get()` — `getInvoiceById`

| Field | Reconciled value |
|---|---|
| Behavior | Get an invoice by ID |
| HTTP | `GET /workspaces/{workspaceId}/invoices/{invoiceId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoices.list()` — `getWorkspaceInvoices`

| Field | Reconciled value |
|---|---|
| Behavior | Get all invoices on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/invoices` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `statuses` | `statuses` | `query` | no | array[[`InvoiceStatus`](#schema-invoicestatus)]<br>Filter invoices by one or more invoice statuses. | repeated query key |
| `sort_column` | `sort-column` | `query` | no | [`InvoiceSortColumn`](#schema-invoicesortcolumn)<br>Valid column name as sorting criteria. Default: ID. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | [`InvoicesSortOrder`](#schema-invoicessortorder)<br>Sort order. Default: ASCENDING. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceListResponse`](#schema-invoicelistresponse) | object envelope; item arrays: `invoices` |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; object envelope; item arrays: `invoices`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `statuses`:**

```yaml
items:
  $ref: '#/components/schemas/InvoiceStatus'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoices.update()` — `updateInvoice`

| Field | Reconciled value |
|---|---|
| Behavior | Update an invoice |
| HTTP | `PUT /workspaces/{workspaceId}/invoices/{invoiceId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateInvoiceRequest`](#schema-updateinvoicerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`InvoiceDtoFull`](#schema-invoicedtofull) | object envelope; item arrays: `items`, `visibleZeroFields` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** replacement update; omitted tax/discount fields can be zeroed.
- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `invoices.update.missing-bill-from-and-client-address`:** `fixed-in-canonical-source`. This was first recorded as pending in downstream ledger commit `90fefb7`. GOCLMCP test commit `b6d4560` locked both fields as optional strings and preserved the exact pre-existing required set; source commit `a4e72bb` corrected the update schema and examples, refreshed the manifest, and regenerated the green canonical document. The downstream byte-for-byte copy has SHA-256 `0a1eeb34f6f8e7693b92d3edfb5841e512e6fa1b402b3ea49c82be70fd5565e7`; `make sdk-codegen` regenerated the request type and docs. Runtime GET-then-PUT preservation remains necessary for replacement semantics.
- **FACT — `invoices.update.replace-and-tax-discount-zeroing`:** the PUT **replaces** the whole document — a sparse body drops every omitted field (note, subject, billFrom, clientAddress, …). AND tax/discount are asymmetric: the GET returns `discount`/`tax`/`tax2` as ×100-scaled integers (10% reads back as `1000`), but the PUT body wants `discountPercent`/`taxPercent`/`tax2Percent` as plain percents. Copying the GET names verbatim **silently ZEROES** tax/discount on every update. goclmcp (this repo's spec source) inherits the bug. `compensated-in-tool-layer`. Shipped here as the pure wrapper helper `wrapper/invoice-body.ts` (`invoiceUpdateBodyFromExisting` — editable whitelist + name+scale ÷100 map) con…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `invoices.update_status()` — `changeInvoiceStatus`

| Field | Reconciled value |
|---|---|
| Behavior | Change an invoice status |
| HTTP | `PATCH /workspaces/{workspaceId}/invoices/{invoiceId}/status` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `invoice_id` | `invoiceId` | `path` | yes | string<br>Represents an invoice identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`InvoiceStatusRequest`](#schema-invoicestatusrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `invoiceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Invoice item unitPrice is minor units x100 (hundredths of a cent); amount = unitPrice * quantity / 100.
- **FACT — wire units:** Invoice tax/tax2/discount read back as percent x100 floats; PUT takes taxPercent/tax2Percent/discountPercent as plain percents.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_invoices_update_status`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`transition`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `member_profiles`

### `member_profiles.get()` — `getMemberProfile`

| Field | Reconciled value |
|---|---|
| Behavior | Get a member's profile |
| HTTP | `GET /workspaces/{workspaceId}/member-profile/{userId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`MemberProfileDtoV1`](#schema-memberprofiledtov1) | object envelope; item arrays: `userCustomFieldValues`, `workingDays` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_member_profiles_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `member_profiles.update()` — `updateMemberProfile`

| Field | Reconciled value |
|---|---|
| Behavior | Update a member's profile |
| HTTP | `PATCH /workspaces/{workspaceId}/member-profile/{userId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`MemberProfileUpdateRequest`](#schema-memberprofileupdaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`MemberProfileDtoV1`](#schema-memberprofiledtov1) | object envelope; item arrays: `userCustomFieldValues`, `workingDays` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_member_profiles_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `projects`

### `projects.create()` — `createProject`

| Field | Reconciled value |
|---|---|
| Behavior | Add a new project |
| HTTP | `POST /workspaces/{workspaceId}/projects` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateProjectRequest`](#schema-createprojectrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `entity.name-reserved-after-delete.cross-repo-2026-06-09`:** a project / tag / client NAME stays reserved even after the entity is archived and then deleted. Re-creating with the same name returns `... with this name already exists` (e.g. `"Project with this name already exists"`) even though the name no longer appears in any list — so a "list, then reuse the name" recovery never surfaces it. The only fix is a distinct name. `documented; ts-side-hint-pending`. Recommend the TS MCP `clockify_*_create` tools (and the SDK `create` docstrings) warn that a previously deleted name may report "already exists" and to retry with a distinct name. No spec change — a platform behavior, not a shape divergence.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.create_from_template()` — `createProjectFromTemplate`

| Field | Reconciled value |
|---|---|
| Behavior | Create project from a template |
| HTTP | `POST /workspaces/{workspaceId}/projects/from-template` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateProjectFromTemplateRequest`](#schema-createprojectfromtemplaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_create_from_template`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.delete()` — `deleteProject`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a project from a workspace |
| HTTP | `DELETE /workspaces/{workspaceId}/projects/{projectId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** archive or complete before delete.
- **FACT — lifecycle:** project must be archived; task must be DONE before delete.
- **FACT — `deletes.archive-first`:** Clockify rejects DELETE of an ACTIVE entity. Projects/clients/expense-categories must be archived first; tasks marked DONE first. `compensated-in-tool-layer` for expense categories (2026-06-14) — `clockify_expenses_categories_delete` now `expenseCategories.archive({archived:true})` (the dedicated PATCH `/status`, no replace risk) before delete. Test: `mcp/tests/sweep-fixes.test.ts`. Projects/tasks compensated 2026-06-15 and clients 2026-06-17 (see the sub-entries below) — each archives via GET-then-PUT (carry the entity's fields, overlay `archived:true`/`status:"DONE"`) then DELETE, because their archive is a **replace-PUT** (`*.update`) w…
- **FACT — `deletes.archive-first.projects-tasks`:** `compensated-in-tool-layer` (2026-06-15). `clockify_projects_delete` and `clockify_tasks_delete` GET-then-PUT (archive / DONE) before DELETE, after the confirm gate. Verified LIVE end-to-end through the real MCP tools (dry_run → confirm_token → execute): both returned `deleted:true` against a real active project + task. Order pinned by `mcp/tests/archive-then-delete.test.ts`.
- **FACT — `projects.get.deleted-returns-400-not-404`:** reading a deleted project returns **400** with `{"message":"Project doesn't belong to Workspace","code":501}` — never 404. A never-existing id returns the byte-identical body, so the wire cannot distinguish "deleted" from "never existed" or from "belongs to another workspace". `compensated-in-sdk`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.get()` — `getProjectById`

| Field | Reconciled value |
|---|---|
| Behavior | Find a project by ID |
| HTTP | `GET /workspaces/{workspaceId}/projects/{projectId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `hydrated` | `hydrated` | `query` | no | boolean<br>If true, results contain additional information about the project. | single query value; omit only when `None` |
| `custom_field_entity_type` | `custom-field-entity-type` | `query` | no | string<br>Filters custom fields by custom field entity type. | single query value; omit only when `None` |
| `expense_limit` | `expense-limit` | `query` | no | integer<int32><br>Represents the maximum number of expenses to fetch. | single query value; omit only when `None` |
| `expense_date` | `expense-date` | `query` | no | string<date><br>If provided, returns expenses dated before the provided yyyy-MM-dd date. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

**parameter query `hydrated`:**

```yaml
default: false
type: boolean
```

**parameter query `custom-field-entity-type`:**

```yaml
default: TIMEENTRY
type: string
```

**parameter query `expense-limit`:**

```yaml
default: 20
format: int32
type: integer
```

**parameter query `expense-date`:**

```yaml
format: date
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `projects.get.deleted-returns-400-not-404`:** reading a deleted project returns **400** with `{"message":"Project doesn't belong to Workspace","code":501}` — never 404. A never-existing id returns the byte-identical body, so the wire cannot distinguish "deleted" from "never existed" or from "belongs to another workspace". `compensated-in-sdk`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.list()` — `getWorkspaceProjects`

| Field | Reconciled value |
|---|---|
| Behavior | Get all projects on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/projects` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `name` | `name` | `query` | no | string<br>If provided, returns projects whose name contains the provided string. | single query value; omit only when `None` |
| `strict_name_search` | `strict-name-search` | `query` | no | boolean<br>When true, search by name returns only projects whose name exactly matches the name parameter. | single query value; omit only when `None` |
| `archived` | `archived` | `query` | no | boolean<br>If true, returns only archived projects. If omitted, returns both archived and non-archived projects. | single query value; omit only when `None` |
| `billable` | `billable` | `query` | no | boolean<br>If true, returns only billable projects. If omitted, returns both billable and non-billable projects. | single query value; omit only when `None` |
| `clients` | `clients` | `query` | no | array[string]<br>If provided, returns projects that contain clients matching any provided ids. | repeated query key |
| `contains_client` | `contains-client` | `query` | no | boolean<br>Controls whether the clients filter includes or excludes matching client ids. | single query value; omit only when `None` |
| `client_status` | `client-status` | `query` | no | string enum["ACTIVE", "ARCHIVED", "ALL"]<br>Filters projects based on client status. | single query value; omit only when `None` |
| `users` | `users` | `query` | no | array[string]<br>If provided, returns projects that contain users matching any provided ids. | repeated query key |
| `contains_user` | `contains-user` | `query` | no | boolean<br>Controls whether the users filter includes or excludes matching user ids. | single query value; omit only when `None` |
| `user_status` | `user-status` | `query` | no | string enum["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]<br>Filters projects based on user status. | single query value; omit only when `None` |
| `is_template` | `is-template` | `query` | no | boolean<br>Filters projects based on whether they are used as a template or not. | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | string enum["ID", "NAME", "CLIENT_NAME", "DURATION", "BUDGET", "PROGRESS"]<br>Sorts the results by the given column/field. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"]<br>Sorting mode. | single query value; omit only when `None` |
| `hydrated` | `hydrated` | `query` | no | boolean<br>If true, results contain additional information about the project. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `access` | `access` | `query` | no | string enum["PUBLIC", "PRIVATE"]<br>If provided, returns projects that match the provided access. | single query value; omit only when `None` |
| `expense_limit` | `expense-limit` | `query` | no | integer<int32><br>Represents the maximum number of expenses to fetch. | single query value; omit only when `None` |
| `expense_date` | `expense-date` | `query` | no | string<date><br>If provided, returns expenses dated before the provided yyyy-MM-dd date. | single query value; omit only when `None` |
| `user_groups` | `userGroups` | `query` | no | array[string]<br>If provided, returns projects that contain groups matching any provided ids. | repeated query key |
| `contains_group` | `contains-group` | `query` | no | boolean<br>Controls whether the userGroups filter includes or excludes matching group ids. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`Project`](#schema-project)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `name`:**

```yaml
type: string
```

**parameter query `strict-name-search`:**

```yaml
default: false
type: boolean
```

**parameter query `archived`:**

```yaml
default: false
type: boolean
```

**parameter query `billable`:**

```yaml
default: false
type: boolean
```

**parameter query `clients`:**

```yaml
items:
  type: string
type: array
uniqueItems: true
```

**parameter query `contains-client`:**

```yaml
default: true
type: boolean
```

**parameter query `client-status`:**

```yaml
enum:
- ACTIVE
- ARCHIVED
- ALL
type: string
```

**parameter query `users`:**

```yaml
items:
  type: string
type: array
uniqueItems: true
```

**parameter query `contains-user`:**

```yaml
default: true
type: boolean
```

**parameter query `user-status`:**

```yaml
enum:
- PENDING
- ACTIVE
- DECLINED
- INACTIVE
- ALL
type: string
```

**parameter query `is-template`:**

```yaml
default: false
type: boolean
```

**parameter query `sort-column`:**

```yaml
enum:
- ID
- NAME
- CLIENT_NAME
- DURATION
- BUDGET
- PROGRESS
type: string
```

**parameter query `sort-order`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**parameter query `hydrated`:**

```yaml
default: false
type: boolean
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `access`:**

```yaml
enum:
- PUBLIC
- PRIVATE
type: string
```

**parameter query `expense-limit`:**

```yaml
default: 20
format: int32
type: integer
```

**parameter query `expense-date`:**

```yaml
format: date
type: string
```

**parameter query `userGroups`:**

```yaml
items:
  type: string
type: array
uniqueItems: true
```

**parameter query `contains-group`:**

```yaml
default: true
type: boolean
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/Project'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `list.archived-default-returns-both`:** omitting `archived` returns archived **and** active rows. Only `archived=false` restricts the result to active rows. `documented`.
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.set_members()` — `assignOrRemoveProjectUsers`

| Field | Reconciled value |
|---|---|
| Behavior | Assign/remove users to/from the project |
| HTTP | `POST /workspaces/{workspaceId}/projects/{projectId}/memberships` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AssignRemoveUsersRequest`](#schema-assignremoveusersrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_set_members`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`multi-entity`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.update()` — `updateProject`

| Field | Reconciled value |
|---|---|
| Behavior | Update a project on a workspace |
| HTTP | `PUT /workspaces/{workspaceId}/projects/{projectId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateProjectRequest`](#schema-updateprojectrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** mixed omission behavior; billable/public can reset while other fields may persist.
- **FACT/INFERENCE — replacement risk:** mixed and unresolved.
- **FACT — `fern.sdk.clients-update-body-vs-projects-update-top-level`:** Clockify accepts client archive updates only with the nested client body shape (`body: { name, archived: true }`). Sending client update fields at the top level returns "Required request body is missing". Project archive updates, by contrast, accept the generated top-level project fields (`{ name, archived: true }`) and do not use a nested `body` wrapper in the generated SDK surface. The `archive` helper routes for both clients and projects returned 404 in this live cleanup path, so archive+delete cleanup must use the update methods first. accepted local SDK shape split. Keep client update fields nested under `body`; keep project update fi…
- **FACT — `project.update.omitted-field-semantics-unconfirmed`:** `compensated-in-surfaces`; CLI `projects update` and the MCP project-update/delete paths now GET the current project and carry `billable` plus GET-side `public` back as request-side `isPublic` before every metadata/archive PUT. PROJECT-001/P02-11's offline-tested, credential- and sacrificial-workspace-gated probe harness was corrected to compare `isPublic` against `public` and to include `billable`: (`scripts/live/project-update-omission-probe.mjs`, `scripts/live/project-update-omission-probe.test.mjs`) implementing the exact create → hydrate → minimal-update → re-fetch → compare → archive-then-delete sequence and producing a boolean-only,…
- **FACT — `projects.update.rate-omission-preserves-rates`:** **omission preserves both rates.** This is the same keep-under-omission family as the client currency, not the clearing family. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`mixed and unresolved`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** Project PUT omission semantics are only partially observed; do not build a sparse-update helper or MCP execution path that assumes preservation.

### `projects.update_estimate()` — `updateProjectEstimate`

| Field | Reconciled value |
|---|---|
| Behavior | Update project estimate |
| HTTP | `PATCH /workspaces/{workspaceId}/projects/{projectId}/estimate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateProjectEstimateRequest`](#schema-updateprojectestimaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_update_estimate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.update_memberships()` — `updateProjectMemberships`

| Field | Reconciled value |
|---|---|
| Behavior | Update project memberships |
| HTTP | `PATCH /workspaces/{workspaceId}/projects/{projectId}/memberships` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateProjectMembershipsRequest`](#schema-updateprojectmembershipsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_update_memberships`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`multi-entity`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.update_template()` — `updateProjectTemplate`

| Field | Reconciled value |
|---|---|
| Behavior | Update a project template |
| HTTP | `PATCH /workspaces/{workspaceId}/projects/{projectId}/template` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateProjectTemplateRequest`](#schema-updateprojecttemplaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_update_template`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`transition`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `projects.update_user_cost_rate()` — `updateProjectUserCostRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update project user's cost rate |
| HTTP | `PUT /workspaces/{workspaceId}/projects/{projectId}/users/{userId}/cost-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`RateRequest`](#schema-raterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `rates.put-minor-units-no-get`:** rates are PUTs of an integer **minor-unit** `{amount}` body; **GET on a rate path 405s** (discover the current value from a membership/project doc). Per-scope endpoints: per-project member `…/projects/{p}/users/{u}/{hourly-rate|cost-rate}`; Team-section workspace member `…/users/{u}/{hourly-rate|cost-rate}`; task `…/projects/{p}/tasks/{t}/{cost-rate|hourly-rate}`. The project **default** rate has NO standalone endpoint in the addon's experience — it set `hourlyRate`/`costRate` in the project create/update BODY. `compensated-in-tool-layer` for the LIVE-VERIFIED member/task rates (2026-06-14); the project-DEFAULT rate stays `open`. Shipped t…
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_update_user_cost_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `projects.update_user_hourly_rate()` — `updateProjectUserHourlyRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update a project user's billable rate |
| HTTP | `PUT /workspaces/{workspaceId}/projects/{projectId}/users/{userId}/hourly-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`RateRequest`](#schema-raterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Project`](#schema-project) | object envelope; item arrays: `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `rates.put-minor-units-no-get`:** rates are PUTs of an integer **minor-unit** `{amount}` body; **GET on a rate path 405s** (discover the current value from a membership/project doc). Per-scope endpoints: per-project member `…/projects/{p}/users/{u}/{hourly-rate|cost-rate}`; Team-section workspace member `…/users/{u}/{hourly-rate|cost-rate}`; task `…/projects/{p}/tasks/{t}/{cost-rate|hourly-rate}`. The project **default** rate has NO standalone endpoint in the addon's experience — it set `hourlyRate`/`costRate` in the project create/update BODY. `compensated-in-tool-layer` for the LIVE-VERIFIED member/task rates (2026-06-14); the project-DEFAULT rate stays `open`. Shipped t…
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_projects_update_user_hourly_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `reports`

### `reports.attendance()` — `generateAttendanceReport`

| Field | Reconciled value |
|---|---|
| Behavior | Generate an attendance report |
| HTTP | `POST /workspaces/{workspaceId}/reports/attendance` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AttendanceReportRequest`](#schema-attendancereportrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`AttendanceReportResponse`](#schema-attendancereportresponse) | object envelope; item arrays: `entities` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `reports.date-range.evaluated-as-wall-clock-in-request-timezone`:** the reports host applies the same wall-clock rule to `dateRangeStart`/`dateRangeEnd`, and here the timezone is **selectable per request** through the body's `timeZone` field. `timeZone: "UTC"` restores the literal reading. `documented`.
- **FACT — `reports.response.timestamps-rendered-in-request-timezone`:** the two hosts render the same instant differently. The core host returns `timeInterval.start` as UTC with a `Z`; the reports host returns it as a local offset in the request's `timeZone`. The calendar date can differ. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_reports_attendance`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `reports.detailed()` — `generateDetailedReport`

| Field | Reconciled value |
|---|---|
| Behavior | Generate a detailed report |
| HTTP | `POST /workspaces/{workspaceId}/reports/detailed` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`DetailedReportRequest`](#schema-detailedreportrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`DetailedReportResponse`](#schema-detailedreportresponse) | object envelope; item arrays: `timeEntries`, `timeentries`, `totals` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `reports.date-range.evaluated-as-wall-clock-in-request-timezone`:** the reports host applies the same wall-clock rule to `dateRangeStart`/`dateRangeEnd`, and here the timezone is **selectable per request** through the body's `timeZone` field. `timeZone: "UTC"` restores the literal reading. `documented`.
- **FACT — `reports.response.timestamps-rendered-in-request-timezone`:** the two hosts render the same instant differently. The core host returns `timeInterval.start` as UTC with a `Z`; the reports host returns it as a local offset in the request's `timeZone`. The calendar date can differ. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_reports_detailed`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `reports.expense_details()` — `generateDetailedReportV1`

| Field | Reconciled value |
|---|---|
| Behavior | Generate an expense report |
| HTTP | `POST /workspaces/{workspaceId}/reports/expenses/detailed` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **no**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ExpenseReportFilterV1`](#schema-expensereportfilterv1) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ExpenseDetailedReportDtoV1`](#schema-expensedetailedreportdtov1) | object envelope; item arrays: `expenses` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents a workspace identifier across the system.
example: 60f91b3ffdaf031696ec6bbb
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `reports.date-range.evaluated-as-wall-clock-in-request-timezone`:** the reports host applies the same wall-clock rule to `dateRangeStart`/`dateRangeEnd`, and here the timezone is **selectable per request** through the body's `timeZone` field. `timeZone: "UTC"` restores the literal reading. `documented`.
- **FACT — `reports.response.timestamps-rendered-in-request-timezone`:** the two hosts render the same instant differently. The core host returns `timeInterval.start` as UTC with a `Z`; the reports host returns it as a local offset in the request's `timeZone`. The calendar date can differ. `documented`.
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.
- **FACT — wire units:** Expense amount and total fields preserve upstream scaling observed in live probes.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_reports_expense_details`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`.
- No operation-specific unresolved item blocks the raw SDK method.

### `reports.summary()` — `generateSummaryReport`

| Field | Reconciled value |
|---|---|
| Behavior | Generate a summary report |
| HTTP | `POST /workspaces/{workspaceId}/reports/summary` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`SummaryReportRequest`](#schema-summaryreportrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`SummaryReportResponse`](#schema-summaryreportresponse) | object envelope; item arrays: `groupOne`, `totals`, `donutChart` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `reports.date-range.evaluated-as-wall-clock-in-request-timezone`:** the reports host applies the same wall-clock rule to `dateRangeStart`/`dateRangeEnd`, and here the timezone is **selectable per request** through the body's `timeZone` field. `timeZone: "UTC"` restores the literal reading. `documented`.
- **FACT — `reports.response.timestamps-rendered-in-request-timezone`:** the two hosts render the same instant differently. The core host returns `timeInterval.start` as UTC with a `Z`; the reports host returns it as a local offset in the request's `timeZone`. The calendar date can differ. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_reports_summary`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `reports.weekly()` — `generateWeeklyReport`

| Field | Reconciled value |
|---|---|
| Behavior | Generate a weekly report |
| HTTP | `POST /workspaces/{workspaceId}/reports/weekly` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`WeeklyReportRequest`](#schema-weeklyreportrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`WeeklyReportResponse`](#schema-weeklyreportresponse) | object envelope; item arrays: `groupOne`, `totals`, `totalsByDay`, `usersWithoutTime` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** weekly report requires an exact seven-day interval.
- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `reports.date-range.evaluated-as-wall-clock-in-request-timezone`:** the reports host applies the same wall-clock rule to `dateRangeStart`/`dateRangeEnd`, and here the timezone is **selectable per request** through the body's `timeZone` field. `timeZone: "UTC"` restores the literal reading. `documented`.
- **FACT — `reports.response.timestamps-rendered-in-request-timezone`:** the two hosts render the same instant differently. The core host returns `timeInterval.start` as UTC with a `Z`; the reports host returns it as a local offset in the request's `timeZone`. The calendar date can differ. `documented`.
- **FACT — evidence anchor:** `reports.weekly.exact-seven-day-window` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_reports_weekly`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `scheduling`

### `scheduling.change_recurring_period()` — `changeRecurringPeriod`

| Field | Reconciled value |
|---|---|
| Behavior | Change the recurring period |
| HTTP | `PUT /workspaces/{workspaceId}/scheduling/assignments/series/{assignmentId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `assignment_id` | `assignmentId` | `path` | yes | string<br>Represents an assignment identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ChangeRecurringPeriodRequest`](#schema-changerecurringperiodrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`SchedulingAssignment`](#schema-schedulingassignment)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `assignmentId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/SchedulingAssignment'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_change_recurring_period`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `scheduling.copy_assignment()` — `copyScheduledAssignment`

| Field | Reconciled value |
|---|---|
| Behavior | Copy a scheduled assignment |
| HTTP | `POST /workspaces/{workspaceId}/scheduling/assignments/{assignmentId}/copy` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `assignment_id` | `assignmentId` | `path` | yes | string<br>Represents an assignment identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CopyAssignmentRequest`](#schema-copyassignmentrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`SchedulingAssignment`](#schema-schedulingassignment)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `assignmentId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/SchedulingAssignment'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_copy_assignment`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.create_recurring()` — `createRecurringAssignment`

| Field | Reconciled value |
|---|---|
| Behavior | Create a recurring assignment |
| HTTP | `POST /workspaces/{workspaceId}/scheduling/assignments/recurring` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateRecurringAssignmentRequest`](#schema-createrecurringassignmentrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | array[[`SchedulingAssignment`](#schema-schedulingassignment)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**response `201` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/SchedulingAssignment'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `scheduling.createRecurring.returns-array-and-publish-is-range-scoped`:** `POST /scheduling/assignments/recurring` (`scheduling.createRecurring`, the live assignment-create path that replaced the dead `POST /scheduling/assignments`) returns a **201 array** of `SchedulingAssignment` — one entry per occurrence; a one-off has a single element — NOT a single object. The generated SDK types it `Promise<SchedulingAssignment[]>`. Callers must read element `[0]` for the created-entity id: `clk115 scheduling create`, `clockify_scheduling_assignments_create`, and the `clockify_schedule_work` workflow all do (the receipt `changed.created` id comes from the first element). A regression that read the id off the bare array pr…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_create_recurring`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.delete_recurring()` — `deleteRecurringAssignment`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a recurring assignment |
| HTTP | `DELETE /workspaces/{workspaceId}/scheduling/assignments/recurring/{assignmentId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `assignment_id` | `assignmentId` | `path` | yes | string<br>Represents an assignment identifier across the system. | path segment; percent-encode once |
| `series_update_option` | `seriesUpdateOption` | `query` | no | [`SeriesUpdateOption`](#schema-seriesupdateoption)<br>Represents a series option. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`SchedulingAssignment`](#schema-schedulingassignment)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `assignmentId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/SchedulingAssignment'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_delete_recurring`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.get_filtered_user_capacity()` — `getUsersCapacityTotals`

| Field | Reconciled value |
|---|---|
| Behavior | Get total of users' capacity on workspace |
| HTTP | `POST /workspaces/{workspaceId}/scheduling/assignments/user-filter/totals` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UserCapacityTotalsRequest`](#schema-usercapacitytotalsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`UserCapacityTotal`](#schema-usercapacitytotal)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/UserCapacityTotal'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_get_filtered_user_capacity`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.get_project_totals()` — `getScheduledAssignmentsOnProject`

| Field | Reconciled value |
|---|---|
| Behavior | Get all scheduled assignments on project |
| HTTP | `GET /workspaces/{workspaceId}/scheduling/assignments/projects/totals/{projectId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `start` | `start` | `query` | yes | string<date-time><br>Required by live Clockify; the single-project schedule-totals GET 400s without an ISO-8601 start. | single query value; omit only when `None` |
| `end` | `end` | `query` | yes | string<date-time><br>Required by live Clockify; the single-project schedule-totals GET 400s without an ISO-8601 end. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`ProjectAssignmentsTotal`](#schema-projectassignmentstotal) | object envelope; item arrays: `assignments`, `milestones` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `projectId`:**

```yaml
type: string
```

**parameter query `start`:**

```yaml
type: string
format: date-time
```

**parameter query `end`:**

```yaml
type: string
format: date-time
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `scheduling.list-per-project.start-end-required-camel-pagesize`:** the all-projects totals search **POST** `…/scheduling/assignments/projects/totals` requires `start` AND `end` in the body and reads only the **camel** `pageSize` off its whitelist. Probe matrix (sandbox WS): - omit `start`/`end` → **400** (start+end REQUIRED). - `start`+`end` + camel `pageSize` → **200** returning a real `ProjectAssignmentsTotal[]` (a 2-item page honored). - `start`+`end` + kebab `page-size` → **200** but **21 items** — the kebab key is silently IGNORED (page size not applied), confirming the body whitelist `["end","page","pageSize","search","start","statusFilter"]` (camel only). `compensated-in-tool-layer` (2026-06-18). `…
- **FACT — `scheduling.project-totals.get-vs-post`:** a single project's schedule totals live at **GET** `…/scheduling/assignments/projects/totals/{projectId}?start&end`. The all-projects search is a **POST** whose body has NO `projectId` field — sending one was silently dropped and returned ALL projects. `compensated-in-tool-layer` (2026-06-14). `clockify_scheduling_assignments_list_per_project` now takes an optional `projectId` and routes to the single-project GET (`scheduling.listOnProject`); without it, the all-projects POST (`listPerProject`). Tests: `mcp/tests/scheduling-totals.test.ts`. Port from addon `src/clockify/rest/scheduling.ts:102-120`. - Re-verified 2026-06-20: confirmed-still…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_get_project_totals`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.get_user_capacity()` — `getUserCapacityTotal`

| Field | Reconciled value |
|---|---|
| Behavior | Get total capacity of a user |
| HTTP | `GET /workspaces/{workspaceId}/scheduling/assignments/users/{userId}/totals` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `start` | `start` | `query` | yes | string<date-time><br>Represents a start date in the yyyy-MM-ddThh:mm:ssZ format. | single query value; omit only when `None` |
| `end` | `end` | `query` | yes | string<date-time><br>Represents an end date in the yyyy-MM-ddThh:mm:ssZ format. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`UserCapacityTotal`](#schema-usercapacitytotal) | object envelope; item arrays: `totalHoursPerDay` |

**Pagination:** page=`page`; page size=`page-size`; object envelope; item arrays: `totalHoursPerDay`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `start`:**

```yaml
format: date-time
type: string
```

**parameter query `end`:**

```yaml
format: date-time
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_get_user_capacity`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.list_assignments()` — `getAllSchedulingAssignments`

| Field | Reconciled value |
|---|---|
| Behavior | Get all assignments |
| HTTP | `GET /workspaces/{workspaceId}/scheduling/assignments/all` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `name` | `name` | `query` | no | string<br>If provided, assignments will be filtered by name. | single query value; omit only when `None` |
| `start` | `start` | `query` | yes | string<date-time><br>Represents a start date in the yyyy-MM-ddThh:mm:ssZ format. | single query value; omit only when `None` |
| `end` | `end` | `query` | yes | string<date-time><br>Represents an end date in the yyyy-MM-ddThh:mm:ssZ format. | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | [`AssignmentSortColumn`](#schema-assignmentsortcolumn)<br>Represents the column as the sorting criteria. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | [`SortOrder`](#schema-sortorder)<br>Represents the sorting mode. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`AssignmentListItem`](#schema-assignmentlistitem)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `name`:**

```yaml
default: ''
type: string
```

**parameter query `start`:**

```yaml
format: date-time
type: string
```

**parameter query `end`:**

```yaml
format: date-time
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/AssignmentListItem'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_list_assignments`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.list_project_totals()` — `getScheduledAssignmentsPerProject`

| Field | Reconciled value |
|---|---|
| Behavior | Get all scheduled assignments per project |
| HTTP | `POST /workspaces/{workspaceId}/scheduling/assignments/projects/totals` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ProjectTotalsRequest`](#schema-projecttotalsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`ProjectAssignmentsTotal`](#schema-projectassignmentstotal)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/ProjectAssignmentsTotal'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `scheduling.list-per-project.start-end-required-camel-pagesize`:** the all-projects totals search **POST** `…/scheduling/assignments/projects/totals` requires `start` AND `end` in the body and reads only the **camel** `pageSize` off its whitelist. Probe matrix (sandbox WS): - omit `start`/`end` → **400** (start+end REQUIRED). - `start`+`end` + camel `pageSize` → **200** returning a real `ProjectAssignmentsTotal[]` (a 2-item page honored). - `start`+`end` + kebab `page-size` → **200** but **21 items** — the kebab key is silently IGNORED (page size not applied), confirming the body whitelist `["end","page","pageSize","search","start","statusFilter"]` (camel only). `compensated-in-tool-layer` (2026-06-18). `…
- **FACT — `scheduling.project-totals.get-vs-post`:** a single project's schedule totals live at **GET** `…/scheduling/assignments/projects/totals/{projectId}?start&end`. The all-projects search is a **POST** whose body has NO `projectId` field — sending one was silently dropped and returned ALL projects. `compensated-in-tool-layer` (2026-06-14). `clockify_scheduling_assignments_list_per_project` now takes an optional `projectId` and routes to the single-project GET (`scheduling.listOnProject`); without it, the all-projects POST (`listPerProject`). Tests: `mcp/tests/scheduling-totals.test.ts`. Port from addon `src/clockify/rest/scheduling.ts:102-120`. - Re-verified 2026-06-20: confirmed-still…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_list_project_totals`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `scheduling.publish_assignments()` — `publishAssignments`

| Field | Reconciled value |
|---|---|
| Behavior | Publish assignments |
| HTTP | `PUT /workspaces/{workspaceId}/scheduling/assignments/publish` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`PublishAssignmentsRequest`](#schema-publishassignmentsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `fern-check.no-conflicting-endpoint-paths.literal-vs-id-siblings`:** - `GET /expenses/categories` → 200, 140 categories returned (probes/`20260524-expenses-categories-list.json`). - `GET /expenses/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Expense doesn't belong to Workspace` (probes/`20260524-expenses-id-not-found.json`). Server routed the 24-hex segment to the `{expenseId}` handler. - `GET /invoices/settings` → 200, settings payload (probes/`20260524-invoices-settings.json`). - `GET /invoices/aaaaaaaaaaaaaaaaaaaaaaaa` → 400, error code 501 `Invoice doesn't belong to Workspace` (probes/`20260524-invoices-id-not-found.json`). - `GET /scheduling/assignments/publish` → 405, `Request method 'GET' is not…
- **FACT — `routes.literal-vs-parameterized.collisions`:** `fixed-in-canonical-generator` with a residual Fern-noise caveat.
- **FACT — `scheduling.createRecurring.returns-array-and-publish-is-range-scoped`:** `POST /scheduling/assignments/recurring` (`scheduling.createRecurring`, the live assignment-create path that replaced the dead `POST /scheduling/assignments`) returns a **201 array** of `SchedulingAssignment` — one entry per occurrence; a one-off has a single element — NOT a single object. The generated SDK types it `Promise<SchedulingAssignment[]>`. Callers must read element `[0]` for the created-entity id: `clk115 scheduling create`, `clockify_scheduling_assignments_create`, and the `clockify_schedule_work` workflow all do (the receipt `changed.created` id comes from the first element). A regression that read the id off the bare array pr…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_publish_assignments`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`multi-entity`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `scheduling.update_recurring()` — `updateRecurringAssignment`

| Field | Reconciled value |
|---|---|
| Behavior | Update a recurring assignment |
| HTTP | `PATCH /workspaces/{workspaceId}/scheduling/assignments/recurring/{assignmentId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `assignment_id` | `assignmentId` | `path` | yes | string<br>Represents an assignment identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateRecurringAssignmentRequest`](#schema-updaterecurringassignmentrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`SchedulingAssignment`](#schema-schedulingassignment)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `assignmentId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/SchedulingAssignment'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_scheduling_update_recurring`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `shared_reports`

### `shared_reports.create()` — `postWorkspacesWorkspaceIdSharedReports`

| Field | Reconciled value |
|---|---|
| Behavior | Create shared report |
| HTTP | `POST /workspaces/{workspaceId}/shared-reports` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`SharedReportCreate`](#schema-sharedreportcreate) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`SharedReport`](#schema-sharedreport) | object envelope; item arrays: `visibleToUserGroups`, `visibleToUsers` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `shared-reports.create.success-code-201-vs-200`:** the corrected spec's winning source (`clockify-api-probe-lab/openapi.yaml`, which wins the generator's source-priority merge over AIII for any operation it defines) stamped the same operation `201`. This was a pure transcription defect, not a real wire discrepancy: `clockify-api-probe-lab/findings/shared-reports.md` already recorded **200** from two independent earlier live probes (2026-05-03 B.4 and a 2026-06-21 re-probe) — the YAML stamp had simply never been corrected to match its own evidence. `fixed-in-generator-source`. Corrected the response stamp in `../GOCLMCP/docs/openapi/sources/clockify-api-probe-lab/openapi.yaml`, updated the…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_shared_reports_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `shared_reports.delete()` — `deleteWorkspacesWorkspaceIdSharedReportsSharedReportId`

| Field | Reconciled value |
|---|---|
| Behavior | Delete shared report |
| HTTP | `DELETE /workspaces/{workspaceId}/shared-reports/{sharedReportId}` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `shared_report_id` | `sharedReportId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `204` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `sharedReportId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_shared_reports_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `shared_reports.list()` — `getWorkspacesWorkspaceIdSharedReports`

| Field | Reconciled value |
|---|---|
| Behavior | List shared reports |
| HTTP | `GET /workspaces/{workspaceId}/shared-reports` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer | single query value; omit only when `None` |
| `page_size` | `pageSize` | `query` | no | integer | single query value; omit only when `None` |
| `shared_reports_filter` | `sharedReportsFilter` | `query` | no | string enum["ALL", "ALL_ADMIN", "CREATED_BY_ME", "SHARED_WITH_ME"]<br>Filters shared reports by origin. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`SharedReportListEnvelope`](#schema-sharedreportlistenvelope) | object envelope; item arrays: `reports` |

**Pagination:** page=`page`; page size=`pageSize`; object envelope; item arrays: `reports`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter query `page`:**

```yaml
default: 1
minimum: 1
type: integer
```

**parameter query `pageSize`:**

```yaml
default: 50
minimum: 1
type: integer
```

**parameter query `sharedReportsFilter`:**

```yaml
default: ALL
enum:
- ALL
- ALL_ADMIN
- CREATED_BY_ME
- SHARED_WITH_ME
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `params.dropped-by-source-shadowing`:** `compensated-in-corrected-spec`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_shared_reports_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `shared_reports.update()` — `putWorkspacesWorkspaceIdSharedReportsSharedReportId`

| Field | Reconciled value |
|---|---|
| Behavior | Update shared report (merge semantics) |
| HTTP | `PUT /workspaces/{workspaceId}/shared-reports/{sharedReportId}` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `shared_report_id` | `sharedReportId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`SharedReportCreate`](#schema-sharedreportcreate) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`SharedReport`](#schema-sharedreport) | object envelope; item arrays: `visibleToUserGroups`, `visibleToUsers` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `sharedReportId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** documented merge semantics.
- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_shared_reports_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`documented merge semantics`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `shared_reports.view_public()` — `getSharedReportsSharedReportId`

| Field | Reconciled value |
|---|---|
| Behavior | Public/bare GET of a shared report or export |
| HTTP | `GET /shared-reports/{sharedReportId}` |
| Service | `REPORTS` · `https://reports.api.clockify.me/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `shared_report_id` | `sharedReportId` | `path` | yes | string | path segment; percent-encode once |
| `export_type` | `exportType` | `query` | no | string enum["JSON_V1", "JSON", "CSV", "XLSX", "PDF"] | single query value; omit only when `None` |
| `date_range_start` | `dateRangeStart` | `query` | no | string<br>Overrides the saved range start. `YYYY-MM-DDTHH:MM:SS`. | single query value; omit only when `None` |
| `date_range_end` | `dateRangeEnd` | `query` | no | string<br>Overrides the saved range end. `YYYY-MM-DDTHH:MM:SS`. | single query value; omit only when `None` |
| `sort_column` | `sortColumn` | `query` | no | string<br>Validated against the report type; an unknown column returns 400. | single query value; omit only when `None` |
| `sort_order` | `sortOrder` | `query` | no | string enum["ASCENDING", "DESCENDING"] | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer | single query value; omit only when `None` |
| `page_size` | `pageSize` | `query` | no | integer | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`SharedReportData`](#schema-sharedreportdata) | object envelope; item arrays: `donutChart`, `groupOne`, `totals` |
| `200` | `application/pdf` | `bytes` | string<binary> | string |
| `200` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `bytes` | string<binary> | string |
| `200` | `text/csv` | `text` | string | string |

**Pagination:** page=`page`; page size=`pageSize`; object envelope; item arrays: `donutChart`, `groupOne`, `totals`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `sharedReportId`:**

```yaml
type: string
```

**parameter query `exportType`:**

```yaml
enum:
- JSON_V1
- JSON
- CSV
- XLSX
- PDF
type: string
```

**parameter query `dateRangeStart`:**

```yaml
type: string
```

**parameter query `dateRangeEnd`:**

```yaml
type: string
```

**parameter query `sortColumn`:**

```yaml
type: string
```

**parameter query `sortOrder`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**parameter query `page`:**

```yaml
default: 1
minimum: 1
type: integer
```

**parameter query `pageSize`:**

```yaml
default: 50
minimum: 1
type: integer
```

**response `200` `application/pdf`:**

```yaml
format: binary
type: string
```

**response `200` `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`:**

```yaml
format: binary
type: string
```

**response `200` `text/csv`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `config.per-op-host-vs-environment-override.cross-repo-2026-06-09`:** the generated `core/request.ts` resolves `clientOptions.baseUrl ?? clientOptions.environment ?? operation.baseUrl ?? Default` (emitter: `scripts/generate-sdk-from-openapi.mjs` `requestRuntimeSourceWithTimeoutAndRetry`). A client-level `baseUrl`/`environment` override therefore **wins over** the per-op reports/audit host. This is INTENTIONAL per `docs/config-precedence-policy.md` ("Base URL override rule": `environment`/`baseUrl` are mock/replay/private-gateway levers) — it lets one mock host capture ALL traffic, including reports/ audit (`wrapper/tests/mock-clockify.test.ts` points `environment` at a localhost mock). Reordering `operation.…
- **FACT — `params.dropped-by-source-shadowing`:** `compensated-in-corrected-spec`.
- **FACT — `shared-reports.bare-get.returns-rendered-report`:** `GET /shared-reports/{id}` on the reports host returns `{totals, donutChart, groupTotals, groupOne, filters}` — the rendered report, with the saved configuration nested under `filters` alongside the viewer's presentation context. `groupOne` and `donutChart` row shapes follow the saved grouping, so the new `SharedReportData` models the observed keys and stays open (`additionalProperties: true`). `SharedReport`, the list/create item shape, which shares *no* top-level key with the response.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_shared_reports_view_public`.
- Eligibility: **ELIGIBLE WITH JSON/CSV-ONLY MCP CONTRACT**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `tags`

### `tags.create()` — `postWorkspacesWorkspaceIdTags`

| Field | Reconciled value |
|---|---|
| Behavior | Create tag |
| HTTP | `POST /workspaces/{workspaceId}/tags` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`TagCreate`](#schema-tagcreate) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`Tag`](#schema-tag) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `entity.name-reserved-after-delete.cross-repo-2026-06-09`:** a project / tag / client NAME stays reserved even after the entity is archived and then deleted. Re-creating with the same name returns `... with this name already exists` (e.g. `"Project with this name already exists"`) even though the name no longer appears in any list — so a "list, then reuse the name" recovery never surfaces it. The only fix is a distinct name. `documented; ts-side-hint-pending`. Recommend the TS MCP `clockify_*_create` tools (and the SDK `create` docstrings) warn that a previously deleted name may report "already exists" and to retry with a distinct name. No spec change — a platform behavior, not a shape divergence.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tags_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tags.delete()` — `deleteWorkspacesWorkspaceIdTagsTagId`

| Field | Reconciled value |
|---|---|
| Behavior | Delete tag |
| HTTP | `DELETE /workspaces/{workspaceId}/tags/{tagId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `tag_id` | `tagId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Tag`](#schema-tag) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `tagId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `deletes.clients-tags.response-body-dropped`:** both DELETEs answer 200 with the full deleted entity. `deleteExpense` really is empty-bodied, so the contrast is what makes the finding narrow rather than a blanket rule. 200 with no content.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tags_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tags.get()` — `getWorkspacesWorkspaceIdTagsTagId`

| Field | Reconciled value |
|---|---|
| Behavior | Get tag |
| HTTP | `GET /workspaces/{workspaceId}/tags/{tagId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `tag_id` | `tagId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Tag`](#schema-tag) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `tagId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tags_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tags.list()` — `getWorkspacesWorkspaceIdTags`

| Field | Reconciled value |
|---|---|
| Behavior | List tags |
| HTTP | `GET /workspaces/{workspaceId}/tags` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `name` | `name` | `query` | no | string | single query value; omit only when `None` |
| `strict_name_search` | `strict-name-search` | `query` | no | boolean | single query value; omit only when `None` |
| `excluded_ids` | `excluded-ids` | `query` | no | string | single query value; omit only when `None` |
| `archived` | `archived` | `query` | no | boolean | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | string enum["ID", "NAME"] | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"] | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<br>Hyphenated `page-size` is the documented spelling for v1 listing endpoints. Note: shared-reports uses `pageSize` (camelCase); the hyphenated form is silently ignored there. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`Tag`](#schema-tag)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter query `name`:**

```yaml
type: string
```

**parameter query `strict-name-search`:**

```yaml
default: false
type: boolean
```

**parameter query `excluded-ids`:**

```yaml
type: string
```

**parameter query `archived`:**

```yaml
type: boolean
```

**parameter query `sort-column`:**

```yaml
enum:
- ID
- NAME
type: string
```

**parameter query `sort-order`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**parameter query `page`:**

```yaml
default: 1
minimum: 1
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/Tag'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `list.archived-default-returns-both`:** omitting `archived` returns archived **and** active rows. Only `archived=false` restricts the result to active rows. `documented`.
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — `params.dropped-by-source-shadowing`:** `compensated-in-corrected-spec`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tags_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tags.update()` — `putWorkspacesWorkspaceIdTagsTagId`

| Field | Reconciled value |
|---|---|
| Behavior | Update tag |
| HTTP | `PUT /workspaces/{workspaceId}/tags/{tagId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `tag_id` | `tagId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | {`archived?`: boolean; `name?`: string} | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Tag`](#schema-tag) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `tagId`:**

```yaml
type: string
```

**request `application/json`:**

```yaml
properties:
  archived:
    type: boolean
  name:
    type: string
type: object
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** replacement update; omitted archived resets false.
- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- **FACT — `tags.update.replace-resets-archived`:** the `PUT` is a **full replace**: omitting `archived` resets it to `false`. Renaming an archived tag with a name-only body silently un-archives it. `compensated-in-surfaces`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tags_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `tasks`

### `tasks.create()` — `addTaskOnProject`

| Field | Reconciled value |
|---|---|
| Behavior | Add a new task on a project |
| HTTP | `POST /workspaces/{workspaceId}/projects/{projectId}/tasks` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `contains_assignee` | `contains-assignee` | `query` | no | boolean<br>Flag to set whether task will have assignee or none. | single query value; omit only when `None` |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`TaskCreateRequest`](#schema-taskcreaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`Task`](#schema-task) | object envelope; item arrays: `assigneeIds`, `userGroupIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `projectId`:**

```yaml
example: 25b687e29ae1f428e7ebe123
type: string
```

**parameter query `contains-assignee`:**

```yaml
default: true
type: boolean
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `tasks.create.billable-missing-from-create-request`:** `fixed-in-canonical-source`. This was first recorded as pending in downstream ledger commit `90fefb7`. GOCLMCP test commit `b6d4560` locked optional `billable` plus its `false` example, and source commit `a4e72bb` corrected the create schema, refreshed the manifest, and regenerated the green canonical document. The byte-for-byte downstream copy has SHA-256 `0a1eeb34f6f8e7693b92d3edfb5841e512e6fa1b402b3ea49c82be70fd5565e7`; `make sdk-codegen` regenerated the request type and resource docs from it.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tasks_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tasks.delete()` — `deleteTaskFromProject`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a task from a project |
| HTTP | `DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `task_id` | `taskId` | `path` | yes | string<br>Represents a task identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Task`](#schema-task) | object envelope; item arrays: `assigneeIds`, `userGroupIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `projectId`:**

```yaml
example: 25b687e29ae1f428e7ebe123
type: string
```

**parameter path `taskId`:**

```yaml
example: 57a687e29ae1f428e7ebe107
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** archive or complete before delete.
- **FACT — lifecycle:** project must be archived; task must be DONE before delete.
- **FACT — `deletes.archive-first`:** Clockify rejects DELETE of an ACTIVE entity. Projects/clients/expense-categories must be archived first; tasks marked DONE first. `compensated-in-tool-layer` for expense categories (2026-06-14) — `clockify_expenses_categories_delete` now `expenseCategories.archive({archived:true})` (the dedicated PATCH `/status`, no replace risk) before delete. Test: `mcp/tests/sweep-fixes.test.ts`. Projects/tasks compensated 2026-06-15 and clients 2026-06-17 (see the sub-entries below) — each archives via GET-then-PUT (carry the entity's fields, overlay `archived:true`/`status:"DONE"`) then DELETE, because their archive is a **replace-PUT** (`*.update`) w…
- **FACT — `deletes.archive-first.projects-tasks`:** `compensated-in-tool-layer` (2026-06-15). `clockify_projects_delete` and `clockify_tasks_delete` GET-then-PUT (archive / DONE) before DELETE, after the confirm gate. Verified LIVE end-to-end through the real MCP tools (dry_run → confirm_token → execute): both returned `deleted:true` against a real active project + task. Order pinned by `mcp/tests/archive-then-delete.test.ts`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tasks_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tasks.get()` — `getTaskById`

| Field | Reconciled value |
|---|---|
| Behavior | Get a task by id |
| HTTP | `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `task_id` | `taskId` | `path` | yes | string<br>Represents a task identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Task`](#schema-task) | object envelope; item arrays: `assigneeIds`, `userGroupIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `projectId`:**

```yaml
example: 25b687e29ae1f428e7ebe123
type: string
```

**parameter path `taskId`:**

```yaml
example: 57a687e29ae1f428e7ebe107
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tasks_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tasks.list()` — `findTasksOnProject`

| Field | Reconciled value |
|---|---|
| Behavior | Find tasks on a project |
| HTTP | `GET /workspaces/{workspaceId}/projects/{projectId}/tasks` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `name` | `name` | `query` | no | string<br>If provided, you'll get a filtered list of tasks that matches the provided string in their name. | single query value; omit only when `None` |
| `strict_name_search` | `strict-name-search` | `query` | no | boolean<br>Flag to toggle strict search mode. When true, search by name returns only exact matches. | single query value; omit only when `None` |
| `is_active` | `is-active` | `query` | no | boolean<br>Filters search results whether task is active or not. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | string enum["ID", "NAME"]<br>Represents the column as criteria for sorting tasks. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"]<br>Sorting mode. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`Task`](#schema-task)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `projectId`:**

```yaml
example: 25b687e29ae1f428e7ebe123
type: string
```

**parameter query `name`:**

```yaml
default: '##default'
type: string
```

**parameter query `strict-name-search`:**

```yaml
default: false
type: boolean
```

**parameter query `is-active`:**

```yaml
default: false
type: boolean
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `sort-column`:**

```yaml
enum:
- ID
- NAME
type: string
```

**parameter query `sort-order`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/Task'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tasks_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tasks.update()` — `updateTaskOnProject`

| Field | Reconciled value |
|---|---|
| Behavior | Update a task on a project |
| HTTP | `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `task_id` | `taskId` | `path` | yes | string<br>Represents a task identifier across the system. | path segment; percent-encode once |
| `contains_assignee` | `contains-assignee` | `query` | no | boolean<br>Flag to set whether task will have assignee or none. | single query value; omit only when `None` |
| `membership_status` | `membership-status` | `query` | no | string enum["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]<br>Represents a membership status. | single query value; omit only when `None` |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`TaskUpdateRequest`](#schema-taskupdaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Task`](#schema-task) | object envelope; item arrays: `assigneeIds`, `userGroupIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `projectId`:**

```yaml
example: 25b687e29ae1f428e7ebe123
type: string
```

**parameter path `taskId`:**

```yaml
example: 57a687e29ae1f428e7ebe107
type: string
```

**parameter query `contains-assignee`:**

```yaml
default: true
type: boolean
```

**parameter query `membership-status`:**

```yaml
enum:
- PENDING
- ACTIVE
- DECLINED
- INACTIVE
- ALL
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tasks_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `tasks.update_billable_rate()` — `updateTaskBillableRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update a task's billable rate |
| HTTP | `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/hourly-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `task_id` | `taskId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`RateUpdateRequest`](#schema-rateupdaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Task`](#schema-task) | object envelope; item arrays: `assigneeIds`, `userGroupIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `projectId`:**

```yaml
example: 25b687e29ae1f428e7ebe123
type: string
```

**parameter path `taskId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `rates.put-minor-units-no-get`:** rates are PUTs of an integer **minor-unit** `{amount}` body; **GET on a rate path 405s** (discover the current value from a membership/project doc). Per-scope endpoints: per-project member `…/projects/{p}/users/{u}/{hourly-rate|cost-rate}`; Team-section workspace member `…/users/{u}/{hourly-rate|cost-rate}`; task `…/projects/{p}/tasks/{t}/{cost-rate|hourly-rate}`. The project **default** rate has NO standalone endpoint in the addon's experience — it set `hourlyRate`/`costRate` in the project create/update BODY. `compensated-in-tool-layer` for the LIVE-VERIFIED member/task rates (2026-06-14); the project-DEFAULT rate stays `open`. Shipped t…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tasks_update_billable_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `tasks.update_cost_rate()` — `updateTaskCostRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update a task's cost rate |
| HTTP | `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/cost-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `projectId` | `path` | yes | string<br>Represents a project identifier across the system. | path segment; percent-encode once |
| `task_id` | `taskId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`RateUpdateRequest`](#schema-rateupdaterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Task`](#schema-task) | object envelope; item arrays: `assigneeIds`, `userGroupIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `projectId`:**

```yaml
example: 25b687e29ae1f428e7ebe123
type: string
```

**parameter path `taskId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `rates.put-minor-units-no-get`:** rates are PUTs of an integer **minor-unit** `{amount}` body; **GET on a rate path 405s** (discover the current value from a membership/project doc). Per-scope endpoints: per-project member `…/projects/{p}/users/{u}/{hourly-rate|cost-rate}`; Team-section workspace member `…/users/{u}/{hourly-rate|cost-rate}`; task `…/projects/{p}/tasks/{t}/{cost-rate|hourly-rate}`. The project **default** rate has NO standalone endpoint in the addon's experience — it set `hourlyRate`/`costRate` in the project create/update BODY. `compensated-in-tool-layer` for the LIVE-VERIFIED member/task rates (2026-06-14); the project-DEFAULT rate stays `open`. Shipped t…
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_tasks_update_cost_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `time_entries`

### `time_entries.bulk_update_for_user()` — `putWorkspacesWorkspaceIdUserUserIdTimeEntries`

| Field | Reconciled value |
|---|---|
| Behavior | Bulk edit time entries |
| HTTP | `PUT /workspaces/{workspaceId}/user/{userId}/time-entries` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string | path segment; percent-encode once |
| `hydrated` | `hydrated` | `query` | no | boolean | single query value; omit only when `None` |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | array[[`BulkEditTimeEntryRequest`](#schema-bulkedittimeentryrequest)] | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`TimeEntriesTimeEntry`](#schema-timeentriestimeentry)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**parameter query `hydrated`:**

```yaml
type: boolean
```

**request `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/BulkEditTimeEntryRequest'
type: array
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/TimeEntriesTimeEntry'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `schemas.minor-wire-mismatches`:** `compensated-in-corrected-spec`.
- **FACT — `time-entries.user-scoped.fern-method-names-mispaired`:** two verbs on `/workspaces/{workspaceId}/user/{userId}/time-entries` carry a method name that names a different operation than their own summary: `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_bulk_update_for_user`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`multi-entity`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `time_entries.create()` — `postWorkspacesWorkspaceIdTimeEntries`

| Field | Reconciled value |
|---|---|
| Behavior | Add a new time entry |
| HTTP | `POST /workspaces/{workspaceId}/time-entries` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateTimeEntryRequest`](#schema-createtimeentryrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`TimeEntriesTimeEntry`](#schema-timeentriestimeentry) | object envelope; item arrays: `customFieldValues`, `tagIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `schemas.minor-wire-mismatches`:** `compensated-in-corrected-spec`.
- **FACT — `time-entries.create.custom-field-write-key`:** the write key and the read key are **different words**, and sending the read key fails silently. `customFields: [{customFieldId, sourceType: "WORKSPACE", value}]` on create returns 201 and the value is stored. The response-shaped key `customFieldValues`, with the identical array, also returns **201** — and the value is dropped. No error, no warning, no echo: the response lists the field with `value: null`. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.create_for_user()` — `postWorkspacesWorkspaceIdUserUserIdTimeEntries`

| Field | Reconciled value |
|---|---|
| Behavior | Create time entry for a user |
| HTTP | `POST /workspaces/{workspaceId}/user/{userId}/time-entries` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string | path segment; percent-encode once |
| `from_entry` | `from-entry` | `query` | no | string | single query value; omit only when `None` |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`TimeEntryCreate`](#schema-timeentrycreate) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`TimeEntry`](#schema-timeentry) | object envelope; item arrays: `customFieldValues`, `tagIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**parameter query `from-entry`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `time-entries.create.archived-project-accepted`:** on a workspace that requires a project, creating an entry with **no** project returns 400 `{"message":"Time entry couldn't be created. Project is either required field or given project is archived. ...","code":501}`. That message names two causes, but only the first is real: passing an **archived** project id returns **201** and the entry is created against the archived project. `documented`.
- **FACT — `time-entries.create.custom-field-write-key`:** the write key and the read key are **different words**, and sending the read key fails silently. `customFields: [{customFieldId, sourceType: "WORKSPACE", value}]` on create returns 201 and the value is stored. The response-shaped key `customFieldValues`, with the identical array, also returns **201** — and the value is dropped. No error, no warning, no echo: the response lists the field with `value: null`. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_create_for_user`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.delete()` — `deleteWorkspacesWorkspaceIdTimeEntriesTimeEntryId`

| Field | Reconciled value |
|---|---|
| Behavior | Delete time entry |
| HTTP | `DELETE /workspaces/{workspaceId}/time-entries/{timeEntryId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `time_entry_id` | `timeEntryId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `204` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `timeEntryId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.delete_all_for_user()` — `deleteMany`

| Field | Reconciled value |
|---|---|
| Behavior | Delete all time entries for a user on a workspace |
| HTTP | `DELETE /workspaces/{workspaceId}/user/{userId}/time-entries` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |
| `time_entry_ids` | `time-entry-ids` | `query` | yes | array[string]<br>Represents a list of time entry ids to delete. | repeated query key |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`TimeEntryDtoImplV1`](#schema-timeentrydtoimplv1)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents a workspace identifier across the system.
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `userId`:**

```yaml
description: Represents a user identifier across the system.
example: 5a0ab5acb07987125438b60f
type: string
```

**parameter query `time-entry-ids`:**

```yaml
description: Represents a list of time entry ids to delete.
example: 5a0ab5acb07987125438b60f
items:
  description: Represents a list of time entry ids to delete.
  example: 5a0ab5acb07987125438b60f
  type: string
type: array
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/TimeEntryDtoImplV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_delete_all_for_user`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`multi-entity`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.duplicate()` — `postWorkspacesWorkspaceIdUserUserIdTimeEntriesTimeEntryIdDuplicate`

| Field | Reconciled value |
|---|---|
| Behavior | Duplicate time entry |
| HTTP | `POST /workspaces/{workspaceId}/user/{userId}/time-entries/{timeEntryId}/duplicate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string | path segment; percent-encode once |
| `time_entry_id` | `timeEntryId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`TimeEntriesTimeEntry`](#schema-timeentriestimeentry) | object envelope; item arrays: `customFieldValues`, `tagIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**parameter path `timeEntryId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `schemas.minor-wire-mismatches`:** `compensated-in-corrected-spec`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_duplicate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`action`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.get()` — `getWorkspacesWorkspaceIdTimeEntriesTimeEntryId`

| Field | Reconciled value |
|---|---|
| Behavior | Get time entry |
| HTTP | `GET /workspaces/{workspaceId}/time-entries/{timeEntryId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `time_entry_id` | `timeEntryId` | `path` | yes | string | path segment; percent-encode once |
| `hydrated` | `hydrated` | `query` | no | boolean | single query value; omit only when `None` |
| `consider_duration_format` | `consider-duration-format` | `query` | no | boolean | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeEntry`](#schema-timeentry) | object envelope; item arrays: `customFieldValues`, `tagIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `timeEntryId`:**

```yaml
type: string
```

**parameter query `hydrated`:**

```yaml
type: boolean
```

**parameter query `consider-duration-format`:**

```yaml
type: boolean
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.get_many()` — `getMultipleTimeEntries`

| Field | Reconciled value |
|---|---|
| Behavior | Get multiple time entries on a workspace |
| HTTP | `POST /workspaces/{workspaceId}/time-entries/batch` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`GetTimeEntriesByIdsRequest`](#schema-gettimeentriesbyidsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`TimeEntryWithRatesDtoV1`](#schema-timeentrywithratesdtov1)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents a workspace identifier across the system.
example: 64a687e29ae1f428e7ebe303
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/TimeEntryWithRatesDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `approval-requests.balance-assignment.official-spec-surface-add-2026-08-05`:** a live fetch of the official public spec (`https://docs.clockify.me/openapi.json`, `openapi: 3.0.1`, `info.version: v1`, fetched 2026-08-05) diffed against the canonical 161-operation inventory (path-parameter names normalized to `{}` before comparison, to avoid false positives from e.g. `{id}` vs `{clientId}` naming) surfaced 14 raw additions, 7 of which the official spec itself marks `deprecated: true` (a new `templates` resource: `getTemplates`/`getTemplate`/ `createMany`/`update`/`delete_1`; plus `getProjectTotals`; plus `removeMember` — see the correction above). The remaining 7 are current, non-deprecated, and were independently corr…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_get_many`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `live-success`, `probe-fragment`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.list_for_user()` — `getWorkspacesWorkspaceIdUserUserIdTimeEntries`

| Field | Reconciled value |
|---|---|
| Behavior | List time entries for a user |
| HTTP | `GET /workspaces/{workspaceId}/user/{userId}/time-entries` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string | path segment; percent-encode once |
| `description` | `description` | `query` | no | string | single query value; omit only when `None` |
| `start` | `start` | `query` | no | string<date-time> | single query value; omit only when `None` |
| `end` | `end` | `query` | no | string<date-time> | single query value; omit only when `None` |
| `project` | `project` | `query` | no | string | single query value; omit only when `None` |
| `task` | `task` | `query` | no | string | single query value; omit only when `None` |
| `tags` | `tags` | `query` | no | array[string] | repeated query key |
| `project_required` | `project-required` | `query` | no | boolean | single query value; omit only when `None` |
| `task_required` | `task-required` | `query` | no | boolean | single query value; omit only when `None` |
| `hydrated` | `hydrated` | `query` | no | boolean | single query value; omit only when `None` |
| `in_progress` | `in-progress` | `query` | no | boolean | single query value; omit only when `None` |
| `get_week_before` | `get-week-before` | `query` | no | string<date-time> | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<br>Hyphenated `page-size` is the documented spelling for v1 listing endpoints. Note: shared-reports uses `pageSize` (camelCase); the hyphenated form is silently ignored there. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`TimeEntry`](#schema-timeentry)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**parameter query `description`:**

```yaml
type: string
```

**parameter query `start`:**

```yaml
format: date-time
type: string
```

**parameter query `end`:**

```yaml
format: date-time
type: string
```

**parameter query `project`:**

```yaml
type: string
```

**parameter query `task`:**

```yaml
type: string
```

**parameter query `tags`:**

```yaml
items:
  type: string
type: array
```

**parameter query `project-required`:**

```yaml
type: boolean
```

**parameter query `task-required`:**

```yaml
type: boolean
```

**parameter query `hydrated`:**

```yaml
type: boolean
```

**parameter query `in-progress`:**

```yaml
type: boolean
```

**parameter query `get-week-before`:**

```yaml
format: date-time
type: string
```

**parameter query `page`:**

```yaml
default: 1
minimum: 1
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/TimeEntry'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — `time-entries.list.window-evaluated-as-wall-clock-in-account-timezone`:** the value is parsed to an instant, then **re-read as a wall clock in the account's timezone**. The `Z`/offset suffix does not select the instant the window covers. On this account (`Europe/Belgrade`, UTC+2 in August) the effective window sits two hours earlier than the literal reading. `documented`.
- **FACT — `time-entries.list-for-user.start-instant-filters-correctly`:** **it filters correctly.** Passing `start` excludes every entry whose `timeInterval.start` is before the given instant. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_list_for_user`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.list_in_progress()` — `getWorkspacesWorkspaceIdTimeEntriesStatusInProgress`

| Field | Reconciled value |
|---|---|
| Behavior | Get all in progress time entries |
| HTTP | `GET /workspaces/{workspaceId}/time-entries/status/in-progress` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`TimeEntriesTimeEntry`](#schema-timeentriestimeentry)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `page`:**

```yaml
default: 1
type: integer
```

**parameter query `page-size`:**

```yaml
default: 10
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/TimeEntriesTimeEntry'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `entries.stoptimer.route-404-no-static-resource`:** - **Live evidence:** `resolved` (2026-06-18). Callers were migrated to the bound route (2026-06-17); the dead `stopTimer` method + `/stop` route are now removed from generated output via the GOCLMCP quarantine (added to `PHANTOM_PATHS`, dropped its `SDK_METHOD_NAMES` entry, regenerated — live surface 185→184 ops, SDK stamps 172→171). Tests: `cli/tests/stop.test.ts`, `mcp/tests/work-time-tracking.test.ts`, `mcp/tests/server.test.ts`. - Re-verified 2026-06-20: confirmed-still-holds. /stop suffix routes (user-scoped PATCH and entry-id GET/PATCH with a fake 24-hex id) all return HTTP 404 code:3000 'No static resource ...time-entries/stop.', wh…
- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — `schemas.minor-wire-mismatches`:** `compensated-in-corrected-spec`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_list_in_progress`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.mark_invoiced()` — `patchWorkspacesWorkspaceIdTimeEntriesInvoiced`

| Field | Reconciled value |
|---|---|
| Behavior | Mark time entries as invoiced |
| HTTP | `PATCH /workspaces/{workspaceId}/time-entries/invoiced` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | {`invoiced*`: boolean; `timeEntryIds*`: array[string]} | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**request `application/json`:**

```yaml
properties:
  invoiced:
    type: boolean
  timeEntryIds:
    items:
      type: string
    type: array
required:
- invoiced
- timeEntryIds
type: object
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_mark_invoiced`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`transition`; blast radius=`multi-entity`; sensitivity=`financial`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.stop_timer_for_user()` — `patchWorkspacesWorkspaceIdUserUserIdTimeEntries`

| Field | Reconciled value |
|---|---|
| Behavior | Stop running timer |
| HTTP | `PATCH /workspaces/{workspaceId}/user/{userId}/time-entries` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | {`end*`: string<date-time>} | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeEntriesTimeEntry`](#schema-timeentriestimeentry) | object envelope; item arrays: `customFieldValues`, `tagIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**request `application/json`:**

```yaml
properties:
  end:
    format: date-time
    type: string
required:
- end
type: object
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `entries.stoptimer.route-404-no-static-resource`:** - **Live evidence:** `resolved` (2026-06-18). Callers were migrated to the bound route (2026-06-17); the dead `stopTimer` method + `/stop` route are now removed from generated output via the GOCLMCP quarantine (added to `PHANTOM_PATHS`, dropped its `SDK_METHOD_NAMES` entry, regenerated — live surface 185→184 ops, SDK stamps 172→171). Tests: `cli/tests/stop.test.ts`, `mcp/tests/work-time-tracking.test.ts`, `mcp/tests/server.test.ts`. - Re-verified 2026-06-20: confirmed-still-holds. /stop suffix routes (user-scoped PATCH and entry-id GET/PATCH with a fake 24-hex id) all return HTTP 404 code:3000 'No static resource ...time-entries/stop.', wh…
- **FACT — `schemas.minor-wire-mismatches`:** `compensated-in-corrected-spec`.
- **FACT — `time-entries.user-scoped.fern-method-names-mispaired`:** two verbs on `/workspaces/{workspaceId}/user/{userId}/time-entries` carry a method name that names a different operation than their own summary: `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_stop_timer_for_user`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_entries.update()` — `putWorkspacesWorkspaceIdTimeEntriesTimeEntryId`

| Field | Reconciled value |
|---|---|
| Behavior | Update time entry |
| HTTP | `PUT /workspaces/{workspaceId}/time-entries/{timeEntryId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `time_entry_id` | `timeEntryId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`TimeEntryUpdate`](#schema-timeentryupdate) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeEntry`](#schema-timeentry) | object envelope; item arrays: `customFieldValues`, `tagIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: <REDACTED_ID>
type: string
```

**parameter path `timeEntryId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_entries_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `time_off_balance_assignments`

### `time_off_balance_assignments.create()` — `createBalanceAssignment`

| Field | Reconciled value |
|---|---|
| Behavior | Creates a new balance assignment for a user in policy |
| HTTP | `POST /workspaces/{workspaceId}/time-off/balance/assignment` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateBalanceAssignmentV1Request`](#schema-createbalanceassignmentv1request) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: 60f91b3ffdaf031696ec61a8
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** create applies a delta/addition when an assignment already exists.
- **FACT — `approval-requests.balance-assignment.official-spec-surface-add-2026-08-05`:** a live fetch of the official public spec (`https://docs.clockify.me/openapi.json`, `openapi: 3.0.1`, `info.version: v1`, fetched 2026-08-05) diffed against the canonical 161-operation inventory (path-parameter names normalized to `{}` before comparison, to avoid false positives from e.g. `{id}` vs `{clientId}` naming) surfaced 14 raw additions, 7 of which the official spec itself marks `deprecated: true` (a new `templates` resource: `getTemplates`/`getTemplate`/ `createMany`/`update`/`delete_1`; plus `getProjectTotals`; plus `removeMember` — see the correction above). The remaining 7 are current, non-deprecated, and were independently corr…
- **FACT — `time-off.balance-assignment.create-is-additive`:** - A balance assignment is a per-(user, policy) singleton. `createBalanceAssignment` is **additive**, not idempotent: with an existing assignment (`balance 0.0`, `accrued 3.0`) a create of `balance: 2` returned HTTP 201 with an empty body and left the **same** assignment id with `accrued 5.0`; a second identical create gave `accrued 7.0`. Against a user with no assignment (`[]`) the same call created one (`balance 1.0`, `accrued 1.0`). So create means "add, or create when absent". - `updateBalanceAssignment` applies `balanceChange` as a **delta**, not a replacement value. `balanceChange: -4` returned HTTP 204 and took `accrued` from 7.0 bac…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_balance_assignments_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `live-success`, `probe-fragment`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_balance_assignments.delete()` — `deleteBalanceAssignment`

| Field | Reconciled value |
|---|---|
| Behavior | Deletes a specific balance assignment |
| HTTP | `DELETE /workspaces/{workspaceId}/time-off/balance/assignment/{balanceAssignmentId}/user/{userId}/policy/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents user identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents policy identifier across the system. | path segment; percent-encode once |
| `balance_assignment_id` | `balanceAssignmentId` | `path` | yes | string<br>Represents balance assignment identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`DeleteBalanceAssignmentV1Request`](#schema-deletebalanceassignmentv1request) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: 60f91b3ffdaf031696ec61a8
type: string
```

**parameter path `userId`:**

```yaml
description: Represents user identifier across the system.
example: 60f924bafdaf031696ec6218
type: string
```

**parameter path `policyId`:**

```yaml
description: Represents policy identifier across the system.
example: 63034cd0cb0fb876a57e93ad
type: string
```

**parameter path `balanceAssignmentId`:**

```yaml
description: Represents balance assignment identifier across the system.
example: 63034cd0cb0fb876a57e01d7
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** create applies a delta/addition when an assignment already exists.
- **FACT — `approval-requests.balance-assignment.official-spec-surface-add-2026-08-05`:** a live fetch of the official public spec (`https://docs.clockify.me/openapi.json`, `openapi: 3.0.1`, `info.version: v1`, fetched 2026-08-05) diffed against the canonical 161-operation inventory (path-parameter names normalized to `{}` before comparison, to avoid false positives from e.g. `{id}` vs `{clientId}` naming) surfaced 14 raw additions, 7 of which the official spec itself marks `deprecated: true` (a new `templates` resource: `getTemplates`/`getTemplate`/ `createMany`/`update`/`delete_1`; plus `getProjectTotals`; plus `removeMember` — see the correction above). The remaining 7 are current, non-deprecated, and were independently corr…
- **FACT — `time-off.balance-assignment.create-is-additive`:** - A balance assignment is a per-(user, policy) singleton. `createBalanceAssignment` is **additive**, not idempotent: with an existing assignment (`balance 0.0`, `accrued 3.0`) a create of `balance: 2` returned HTTP 201 with an empty body and left the **same** assignment id with `accrued 5.0`; a second identical create gave `accrued 7.0`. Against a user with no assignment (`[]`) the same call created one (`balance 1.0`, `accrued 1.0`). So create means "add, or create when absent". - `updateBalanceAssignment` applies `balanceChange` as a **delta**, not a replacement value. `balanceChange: -4` returned HTTP 204 and took `accrued` from 7.0 bac…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_balance_assignments_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `live-success`, `probe-fragment`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_balance_assignments.get_for_user_and_policy()` — `getBalanceAssignmentsForUserAndPolicy`

| Field | Reconciled value |
|---|---|
| Behavior | Get all balance assignments of a user in policy |
| HTTP | `GET /workspaces/{workspaceId}/time-off/balance/assignment/user/{userId}/policy/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents user identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents policy identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `*/*` | `json` | array[[`BalanceAssignmentV1Dto`](#schema-balanceassignmentv1dto)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: 60f91b3ffdaf031696ec61a8
type: string
```

**parameter path `userId`:**

```yaml
description: Represents user identifier across the system.
example: 60f924bafdaf031696ec6218
type: string
```

**parameter path `policyId`:**

```yaml
description: Represents policy identifier across the system.
example: 63034cd0cb0fb876a57e93ad
type: string
```

**response `200` `*/*`:**

```yaml
items:
  $ref: '#/components/schemas/BalanceAssignmentV1Dto'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `approval-requests.balance-assignment.official-spec-surface-add-2026-08-05`:** a live fetch of the official public spec (`https://docs.clockify.me/openapi.json`, `openapi: 3.0.1`, `info.version: v1`, fetched 2026-08-05) diffed against the canonical 161-operation inventory (path-parameter names normalized to `{}` before comparison, to avoid false positives from e.g. `{id}` vs `{clientId}` naming) surfaced 14 raw additions, 7 of which the official spec itself marks `deprecated: true` (a new `templates` resource: `getTemplates`/`getTemplate`/ `createMany`/`update`/`delete_1`; plus `getProjectTotals`; plus `removeMember` — see the correction above). The remaining 7 are current, non-deprecated, and were independently corr…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_balance_assignments_get_for_user_and_policy`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `live-success`, `probe-fragment`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_balance_assignments.update()` — `updateBalanceAssignment`

| Field | Reconciled value |
|---|---|
| Behavior | Updates a specific balance assignment |
| HTTP | `PUT /workspaces/{workspaceId}/time-off/balance/assignment/{balanceAssignmentId}/user/{userId}/policy/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents user identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents policy identifier across the system. | path segment; percent-encode once |
| `balance_assignment_id` | `balanceAssignmentId` | `path` | yes | string<br>Represents balance assignment identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateBalanceAssignmentV1Request`](#schema-updatebalanceassignmentv1request) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `204` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents workspace identifier across the system.
example: 60f91b3ffdaf031696ec61a8
type: string
```

**parameter path `userId`:**

```yaml
description: Represents user identifier across the system.
example: 60f924bafdaf031696ec6218
type: string
```

**parameter path `policyId`:**

```yaml
description: Represents policy identifier across the system.
example: 63034cd0cb0fb876a57e93ad
type: string
```

**parameter path `balanceAssignmentId`:**

```yaml
description: Represents balance assignment identifier across the system.
example: 63034cd0cb0fb876a57e93ad
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** create applies a delta/addition when an assignment already exists.
- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `approval-requests.balance-assignment.official-spec-surface-add-2026-08-05`:** a live fetch of the official public spec (`https://docs.clockify.me/openapi.json`, `openapi: 3.0.1`, `info.version: v1`, fetched 2026-08-05) diffed against the canonical 161-operation inventory (path-parameter names normalized to `{}` before comparison, to avoid false positives from e.g. `{id}` vs `{clientId}` naming) surfaced 14 raw additions, 7 of which the official spec itself marks `deprecated: true` (a new `templates` resource: `getTemplates`/`getTemplate`/ `createMany`/`update`/`delete_1`; plus `getProjectTotals`; plus `removeMember` — see the correction above). The remaining 7 are current, non-deprecated, and were independently corr…
- **FACT — `time-off.balance-assignment.create-is-additive`:** - A balance assignment is a per-(user, policy) singleton. `createBalanceAssignment` is **additive**, not idempotent: with an existing assignment (`balance 0.0`, `accrued 3.0`) a create of `balance: 2` returned HTTP 201 with an empty body and left the **same** assignment id with `accrued 5.0`; a second identical create gave `accrued 7.0`. Against a user with no assignment (`[]`) the same call created one (`balance 1.0`, `accrued 1.0`). So create means "add, or create when absent". - `updateBalanceAssignment` applies `balanceChange` as a **delta**, not a replacement value. `balanceChange: -4` returned HTTP 204 and took `accrued` from 7.0 bac…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_balance_assignments_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `live-success`, `probe-fragment`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `time_off_balances`

### `time_off_balances.list_for_policy()` — `getBalancesForPolicy`

| Field | Reconciled value |
|---|---|
| Behavior | Get balances for a policy |
| HTTP | `GET /workspaces/{workspaceId}/time-off/balance/policy/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents a policy identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `sort` | `sort` | `query` | no | [`BalanceSortColumn`](#schema-balancesortcolumn)<br>If provided, the result is sorted by this column. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | [`BalanceSortOrder`](#schema-balancesortorder)<br>Sort results in ascending or descending order. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`BalanceListResponse`](#schema-balancelistresponse) | object envelope; item arrays: `balances` |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; object envelope; item arrays: `balances`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `policyId`:**

```yaml
default: '##default'
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
maximum: 1000
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
maximum: 200
minimum: 1
type: integer
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `getBalanceForUser.page-types.docs-claim-string`:** both balance endpoints' source-bundle declarations in `docs/openapi/sources/realOPENAPI/BALANCEOPEANI.yaml` normalize these params to `type: integer, format: int32` with consistent min/max constraints (consistent with the broader API where every other `page` / `page-size` is int32). The live API accepts integer values on both routes. `documented-prefer-source-bundle`. No spec change. This entry exists so a future reviewer who reads the official docs paste and notices the string-vs-int divergence sees the decision already taken. - Re-verified 2026-06-20: confirmed-still-holds. Live getBalanceForUser accepts integer page-size=50 -> HTTP 200,…
- **FACT — `pagination.iter-known-set.envelope-and-unpaginated`:** each endpoint was probed with `?page=1&page-size=2` (results-available) and the paginated endpoints additionally with `?page=999&page-size=2` (results- exhausted). Result: `audited-and-shipped`. Two changes ship in this session: 1. **Generator (GOCLMCP):** new `LAST_PAGE_HEADER_OPS` set (15 entries) + `stamp_last_page_header!` function called in the per-op finalization loop. The canonical YAML now carries `x-clockify-last-page-header: true` on each of the 15 audited-emitting operations. 2. **Wrapper (this repo):** `iterPages` now feature-detects `.withRawResponse()` on the fetcher's return, reads the `Last-Page` response header via the cas…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_balances_list_for_policy`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_balances.list_for_user()` — `getBalanceForUser`

| Field | Reconciled value |
|---|---|
| Behavior | Get balance for a user |
| HTTP | `GET /workspaces/{workspaceId}/time-off/balance/user/{userId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `sort` | `sort` | `query` | no | [`BalanceSortColumn`](#schema-balancesortcolumn)<br>Sort result based on given criteria. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | [`BalanceSortOrder`](#schema-balancesortorder)<br>Sort result by providing sort order. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`BalanceListResponse`](#schema-balancelistresponse) | object envelope; item arrays: `balances` |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; object envelope; item arrays: `balances`.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `userId`:**

```yaml
default: '##default'
type: string
```

**parameter query `page`:**

```yaml
format: int32
maximum: 1000
type: integer
```

**parameter query `page-size`:**

```yaml
format: int32
maximum: 200
minimum: 1
type: integer
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `getBalanceForUser.page-types.docs-claim-string`:** both balance endpoints' source-bundle declarations in `docs/openapi/sources/realOPENAPI/BALANCEOPEANI.yaml` normalize these params to `type: integer, format: int32` with consistent min/max constraints (consistent with the broader API where every other `page` / `page-size` is int32). The live API accepts integer values on both routes. `documented-prefer-source-bundle`. No spec change. This entry exists so a future reviewer who reads the official docs paste and notices the string-vs-int divergence sees the decision already taken. - Re-verified 2026-06-20: confirmed-still-holds. Live getBalanceForUser accepts integer page-size=50 -> HTTP 200,…
- **FACT — `pagination.iter-known-set.envelope-and-unpaginated`:** each endpoint was probed with `?page=1&page-size=2` (results-available) and the paginated endpoints additionally with `?page=999&page-size=2` (results- exhausted). Result: `audited-and-shipped`. Two changes ship in this session: 1. **Generator (GOCLMCP):** new `LAST_PAGE_HEADER_OPS` set (15 entries) + `stamp_last_page_header!` function called in the per-op finalization loop. The canonical YAML now carries `x-clockify-last-page-header: true` on each of the 15 audited-emitting operations. 2. **Wrapper (this repo):** `iterPages` now feature-detects `.withRawResponse()` on the fetcher's return, reads the `Last-Page` response header via the cas…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — `time-off.balance.negativeBalanceUsed-dropped`:** the wire returns `balances[].negativeBalanceUsed`. **RESOLVED 2026-07-29.** `apply_live_overrides!` in `../GOCLMCP/scripts/gen-clockify-openapi` adds `negativeBalanceUsed` (`number`, `format: double`) to `BalanceDtoV1`; re-snapshotted into `spec/corrected`. `live-differential` now reports this operation as an exact match — `schemaPathCount: 16`, `wirePathCount: 16`, `schemaOnlyCount: 0` — and the `knownDrift` record is removed.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_balances_list_for_user`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-fragment`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_balances.update_for_policy()` — `updateBalance`

| Field | Reconciled value |
|---|---|
| Behavior | Update a balance |
| HTTP | `PATCH /workspaces/{workspaceId}/time-off/balance/policy/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents a policy identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateBalanceRequest`](#schema-updatebalancerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `204` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
default: '##default'
type: string
```

**parameter path `policyId`:**

```yaml
default: '##default'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_balances_update_for_policy`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `time_off_policies`

### `time_off_policies.create()` — `createTimeOffPolicy`

| Field | Reconciled value |
|---|---|
| Behavior | Create a time off policy |
| HTTP | `POST /workspaces/{workspaceId}/time-off/policies` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateTimeOffPolicyRequest`](#schema-createtimeoffpolicyrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`Policy`](#schema-policy) | object envelope; item arrays: `userGroupIds`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** replacement update; preserve full policy and assignment scope.
- **FACT — `time-off-policies.create.approve-is-optional`:** creating a policy without `approve` returns `{"message":"must not be null","code":501}`. Proven under four independent assignee shapes — flat `userIds`, the spec-faithful `users` envelope, `everyoneIncludingNew: true` with no assignees, and both together. The same body plus `approve` returns 201. `compensated-in-corrected-spec`. Guarded by `TestGeneratedOpenAPITimeOffPolicyCreateRequiresApprove`, which previously asserted the opposite and so let the wrong contract ship.
- **FACT — `time-off.policies.scope.status-active-not-all`:** holiday assignments and time-off **policy** scope share the `{contains:"CONTAINS", ids, status}` filter shape but use DIFFERENT `status` values — holidays send `status:"ALL"` (`ai-assistant-addon/src/clockify/rest/holidays.ts:7`, corroboration only) while policies send `status:"ACTIVE"` (`ai-assistant-addon/src/clockify/rest/time-off.ts:13`, corroboration only). **In-repo source of record:** `docs/live-probe-ledger.json` (`getTimeOffRequests`/`getWorkspaceProjects` fixture rows, recorded 2026-06-18) plus the committed fixture `spec/evidence/fixtures/timeoff.requests.search.json`. The SDK's shared `mcp/src/scope-filter.ts` previously hard-c…
- **FACT — `time-off.policies.update.replace-and-scope-filter`:** identical class to holidays — `PUT /time-off/policies/{policyId}` replaces the doc and wants `users`/`userGroups` as `{contains,ids,status}` filters; GET echoes them flat. Unlike holidays, policies DO have a single GET (`timeOffPolicies.get`). `compensated-in-tool-layer` (2026-06-14). `clockify_time_off_policies_update` now GET-then-PUTs via `timeOffPolicies.get`, carries forward the accepted policy fields (`POLICY_CARRY_FIELDS`), reconstructs the scope via the shared `mcp/src/scope-filter.ts`, and passes the body **FLAT** — the generated method reads fields flat and silently dropped the prior nested `body` (a pre-existing bug also fixed);…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_policies_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_policies.delete()` — `deleteTimeOffPolicy`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a policy |
| HTTP | `DELETE /workspaces/{workspaceId}/time-off/policies/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `policyId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_policies_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_policies.get()` — `getTimeOffPolicy`

| Field | Reconciled value |
|---|---|
| Behavior | Get a time off policy |
| HTTP | `GET /workspaces/{workspaceId}/time-off/policies/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Policy`](#schema-policy) | object envelope; item arrays: `userGroupIds`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `policyId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `time-off-policies.response.missing-replacement-fields`:** `fixed-in-canonical-source`. This was first recorded as pending in downstream ledger commit `90fefb7`. GOCLMCP test commit `b6d4560` locked the three response fields and exact icon enum; source commit `a4e72bb` added them to `Policy`, refreshed the manifest, and regenerated the green canonical document. The downstream byte-for-byte copy has SHA-256 `0a1eeb34f6f8e7693b92d3edfb5841e512e6fa1b402b3ea49c82be70fd5565e7`, and `make sdk-codegen` regenerated the DTO/docs. The legacy-policy nullability/absence question above remains open; consumers still validate required replacement state instead of inventing it.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_policies_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_policies.list()` — `getTimeOffPolicies`

| Field | Reconciled value |
|---|---|
| Behavior | Get policies on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/time-off/policies` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | string<br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `name` | `name` | `query` | no | string<br>Filters policies to names that contain the provided string. | single query value; omit only when `None` |
| `status` | `status` | `query` | no | string enum["ACTIVE", "ARCHIVED", "ALL"]<br>Filters policies by status. | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | string<br>Column to use for sorting policies. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"]<br>Sort order. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`Policy`](#schema-policy)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `page`:**

```yaml
maxLength: 1000
type: string
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
maximum: 200
minimum: 1
type: integer
```

**parameter query `name`:**

```yaml
type: string
```

**parameter query `status`:**

```yaml
enum:
- ACTIVE
- ARCHIVED
- ALL
type: string
```

**parameter query `sort-column`:**

```yaml
default: DEFAULT_SORT
type: string
```

**parameter query `sort-order`:**

```yaml
default: ASCENDING
enum:
- ASCENDING
- DESCENDING
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/Policy'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — `getTimeOffPolicies.sort-order.enum-tightened`:** the source-bundle declaration in `docs/openapi/sources/realOPENAPI/POLICIESOPENAPI.YAML:74-80` modelled `sort-order` as a plain `type: string` with a default, no enum. The canonical preserved the looser shape. The Fern-generated TS SDK therefore typed `GetTimeOffPoliciesRequest['sort-order']` as `string`, losing the enum surface that the official docs imply. `fixed-at-source`. Added the enum + restated default in `docs/openapi/sources/realOPENAPI/POLICIESOPENAPI.YAML`, refreshed source manifest (28915 → 28976 bytes; sha256 `1228ecd0ffa99882bbc284b4df517eb05703ce046fc1f5b7eccf96491029f881`). `make gen-openapi` clean; all four drift gates pa…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — `time-off-policies.response.missing-replacement-fields`:** `fixed-in-canonical-source`. This was first recorded as pending in downstream ledger commit `90fefb7`. GOCLMCP test commit `b6d4560` locked the three response fields and exact icon enum; source commit `a4e72bb` added them to `Policy`, refreshed the manifest, and regenerated the green canonical document. The downstream byte-for-byte copy has SHA-256 `0a1eeb34f6f8e7693b92d3edfb5841e512e6fa1b402b3ea49c82be70fd5565e7`, and `make sdk-codegen` regenerated the DTO/docs. The legacy-policy nullability/absence question above remains open; consumers still validate required replacement state instead of inventing it.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_policies_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_policies.update()` — `updateTimeOffPolicy`

| Field | Reconciled value |
|---|---|
| Behavior | Update a policy |
| HTTP | `PUT /workspaces/{workspaceId}/time-off/policies/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateTimeOffPolicyRequest`](#schema-updatetimeoffpolicyrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Policy`](#schema-policy) | object envelope; item arrays: `userGroupIds`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `policyId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** replacement update; preserve full policy and assignment scope.
- **FACT/INFERENCE — replacement risk:** proven replacement risk.
- **FACT — `time-off-policies.response.missing-replacement-fields`:** `fixed-in-canonical-source`. This was first recorded as pending in downstream ledger commit `90fefb7`. GOCLMCP test commit `b6d4560` locked the three response fields and exact icon enum; source commit `a4e72bb` added them to `Policy`, refreshed the manifest, and regenerated the green canonical document. The downstream byte-for-byte copy has SHA-256 `0a1eeb34f6f8e7693b92d3edfb5841e512e6fa1b402b3ea49c82be70fd5565e7`, and `make sdk-codegen` regenerated the DTO/docs. The legacy-policy nullability/absence question above remains open; consumers still validate required replacement state instead of inventing it.
- **FACT — `time-off.policies.scope.status-active-not-all`:** holiday assignments and time-off **policy** scope share the `{contains:"CONTAINS", ids, status}` filter shape but use DIFFERENT `status` values — holidays send `status:"ALL"` (`ai-assistant-addon/src/clockify/rest/holidays.ts:7`, corroboration only) while policies send `status:"ACTIVE"` (`ai-assistant-addon/src/clockify/rest/time-off.ts:13`, corroboration only). **In-repo source of record:** `docs/live-probe-ledger.json` (`getTimeOffRequests`/`getWorkspaceProjects` fixture rows, recorded 2026-06-18) plus the committed fixture `spec/evidence/fixtures/timeoff.requests.search.json`. The SDK's shared `mcp/src/scope-filter.ts` previously hard-c…
- **FACT — `time-off.policies.update.replace-and-scope-filter`:** identical class to holidays — `PUT /time-off/policies/{policyId}` replaces the doc and wants `users`/`userGroups` as `{contains,ids,status}` filters; GET echoes them flat. Unlike holidays, policies DO have a single GET (`timeOffPolicies.get`). `compensated-in-tool-layer` (2026-06-14). `clockify_time_off_policies_update` now GET-then-PUTs via `timeOffPolicies.get`, carries forward the accepted policy fields (`POLICY_CARRY_FIELDS`), reconstructs the scope via the shared `mcp/src/scope-filter.ts`, and passes the body **FLAT** — the generated method reads fields flat and silently dropped the prior nested `body` (a pre-existing bug also fixed);…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_policies_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`proven replacement risk`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_policies.update_status()` — `changeTimeOffPolicyStatus`

| Field | Reconciled value |
|---|---|
| Behavior | Change a policy status |
| HTTP | `PATCH /workspaces/{workspaceId}/time-off/policies/{policyId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`PolicyStatusChangeRequest`](#schema-policystatuschangerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Policy`](#schema-policy) | object envelope; item arrays: `userGroupIds`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `policyId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `schemas.minor-wire-mismatches`:** `compensated-in-corrected-spec`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_policies_update_status`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`transition`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `time_off_requests`

### `time_off_requests.list()` — `getAllTimeOffRequestsOnWorkspace`

| Field | Reconciled value |
|---|---|
| Behavior | Get all time off requests on a workspace |
| HTTP | `POST /workspaces/{workspaceId}/time-off/requests` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`TimeOffRequestSearchRequest`](#schema-timeoffrequestsearchrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeOffRequestsResponse`](#schema-timeoffrequestsresponse) | object envelope; item arrays: `requests` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `time-off-b.yaml.changedForUserName.malformed-inline-yaml`:** in `docs/openapi/sources/clockify-api-probe-lab/openapi-fragments/time-off-b.yaml:157` the line was written without a space after the key colon: `changedForUserName:{ type: string }`. YAML accepts this leniently (some parsers treat it as a scalar key with mapping value, some reject), but the bytes propagated into the canonical spec unchanged at line 21323. Fern CLI 5.37.9's new `--from-openapi` parser correctly flagged this as `Schema property changedForUserName: { type should be an object`. `fixed-at-source`. Single character added (a space after the colon) in `time-off-b.yaml:157`. Source manifest (`docs/openapi/sources/manifest.json`) u…
- **FACT — `time-off.request.missing-top-level-fields`:** `fixed-in-canonical-generator`. Patched the same `TimeOffRequest` block in `docs/openapi/sources/clockify-api-probe-lab/openapi.yaml`, refreshed `manifest.json` (`126895 → 128402` bytes). `make gen-openapi` regenerated `docs/openapi/clockify-openapi.yaml`; all four drift gates green, `go test ./internal/tools/...` passes. The regenerated TS SDK now has 17 fields on `TimeOffRequest` (was 10), an inline `HalfDayPeriod` enum, and a typed `HalfDayHours { start, end }` namespace.
- **FACT — `time-off.request.status.schema-collision`:** real shape is ```json { "statusType": "APPROVED", "changedByUserId": "64621fae…", "changedByUserName": "Firstname Lastname", "changedForUserName": "Firstname Lastname", "changedAt": "2026-05-17T23:51:17.160269150Z", "note": null } ``` For PENDING, `changedByUserId` and `changedAt` come back as `null` but the keys are still present. **No `createdBy` field exists at any level.** **`createdAt` lives at top level**, not under `status` — captured from a separate probe on the same record. `fixed-in-canonical-generator`. The inline status definition lived in `docs/openapi/sources/clockify-api-probe-lab/openapi.yaml` at the `TimeOffRequest` block…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_requests_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_requests.submit()` — `createTimeOffRequest`

| Field | Reconciled value |
|---|---|
| Behavior | Create a time off request |
| HTTP | `POST /workspaces/{workspaceId}/time-off/policies/{policyId}/requests` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents a policy identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateTimeOffRequest`](#schema-createtimeoffrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeOffRequestFullV1Dto`](#schema-timeoffrequestfullv1dto) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `policyId`:**

```yaml
type: string
x-clockify-default: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** request period shape depends on policy unit/type.
- **FACT — `schemas.minor-wire-mismatches`:** `compensated-in-corrected-spec`.
- **FACT — `time-off-b.yaml.changedForUserName.malformed-inline-yaml`:** in `docs/openapi/sources/clockify-api-probe-lab/openapi-fragments/time-off-b.yaml:157` the line was written without a space after the key colon: `changedForUserName:{ type: string }`. YAML accepts this leniently (some parsers treat it as a scalar key with mapping value, some reject), but the bytes propagated into the canonical spec unchanged at line 21323. Fern CLI 5.37.9's new `--from-openapi` parser correctly flagged this as `Schema property changedForUserName: { type should be an object`. `fixed-at-source`. Single character added (a space after the colon) in `time-off-b.yaml:157`. Source manifest (`docs/openapi/sources/manifest.json`) u…
- **FACT — `time-off.request.status.schema-collision`:** real shape is ```json { "statusType": "APPROVED", "changedByUserId": "64621fae…", "changedByUserName": "Firstname Lastname", "changedForUserName": "Firstname Lastname", "changedAt": "2026-05-17T23:51:17.160269150Z", "note": null } ``` For PENDING, `changedByUserId` and `changedAt` come back as `null` but the keys are still present. **No `createdBy` field exists at any level.** **`createdAt` lives at top level**, not under `status` — captured from a separate probe on the same record. `fixed-in-canonical-generator`. The inline status definition lived in `docs/openapi/sources/clockify-api-probe-lab/openapi.yaml` at the `TimeOffRequest` block…
- **FACT — `time-off.submit.period-shape-is-policy-type-dependent`:** the submit period shape depends on the policy's time unit. A **DAYS**-unit policy rejects `{start,end}` with 400 "Value for number of days is not allowed" and wants `{start, days}` (date-only start); an **HOURS**-unit policy accepts `{start, end}` (RFC3339, non-millisecond — a `.000Z` form 400s "invalid date format") and rejects `days`. The stored request always echoes a server-computed `{start,end}`. `compensated-in-tool-layer` (2026-06-21). `end` is now OPTIONAL and sent conditionally; the handler requires at least one of `{end, days}` (clear error before the wire otherwise), and the field descriptions explain the per-unit shape. No surf…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_requests_submit`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_requests.submit_for_user()` — `createTimeOffRequestForUser`

| Field | Reconciled value |
|---|---|
| Behavior | Create a time off request for a user |
| HTTP | `POST /workspaces/{workspaceId}/time-off/policies/{policyId}/users/{userId}/requests` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents a policy identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateTimeOffRequest`](#schema-createtimeoffrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeOffRequestFullV1Dto`](#schema-timeoffrequestfullv1dto) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `policyId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `userId`:**

```yaml
type: string
x-clockify-default: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** request period shape depends on policy unit/type.
- **FACT — `time-off-b.yaml.changedForUserName.malformed-inline-yaml`:** in `docs/openapi/sources/clockify-api-probe-lab/openapi-fragments/time-off-b.yaml:157` the line was written without a space after the key colon: `changedForUserName:{ type: string }`. YAML accepts this leniently (some parsers treat it as a scalar key with mapping value, some reject), but the bytes propagated into the canonical spec unchanged at line 21323. Fern CLI 5.37.9's new `--from-openapi` parser correctly flagged this as `Schema property changedForUserName: { type should be an object`. `fixed-at-source`. Single character added (a space after the colon) in `time-off-b.yaml:157`. Source manifest (`docs/openapi/sources/manifest.json`) u…
- **FACT — `time-off.request.status.schema-collision`:** real shape is ```json { "statusType": "APPROVED", "changedByUserId": "64621fae…", "changedByUserName": "Firstname Lastname", "changedForUserName": "Firstname Lastname", "changedAt": "2026-05-17T23:51:17.160269150Z", "note": null } ``` For PENDING, `changedByUserId` and `changedAt` come back as `null` but the keys are still present. **No `createdBy` field exists at any level.** **`createdAt` lives at top level**, not under `status` — captured from a separate probe on the same record. `fixed-in-canonical-generator`. The inline status definition lived in `docs/openapi/sources/clockify-api-probe-lab/openapi.yaml` at the `TimeOffRequest` block…
- **FACT — `time-off.submit.period-shape-is-policy-type-dependent`:** the submit period shape depends on the policy's time unit. A **DAYS**-unit policy rejects `{start,end}` with 400 "Value for number of days is not allowed" and wants `{start, days}` (date-only start); an **HOURS**-unit policy accepts `{start, end}` (RFC3339, non-millisecond — a `.000Z` form 400s "invalid date format") and rejects `days`. The stored request always echoes a server-computed `{start,end}`. `compensated-in-tool-layer` (2026-06-21). `end` is now OPTIONAL and sent conditionally; the handler requires at least one of `{end, days}` (clear error before the wire otherwise), and the field descriptions explain the per-unit shape. No surf…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_requests_submit_for_user`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_requests.update_status()` — `changeTimeOffRequestStatus`

| Field | Reconciled value |
|---|---|
| Behavior | Change a time off request status |
| HTTP | `PATCH /workspaces/{workspaceId}/time-off/policies/{policyId}/requests/{requestId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents a policy identifier across the system. | path segment; percent-encode once |
| `request_id` | `requestId` | `path` | yes | string<br>Represents a time off request identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ChangeTimeOffRequestStatusRequest`](#schema-changetimeoffrequeststatusrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeOffRequestDto`](#schema-timeoffrequestdto) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `policyId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `requestId`:**

```yaml
type: string
x-clockify-default: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** status transition body depends on target state and may require a note.
- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…
- **FACT — `time-off-b.yaml.changedForUserName.malformed-inline-yaml`:** in `docs/openapi/sources/clockify-api-probe-lab/openapi-fragments/time-off-b.yaml:157` the line was written without a space after the key colon: `changedForUserName:{ type: string }`. YAML accepts this leniently (some parsers treat it as a scalar key with mapping value, some reject), but the bytes propagated into the canonical spec unchanged at line 21323. Fern CLI 5.37.9's new `--from-openapi` parser correctly flagged this as `Schema property changedForUserName: { type should be an object`. `fixed-at-source`. Single character added (a space after the colon) in `time-off-b.yaml:157`. Source manifest (`docs/openapi/sources/manifest.json`) u…
- **FACT — `time-off.change-status.union-and-note`:** the request-status PATCH `…/time-off/policies/{policyId}/requests/{requestId}` accepts only `APPROVED` / `REJECTED` as the target `status`. `PENDING` and `WITHDRAWN` are read-only request states the wire rejects as a target. The generated `RequestStatusType` (`PENDING|APPROVED|REJECTED|ALL`) is a search-filter union, not the valid set of status TARGETS. `compensated` (2026-06-20). The status union is restricted at the input layer to `z.enum(["APPROVED","REJECTED"])`; the note-required branch is now live-verified optional and bound through a clean typed body-envelope form (the `wireBody` escape was dropped after the 2026-06-21 upstream note…
- **FACT — `time-off.request.status.schema-collision`:** real shape is ```json { "statusType": "APPROVED", "changedByUserId": "64621fae…", "changedByUserName": "Firstname Lastname", "changedForUserName": "Firstname Lastname", "changedAt": "2026-05-17T23:51:17.160269150Z", "note": null } ``` For PENDING, `changedByUserId` and `changedAt` come back as `null` but the keys are still present. **No `createdBy` field exists at any level.** **`createdAt` lives at top level**, not under `status` — captured from a separate probe on the same record. `fixed-in-canonical-generator`. The inline status definition lived in `docs/openapi/sources/clockify-api-probe-lab/openapi.yaml` at the `TimeOffRequest` block…
- **FACT — `time-off.requests.update-status.wrong-method-and-field`:** the request status endpoint is PATCH `/time-off/policies/{policyId}/requests/{requestId}` and the wire field is **`status`** (`statusType` only appears in responses). The flat `/time-off/requests/{requestId}/status` route 404s. `compensated-in-tool-layer`. The tool now requires `policyId`, calls `changeTimeOffRequestStatus`, and sends `status`. Test: `mcp/tests/sweep-fixes.test.ts`. - Live note: the same policy-scoped path also accepts **DELETE** of a PENDING request — promoted to its own atomic entry below (`time-off.requests.delete.policy-scoped-only-pending`).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_requests_update_status`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`transition`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `time_off_requests.withdraw()` — `deleteTimeOffRequest`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a time off request |
| HTTP | `DELETE /workspaces/{workspaceId}/time-off/policies/{policyId}/requests/{requestId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `policy_id` | `policyId` | `path` | yes | string<br>Represents a policy identifier across the system. | path segment; percent-encode once |
| `request_id` | `requestId` | `path` | yes | string<br>Represents a time off request identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`TimeOffRequestDto`](#schema-timeoffrequestdto) | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `policyId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `requestId`:**

```yaml
type: string
x-clockify-default: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — lifecycle:** withdraw/delete is policy-scoped and valid only while pending.
- **FACT — `time-off-b.yaml.changedForUserName.malformed-inline-yaml`:** in `docs/openapi/sources/clockify-api-probe-lab/openapi-fragments/time-off-b.yaml:157` the line was written without a space after the key colon: `changedForUserName:{ type: string }`. YAML accepts this leniently (some parsers treat it as a scalar key with mapping value, some reject), but the bytes propagated into the canonical spec unchanged at line 21323. Fern CLI 5.37.9's new `--from-openapi` parser correctly flagged this as `Schema property changedForUserName: { type should be an object`. `fixed-at-source`. Single character added (a space after the colon) in `time-off-b.yaml:157`. Source manifest (`docs/openapi/sources/manifest.json`) u…
- **FACT — `time-off.request.status.schema-collision`:** real shape is ```json { "statusType": "APPROVED", "changedByUserId": "64621fae…", "changedByUserName": "Firstname Lastname", "changedForUserName": "Firstname Lastname", "changedAt": "2026-05-17T23:51:17.160269150Z", "note": null } ``` For PENDING, `changedByUserId` and `changedAt` come back as `null` but the keys are still present. **No `createdBy` field exists at any level.** **`createdAt` lives at top level**, not under `status` — captured from a separate probe on the same record. `fixed-in-canonical-generator`. The inline status definition lived in `docs/openapi/sources/clockify-api-probe-lab/openapi.yaml` at the `TimeOffRequest` block…
- **FACT — `time-off.requests.delete.policy-scoped-only-pending`:** only the policy-scoped DELETE works — it returns **200** and removes a PENDING request; the flat `DELETE /time-off/requests/{requestId}` **404s** (and a `…/status` PATCH to `WITHDRAWN` 404s). Only PENDING is deletable; terminal APPROVED/REJECTED requests have no delete path (a REJECTED request stays; rejecting an APPROVED one only moves it to the undeletable REJECTED pile — the web-UI "withdraw" is likewise pending-only). Net: the ~196 approved/rejected sandbox requests are permanent litter; only PENDING ones are removable. `createTimeOffRequest` on a DAYS policy wants `{note, timeOffPeriod:{period:{start,days}}}` and returns PENDING when…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_time_off_requests_withdraw`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`time_entitlement`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

## Resource: `user_groups`

### `user_groups.add_members()` — `addUsersToGroup`

| Field | Reconciled value |
|---|---|
| Behavior | Add users to a group |
| HTTP | `POST /workspaces/{workspaceId}/user-groups/{groupId}/users` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `group_id` | `groupId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AddUserToGroupRequest`](#schema-addusertogrouprequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`UserGroupDtoV1`](#schema-usergroupdtov1) | object envelope; item arrays: `teamManagers`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `groupId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_user_groups_add_members`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`multi-entity`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `user_groups.create()` — `addNewGroup`

| Field | Reconciled value |
|---|---|
| Behavior | Add a new group |
| HTTP | `POST /workspaces/{workspaceId}/user-groups` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UserGroupRequest`](#schema-usergrouprequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`UserGroupDtoV1`](#schema-usergroupdtov1) | object envelope; item arrays: `teamManagers`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_user_groups_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `user_groups.delete()` — `deleteGroup`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a group |
| HTTP | `DELETE /workspaces/{workspaceId}/user-groups/{groupId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `group_id` | `groupId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`UserGroupDtoV1`](#schema-usergroupdtov1) | object envelope; item arrays: `teamManagers`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `groupId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_user_groups_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `user_groups.list()` — `findAllGroupsOnWorkspace`

| Field | Reconciled value |
|---|---|
| Behavior | Find all groups on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/user-groups` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `project_id` | `project-id` | `query` | no | string<br>If provided, you'll get a filtered list of groups that matches the string provided in their project id. | single query value; omit only when `None` |
| `name` | `name` | `query` | no | string<br>If provided, you'll get a filtered list of groups that matches the string provided in their name. | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | [`UserGroupSortColumn`](#schema-usergroupsortcolumn)<br>Column to be used as the sorting criteria. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | [`UserGroupsSortOrder`](#schema-usergroupssortorder)<br>Sorting mode. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `include_team_managers` | `includeTeamManagers` | `query` | no | boolean<br>If provided, you'll get a list of team managers assigned to this user group. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`UserGroupDtoV1`](#schema-usergroupdtov1)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter query `project-id`:**

```yaml
type: string
```

**parameter query `name`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `includeTeamManagers`:**

```yaml
default: false
type: boolean
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/UserGroupDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_user_groups_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `user_groups.remove_member()` — `removeUserFromGroup`

| Field | Reconciled value |
|---|---|
| Behavior | Remove a user from a group |
| HTTP | `DELETE /workspaces/{workspaceId}/user-groups/{groupId}/users/{userId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |
| `group_id` | `groupId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`UserGroupDtoV1`](#schema-usergroupdtov1) | object envelope; item arrays: `teamManagers`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `userId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `groupId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_user_groups_remove_member`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `user_groups.update()` — `updateGroup`

| Field | Reconciled value |
|---|---|
| Behavior | Update a group |
| HTTP | `PUT /workspaces/{workspaceId}/user-groups/{groupId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `group_id` | `groupId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UserGroupRequest`](#schema-usergrouprequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`UserGroupDtoV1`](#schema-usergroupdtov1) | object envelope; item arrays: `teamManagers`, `userIds` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-clockify-default: '##default'
```

**parameter path `groupId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_user_groups_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `users`

### `users.add_limited_to_workspace()` — `addLimitedUsersWithInfo`

| Field | Reconciled value |
|---|---|
| Behavior | No source summary; use operation ID and schema only. |
| HTTP | `POST /workspaces/{workspaceId}/limited-users` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `probe-documented` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AddLimitedUsersRequest`](#schema-addlimitedusersrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | object | object |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
additionalProperties: true
type: object
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_add_limited_to_workspace`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`multi-entity`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **MEDIUM**.
- Source evidence classes: `probe-fragment`.
- **UNRESOLVED:** Operation success is not in the `live-success` bucket (`probe-documented`); keep the SDK method but do not expose an MCP write until a controlled success probe exists.

### `users.add_to_workspace()` — `addUserToWorkspace`

| Field | Reconciled value |
|---|---|
| Behavior | Add user to a workspace |
| HTTP | `POST /workspaces/{workspaceId}/users` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `probe-documented` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `send_email` | `send-email` | `query` | yes | string enum["true", "false"]<br>Indicates whether to send an email when user is added to the workspace. | single query value; omit only when `None` |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`AddUserToWorkspaceRequest`](#schema-addusertoworkspacerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter query `send-email`:**

```yaml
default: 'true'
enum:
- 'true'
- 'false'
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_add_to_workspace`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **MEDIUM**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `probe-fragment`, `real-openapi`.
- **UNRESOLVED:** Operation success is not in the `live-success` bucket (`probe-documented`); keep the SDK method but do not expose an MCP write until a controlled success probe exists.

### `users.filter()` — `filterWorkspaceUsers`

| Field | Reconciled value |
|---|---|
| Behavior | Filter workspace users |
| HTTP | `POST /workspaces/{workspaceId}/users/info` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UserFilterRequest`](#schema-userfilterrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`UserDtoV1`](#schema-userdtov1)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/UserDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_filter`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `users.grant_manager_role()` — `giveUserManagerRole`

| Field | Reconciled value |
|---|---|
| Behavior | Give manager role to a user |
| HTTP | `POST /workspaces/{workspaceId}/users/{userId}/roles` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ManagerRoleRequest`](#schema-managerrolerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | array[[`RoleAssignmentDtoV1`](#schema-roleassignmentdtov1)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**response `201` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/RoleAssignmentDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_grant_manager_role`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `users.list()` — `findWorkspaceUsers`

| Field | Reconciled value |
|---|---|
| Behavior | Find all users on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/users` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `email` | `email` | `query` | no | string<br>Filters users by email substring. | single query value; omit only when `None` |
| `project_id` | `project-id` | `query` | no | string<br>If provided, returns users that have access to the project. | single query value; omit only when `None` |
| `status` | `status` | `query` | no | string enum["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]<br>Filters users with the corresponding status. | single query value; omit only when `None` |
| `account_statuses` | `account-statuses` | `query` | no | string<br>Filters users with the corresponding account status filter. | single query value; omit only when `None` |
| `name` | `name` | `query` | no | string<br>Filters users by name substring. | single query value; omit only when `None` |
| `sort_column` | `sort-column` | `query` | no | string enum["ID", "EMAIL", "NAME", "NAME_LOWERCASE", "ACCESS", "HOURLYRATE", "COSTRATE"]<br>Sorting column criteria. Default value: EMAIL | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"]<br>Sorting mode. Default value: ASCENDING | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `memberships` | `memberships` | `query` | no | string enum["ALL", "NONE", "WORKSPACE", "PROJECT", "USERGROUP"]<br>If provided, returns users along with workspaces, groups, or projects they have access to. Default value is NONE. | single query value; omit only when `None` |
| `include_roles` | `include-roles` | `query` | yes | boolean<br>If true, each user's detailed manager roles are included. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`UserDtoV1`](#schema-userdtov1)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter query `email`:**

```yaml
type: string
```

**parameter query `project-id`:**

```yaml
type: string
```

**parameter query `status`:**

```yaml
enum:
- PENDING
- ACTIVE
- DECLINED
- INACTIVE
- ALL
type: string
```

**parameter query `account-statuses`:**

```yaml
type: string
```

**parameter query `name`:**

```yaml
type: string
```

**parameter query `sort-column`:**

```yaml
enum:
- ID
- EMAIL
- NAME
- NAME_LOWERCASE
- ACCESS
- HOURLYRATE
- COSTRATE
type: string
```

**parameter query `sort-order`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**parameter query `memberships`:**

```yaml
enum:
- ALL
- NONE
- WORKSPACE
- PROJECT
- USERGROUP
type: string
```

**parameter query `include-roles`:**

```yaml
default: false
type: boolean
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/UserDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — `users.list.settings-always-present-null-when-unset`:** the `settings` key is **always present** in every member's record. For a user without settings populated yet, the value is explicit `null`, never an absent key. `documented`.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `users.list_managers()` — `findUserTeamManagers`

| Field | Reconciled value |
|---|---|
| Behavior | Find user's team manager |
| HTTP | `GET /workspaces/{workspaceId}/users/{userId}/managers` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |
| `sort_column` | `sort-column` | `query` | no | string enum["ID", "EMAIL", "NAME", "NAME_LOWERCASE", "ACCESS", "HOURLYRATE", "COSTRATE"]<br>Sorting column criteria. | single query value; omit only when `None` |
| `sort_order` | `sort-order` | `query` | no | string enum["ASCENDING", "DESCENDING"]<br>Sorting mode. | single query value; omit only when `None` |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `page_size` | `page-size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`UserDtoV1`](#schema-userdtov1)] | bare array |

**Pagination:** page=`page`; page size=`page-size`; `Last-Page` response header is authoritative; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**parameter query `sort-column`:**

```yaml
enum:
- ID
- EMAIL
- NAME
- NAME_LOWERCASE
- ACCESS
- HOURLYRATE
- COSTRATE
type: string
```

**parameter query `sort-order`:**

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

**parameter query `page`:**

```yaml
default: 1
format: int32
type: integer
```

**parameter query `page-size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/UserDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…
- **FACT — `gen-clockify-openapi.pagination-params-stamped`:** the live API accepts `?page=N&page-size=M` and returns a `Last-Page: <bool>` header on 11 *additional* list endpoints whose source-spec declarations omit those params. Probe evidence (raw JSON bodies + raw response headers) saved as `probes/20260524-pagination-<endpoint>.{json,hdr}` for: approval-requests, clients, tags, user-groups, custom-fields, holidays, scheduling-assignments-all, user-time-entries, invoice-payments, project-custom-fields, project-tasks. Three additional endpoints from the array-returning-GET survey were probed but skipped from the stamping list: `/workspaces` (top-level) ignores `page-size` and returns the full colle…
- **FACT — evidence anchor:** `pagination.last-page-header.live-audit-2026-05-25` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_list_managers`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `users.me()` — `getCurrentUser`

| Field | Reconciled value |
|---|---|
| Behavior | Get currently logged-in user's info |
| HTTP | `GET /user` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `include_memberships` | `include-memberships` | `query` | no | boolean<br>If set to true, memberships will be included. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`UserDtoV1`](#schema-userdtov1) | object envelope; item arrays: `customFields`, `memberships`, `roles` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter query `include-memberships`:**

```yaml
default: false
type: boolean
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_me`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `users.revoke_manager_role()` — `removeUserManagerRole`

| Field | Reconciled value |
|---|---|
| Behavior | Remove user's manager role |
| HTTP | `DELETE /workspaces/{workspaceId}/users/{userId}/roles` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`ManagerRoleRequest`](#schema-managerrolerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `204` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_revoke_manager_role`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`access_control`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `users.update_cost_rate()` — `updateUserCostRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update a user's cost rate |
| HTTP | `PUT /workspaces/{workspaceId}/users/{userId}/cost-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateCostRateRequest`](#schema-updatecostraterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `userId`:**

```yaml
example: 89b687e29ae1f428e7ebe912
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `rates.put-minor-units-no-get`:** rates are PUTs of an integer **minor-unit** `{amount}` body; **GET on a rate path 405s** (discover the current value from a membership/project doc). Per-scope endpoints: per-project member `…/projects/{p}/users/{u}/{hourly-rate|cost-rate}`; Team-section workspace member `…/users/{u}/{hourly-rate|cost-rate}`; task `…/projects/{p}/tasks/{t}/{cost-rate|hourly-rate}`. The project **default** rate has NO standalone endpoint in the addon's experience — it set `hourlyRate`/`costRate` in the project create/update BODY. `compensated-in-tool-layer` for the LIVE-VERIFIED member/task rates (2026-06-14); the project-DEFAULT rate stays `open`. Shipped t…
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_update_cost_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `users.update_custom_field_value()` — `updateUserCustomFieldValue`

| Field | Reconciled value |
|---|---|
| Behavior | Update a user's custom field |
| HTTP | `PUT /workspaces/{workspaceId}/users/{userId}/custom-field/{customFieldId}/value` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |
| `custom_field_id` | `customFieldId` | `path` | yes | string<br>Represents a custom field identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateUserCustomFieldValueRequest`](#schema-updateusercustomfieldvaluerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | value | unknown |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `userId`:**

```yaml
type: string
```

**parameter path `customFieldId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_update_custom_field_value`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-openapi`, `probe-supplement`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `users.update_hourly_rate()` — `updateUserHourlyRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update a user's hourly rate |
| HTTP | `PUT /workspaces/{workspaceId}/users/{userId}/hourly-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateUserHourlyRateRequest`](#schema-updateuserhourlyraterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `userId`:**

```yaml
example: 89b687e29ae1f428e7ebe912
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…
- **FACT — `money.amount-units.expenses-major-invoices-minor`:** units are NOT uniform — invoice, invoice-payment, and rate request/response fields are **minor** (cents) on the wire; an expense create/update `amount` is **MAJOR** (dollars), while the expense response `total` is **MINOR** (cents). An invoice item `unitPrice` is a third scale, minor×100 (Clockify computes `amount = unitPrice × quantity / 100`). `compensated-in-wrapper`. Shipped here as `wrapper/money.ts` (`toMinor`/`toMajor`, `expenseAmountToWire`, `CLOCKIFY_AMOUNT_UNITS`, `invoiceItemUnitPrice*`). Expense request `amount` uses the explicit `expenseAmountToWire` major-unit pass-through; feeding that field's `"major"` wire label to `toMino…
- **FACT — `rates.put-minor-units-no-get`:** rates are PUTs of an integer **minor-unit** `{amount}` body; **GET on a rate path 405s** (discover the current value from a membership/project doc). Per-scope endpoints: per-project member `…/projects/{p}/users/{u}/{hourly-rate|cost-rate}`; Team-section workspace member `…/users/{u}/{hourly-rate|cost-rate}`; task `…/projects/{p}/tasks/{t}/{cost-rate|hourly-rate}`. The project **default** rate has NO standalone endpoint in the addon's experience — it set `hourlyRate`/`costRate` in the project create/update BODY. `compensated-in-tool-layer` for the LIVE-VERIFIED member/task rates (2026-06-14); the project-DEFAULT rate stays `open`. Shipped t…
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_update_hourly_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`financial`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `users.update_status()` — `updateUserStatus`

| Field | Reconciled value |
|---|---|
| Behavior | Update a user's status |
| HTTP | `PUT /workspaces/{workspaceId}/users/{userId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `user_id` | `userId` | `path` | yes | string<br>Represents a user identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateUserStatusRequest`](#schema-updateuserstatusrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `userId`:**

```yaml
example: 89b687e29ae1f428e7ebe912
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_users_update_status`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `webhooks`

### `webhooks.create()` — `createWebhook`

| Field | Reconciled value |
|---|---|
| Behavior | Create a webhook |
| HTTP | `POST /workspaces/{workspaceId}/webhooks` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`WebhookRequest`](#schema-webhookrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`WebhookDtoV1`](#schema-webhookdtov1) | object envelope; item arrays: `triggerSource` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `webhook.create.name-required-on-api-key-not-addon`:** `name` requiredness on `POST /workspaces/{id}/webhooks` is **auth-scheme-dependent** (maintainer-confirmed 2026-06-22): - **API key** (user-created webhooks, `X-Api-Key`) — `name` is REQUIRED. - **Addon token** (addon-created webhooks) — `name` is NOT required. The same `required[]` over-specifies in the other direction too: `triggerSource` is accepted EMPTY for a workspace-scoped event (the 2026-06-21 live probe sent `triggerSource:[]` and got 201), so `required[]` is not a reliable per-field oracle for this schema.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`single target`; sensitivity=`external_delivery`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.delete()` — `deleteWebhook`

| Field | Reconciled value |
|---|---|
| Behavior | Delete a webhook |
| HTTP | `DELETE /workspaces/{workspaceId}/webhooks/{webhookId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `webhook_id` | `webhookId` | `path` | yes | string<br>Represents a webhook identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `—` | `none` | — | none |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `webhookId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_delete`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`delete`; blast radius=`single target`; sensitivity=`external_delivery`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.get()` — `getWebhookById`

| Field | Reconciled value |
|---|---|
| Behavior | Get a specific webhook by ID |
| HTTP | `GET /workspaces/{workspaceId}/webhooks/{webhookId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `webhook_id` | `webhookId` | `path` | yes | string<br>Represents a webhook identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`WebhookDtoV1`](#schema-webhookdtov1) | object envelope; item arrays: `triggerSource` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `webhookId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.list()` — `getWebhooksOnWorkspace`

| Field | Reconciled value |
|---|---|
| Behavior | Get all webhooks on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/webhooks` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `type` | `type` | `query` | no | [`WebhookType`](#schema-webhooktype)<br>Represents a webhook type. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`WebhookCollectionDtoV1`](#schema-webhookcollectiondtov1) | object envelope; item arrays: `webhooks` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.list_event_statuses()` — `getWebhookEventStatusesWithLatestLog`

| Field | Reconciled value |
|---|---|
| Behavior | Get webhook event statuses for a webhook |
| HTTP | `GET /workspaces/{workspaceId}/webhooks/{webhookId}/statuses` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `operationId-derived` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `webhook_id` | `webhookId` | `path` | yes | string<br>Represents a webhook identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `size` | `size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |
| `statuses` | `statuses` | `query` | no | string enum["SUCCEEDED", "RETRYING", "FAILED"]<br>Represents a filter for webhook event status. | single query value; omit only when `None` |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`WebhookEventStatusWithLatestLogDtoV1`](#schema-webhookeventstatuswithlatestlogdtov1)] | bare array |

**Pagination:** page=`page`; page size=`size`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
description: Represents a workspace identifier across the system.
example: 64a687e29ae1f428e7ebe303
type: string
```

**parameter path `webhookId`:**

```yaml
description: Represents a webhook identifier across the system.
example: 6973710805e44c5a46763239
type: string
```

**parameter query `page`:**

```yaml
default: 0
description: Page number.
example: 1
format: int32
type: integer
```

**parameter query `size`:**

```yaml
default: 50
description: Page size.
example: 50
format: int32
minimum: 1
type: integer
```

**parameter query `statuses`:**

```yaml
enum:
- SUCCEEDED
- RETRYING
- FAILED
type: string
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/WebhookEventStatusWithLatestLogDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `fern.x-fern-sdk-method-name.drops-resource-modules`:** stamping `x-fern-sdk-method-name` on 135 of 193 operations via a generator post-processor (heuristic deriving list / get / create / update / delete / partialUpdate / archive from method + URL shape) caused Fern's TS generator to **silently drop 12 entire resource modules** from the output: - tags, holidays, expenses, expenseCategories, expenseReport, files, memberProfiles, reports, sharedReport, timeOffPolicies, auditLogReport, entityChangesExperimental. `deferred-needs-upstream-investigation`. The `stamp_sdk_method_name!` call has been removed from the generator's per-op finalization loop and the `derive_sdk_method_name` + `stamp_sdk_meth…
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_list_event_statuses`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `live-success`, `probe-fragment`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.list_for_addon()` — `getAddonWebhooksOnWorkspace`

| Field | Reconciled value |
|---|---|
| Behavior | Get all webhooks for addon on a workspace |
| HTTP | `GET /workspaces/{workspaceId}/addons/{addonId}/webhooks` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `addon_id` | `addonId` | `path` | yes | string<br>Represents an addon identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`WebhookCollectionDtoV1`](#schema-webhookcollectiondtov1) | object envelope; item arrays: `webhooks` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `addonId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_list_for_addon`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.rotate_token()` — `patchWorkspacesWorkspaceIdWebhooksWebhookIdToken`

| Field | Reconciled value |
|---|---|
| Behavior | Generate a new webhook token |
| HTTP | `PATCH /workspaces/{workspaceId}/webhooks/{webhookId}/token` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string | path segment; percent-encode once |
| `webhook_id` | `webhookId` | `path` | yes | string | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`WebhooksWebhook2`](#schema-webhookswebhook2) | object envelope; item arrays: `triggerSource` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
```

**parameter path `webhookId`:**

```yaml
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_rotate_token`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`partial_update`; blast radius=`single target`; sensitivity=`external_delivery`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `live-success`, `probe-fragment`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.search_logs()` — `getWebhookLogs`

| Field | Reconciled value |
|---|---|
| Behavior | Get logs for a webhook |
| HTTP | `POST /workspaces/{workspaceId}/webhooks/{webhookId}/logs` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `webhook_id` | `webhookId` | `path` | yes | string<br>Represents a webhook identifier across the system. | path segment; percent-encode once |
| `page` | `page` | `query` | no | integer<int32><br>Page number. | single query value; omit only when `None` |
| `size` | `size` | `query` | no | integer<int32><br>Page size. | single query value; omit only when `None` |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`WebhookLogsRequest`](#schema-webhooklogsrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`WebhookLogDtoV1`](#schema-webhooklogdtov1)] | bare array |

**Pagination:** page=`page`; page size=`size`; bare array.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `webhookId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter query `page`:**

```yaml
default: 0
format: int32
type: integer
```

**parameter query `size`:**

```yaml
default: 50
format: int32
minimum: 1
type: integer
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/WebhookLogDtoV1'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_search_logs`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `webhooks.update()` — `updateWebhook`

| Field | Reconciled value |
|---|---|
| Behavior | Update a webhook |
| HTTP | `PUT /workspaces/{workspaceId}/webhooks/{webhookId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |
| `webhook_id` | `webhookId` | `path` | yes | string<br>Represents a webhook identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`WebhookRequest`](#schema-webhookrequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`WebhookDtoV1`](#schema-webhookdtov1) | object envelope; item arrays: `triggerSource` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

**parameter path `webhookId`:**

```yaml
type: string
x-sourceDefault: '##default'
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_webhooks_update`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`single target`; sensitivity=`external_delivery`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Resource: `workspaces`

### `workspaces.create()` — `addWorkspace`

| Field | Reconciled value |
|---|---|
| Behavior | Add a workspace |
| HTTP | `POST /workspaces` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `probe-documented` |
| Existing TS naming evidence | `explicit` |

#### Parameters

None.

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`CreateWorkspaceRequest`](#schema-createworkspacerequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `201` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_workspaces_create`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`create_or_action`; blast radius=`workspace-wide configuration`; sensitivity=`ordinary_workspace_data`; replacement risk=`none`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **MEDIUM**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `probe-fragment`, `real-openapi`.
- **UNRESOLVED:** Operation success is not in the `live-success` bucket (`probe-documented`); keep the SDK method but do not expose an MCP write until a controlled success probe exists.

### `workspaces.get()` — `getWorkspaceInfo`

| Field | Reconciled value |
|---|---|
| Behavior | Get workspace info |
| HTTP | `GET /workspaces/{workspaceId}` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

#### Corrected behavior, lifecycle, and evidence

- No operation-specific discrepancy anchor is assigned. The corrected OpenAPI remains the implementation source for shape and routing.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_workspaces_get`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `workspaces.list()` — `getAllMyWorkspaces`

| Field | Reconciled value |
|---|---|
| Behavior | Get all my workspaces |
| HTTP | `GET /workspaces` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `non-mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `roles` | `roles` | `query` | no | array[string enum["WORKSPACE_ADMIN", "OWNER", "TEAM_MANAGER", "PROJECT_MANAGER"]]<br>If provided, returns workspaces where the user has any of the specified roles. Owners are not counted as admins when filtering. | repeated query key |

#### Request body

None.

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | array[[`Workspace`](#schema-workspace)] | bare array |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter query `roles`:**

```yaml
items:
  enum:
  - WORKSPACE_ADMIN
  - OWNER
  - TEAM_MANAGER
  - PROJECT_MANAGER
  type: string
type: array
```

**response `200` `application/json`:**

```yaml
items:
  $ref: '#/components/schemas/Workspace'
type: array
```

#### Corrected behavior, lifecycle, and evidence

- **FACT — `deferred-list-endpoints.not-paginated-or-not-live`:** 1. `GET /workspaces?page=1&page-size=1` returned **all 28** records (200 102 bytes). Also tried `?per_page=1`, `?size=1`, `?limit=1`, `?pageSize=1` — every variant returned the full 28-record list unchanged. The endpoint is a collection enumerator with no server-side paging. 2. `GET /workspaces/{wsId}/balance?policyId=<real>` returned `HTTP 404 {"message":"No static resource v1/workspaces/{wsId}/balance.","code":3000}`. The bare `/balance` route does not exist on the live API. The granular routes `/workspaces/{wsId}/time-off/balance/policy/{policyId}` and `/workspaces/{wsId}/time-off/balance/user/{userId}` are the live equivalents and are…

#### MCP and write-safety disposition

- Proposed tool name: `clockify_workspaces_list`.
- Eligibility: **READ-ELIGIBLE**.
- Tool annotations: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=true`. These are metadata; `ReadOnlyExecutor` is the boundary.

#### Confidence and unresolved items

- Confidence: **HIGH**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- No operation-specific unresolved item blocks the raw SDK method.

### `workspaces.update_billable_rate()` — `updateWorkspaceBillableRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update workspace billable rate |
| HTTP | `PUT /workspaces/{workspaceId}/hourly-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateWorkspaceBillableRateRequest`](#schema-updateworkspacebillableraterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_workspaces_update_billable_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`workspace-wide configuration`; sensitivity=`ordinary_workspace_data`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

### `workspaces.update_cost_rate()` — `updateWorkspaceCostRate`

| Field | Reconciled value |
|---|---|
| Behavior | Update workspace cost rate |
| HTTP | `PUT /workspaces/{workspaceId}/cost-rate` |
| Service | `REGULAR` · `https://api.clockify.me/api/v1` |
| Authentication | Exactly one of `X-Api-Key` or `X-Addon-Token`; injected only after host validation |
| Mutation | `mutating` |
| Live evidence bucket | `live-success` |
| Existing TS naming evidence | `explicit` |

#### Parameters

| Python | Wire | Location | Required | Schema | Serialization |
|---|---|---|:---:|---|---|
| `workspace_id` | `workspaceId` | `path` | yes | string<br>Represents a workspace identifier across the system. | path segment; percent-encode once |

#### Request body

Required: **yes**.

| Content type | Schema | Encoding notes |
|---|---|---|
| `application/json` | [`UpdateCostRateRequest`](#schema-updatecostraterequest) | standard encoding for content type |

#### Successful response

| Status | Content type | Decoder | Schema / shape | Envelope |
|---:|---|---|---|---|
| `200` | `application/json` | `json` | [`Workspace`](#schema-workspace) | object envelope; item arrays: `currencies`, `features`, `memberships` |

**Pagination:** not declared as transport pagination.

#### Exact inline schema fragments

Component `$ref` targets are defined in the component-schema appendix. The following fragments are inline in the corrected OpenAPI and are reproduced exactly:

**parameter path `workspaceId`:**

```yaml
example: 64a687e29ae1f428e7ebe303
type: string
```

#### Corrected behavior, lifecycle, and evidence

- **FACT/INFERENCE — replacement risk:** conservative: treat as replacement until live-proven otherwise.
- **FACT — evidence anchor:** `surface.audit.2026-06-23` (see `spec/evidence/discrepancies.md` or the operation evidence map).
- **FACT — wire units:** Money/rate fields use raw upstream integer units; no currency scaling is applied.

#### MCP and write-safety disposition

- Proposed tool name: `clockify_workspaces_update_cost_rate`.
- Eligibility: **WRITE-DEFERRED**.
- Mutation dimensions: effect=`replace_or_set`; blast radius=`workspace-wide configuration`; sensitivity=`financial`; replacement risk=`conservative: treat as replacement until live-proven otherwise`; automatic retry=`forbidden`.
- Proposed annotations after write approval: `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true`.

#### Confidence and unresolved items

- Confidence: **HIGH for transport; MEDIUM for flagged semantics**.
- Source evidence classes: `aiii-openapi`, `doc-md`, `live-success`, `probe-fragment`, `probe-openapi`, `real-openapi`.
- **UNRESOLVED:** PUT omission behavior is not independently proven for this operation; the raw SDK sends exactly the caller body and MCP preview must label it potential replacement.

## Reachable component schema catalog

This appendix preserves the exact corrected JSON Schema fragments needed by the 168 operations. The implementation importer may translate these fragments into committed `TypedDict`, `Literal`, and `TypeAlias` definitions. It must not silently strengthen or weaken them.

<a id="schema-accountstatus"></a>
### `AccountStatus`

```yaml
description: Represents account status enum.
enum:
- ACTIVE
- PENDING_EMAIL_VERIFICATION
- DELETED
- NOT_REGISTERED
- LIMITED
- LIMITED_DELETED
type: string
```

<a id="schema-addinvoiceitemrequest"></a>
### `AddInvoiceItemRequest`

```yaml
example:
  applyTaxes: TAX1TAX2
  description: This is a description of an invoice item.
  itemType: Service
  quantity: 10000
  unitPrice: 500
properties:
  applyTaxes:
    $ref: '#/components/schemas/ApplyTaxes'
  description:
    default: '##default'
    description: Represents an invoice item description.
    type: string
  itemType:
    default: '##default'
    description: Represents an item type.
    minLength: 1
    type: string
  quantity:
    description: Represents an item quantity.
    format: int64
    type: integer
  unitPrice:
    description: Represents an item unit price.
    format: int64
    type: integer
required:
- applyTaxes
- description
- itemType
- quantity
- unitPrice
type: object
```

<a id="schema-addinvoicepaymentrequest"></a>
### `AddInvoicePaymentRequest`

```yaml
example:
  amount: 100
  note: This is a sample note for this invoice payment.
  paymentDate: '2021-01-01T12:00:00Z'
properties:
  amount:
    description: Represents an invoice payment amount as long.
    format: int64
    minimum: 1
    type: integer
  note:
    default: '##default'
    description: Represents an invoice payment note.
    maxLength: 1000
    minLength: 0
    type: string
  paymentDate:
    default: '##default'
    description: Represents an invoice payment date in yyyy-MM-ddThh:mm:ssZ format.
    type: string
required:
- amount
type: object
```

<a id="schema-addlimitedusersrequest"></a>
### `AddLimitedUsersRequest`

```yaml
properties:
  users:
    items:
      $ref: '#/components/schemas/LimitedUserRequest'
    maxItems: 250
    minItems: 1
    type: array
required:
- users
type: object
```

<a id="schema-addusertogrouprequest"></a>
### `AddUserToGroupRequest`

```yaml
description: Request body for adding a user to a group.
example:
  userId: 5a0ab5acb07987125438b60f
properties:
  userId:
    description: Represents a user identifier across the system.
    type: string
    x-clockify-default: '##default'
required:
- userId
type: object
```

<a id="schema-addusertoworkspacerequest"></a>
### `AddUserToWorkspaceRequest`

```yaml
additionalProperties: false
properties:
  email:
    description: Represents an email address of the user.
    format: email
    minLength: 1
    type: string
required:
- email
type: object
```

<a id="schema-amountdto"></a>
### `AmountDto`

```yaml
additionalProperties: true
properties:
  type:
    $ref: '#/components/schemas/AmountType'
  value:
    description: Amount value.
    type: number
type: object
```

<a id="schema-amounttype"></a>
### `AmountType`

```yaml
description: Report amount type.
enum:
- EARNED
- COST
- PROFIT
- HIDE_AMOUNT
- EXPORT
type: string
```

<a id="schema-applytaxes"></a>
### `ApplyTaxes`

```yaml
description: Represents item applyTaxes type.
enum:
- TAX1
- TAX2
- TAX1TAX2
- NONE
type: string
```

<a id="schema-approvaldaterangedto"></a>
### `ApprovalDateRangeDto`

```yaml
properties:
  end:
    format: date-time
    type: string
  start:
    format: date-time
    type: string
type: object
```

<a id="schema-approvalperiod"></a>
### `ApprovalPeriod`

```yaml
description: Approval period. It must match the workspace approval period setting.
enum:
- WEEKLY
- SEMI_MONTHLY
- MONTHLY
type: string
```

<a id="schema-approvalrequestcreatordtov1"></a>
### `ApprovalRequestCreatorDtoV1`

```yaml
description: Represents approval request creator object.
properties:
  userEmail:
    description: Represents user email.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
  userName:
    description: Represents user name.
    type: string
type: object
```

<a id="schema-approvalrequestdtov1"></a>
### `ApprovalRequestDtoV1`

```yaml
description: Represents a valid approval request data transfer object.
properties:
  creator:
    $ref: '#/components/schemas/ApprovalRequestCreatorDtoV1'
  dateRange:
    $ref: '#/components/schemas/DateRangeDto'
  id:
    description: Represents approval request identifier across the workspace.
    type: string
  owner:
    $ref: '#/components/schemas/ApprovalRequestOwnerDtoV1'
  status:
    $ref: '#/components/schemas/ApprovalRequestStatusDtoV1'
  type:
    description: Represents approval request type.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-approvalrequestfilterstate"></a>
### `ApprovalRequestFilterState`

```yaml
enum:
- PENDING
- APPROVED
- WITHDRAWN_APPROVAL
type: string
```

<a id="schema-approvalrequestlistitem"></a>
### `ApprovalRequestListItem`

```yaml
properties:
  approvalRequest:
    $ref: '#/components/schemas/ApprovalRequestDtoV1'
  approvedTime:
    $ref: '#/components/schemas/DurationString'
  billableAmount:
    format: double
    type: number
  billableTime:
    $ref: '#/components/schemas/DurationString'
  breakTime:
    $ref: '#/components/schemas/DurationString'
  costAmount:
    description: Represents an amount.
    format: double
    type: number
  entries:
    description: Represents a list of time entry info data transfer objects.
    items:
      $ref: '#/components/schemas/TimeEntryInfoDto'
    type: array
  expenseTotal:
    description: Represents an amount.
    format: double
    type: number
  expenses:
    description: Represents a list of expense hydrated data transfer objects.
    items:
      $ref: '#/components/schemas/ExpenseHydratedDto'
    type: array
  pendingTime:
    $ref: '#/components/schemas/DurationString'
  trackedTime:
    $ref: '#/components/schemas/DurationString'
type: object
```

<a id="schema-approvalrequestownerdtov1"></a>
### `ApprovalRequestOwnerDtoV1`

```yaml
description: Represents approval request owner object.
properties:
  startOfWeek:
    $ref: '#/components/schemas/DayOfWeek'
  timeZone:
    description: Represents time zone.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
  userName:
    description: Represents user name.
    type: string
type: object
```

<a id="schema-approvalrequestsortcolumn"></a>
### `ApprovalRequestSortColumn`

```yaml
enum:
- ID
- USER_ID
- START
- UPDATED_AT
type: string
```

<a id="schema-approvalrequeststate"></a>
### `ApprovalRequestState`

```yaml
enum:
- PENDING
- APPROVED
- WITHDRAWN_SUBMISSION
- WITHDRAWN_APPROVAL
- REJECTED
type: string
```

<a id="schema-approvalrequeststatusdtov1"></a>
### `ApprovalRequestStatusDtoV1`

```yaml
description: Represents approval request status object.
properties:
  note:
    description: Represents an approval request note.
    type: string
  state:
    $ref: '#/components/schemas/ApprovalRequestState'
  updatedAt:
    description: Represents a date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  updatedBy:
    description: Represents user identifier across the system.
    type: string
  updatedByUserName:
    description: Represents user name.
    type: string
type: object
```

<a id="schema-approvalrequesttype"></a>
### `ApprovalRequestType`

```yaml
enum:
- TIMESHEET
- EXPENSE
- TIMESHEET_AND_EXPENSE
type: string
```

<a id="schema-assignremoveusersrequest"></a>
### `AssignRemoveUsersRequest`

```yaml
additionalProperties: false
properties:
  remove:
    default: false
    description: Setting this flag to true will remove the given users from the project.
    type: boolean
  userGroups:
    $ref: '#/components/schemas/ProjectsUserGroupIdsSchema'
  userIds:
    description: Represents array of user ids which should be added/removed.
    items:
      type: string
    type: array
type: object
```

<a id="schema-assignmentlistitem"></a>
### `AssignmentListItem`

```yaml
additionalProperties: false
description: Represents a scheduled assignment returned by the list endpoint.
properties:
  billable:
    default: false
    description: Indicates whether assignment is billable or not.
    type: boolean
  clientId:
    description: Represents client identifier across the system.
    type: string
  clientName:
    description: Represents project name.
    type: string
  hoursPerDay:
    description: Represents number of hours per day as double.
    format: double
    type: number
  id:
    description: Represents assignment identifier across the system.
    type: string
  note:
    description: Represents assignment note.
    type: string
  period:
    $ref: '#/components/schemas/SchedulingDateRangeDto'
  projectArchived:
    type: boolean
  projectBillable:
    type: boolean
  projectColor:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  projectId:
    description: Represents project identifier across the system.
    type: string
  projectName:
    description: Represents project name.
    type: string
  startTime:
    description: Represents start time in hh:mm:ss format.
    example: '10:00:00'
    type: string
  taskId:
    description: Represents task identifier across the system.
    type: string
  taskName:
    description: Represents task name.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
  userName:
    description: Represents user name.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-assignmentperdaydto"></a>
### `AssignmentPerDayDto`

```yaml
additionalProperties: false
description: Represents an assignment-per-day object.
properties:
  date:
    format: date-time
    type: string
  hasAssignment:
    type: boolean
type: object
```

<a id="schema-assignmentsortcolumn"></a>
### `AssignmentSortColumn`

```yaml
enum:
- PROJECT
- USER
- ID
type: string
```

<a id="schema-attendancedto"></a>
### `AttendanceDto`

```yaml
additionalProperties: true
properties:
  break:
    description: Break duration.
    format: int64
    type: integer
  capacity:
    description: Daily work capacity.
    format: int32
    type: integer
  date:
    description: Report date.
    type: string
  endTime:
    description: End time.
    type: string
  hasRunningEntry:
    description: Whether the user has a running entry.
    type: boolean
  imageUrl:
    description: User image URL.
    type: string
  overtime:
    description: Overtime duration.
    format: int64
    type: integer
  remainingCapacity:
    description: Remaining capacity.
    format: int64
    type: integer
  startTime:
    description: Start time.
    type: string
  timeOff:
    description: Time off duration.
    format: int64
    type: integer
  totalDuration:
    description: Total duration.
    format: int64
    type: integer
  userId:
    description: User identifier.
    type: string
  userName:
    description: User name.
    type: string
type: object
```

<a id="schema-attendancefilter"></a>
### `AttendanceFilter`

```yaml
additionalProperties: false
description: Attendance report filter. This filter is valid only on /reports/attendance.
properties:
  breakFilters:
    description: Break duration filters. Values are hours multiplied by 100; e.g. 0.5h is 50.
    items:
      $ref: '#/components/schemas/CompareFilter'
    type: array
  capacityFilters:
    description: Daily work capacity filters. Values are hours multiplied by 100; e.g. 7.5h is 750.
    items:
      $ref: '#/components/schemas/CompareFilter'
    type: array
  endFilters:
    description: End time filters in 24-hour notation.
    items:
      $ref: '#/components/schemas/CompareFilter'
    type: array
  hasTimeOff:
    description: If true, the report includes time off hours.
    type: boolean
  overtimeFilters:
    description: Overtime filters. Values are hours multiplied by 100; e.g. 1.5h is 150.
    items:
      $ref: '#/components/schemas/CompareFilter'
    type: array
  page:
    default: 1
    description: Specifies page number.
    format: int32
    minimum: 1
    type: integer
  pageSize:
    description: Specifies page size.
    format: int32
    minimum: 1
    type: integer
  sortColumn:
    description: Column used for sorting attendance report rows.
    enum:
    - USER
    - DATE
    - START
    - END
    - BREAK
    - WORK
    - CAPACITY
    - OVERTIME
    - TIME_OFF
    type: string
  startFilters:
    description: Start time filters in 24-hour notation.
    items:
      $ref: '#/components/schemas/CompareFilter'
    type: array
  workFilters:
    description: Completed work duration filters. Values are hours multiplied by 100; e.g. 7.5h is 750.
    items:
      $ref: '#/components/schemas/CompareFilter'
    type: array
type: object
x-clockify-report-filter: attendance
```

<a id="schema-attendancereportrequest"></a>
### `AttendanceReportRequest`

```yaml
additionalProperties: false
description: Request payload for generating attendance reports. Only attendanceFilter is accepted as the report-specific
  filter.
properties:
  amountShown:
    description: If provided, returns reports with the provided amount shown.
    enum:
    - EARNED
    - COST
    - PROFIT
    - HIDE_AMOUNT
    - EXPORT
    type: string
  amounts:
    description: Amount columns to include.
    items:
      $ref: '#/components/schemas/AmountType'
    type: array
  approvalState:
    description: If provided, returns reports with the provided approval state.
    enum:
    - APPROVED
    - UNAPPROVED
    - ALL
    type: string
  archived:
    description: Indicates whether the report is archived.
    type: boolean
  attendanceFilter:
    $ref: '#/components/schemas/AttendanceFilter'
  billable:
    description: Indicates whether the report is billable.
    type: boolean
  clients:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  currency:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  customFields:
    description: Time entry custom field filters.
    items:
      $ref: '#/components/schemas/CustomFieldFilter'
    type: array
  dateFormat:
    description: Provide date in format YYYY-MM-DD.
    example: '2018-11-01'
    type: string
  dateRangeEnd:
    description: Strict RFC3339 UTC timestamp with milliseconds, for example 2018-11-01T00:00:00.000Z.
    example: '2018-11-30T23:59:59.999Z'
    minLength: 1
    type: string
  dateRangeStart:
    description: Strict RFC3339 UTC timestamp with milliseconds, for example 2018-11-01T00:00:00.000Z.
    example: '2018-11-01T00:00:00.000Z'
    minLength: 1
    type: string
  dateRangeType:
    description: Date range preset.
    enum:
    - ABSOLUTE
    - TODAY
    - YESTERDAY
    - THIS_WEEK
    - LAST_WEEK
    - PAST_TWO_WEEKS
    - THIS_MONTH
    - LAST_MONTH
    - THIS_YEAR
    - LAST_YEAR
    type: string
  description:
    description: Search term for filtering report entries by description.
    type: string
  exportType:
    description: Export format requested for the report.
    enum:
    - JSON
    - JSON_V1
    - PDF
    - CSV
    - XLSX
    - ZIP
    type: string
  invoicingState:
    description: If provided, returns reports with the provided invoicing state.
    enum:
    - INVOICED
    - UNINVOICED
    - ALL
    type: string
  projects:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  rounding:
    description: Indicates whether report filter rounding is enabled.
    type: boolean
  sortOrder:
    description: Sort order.
    enum:
    - ASCENDING
    - DESCENDING
    type: string
  tags:
    $ref: '#/components/schemas/ContainsTagFilter'
  tasks:
    $ref: '#/components/schemas/ContainsTaskFilter'
  timeFormat:
    description: Provide time in format THH:MM:SS.ssssss.
    example: T00:00:00
    type: string
  timeZone:
    description: Timezone used to interpret dates and times.
    example: Europe/Belgrade
    type: string
  userGroups:
    $ref: '#/components/schemas/ContainsUsersFilter'
  userLocale:
    description: Locale used for report formatting.
    example: en
    type: string
  users:
    $ref: '#/components/schemas/ContainsUsersFilter'
  weekStart:
    description: Configured week start day.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  withoutDescription:
    description: If true, report includes only entries with empty description.
    type: boolean
  zoomLevel:
    description: Report zoom level.
    enum:
    - WEEK
    - MONTH
    - YEAR
    type: string
required:
- dateRangeStart
- dateRangeEnd
- attendanceFilter
type: object
```

<a id="schema-attendancereportresponse"></a>
### `AttendanceReportResponse`

```yaml
additionalProperties: true
description: Attendance report response.
properties:
  entities:
    description: List of attendance report entities.
    items:
      $ref: '#/components/schemas/AttendanceDto'
    type: array
type: object
```

<a id="schema-auditfilter"></a>
### `AuditFilter`

```yaml
additionalProperties: false
description: Audit filter for detailed reports.
properties:
  duration:
    description: Audit duration.
    format: int32
    type: integer
  durationShorter:
    description: Whether audit duration should be treated as shorter than the provided duration.
    type: boolean
  withoutProject:
    description: Whether to filter entries without a project.
    type: boolean
  withoutTask:
    description: Whether to filter entries without a task.
    type: boolean
type: object
```

<a id="schema-auditlogaction"></a>
### `AuditLogAction`

```yaml
enum:
- CREATE_TIME_PERSONAL_TIMER
- CREATE_TIME_PERSONAL_MANUAL
- CREATE_TIME_IMPORT
- CREATE_TIME_KIOSK
- CREATE_TIME_FOR_OTHER
- RESTORE_TIME
- RESTORE_TIME_FOR_OTHER
- UPDATE_TIME_PERSONAL
- UPDATE_TIME_FOR_OTHER
- DELETE_TIME_PERSONAL
- DELETE_TIME_FOR_OTHER
- CREATE_PROJECT
- CREATE_PROJECT_IMPORT
- CREATE_PROJECT_QUICKBOOKS
- UPDATE_PROJECT
- DELETE_PROJECT
- CREATE_TASK
- CREATE_TASK_IMPORT
- UPDATE_TASK
- DELETE_TASK
- CREATE_CLIENT
- CREATE_CLIENT_IMPORT
- CREATE_CLIENT_QUICKBOOKS
- UPDATE_CLIENT
- DELETE_CLIENT
- CREATE_TAG
- CREATE_TAG_IMPORT
- UPDATE_TAG
- DELETE_TAG
- CREATE_EXPENSE
- CREATE_EXPENSE_FOR_OTHER
- RESTORE_EXPENSE
- RESTORE_EXPENSE_FOR_OTHER
- UPDATE_EXPENSE
- UPDATE_EXPENSE_FOR_OTHER
- DELETE_EXPENSE
- DELETE_EXPENSE_FOR_OTHER
type: string
```

<a id="schema-auditlogauthorsfilter"></a>
### `AuditLogAuthorsFilter`

```yaml
type: object
description: Author filter. Include SYSTEM to retrieve system audit logs.
additionalProperties: false
properties:
  authorIds:
    type: array
    uniqueItems: true
    items:
      type: string
    example:
    - SYSTEM
  contains:
    type: string
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    example: DOES_NOT_CONTAIN
```

<a id="schema-auditlogentry"></a>
### `AuditLogEntry`

```yaml
additionalProperties: true
description: Minimal audit log entry shape observed from the audit-log service.
properties:
  action:
    type: string
  content:
    nullable: true
    type: string
  previousContent:
    nullable: true
    type: string
  timestamp:
    format: date-time
    type: string
  userEmail:
    format: email
    type: string
  userId:
    type: string
  userName:
    type: string
  workspaceId:
    type: string
type: object
```

<a id="schema-auditlogrequest"></a>
### `AuditLogRequest`

```yaml
additionalProperties: false
description: Request body accepted by the dedicated audit-log service.
properties:
  actions:
    example:
    - CREATE_PROJECT
    - UPDATE_PROJECT
    items:
      $ref: '#/components/schemas/AuditLogAction'
    minItems: 1
    type: array
    uniqueItems: true
  authors:
    $ref: '#/components/schemas/AuditLogAuthorsFilter'
  end:
    description: Audit window end.
    example: '2026-05-15T23:59:59Z'
    format: date-time
    type: string
  page:
    default: 1
    example: 1
    minimum: 0
    type: integer
  page-size:
    default: 20
    example: 20
    maximum: 50
    minimum: 1
    type: integer
  start:
    description: Audit window start.
    example: '2026-05-14T00:00:00Z'
    format: date-time
    type: string
required:
- actions
- authors
- start
- end
type: object
```

<a id="schema-auditlogresponse"></a>
### `AuditLogResponse`

```yaml
items:
  $ref: '#/components/schemas/AuditLogEntry'
type: array
```

<a id="schema-automaticaccrualdto"></a>
### `AutomaticAccrualDto`

```yaml
description: Represents automatic accrual settings.
properties:
  amount:
    description: Represents automatic accrual's amount.
    format: double
    type: number
  period:
    description: Represents automatic accrual's period.
    enum:
    - MONTH
    - YEAR
    type: string
  timeUnit:
    description: Represents automatic accrual's time unit.
    enum:
    - DAYS
    - HOURS
    type: string
type: object
```

<a id="schema-automaticaccrualrequest"></a>
### `AutomaticAccrualRequest`

```yaml
description: Provide automatic accrual settings.
properties:
  amount:
    description: Represents amount of automatic accrual.
    format: double
    minimum: 0
    type: number
  period:
    description: Represents automatic accrual period.
    enum:
    - MONTH
    - YEAR
    type: string
  timeUnit:
    description: Represents automatic accrual time unit.
    enum:
    - DAYS
    - HOURS
    type: string
required:
- amount
type: object
```

<a id="schema-automaticlockdtov1"></a>
### `AutomaticLockDtoV1`

```yaml
additionalProperties: true
description: Represents an automatic lock object.
properties:
  changeDay:
    description: Represents a day of the week.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  dayOfMonth:
    description: Represents a day of month as integer.
    format: int32
    type: integer
  firstDay:
    description: Represents a day of the week.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  olderThanPeriod:
    description: Represents a time entry automatic lock period enum.
    enum:
    - DAYS
    - WEEKS
    - MONTHS
    type: string
  olderThanValue:
    description: Represents an integer as the criteria for locking time entries.
    format: int32
    type: integer
  type:
    description: Represents a time entry automatic lock type enum.
    enum:
    - WEEKLY
    - MONTHLY
    - OLDER_THAN
    type: string
type: object
```

<a id="schema-automatictimeentrycreationdto"></a>
### `AutomaticTimeEntryCreationDto`

```yaml
description: Represents automatic time entry creation settings.
properties:
  defaultEntities:
    $ref: '#/components/schemas/DefaultEntitiesDto'
  enabled:
    type: boolean
type: object
```

<a id="schema-automatictimeentrycreationrequest"></a>
### `AutomaticTimeEntryCreationRequest`

```yaml
description: Provides automatic time entry creation settings.
properties:
  defaultEntities:
    $ref: '#/components/schemas/PoliciesDefaultEntitiesRequest'
  enabled:
    default: false
    description: Indicates that automatic time entry creation is enabled.
    type: boolean
required:
- defaultEntities
type: object
```

<a id="schema-balanceassignmentv1dto"></a>
### `BalanceAssignmentV1Dto`

```yaml
properties:
  accrued:
    format: double
    type: number
  balance:
    format: double
    type: number
  dateRange:
    $ref: '#/components/schemas/ApprovalDateRangeDto'
  id:
    type: string
  policyId:
    type: string
  userId:
    type: string
  workspaceId:
    type: string
type: object
```

<a id="schema-balancedtov1"></a>
### `BalanceDtoV1`

```yaml
description: Balance data transfer object.
properties:
  balance:
    description: Represents the balance amount of the time unit.
    format: double
    type: number
  id:
    description: Represents balance identifier across the system.
    type: string
  negativeBalanceAmount:
    description: Represents negative balance amount.
    format: double
    type: number
  negativeBalanceLimit:
    default: false
    description: Indicates whether the negative balance limit is allowed.
    type: boolean
  policyArchived:
    default: false
    description: Indicates whether the policy is archived.
    type: boolean
  policyId:
    default: '##default'
    description: Represents policy identifier across the system.
    type: string
  policyName:
    default: '##default'
    description: Represents policy name.
    type: string
  policyTimeUnit:
    $ref: '#/components/schemas/PolicyTimeUnit'
  total:
    description: Represents the total amount.
    format: double
    type: number
  used:
    description: Represents the balance used amount.
    format: double
    type: number
  userId:
    default: '##default'
    description: Represents user identifier across the system.
    type: string
  userName:
    default: '##default'
    description: Represents user's username.
    type: string
  workspaceId:
    default: '##default'
    description: Represents workspace identifier across the system.
    type: string
  negativeBalanceUsed:
    description: Represents the amount of the negative balance that has been used.
    format: double
    type: number
type: object
```

<a id="schema-balancelistresponse"></a>
### `BalanceListResponse`

```yaml
description: Paginated balance list response.
properties:
  balances:
    description: List of balances.
    items:
      $ref: '#/components/schemas/BalanceDtoV1'
    type: array
  count:
    description: Represents the count of balances.
    format: int32
    type: integer
type: object
```

<a id="schema-balancesortcolumn"></a>
### `BalanceSortColumn`

```yaml
description: Valid column for sorting balance results.
enum:
- USER
- POLICY
- USED
- BALANCE
- TOTAL
type: string
```

<a id="schema-balancesortorder"></a>
### `BalanceSortOrder`

```yaml
description: Sort order.
enum:
- ASCENDING
- DESCENDING
type: string
```

<a id="schema-basefilterrequest"></a>
### `BaseFilterRequest`

```yaml
description: Represents a base filter object.
properties:
  contains:
    $ref: '#/components/schemas/ContainsOperator'
  ids:
    description: Represents a list of filter identifiers.
    items:
      type: string
    type: array
    uniqueItems: true
type: object
```

<a id="schema-bulkedittimeentryrequest"></a>
### `BulkEditTimeEntryRequest`

```yaml
description: LIVE VERIFICATION REVEALED - Field 'end' is mandatory for bulk edits on live system, contrary to single-update
  documentation.
properties:
  billable:
    type: boolean
  description:
    type: string
  end:
    format: date-time
    type: string
  id:
    type: string
  projectId:
    type: string
  start:
    format: date-time
    type: string
  taskId:
    type: string
required:
- id
- start
- end
type: object
```

<a id="schema-calculationtype"></a>
### `CalculationType`

```yaml
description: Represents whether tax is calculated as item based or invoice based.
enum:
- INVOICE_BASED
- ITEM_BASED
type: string
```

<a id="schema-changerecurringperiodrequest"></a>
### `ChangeRecurringPeriodRequest`

```yaml
additionalProperties: false
description: Request for changing a recurring assignment period.
properties:
  repeat:
    default: false
    description: Indicates whether assignment is recurring or not.
    type: boolean
  weeks:
    description: Indicates number of weeks for assignment.
    format: int32
    maximum: 99
    minimum: 1
    type: integer
required:
- repeat
- weeks
type: object
```

<a id="schema-changetimeoffrequeststatusrequest"></a>
### `ChangeTimeOffRequestStatusRequest`

```yaml
example:
  note: Time Off Request Note
  status: APPROVED
properties:
  note:
    description: Provide the note you would like to use for changing the time off request.
    type: string
    x-clockify-default: '##default'
  status:
    description: Provide the status you would like to use for changing the time off request.
    enum:
    - APPROVED
    - REJECTED
    type: string
    x-clockify-default: '##default'
required:
- status
type: object
```

<a id="schema-changetrackerdocumenttype"></a>
### `ChangeTrackerDocumentType`

```yaml
type: string
description: Entity-change document type accepted by Clockify. Values are plural except TIME_ENTRY and USER.
enum:
- APPROVAL_REQUESTS
- BALANCE
- CLIENTS
- CUSTOM_FIELDS
- HOLIDAYS
- INVOICES
- PROJECTS
- PTO_POLICY
- SCHEDULED_ASSIGNMENT
- TAGS
- TASKS
- TIME_ENTRY
- TIME_ENTRY_CUSTOM_FIELD_VALUE
- TIME_ENTRY_RATE
- TIME_OFF_REQUEST
- USER
- USER_GROUPS
```

<a id="schema-client"></a>
### `Client`

```yaml
properties:
  address:
    nullable: true
    type: string
  archived:
    type: boolean
  ccEmails:
    items:
      type: string
    nullable: true
    type: array
  currencyCode:
    $ref: '#/components/schemas/Currency'
  currencyId:
    nullable: true
    type: string
  email:
    format: email
    nullable: true
    type: string
  id:
    type: string
  name:
    type: string
  note:
    nullable: true
    type: string
  workspaceId:
    type: string
type: object
required:
- id
- name
- workspaceId
- archived
```

<a id="schema-clientcreate"></a>
### `ClientCreate`

```yaml
properties:
  address:
    type: string
  email:
    format: email
    type: string
  name:
    type: string
  note:
    type: string
required:
- name
type: object
```

<a id="schema-clientupdate"></a>
### `ClientUpdate`

```yaml
allOf:
- $ref: '#/components/schemas/ClientCreate'
- properties:
    archived:
      default: false
      description: Indicates if client will be archived or not.
      type: boolean
    ccEmails:
      description: Additional invoice recipients. Honoured on PUT only; a create ignores it. At most three addresses
        — a fourth returns 400 `{"message":"Number of additional emails must be less than 3","code":501}`, whose
        wording is off by one. Omitting the field on an update clears the stored list.
      items:
        format: email
        type: string
      maxItems: 3
      type: array
    currencyId:
      description: Id of one of the workspace's currencies. Honoured on PUT only; a create ignores it and falls
        back to the workspace default. Sticky when omitted from an update.
      type: string
  type: object
```

<a id="schema-comparefilter"></a>
### `CompareFilter`

```yaml
additionalProperties: false
description: Comparison filter used by attendance filters.
properties:
  filtrationType:
    description: Comparison operator for the filter.
    enum:
    - EXACTLY
    - LARGER_THAN
    - SMALLER_THAN
    type: string
  value:
    description: Value used for comparison. Durations are represented as hours multiplied by 100; start and end
      filters use 24-hour notation.
    type: string
required:
- filtrationType
- value
type: object
```

<a id="schema-containsarchivedfilter"></a>
### `ContainsArchivedFilter`

```yaml
additionalProperties: false
description: Filter by contained archived-aware entities.
properties:
  contains:
    description: Represents a contains type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    type: string
  ids:
    description: Filter includes the provided list of ids.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filter entities by status.
    enum:
    - ACTIVE
    - ARCHIVED
    - ALL
    type: string
type: object
```

<a id="schema-containsarchivedfilterrequest"></a>
### `ContainsArchivedFilterRequest`

```yaml
description: Represents a filter for imported items that can include archived entities.
properties:
  contains:
    $ref: '#/components/schemas/ContainsOperator'
  ids:
    description: Represents a list of filter identifiers.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    $ref: '#/components/schemas/EntityStatus'
type: object
```

<a id="schema-containsarchivedfilterv1"></a>
### `ContainsArchivedFilterV1`

```yaml
properties:
  contains:
    description: Represents a contains type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    example: CONTAINS
    type: string
  ids:
    description: Filter includes provided list of ids.
    example:
    - 5b715448b079875110792222
    - 5b715448b079875110791111
    items:
      description: Filter includes provided list of ids.
      example: '["5b715448b079875110792222","5b715448b079875110791111"]'
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filter entities in 'contains' by their status.
    enum:
    - ACTIVE
    - ARCHIVED
    - ALL
    example: ACTIVE
    type: string
type: object
```

<a id="schema-containsfiltertype"></a>
### `ContainsFilterType`

```yaml
enum:
- CONTAINS
- DOES_NOT_CONTAIN
- CONTAINS_ONLY
type: string
```

<a id="schema-containsoperator"></a>
### `ContainsOperator`

```yaml
description: Filter type.
enum:
- CONTAINS
- DOES_NOT_CONTAIN
- CONTAINS_ONLY
type: string
```

<a id="schema-containstagfilter"></a>
### `ContainsTagFilter`

```yaml
additionalProperties: false
description: Filter criteria for tags.
properties:
  containedInTimeentry:
    description: Filters whether tags are contained in time entries.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    type: string
  contains:
    description: Represents a contains type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    type: string
  ids:
    description: Filter includes the provided list of ids.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filter entities by status.
    enum:
    - ACTIVE
    - ARCHIVED
    - ALL
    type: string
type: object
```

<a id="schema-containstaskfilter"></a>
### `ContainsTaskFilter`

```yaml
additionalProperties: false
description: Filter criteria for tasks.
properties:
  contains:
    description: Represents a contains type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    type: string
  ids:
    description: Filter includes the provided list of ids.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filter entities by status.
    enum:
    - ACTIVE
    - ARCHIVED
    - ALL
    type: string
type: object
```

<a id="schema-containstaskfilterv1"></a>
### `ContainsTaskFilterV1`

```yaml
description: Represents filter criteria for expenses associated with tasks.
properties:
  contains:
    description: Represents a contains type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    example: CONTAINS
    type: string
  ids:
    description: Filter includes provided list of ids.
    example:
    - 5b715448b079875110792222
    - 5b715448b079875110791111
    items:
      description: Filter includes provided list of ids.
      example: '["5b715448b079875110792222","5b715448b079875110791111"]'
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filter entities in 'contains' by their status.
    enum:
    - ACTIVE
    - ARCHIVED
    - ALL
    example: ACTIVE
    type: string
type: object
```

<a id="schema-containsusergroupfilterrequest"></a>
### `ContainsUserGroupFilterRequest`

```yaml
description: Provide list with user group ids and corresponding status.
properties:
  contains:
    description: Filter type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    type: string
  ids:
    description: Represents a list of filter identifiers.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filters entities by status.
    enum:
    - PENDING
    - ACTIVE
    - DECLINED
    - INACTIVE
    - ALL
    type: string
type: object
```

<a id="schema-containsusergroupfilterrequestv1"></a>
### `ContainsUserGroupFilterRequestV1`

```yaml
additionalProperties: false
description: Represents a user group filter request object.
properties:
  contains:
    $ref: '#/components/schemas/ContainsFilterType'
  ids:
    description: Represents a list of filter identifiers.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    $ref: '#/components/schemas/MembershipStatus'
type: object
```

<a id="schema-containsusersfilter"></a>
### `ContainsUsersFilter`

```yaml
additionalProperties: false
description: Filter by users or user groups.
properties:
  contains:
    description: Represents a contains type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    type: string
  ids:
    description: Filter includes the provided list of user or user-group ids.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filter users in contains by their status.
    enum:
    - ALL
    - ACTIVE_WITH_PENDING
    - ACTIVE
    - PENDING
    - INACTIVE
    type: string
type: object
```

<a id="schema-containsusersfilterrequestforholiday"></a>
### `ContainsUsersFilterRequestForHoliday`

```yaml
description: Provide list with user ids and corresponding status.
properties:
  contains:
    description: Filter type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    type: string
  ids:
    description: Represents a list of filter identifiers.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filters entities by status.
    enum:
    - ALL
    - ACTIVE
    - INACTIVE
    type: string
  statuses:
    items:
      type: string
    type: array
type: object
```

<a id="schema-containsusersfilterrequestv1"></a>
### `ContainsUsersFilterRequestV1`

```yaml
additionalProperties: false
description: Represents a user filter request object.
properties:
  contains:
    $ref: '#/components/schemas/ContainsFilterType'
  ids:
    description: Represents a list of filter identifiers.
    items:
      type: string
    type: array
    uniqueItems: true
  sourceType:
    description: Valid authorization source type.
    enum:
    - USER_GROUP
    type: string
  status:
    $ref: '#/components/schemas/MembershipStatus'
  statuses:
    description: Valid array of membership statuses.
    items:
      $ref: '#/components/schemas/MembershipStatus'
    type: array
type: object
```

<a id="schema-containsusersfilterv1"></a>
### `ContainsUsersFilterV1`

```yaml
properties:
  contains:
    description: Represents a contains type.
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    - CONTAINS_ONLY
    example: CONTAINS
    type: string
  ids:
    description: Filter includes provided list of ids.
    example:
    - 5b715448b079875110792222
    - 5b715448b079875110791111
    items:
      description: Filter includes provided list of ids.
      example: '["5b715448b079875110792222","5b715448b079875110791111"]'
      type: string
    type: array
    uniqueItems: true
  status:
    description: Filter entities in 'contains' by their status.
    enum:
    - ALL
    - ACTIVE_WITH_PENDING
    - ACTIVE
    - PENDING
    - INACTIVE
    example: ACTIVE
    type: string
type: object
```

<a id="schema-copyassignmentrequest"></a>
### `CopyAssignmentRequest`

```yaml
additionalProperties: false
description: Request for copying a scheduled assignment.
properties:
  seriesUpdateOption:
    $ref: '#/components/schemas/SeriesUpdateOption'
  userId:
    description: Represents a user identifier across the system.
    type: string
required:
- seriesUpdateOption
- userId
type: object
```

<a id="schema-createapprovalrequestnotype"></a>
### `CreateApprovalRequestNoType`

```yaml
properties:
  period:
    description: Specifies the approval period. It has to match the workspace approval period setting.
    enum:
    - WEEKLY
    - SEMI_MONTHLY
    - MONTHLY
    example: MONTHLY
    type: string
  periodStart:
    description: Specifies an approval period start date in yyyy-MM-ddThh:mm:ssZ format.
    example: '2020-01-01T00:00:00.000Z'
    minLength: 1
    type: string
required:
- periodStart
type: object
```

<a id="schema-createbalanceassignmentv1request"></a>
### `CreateBalanceAssignmentV1Request`

```yaml
properties:
  balance:
    description: Represents the amount of balance to be created
    example: 12
    format: double
    maximum: 10000
    type: number
  dateRange:
    $ref: '#/components/schemas/DateRangeV1Request'
  note:
    description: Represents note attached to updating balance.
    example: Bonus days added.
    type: string
  policyId:
    description: Represents the identifier of the policy where the balance assignment will be created
    example: 63034cd0cb0fb876a57e93ad
    minLength: 1
    type: string
  userIds:
    description: Represents list of users' identifiers whose balance is to be updated.
    example:
    - 5b715448b079875110792222
    - 5b715448b079875110791111
    items:
      description: Represents list of users' identifiers whose balance is to be updated.
      example: '["5b715448b079875110792222","5b715448b079875110791111"]'
      type: string
    minItems: 1
    type: array
    uniqueItems: true
required:
- balance
- policyId
- userIds
type: object
```

<a id="schema-createcustomfieldrequest"></a>
### `CreateCustomFieldRequest`

```yaml
example:
  allowedValues:
  - New York
  - London
  - Manila
  - Sydney
  - Belgrade
  description: This field contains a location.
  entityType: USER
  name: location
  onlyAdminCanEdit: false
  placeholder: Location
  required: false
  status: VISIBLE
  type: DROPDOWN_MULTIPLE
  workspaceDefaultValue:
  - Manila
properties:
  allowedValues:
    description: Represents a list of custom field allowed values.
    items:
      type: string
    type: array
  description:
    description: Represents custom field description.
    type: string
  entityType:
    $ref: '#/components/schemas/CustomFieldEntityType'
  name:
    description: Represents custom field name.
    type: string
  onlyAdminCanEdit:
    default: false
    description: Flag to set whether custom field is modifiable only by admin users.
    type: boolean
  placeholder:
    description: Represents custom field placeholder value.
    type: string
  required:
    default: false
    description: Flag to set whether custom field is mandatory or not.
    type: boolean
  status:
    $ref: '#/components/schemas/CustomFieldStatus'
  type:
    $ref: '#/components/schemas/CustomFieldType'
  workspaceDefaultValue:
    $ref: '#/components/schemas/CustomFieldValue'
required:
- name
- type
type: object
```

<a id="schema-createholidayrequest"></a>
### `CreateHolidayRequest`

```yaml
properties:
  automaticTimeEntryCreation:
    $ref: '#/components/schemas/AutomaticTimeEntryCreationRequest'
  color:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  datePeriod:
    $ref: '#/components/schemas/DatePeriodRequest'
  everyoneIncludingNew:
    default: false
    description: Indicates whether the holiday is shown to new users.
    type: boolean
  name:
    description: Provide the name of the holiday.
    maxLength: 100
    minLength: 2
    type: string
  occursAnnually:
    default: false
    description: Indicates whether the holiday occurs annually.
    type: boolean
  userGroups:
    $ref: '#/components/schemas/UserGroupIdsSchema'
  users:
    $ref: '#/components/schemas/UserIdsSchema'
required:
- datePeriod
- name
type: object
```

<a id="schema-createprojectfromtemplaterequest"></a>
### `CreateProjectFromTemplateRequest`

```yaml
additionalProperties: false
properties:
  clientId:
    description: Represents a client identifier across the system.
    type: string
  color:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  isPublic:
    default: false
    description: Indicates whether the project is public or not.
    type: boolean
  name:
    description: Represents a project name.
    maxLength: 250
    minLength: 2
    type: string
  templateProjectId:
    description: Represents a project identifier across the system.
    minLength: 1
    type: string
required:
- name
- templateProjectId
type: object
```

<a id="schema-createprojectrequest"></a>
### `CreateProjectRequest`

```yaml
additionalProperties: false
properties:
  billable:
    default: false
    description: Indicates whether project is billable or not.
    type: boolean
  clientId:
    description: Represents client identifier across the system.
    type: string
  color:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  costRate:
    $ref: '#/components/schemas/RateRequest'
  estimate:
    $ref: '#/components/schemas/EstimateRequest'
  hourlyRate:
    $ref: '#/components/schemas/RateRequest'
  isPublic:
    default: false
    description: Indicates whether project is public or not.
    type: boolean
  memberships:
    description: Represents a list of membership request objects.
    items:
      $ref: '#/components/schemas/MembershipRequest'
    type: array
  name:
    description: Represents a project name.
    maxLength: 250
    minLength: 2
    type: string
  note:
    description: Represents project note.
    maxLength: 16384
    type: string
  tasks:
    description: Represents a list of task request objects.
    items:
      $ref: '#/components/schemas/TaskRequest'
    type: array
required:
- name
type: object
```

<a id="schema-createrecurringassignmentrequest"></a>
### `CreateRecurringAssignmentRequest`

```yaml
additionalProperties: false
description: Request for creating a recurring assignment.
properties:
  billable:
    default: false
    description: Indicates whether assignment is billable or not.
    type: boolean
  end:
    description: Represents an end date in the yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  hoursPerDay:
    description: Represents assignment total hours per day.
    format: double
    type: number
  includeNonWorkingDays:
    default: false
    description: Indicates whether to include non-working days or not.
    type: boolean
  note:
    description: Represents an assignment note.
    maxLength: 100
    type: string
  projectId:
    description: Represents a project identifier across the system.
    minLength: 1
    type: string
  recurringAssignment:
    $ref: '#/components/schemas/RecurringAssignmentRequestV1'
  start:
    description: Represents a start date in the yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  startTime:
    description: Represents a start time in the hh:mm:ss format.
    example: '10:00:00'
    type: string
  taskId:
    description: Represents a task identifier across the system.
    type: string
  userId:
    description: Represents a user identifier across the system.
    minLength: 1
    type: string
required:
- end
- hoursPerDay
- projectId
- start
- userId
type: object
```

<a id="schema-createtimeentryrequest"></a>
### `CreateTimeEntryRequest`

```yaml
properties:
  billable:
    type: boolean
  description:
    type: string
  end:
    format: date-time
    type: string
  projectId:
    type: string
  start:
    format: date-time
    type: string
  tagIds:
    items:
      type: string
    type: array
  taskId:
    type: string
  type:
    enum:
    - REGULAR
    - BREAK
    type: string
required:
- start
type: object
```

<a id="schema-createtimeoffpolicyrequest"></a>
### `CreateTimeOffPolicyRequest`

```yaml
description: Request body for creating a time off policy.
properties:
  allowHalfDay:
    default: false
    description: Indicates whether policy allows half days.
    type: boolean
  allowNegativeBalance:
    default: false
    description: Indicates whether policy allows negative balances.
    type: boolean
  approve:
    $ref: '#/components/schemas/PolicyApprovalDto'
  archived:
    default: false
    description: Indicates whether policy is archived.
    type: boolean
  automaticAccrual:
    $ref: '#/components/schemas/AutomaticAccrualRequest'
  automaticTimeEntryCreation:
    $ref: '#/components/schemas/AutomaticTimeEntryCreationRequest'
  color:
    description: Policy color as a hex RGB value.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  everyoneIncludingNew:
    default: false
    description: Indicates whether policy is applied to future new users.
    type: boolean
  hasExpiration:
    default: false
    description: Indicates whether the policy balance should have expiration.
    type: boolean
  icon:
    description: Policy icon.
    enum:
    - UMBRELLA
    - SNOWFLAKE
    - FAMILY
    - PLANE
    - STETHOSCOPE
    - HEALTH_METRICS
    - CHILDCARE
    - LUGGAGE
    - MONETIZATION
    - CALENDAR
    type: string
  name:
    description: Represents a name of the new policy.
    maxLength: 100
    minLength: 2
    type: string
  negativeBalance:
    $ref: '#/components/schemas/NegativeBalanceRequest'
  timeUnit:
    description: Indicates time unit of the policy.
    enum:
    - DAYS
    - HOURS
    type: string
  userGroups:
    $ref: '#/components/schemas/PoliciesUserGroupIdsSchema'
  users:
    $ref: '#/components/schemas/PoliciesUserIdsSchema'
required:
- approve
- name
type: object
```

<a id="schema-createtimeoffrequest"></a>
### `CreateTimeOffRequest`

```yaml
example:
  note: Create Time Off Note
  timeOffPeriod:
    halfDayPeriod: NOT_DEFINED
    isHalfDay: false
    period:
      days: 1
      end: '2022-08-26'
      start: '2022-08-26'
properties:
  note:
    description: Provide the note you would like to use for creating the time off request.
    type: string
    x-clockify-default: '##default'
  timeOffPeriod:
    $ref: '#/components/schemas/TimeOffRequestPeriodV1Request'
required:
- timeOffPeriod
type: object
```

<a id="schema-createworkspacerequest"></a>
### `CreateWorkspaceRequest`

```yaml
additionalProperties: false
properties:
  name:
    description: Represents a workspace name.
    maxLength: 50
    minLength: 1
    type: string
  organizationId:
    description: Represents the Cake organization identifier across the system.
    type: string
required:
- name
- organizationId
type: object
```

<a id="schema-currency"></a>
### `Currency`

```yaml
description: ISO 4217 currency code
example: EUR
type: string
```

<a id="schema-currencywithdefaultinfodtov1"></a>
### `CurrencyWithDefaultInfoDtoV1`

```yaml
additionalProperties: true
description: Represents currency with default info object.
properties:
  code:
    description: Represents currency code.
    type: string
  id:
    description: Represents currency identifier across the system.
    type: string
  isDefault:
    default: false
    description: Indicates whether currency should be set as default.
    type: boolean
type: object
```

<a id="schema-customfield"></a>
### `CustomField`

```yaml
description: Custom field data transfer object.
example:
  allowedValues:
  - New York
  - London
  - Manila
  - Sydney
  - Belgrade
  description: This field contains a location.
  entityType: USER
  id: 44a687e29ae1f428e7ebe305
  name: location
  onlyAdminCanEdit: false
  placeholder: Location
  projectDefaultValues: []
  required: false
  status: VISIBLE
  type: DROPDOWN_MULTIPLE
  workspaceDefaultValue: Manila
  workspaceId: 64a687e29ae1f428e7ebe303
properties:
  allowedValues:
    description: Represents a list of custom field allowed values.
    items:
      type: string
    type: array
  description:
    description: Represents custom field description.
    type: string
  entityType:
    $ref: '#/components/schemas/CustomFieldEntityType'
  id:
    description: Represents custom field identifier across the system.
    type: string
  name:
    description: Represents custom field name.
    type: string
  onlyAdminCanEdit:
    default: false
    description: Flag to set whether custom field is modifiable only by admin users.
    type: boolean
  placeholder:
    description: Represents custom field placeholder value.
    type: string
  projectDefaultValues:
    description: Represents custom field default values for projects.
    items:
      $ref: '#/components/schemas/CustomFieldDefaultValue'
    type: array
  required:
    default: false
    description: Flag to set whether custom field is mandatory or not.
    type: boolean
  status:
    $ref: '#/components/schemas/CustomFieldStatus'
  type:
    $ref: '#/components/schemas/CustomFieldType'
  workspaceDefaultValue:
    $ref: '#/components/schemas/CustomFieldValue'
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-customfielddefaultvalue"></a>
### `CustomFieldDefaultValue`

```yaml
description: Custom field default value for a project.
properties:
  projectId:
    description: Represents project identifier across the system.
    type: string
  status:
    $ref: '#/components/schemas/CustomFieldStatus'
  value:
    $ref: '#/components/schemas/CustomFieldValue'
type: object
```

<a id="schema-customfielddefaultvaluesdtov1"></a>
### `CustomFieldDefaultValuesDtoV1`

```yaml
description: Represents a custom field default values object.
properties:
  projectId:
    description: Represents project identifier across the system.
    type: string
  status:
    description: Represents custom field status.
    type: string
  value:
    description: Represents a custom field's default value.
    nullable: true
type: object
```

<a id="schema-customfielddtov1"></a>
### `CustomFieldDtoV1`

```yaml
description: Represents a custom field.
properties:
  allowedValues:
    description: Represents a list of custom field's allowed values.
    items:
      type: string
    type: array
  description:
    description: Represents custom field description.
    type: string
  entityType:
    description: Represents custom field entity type.
    type: string
  id:
    description: Represents custom field identifier across the system.
    type: string
  name:
    description: Represents custom field name.
    type: string
  onlyAdminCanEdit:
    default: false
    type: boolean
  placeholder:
    description: Represents custom field placeholder value.
    type: string
  projectDefaultValues:
    items:
      $ref: '#/components/schemas/CustomFieldDefaultValuesDtoV1'
    type: array
  required:
    default: false
    type: boolean
  status:
    description: Represents custom field status.
    type: string
  type:
    $ref: '#/components/schemas/UsersCustomFieldType'
  workspaceDefaultValue:
    description: Represents a custom field's default value in the workspace.
    nullable: true
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-customfieldentitytype"></a>
### `CustomFieldEntityType`

```yaml
description: Custom field entity type.
enum:
- TIMEENTRY
- USER
type: string
```

<a id="schema-customfieldfilter"></a>
### `CustomFieldFilter`

```yaml
additionalProperties: false
description: Custom field filter.
properties:
  id:
    description: Represents a custom field identifier across the system.
    type: string
  isEmpty:
    description: Indicates whether the custom field is empty.
    type: boolean
  numberCondition:
    description: Represents a custom field number condition.
    enum:
    - EQUAL
    - GREATER_THAN
    - LESS_THAN
    type: string
  type:
    description: Represents a type of custom field.
    enum:
    - TXT
    - NUMBER
    - DROPDOWN_SINGLE
    - DROPDOWN_MULTIPLE
    - CHECKBOX
    - LINK
    type: string
  value:
    description: Represents a custom field value. The value type depends on the custom field type.
    oneOf:
    - type: string
    - type: number
    - type: boolean
    - items: {}
      type: array
    - additionalProperties: true
      type: object
type: object
```

<a id="schema-customfieldstatus"></a>
### `CustomFieldStatus`

```yaml
description: Custom field status.
enum:
- INACTIVE
- VISIBLE
- INVISIBLE
type: string
```

<a id="schema-customfieldtype"></a>
### `CustomFieldType`

```yaml
description: Custom field type.
enum:
- TXT
- NUMBER
- DROPDOWN_SINGLE
- DROPDOWN_MULTIPLE
- CHECKBOX
- LINK
type: string
```

<a id="schema-customfieldvalue"></a>
### `CustomFieldValue`

```yaml
description: Custom field default value or assigned value. For NUMBER use a number; for DROPDOWN_MULTIPLE use a
  list; for CHECKBOX use true/false; otherwise use a string.
nullable: true
oneOf:
- type: string
- format: double
  type: number
- type: boolean
- items:
    type: string
  type: array
- additionalProperties: true
  type: object
```

<a id="schema-customfieldvaluedto"></a>
### `CustomFieldValueDto`

```yaml
description: Represents a custom field value object.
properties:
  customFieldId:
    description: Represents custom field identifier across the system.
    type: string
  sourceType:
    description: Represents a custom field value source type.
    enum:
    - WORKSPACE
    - PROJECT
    - TIMEENTRY
    type: string
  timeEntryId:
    description: Represents time entry identifier across the system.
    type: string
  value:
    description: Represents custom field value.
type: object
```

<a id="schema-customfieldvaluedtov1"></a>
### `CustomFieldValueDtoV1`

```yaml
description: Represents a list of custom field value objects.
properties:
  customFieldId:
    description: Represents custom field identifier across the system.
    example: 5e4117fe8c625f38930d57b7
    type: string
  name:
    description: Represents custom field name.
    example: TIN
    type: string
  timeEntryId:
    description: Represents time entry identifier across the system.
    example: 64c777ddd3fcab07cfbb210c
    type: string
  type:
    description: Represents a custom field value source type.
    example: WORKSPACE
    type: string
  value:
    description: Represents custom field value.
    example: 20231211-12345
    type: object
type: object
```

<a id="schema-dailytotaldto"></a>
### `DailyTotalDto`

```yaml
additionalProperties: true
properties:
  amount:
    description: Amount.
    type: number
  date:
    description: Date.
    type: string
  duration:
    description: Duration.
    type: number
type: object
```

<a id="schema-dateperiod"></a>
### `DatePeriod`

```yaml
description: Represents startDate and endDate of the holiday. Date is in format yyyy-mm-dd.
properties:
  endDate:
    format: date
    type: string
  startDate:
    format: date
    type: string
type: object
```

<a id="schema-dateperiodrequest"></a>
### `DatePeriodRequest`

```yaml
description: Provide startDate and endDate for the holiday.
properties:
  endDate:
    description: yyyy-MM-dd format date.
    minLength: 1
    type: string
  startDate:
    description: yyyy-MM-dd format date.
    minLength: 1
    type: string
required:
- startDate
- endDate
type: object
```

<a id="schema-daterangedto"></a>
### `DateRangeDto`

```yaml
description: Represents date range object.
properties:
  end:
    format: date-time
    type: string
  start:
    format: date-time
    type: string
type: object
```

<a id="schema-daterangev1request"></a>
### `DateRangeV1Request`

```yaml
description: Represents the date range when the new balance will be usable. If null, this will default to the current
  day until the same day next year.
properties:
  end:
    description: Provide end date in YYYY-MM-DD format.
    example: '2021-12-25'
    type: string
  start:
    description: Provide start date in YYYY-MM-DD format.
    example: '2021-12-23'
    type: string
type: object
```

<a id="schema-datetimeinterval"></a>
### `DateTimeInterval`

```yaml
properties:
  duration:
    description: ISO 8601 duration, e.g. PT1H30M
    nullable: true
    type: string
  end:
    format: date-time
    nullable: true
    type: string
  offEnd:
    nullable: true
    type: integer
  offStart:
    nullable: true
    type: integer
  start:
    format: date-time
    type: string
  timeZone:
    nullable: true
    type: string
  zonedEnd:
    nullable: true
    type: string
  zonedStart:
    nullable: true
    type: string
type: object
```

<a id="schema-dayofweek"></a>
### `DayOfWeek`

```yaml
enum:
- MONDAY
- TUESDAY
- WEDNESDAY
- THURSDAY
- FRIDAY
- SATURDAY
- SUNDAY
type: string
```

<a id="schema-defaultentitiesdto"></a>
### `DefaultEntitiesDto`

```yaml
properties:
  projectId:
    type: string
  taskId:
    type: string
type: object
```

<a id="schema-deletebalanceassignmentv1request"></a>
### `DeleteBalanceAssignmentV1Request`

```yaml
properties:
  note:
    description: Represents a note explaining balance deletion
    example: All balance used.
    minLength: 1
    type: string
required:
- note
type: object
```

<a id="schema-detailedfilter"></a>
### `DetailedFilter`

```yaml
additionalProperties: false
description: 'Detailed report filter. This filter is valid only on /reports/detailed.

  Pagination belongs in this nested filter as page and pageSize; top-level request page fields are not accepted
  by /reports/detailed.'
properties:
  auditFilter:
    $ref: '#/components/schemas/AuditFilter'
  options:
    $ref: '#/components/schemas/DetailedOptions'
  page:
    description: Page number.
    format: int32
    type: integer
  pageSize:
    description: Page size.
    format: int32
    type: integer
  sortColumn:
    description: Column used for sorting detailed report rows.
    enum:
    - ID
    - DESCRIPTION
    - USER
    - DURATION
    - DATE
    - ZONED_DATE
    - NATURAL
    - USER_DATE
    type: string
type: object
x-clockify-report-filter: detailed
```

<a id="schema-detailedoptions"></a>
### `DetailedOptions`

```yaml
additionalProperties: false
description: Detailed report options.
properties:
  totals:
    description: Controls whether totals are calculated or excluded.
    enum:
    - CALCULATE
    - EXCLUDE
    type: string
type: object
```

<a id="schema-detailedreportrequest"></a>
### `DetailedReportRequest`

```yaml
additionalProperties: false
description: Request payload for generating detailed time-entry reports. Only detailedFilter is accepted as the
  report-specific filter.
properties:
  amountShown:
    description: If provided, returns reports with the provided amount shown.
    enum:
    - EARNED
    - COST
    - PROFIT
    - HIDE_AMOUNT
    - EXPORT
    type: string
  amounts:
    description: Amount columns to include.
    items:
      $ref: '#/components/schemas/AmountType'
    type: array
  approvalState:
    description: If provided, returns reports with the provided approval state.
    enum:
    - APPROVED
    - UNAPPROVED
    - ALL
    type: string
  archived:
    description: Indicates whether the report is archived.
    type: boolean
  billable:
    description: Indicates whether the report is billable.
    type: boolean
  clients:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  currency:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  customFields:
    description: Time entry custom field filters.
    items:
      $ref: '#/components/schemas/CustomFieldFilter'
    type: array
  dateFormat:
    description: Provide date in format YYYY-MM-DD.
    example: '2018-11-01'
    type: string
  dateRangeEnd:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. Interpreted using the user's timezone or the
      provided timeZone.
    example: '2018-11-30T23:59:59.999'
    minLength: 1
    type: string
  dateRangeStart:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. Interpreted using the user's timezone or the
      provided timeZone.
    example: '2018-11-01T00:00:00'
    minLength: 1
    type: string
  dateRangeType:
    description: Date range preset.
    enum:
    - ABSOLUTE
    - TODAY
    - YESTERDAY
    - THIS_WEEK
    - LAST_WEEK
    - PAST_TWO_WEEKS
    - THIS_MONTH
    - LAST_MONTH
    - THIS_YEAR
    - LAST_YEAR
    type: string
  description:
    description: Search term for filtering report entries by description.
    type: string
  detailedFilter:
    $ref: '#/components/schemas/DetailedFilter'
  exportType:
    description: Export format requested for the report.
    enum:
    - JSON
    - JSON_V1
    - PDF
    - CSV
    - XLSX
    - ZIP
    type: string
  invoicingState:
    description: If provided, returns reports with the provided invoicing state.
    enum:
    - INVOICED
    - UNINVOICED
    - ALL
    type: string
  projects:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  rounding:
    description: Indicates whether report filter rounding is enabled.
    type: boolean
  sortOrder:
    description: Sort order.
    enum:
    - ASCENDING
    - DESCENDING
    type: string
  tags:
    $ref: '#/components/schemas/ContainsTagFilter'
  tasks:
    $ref: '#/components/schemas/ContainsTaskFilter'
  timeFormat:
    description: Provide time in format THH:MM:SS.ssssss.
    example: T00:00:00
    type: string
  timeZone:
    description: Timezone used to interpret dates and times.
    example: Europe/Belgrade
    type: string
  userCustomFields:
    description: User custom field filters.
    items:
      $ref: '#/components/schemas/CustomFieldFilter'
    type: array
  userGroups:
    $ref: '#/components/schemas/ContainsUsersFilter'
  userLocale:
    description: Locale used for report formatting.
    example: en
    type: string
  users:
    $ref: '#/components/schemas/ContainsUsersFilter'
  weekStart:
    description: Configured week start day.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  withoutDescription:
    description: If true, report includes only entries with empty description.
    type: boolean
  zoomLevel:
    description: Report zoom level.
    enum:
    - WEEK
    - MONTH
    - YEAR
    type: string
required:
- dateRangeStart
- dateRangeEnd
- detailedFilter
type: object
```

<a id="schema-detailedreportresponse"></a>
### `DetailedReportResponse`

```yaml
additionalProperties: true
description: Detailed report response. Both timeEntries and timeentries are valid payload keys.
properties:
  timeEntries:
    description: List of time entries.
    items:
      $ref: '#/components/schemas/TimeEntryDto'
    type: array
  timeentries:
    description: Lowercase alias for timeEntries. Included so both payload spellings validate.
    items:
      $ref: '#/components/schemas/TimeEntryDto'
    type: array
  totals:
    description: List of report totals.
    items:
      $ref: '#/components/schemas/TimeEntryReportTotals'
    type: array
type: object
x-clockify-aliases:
  timeentries: timeEntries
```

<a id="schema-durationstring"></a>
### `DurationString`

```yaml
description: Represents a time duration.
example: PT1H30M
type: string
```

<a id="schema-entitychangedocument"></a>
### `EntityChangeDocument`

```yaml
type: object
description: One entity-change record. Carries audit timestamps and the document type alongside the changed entity's
  own fields, which vary by `type`.
additionalProperties: true
properties:
  auditMetadata:
    type: object
    description: Creation and last-update instants for the record.
    properties:
      createdAt:
        type: string
        format: date-time
        nullable: true
      updatedAt:
        type: string
        format: date-time
        nullable: true
  documentCode:
    $ref: '#/components/schemas/ChangeTrackerDocumentType'
  id:
    type: string
```

<a id="schema-entitycreationpermission"></a>
### `EntityCreationPermission`

```yaml
additionalProperties: true
description: Represents an entity creation permission enum with optional creators.
properties:
  creators:
    items:
      type: string
    type: array
    uniqueItems: true
  value:
    enum:
    - ADMINS
    - ADMINS_AND_PROJECT_MANAGERS
    - EVERYONE
    type: string
type: object
```

<a id="schema-entitycreationpermissionsdtov1"></a>
### `EntityCreationPermissionsDtoV1`

```yaml
additionalProperties: true
description: Represents an entity creation permission object.
properties:
  whoCanCreateProjectsAndClients:
    $ref: '#/components/schemas/EntityCreationPermission'
  whoCanCreateTags:
    $ref: '#/components/schemas/EntityCreationPermission'
  whoCanCreateTasks:
    $ref: '#/components/schemas/EntityCreationPermission'
type: object
```

<a id="schema-entityidnamedto"></a>
### `EntityIdNameDto`

```yaml
properties:
  id:
    type: string
  name:
    type: string
type: object
```

<a id="schema-entitystatus"></a>
### `EntityStatus`

```yaml
description: Filters entities by status.
enum:
- ACTIVE
- ARCHIVED
- ALL
type: string
```

<a id="schema-error"></a>
### `Error`

```yaml
additionalProperties: true
description: Generic error response.
type: object
```

<a id="schema-errorresponse"></a>
### `ErrorResponse`

```yaml
additionalProperties: true
properties:
  code:
    description: Error code.
    type: string
  message:
    description: Error message.
    type: string
type: object
```

<a id="schema-estimatedtov1"></a>
### `EstimateDtoV1`

```yaml
additionalProperties: false
description: Represents a project estimate object.
properties:
  estimate:
    description: Represents a task duration estimate.
    type: string
  type:
    description: Represents an estimate type enum.
    enum:
    - AUTO
    - MANUAL
    type: string
type: object
```

<a id="schema-estimaterequest"></a>
### `EstimateRequest`

```yaml
additionalProperties: false
description: Represents an estimate request object.
properties:
  estimate:
    description: Represents a time duration in ISO-8601 format.
    type: string
  type:
    description: Represents an estimate type enum.
    enum:
    - AUTO
    - MANUAL
    type: string
type: object
```

<a id="schema-estimateresetdto"></a>
### `EstimateResetDto`

```yaml
additionalProperties: false
description: Represents project estimate reset object.
properties:
  dayOfMonth:
    format: int32
    type: integer
  dayOfWeek:
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  hour:
    format: int32
    type: integer
  interval:
    enum:
    - WEEKLY
    - MONTHLY
    - YEARLY
    type: string
  month:
    enum:
    - JANUARY
    - FEBRUARY
    - MARCH
    - APRIL
    - MAY
    - JUNE
    - JULY
    - AUGUST
    - SEPTEMBER
    - OCTOBER
    - NOVEMBER
    - DECEMBER
    type: string
type: object
```

<a id="schema-estimateresetrequest"></a>
### `EstimateResetRequest`

```yaml
additionalProperties: false
description: Represents estimate reset request object.
properties:
  active:
    type: boolean
  dayOfMonth:
    description: Represents a day of the month.
    format: int32
    maximum: 31
    minimum: 1
    type: integer
  dayOfWeek:
    description: Represents a day of the week.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  hour:
    description: Represents an hour of the day in 24-hour time format.
    format: int32
    maximum: 23
    minimum: 0
    type: integer
  interval:
    description: Represents a reset option enum.
    enum:
    - WEEKLY
    - MONTHLY
    - YEARLY
    type: string
  isActive:
    type: boolean
  month:
    description: Represents a month enum.
    enum:
    - JANUARY
    - FEBRUARY
    - MARCH
    - APRIL
    - MAY
    - JUNE
    - JULY
    - AUGUST
    - SEPTEMBER
    - OCTOBER
    - NOVEMBER
    - DECEMBER
    type: string
type: object
```

<a id="schema-estimatewithoptionsdto"></a>
### `EstimateWithOptionsDto`

```yaml
additionalProperties: false
description: Represents a project budget estimate object.
properties:
  active:
    type: boolean
  estimate:
    description: Represents an estimate as long.
    format: int64
    type: integer
  includeExpenses:
    default: false
    description: Indicates whether estimate includes expenses.
    type: boolean
  resetOption:
    description: Represents a reset option enum.
    enum:
    - WEEKLY
    - MONTHLY
    - YEARLY
    type: string
  type:
    description: Represents an estimate type enum.
    enum:
    - AUTO
    - MANUAL
    type: string
type: object
```

<a id="schema-estimatewithoptionsrequest"></a>
### `EstimateWithOptionsRequest`

```yaml
additionalProperties: false
description: Represents estimate with options request object.
properties:
  active:
    default: false
    description: Flag whether to set estimate as active or not.
    type: boolean
  estimate:
    description: Represents an estimate as long.
    format: int64
    minimum: 0
    type: integer
  includeExpenses:
    default: false
    description: Flag whether to include billable expenses.
    type: boolean
  resetOption:
    description: Represents a reset option enum.
    enum:
    - WEEKLY
    - MONTHLY
    - YEARLY
    type: string
  type:
    description: Represents an estimate type enum.
    enum:
    - AUTO
    - MANUAL
    type: string
type: object
```

<a id="schema-expensecategoriesdtov1"></a>
### `ExpenseCategoriesDtoV1`

```yaml
description: Expense categories list response.
example:
  categories:
  - archived: false
    hasUnitPrice: false
    id: 89a687e29ae1f428e7ebe567
    name: Procurement
    priceInCents: 1000
    unit: piece
    workspaceId: 64a687e29ae1f428e7ebe303
  count: 20
properties:
  categories:
    items:
      $ref: '#/components/schemas/ExpenseCategoryDtoV1'
    type: array
  count:
    description: Represents the number of categories returned.
    format: int32
    type: integer
type: object
```

<a id="schema-expensecategorydto"></a>
### `ExpenseCategoryDto`

```yaml
properties:
  archived:
    type: boolean
  hasUnitPrice:
    type: boolean
  id:
    type: string
  name:
    type: string
  priceInCents:
    format: int64
    type: integer
  unit:
    type: string
  workspaceId:
    type: string
type: object
```

<a id="schema-expensecategorydtov1"></a>
### `ExpenseCategoryDtoV1`

```yaml
description: Represents an expense category.
example:
  archived: false
  hasUnitPrice: false
  id: 89a687e29ae1f428e7ebe567
  name: Procurement
  priceInCents: 1000
  unit: piece
  workspaceId: 64a687e29ae1f428e7ebe303
properties:
  archived:
    default: false
    description: Flag that indicates whether the expense category is archived or not.
    type: boolean
  hasUnitPrice:
    default: false
    description: Represents whether expense category has unit price or none.
    type: boolean
  id:
    default: '##default'
    description: Represents expense category identifier across the system.
    type: string
  name:
    default: '##default'
    description: Represents expense category name.
    type: string
  priceInCents:
    description: Represents price in cents as integer.
    format: int32
    type: integer
  unit:
    default: '##default'
    description: Represents expense category unit.
    type: string
  workspaceId:
    default: '##default'
    description: Represents workspace identifier across the system.
    type: string
  status:
    description: Live expense category responses may include status:null.
    nullable: true
    type: string
type: object
```

<a id="schema-expensecategoryrequest"></a>
### `ExpenseCategoryRequest`

```yaml
description: Request body for adding or updating an expense category.
example:
  hasUnitPrice: false
  name: Procurement
  priceInCents: 1000
  unit: piece
properties:
  hasUnitPrice:
    default: false
    description: Flag whether expense category has unit price or none.
    type: boolean
  name:
    default: '##default'
    description: Represents a valid expense category name.
    maxLength: 250
    minLength: 0
    type: string
  priceInCents:
    description: Represents price in cents as integer.
    format: int32
    type: integer
  unit:
    default: '##default'
    description: Represents a valid expense category unit.
    type: string
required:
- name
type: object
```

<a id="schema-expensecategorystatusrequest"></a>
### `ExpenseCategoryStatusRequest`

```yaml
description: Request body for archiving or unarchiving an expense category.
example:
  archived: false
properties:
  archived:
    default: false
    description: Flag whether to archive the expense category or not.
    type: boolean
required:
- archived
type: object
```

<a id="schema-expensecreaterequest"></a>
### `ExpenseCreateRequest`

```yaml
description: Multipart form-data request for creating an expense.
example:
  amount: 10500.5
  billable: false
  categoryId: 45y687e29ae1f428e7ebe890
  date: '2020-01-01T00:00:00Z'
  file: receipt.pdf
  notes: This is a sample note for this expense.
  projectId: 25b687e29ae1f428e7ebe123
  taskId: 25b687e29ae1f428e7ebe123
  userId: 89b687e29ae1f428e7ebe912
properties:
  amount:
    description: 'Represents an expense amount as the double data type.

      Live expense responses expose this value as quantity.'
    format: double
    maximum: 92233720368547760
    type: number
  billable:
    default: false
    description: Indicates whether expense is billable or not.
    type: boolean
  categoryId:
    default: '##default'
    description: Represents a category identifier across the system.
    type: string
  date:
    description: Provides a valid yyyy-MM-ddThh:mm:ssZ format date.
    format: date-time
    type: string
  file:
    format: binary
    type: string
    description: Live Clockify accepts create-expense multipart requests without a file.
  notes:
    default: '##default'
    description: Represents notes for an expense.
    maxLength: 3000
    type: string
  projectId:
    default: '##default'
    description: 'Represents a project identifier across the system.

      Live Clockify accepts create-expense multipart requests without a projectId.'
    type: string
  taskId:
    default: '##default'
    description: Represents a task identifier across the system.
    type: string
  userId:
    default: '##default'
    description: Represents a user identifier across the system.
    minLength: 1
    type: string
required:
- amount
- categoryId
- date
- userId
type: object
```

<a id="schema-expensedailytotalsdtov1"></a>
### `ExpenseDailyTotalsDtoV1`

```yaml
description: Represents an expense daily total data transfer object.
properties:
  date:
    description: Date in yyyy-MM-dd format.
    example: '2020-01-01'
    type: string
  dateAsInstant:
    format: date-time
    type: string
  total:
    description: Represents expense total.
    format: double
    type: number
type: object
```

<a id="schema-expensedetailedreportdtov1"></a>
### `ExpenseDetailedReportDtoV1`

```yaml
description: report
properties:
  expenses:
    description: Represents list of expenses
    items:
      $ref: '#/components/schemas/ExpenseReportDtoV1'
    type: array
  totals:
    $ref: '#/components/schemas/ExpenseTotalsDtoV1'
type: object
```

<a id="schema-expensedtov1"></a>
### `ExpenseDtoV1`

```yaml
description: Represents an expense object.
example:
  billable: false
  categoryId: 45y687e29ae1f428e7ebe890
  date: '2020-01-01'
  fileId: 745687e29ae1f428e7ebe890
  id: 64c777ddd3fcab07cfbb210c
  locked: true
  notes: This is a sample note for this expense.
  projectId: 25b687e29ae1f428e7ebe123
  quantity: 0.1
  taskId: 25b687e29ae1f428e7ebe123
  total: 10500.5
  userId: 89b687e29ae1f428e7ebe912
  workspaceId: 64a687e29ae1f428e7ebe303
properties:
  billable:
    default: false
    description: Indicates whether expense is billable or not.
    type: boolean
  categoryId:
    default: '##default'
    description: Represents category identifier across the system.
    type: string
  date:
    default: '##default'
    description: Represents a date in yyyy-MM-dd format.
    example: '2020-01-01'
    type: string
  fileId:
    default: '##default'
    description: Represents file identifier across the system.
    type: string
  id:
    default: '##default'
    description: Represents expense identifier across the system.
    type: string
  locked:
    description: Indicates whether the expense is locked.
    type: boolean
  notes:
    default: '##default'
    description: Represents notes for an expense.
    type: string
  projectId:
    default: '##default'
    description: Represents project identifier across the system.
    type: string
  quantity:
    description: 'Represents expense quantity as double data type.

      Create/update requests use amount; live expense responses expose the entered amount as quantity and the computed
      value as total.'
    format: double
    type: number
  taskId:
    default: '##default'
    description: Represents task identifier across the system.
    type: string
  total:
    description: Represents expense total as double data type.
    format: double
    type: number
  userId:
    default: '##default'
    description: Represents user identifier across the system.
    type: string
  workspaceId:
    default: '##default'
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-expensefieldsfordetailedgroup"></a>
### `ExpenseFieldsForDetailedGroup`

```yaml
enum:
- PROJECT
- TASK
- CATEGORY
- NOTE
- DATE
- USER
type: string
```

<a id="schema-expensehydrateddto"></a>
### `ExpenseHydratedDto`

```yaml
description: Represents an expense hydrated data transfer object.
properties:
  approvalRequestId:
    type: string
  approvalStatus:
    type: string
  billable:
    type: boolean
  category:
    $ref: '#/components/schemas/ExpenseCategoryDto'
  currency:
    type: string
  date:
    format: date
    type: string
  detailedApprovalStatus:
    type: string
  fileId:
    type: string
  fileName:
    type: string
  fileUrl:
    type: string
  id:
    type: string
  locked:
    type: boolean
  notes:
    type: string
  project:
    $ref: '#/components/schemas/ProjectInfoDto'
  quantity:
    format: double
    type: number
  task:
    $ref: '#/components/schemas/TaskInfoDto'
  total:
    format: double
    type: number
  userId:
    type: string
  workspaceId:
    type: string
type: object
```

<a id="schema-expensehydrateddtov1"></a>
### `ExpenseHydratedDtoV1`

```yaml
description: Hydrated expense row returned by the workspace expenses list. Carries nested category/project/task
  objects and fileName instead of the flat categoryId/projectId/taskId that ExpenseDtoV1 exposes.
type: object
properties:
  billable:
    default: false
    description: Indicates whether expense is billable or not.
    type: boolean
  category:
    $ref: '#/components/schemas/ExpenseCategoryDto'
  date:
    description: Represents a date in yyyy-MM-dd format.
    example: '2020-01-01'
    type: string
  fileId:
    description: Represents file identifier across the system. Usually an empty string when the expense has no receipt
      (2816 of 2845 sandbox rows); 22 rows carried null instead, so consumers must treat both as "no receipt".
    type: string
  fileName:
    description: Represents the uploaded receipt file name. Null when the expense has no receipt.
    type: string
  id:
    description: Represents expense identifier across the system.
    type: string
  locked:
    description: Indicates whether the expense is locked.
    type: boolean
  notes:
    description: Represents notes for an expense.
    type: string
  project:
    $ref: '#/components/schemas/ProjectInfoDto'
  quantity:
    description: Represents expense quantity as double data type.
    format: double
    type: number
  task:
    $ref: '#/components/schemas/TaskInfoDto'
  total:
    description: Represents expense total as double data type.
    format: double
    type: number
  userId:
    description: Represents user identifier across the system.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
```

<a id="schema-expensereportdtov1"></a>
### `ExpenseReportDtoV1`

```yaml
description: Represents list of expenses
properties:
  amount:
    description: Represents expenses amount.
    format: double
    type: number
  approvalRequestId:
    description: Represents approval request identifier across the system.
    example: 5b715612b079875110791336
    type: string
  billable:
    description: Indicates whether the expenses is billable.
    type: boolean
  categoryHasUnitPrice:
    description: Indicates whether category has unit price.
    type: boolean
  categoryId:
    description: Represents category identifier across the system.
    example: 5b715612b079875110791334
    type: string
  categoryName:
    description: Represents category's name.
    type: string
  categoryUnit:
    description: Represents category's unit.
    type: string
  date:
    description: Represents expenses date in YYYY-MM-DDTHH:MM:SS.ssssssZ format.
    example: '2021-10-27T00:00:00Z'
    type: string
  exportFields:
    description: Represents export fields.
    items:
      description: Represents export fields.
      enum:
      - PROJECT
      - CLIENT
      - TASK
      - DESCRIPTION
      - USER
      - TAGS
      - START_DATE
      - START_TIME
      - END_TIME
      - DURATION
      - BILLABLE_AMOUNT
      - COST_AMOUNT
      - PROFIT
      - EMAIL
      - BILLABLE
      - BILLABLE_H
      - NON_BILLABLE_H
      - END_DATE
      - DECIMAL_DURATION
      - BILLABLE_RATE
      - COST_RATE
      - APPROVAL
      - BAR_CHART
      - PIE_CHART_1
      - PIE_CHART_2
      - PIE_CHART_3
      - RTL
      - TOTAL
      - SUBGROUP
      - GROUP
      - DATE
      - TIME
      - CATEGORY
      - NOTE
      - AMOUNT
      - INVOICED
      - INVOICE_ID
      - CATEGORY_NO_OF_UNITS
      - CATEGORY_UNIT
      - KIOSK
      - KIOSK_QR_CODE
      - TYPE
      - BREAK
      - NOTES
      - BILLABLE_TOTAL
      - RECEIPTS
      - EXPENSE_TOTAL
      - DATE_OF_CREATION
      - DATE_OF_APPROVAL
      - NAME
      - ROLE
      - PROJECTS
      - STATUS
      - WEEK_START
      - WORKING_DAYS
      - TEAM_MANAGERS
      - TEAM_MEMBERS
      - DAILY_WORK_CAPACITY
      - VISIBILITY
      - BILLABILITY
      - TASKS
      - TRACKED_H
      - ESTIMATED_H
      - REMAINING_H
      - OVERAGE_H
      - TRACKED_BUDGET
      - ESTIMATED_BUDGET
      - REMAINING_BUDGET
      - OVERAGE_BUDGET
      - PROGRESS
      - RECURRING_ESTIMATE
      - EXPENSES
      - BILLABLE_EXPENSES
      - NON_BILLABLE_EXPENSES
      - ADDITIONAL_FIELDS
      - PROJECT_MEMBERS
      - PROJECT_MANAGER
      - APPROVED_BY
      - ISSUE_DATE
      - DUE_ON
      - BALANCE
      type: string
    type: array
  fileId:
    description: Represents file identifier across the system.
    example: 5b715612b079875110791335
    type: string
  fileName:
    description: Represents expenses file name.
    type: string
  id:
    description: Represents expenses identifier across the system.
    example: 5b715612b079875110791122
    type: string
  invoicingInfo:
    $ref: '#/components/schemas/invoicingInfo'
  locked:
    description: Indicates whether the expenses is locked.
    type: boolean
  notes:
    description: Represents expenses note.
    example: Expenses Note
    type: string
  projectColor:
    description: Represents project's color
    type: string
  projectId:
    description: Represents project identifier across the system.
    example: 5b715612b079875110791333
    type: string
  projectName:
    description: Represents project's name.
    type: string
  quantity:
    description: Represents expenses quantity
    example: 10
    format: double
    type: number
  reportName:
    description: Represents expense name.
    type: string
  time:
    description: Represents expense time.
    type: string
  userEmail:
    description: Represents user's email.
    type: string
  userId:
    description: Represents user identifier across the system.
    example: 5b715612b079875110791121
    type: string
  userName:
    description: Represents user's name.
    type: string
  userStatus:
    description: Represents user's status.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    example: 5b715612b079875110791121
    type: string
type: object
```

<a id="schema-expensereportfilterv1"></a>
### `ExpenseReportFilterV1`

```yaml
properties:
  approvalState:
    description: Represents an approval state
    enum:
    - APPROVED
    - UNAPPROVED
    - ALL
    example: APPROVED
    type: string
  billable:
    description: Indicates whether report is billable
    example: true
    type: boolean
  categories:
    $ref: '#/components/schemas/ContainsArchivedFilterV1'
  clients:
    $ref: '#/components/schemas/ContainsArchivedFilterV1'
  currency:
    $ref: '#/components/schemas/ContainsArchivedFilterV1'
  dateRangeEnd:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. The system interprets this value based on the
      user's timezone (provided in the timeZone request parameter or the timezone configured in the user profile)
    example: '2021-10-27T23:59:59.999'
    minLength: 1
    type: string
  dateRangeStart:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. The system interprets this value based on the
      user's timezone (provided in the timeZone request parameter or the timezone configured in the user profile)
    example: '2021-10-27T00:00:00'
    minLength: 1
    type: string
  dateRangeType:
    description: Represents date range type of expense report
    enum:
    - ABSOLUTE
    - TODAY
    - YESTERDAY
    - THIS_WEEK
    - LAST_WEEK
    - PAST_TWO_WEEKS
    - THIS_MONTH
    - LAST_MONTH
    - THIS_YEAR
    - LAST_YEAR
    example: TODAY
    type: string
  exportType:
    description: Represents an export type
    enum:
    - JSON
    - JSON_V1
    - PDF
    - CSV
    - XLSX
    - ZIP
    example: JSON
    type: string
  invoicingState:
    description: Represents an invoicing state
    enum:
    - INVOICED
    - UNINVOICED
    - ALL
    example: INVOICED
    type: string
  note:
    description: Represents a search term for filtering report entries by note
    example: some note keyword
    type: string
  page:
    description: Page number.
    example: 1
    format: int32
    minimum: 1
    type: integer
  pageSize:
    description: Page size.
    example: 50
    format: int32
    minimum: 1
    type: integer
  projects:
    $ref: '#/components/schemas/ContainsArchivedFilterV1'
  sortColumn:
    description: Represents expenses sort column
    enum:
    - ID
    - PROJECT
    - USER
    - CATEGORY
    - DATE
    - AMOUNT
    example: ID
    type: string
  sortOrder:
    description: Represents a sort order
    enum:
    - ASCENDING
    - DESCENDING
    example: ASCENDING
    type: string
  tasks:
    $ref: '#/components/schemas/ContainsTaskFilterV1'
  timeZone:
    description: Represents a time zone
    example: Europe/Budapest
    type: string
  userGroups:
    $ref: '#/components/schemas/ContainsUsersFilterV1'
  userLocale:
    description: Represents a user locale
    example: en
    type: string
  users:
    $ref: '#/components/schemas/ContainsUsersFilterV1'
  weekStart:
    description: Represents week start
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    example: MONDAY
    type: string
  withoutNote:
    description: If set to 'true', report will only include entries with empty note
    example: false
    type: boolean
  zoomLevel:
    description: Represents a zoom level
    enum:
    - WEEK
    - MONTH
    - YEAR
    example: WEEK
    type: string
required:
- dateRangeEnd
- dateRangeStart
type: object
```

<a id="schema-expensetotalsdtov1"></a>
### `ExpenseTotalsDtoV1`

```yaml
description: Represents expense totals
properties:
  expensesCount:
    description: Represents expenses count
    example: 2
    format: int32
    type: integer
  totalAmount:
    description: Represents total amount of expenses
    example: 20
    format: double
    type: number
  totalAmountBillable:
    description: Represents total billable amount of expenses
    example: 20
    format: double
    type: number
type: object
```

<a id="schema-expenseupdaterequest"></a>
### `ExpenseUpdateRequest`

```yaml
description: Multipart form-data request for updating an expense.
example:
  amount: 10500.5
  billable: false
  categoryId: 45y687e29ae1f428e7ebe890
  changeFields:
  - USER
  - DATE
  - PROJECT
  - TASK
  - CATEGORY
  - NOTES
  - AMOUNT
  - BILLABLE
  - FILE
  date: '2020-01-01T00:00:00Z'
  file: receipt.pdf
  notes: This is a sample note for this expense.
  projectId: 25b687e29ae1f428e7ebe123
  taskId: 25b687e29ae1f428e7ebe123
  userId: 89b687e29ae1f428e7ebe912
properties:
  amount:
    description: Represents an expense amount as the double data type.
    format: double
    maximum: 92233720368547760
    minimum: 0
    type: number
  billable:
    default: false
    description: Indicates whether expense is billable or not.
    type: boolean
  categoryId:
    default: '##default'
    description: Represents a category identifier across the system.
    type: string
  changeFields:
    description: Represents a list of expense change fields.
    items:
      enum:
      - USER
      - DATE
      - PROJECT
      - TASK
      - CATEGORY
      - NOTES
      - AMOUNT
      - BILLABLE
      - FILE
      type: string
    type: array
  date:
    description: Provides a valid yyyy-MM-ddThh:mm:ssZ format date.
    format: date-time
    type: string
  file:
    format: binary
    type: string
  notes:
    default: '##default'
    description: Represents notes for an expense.
    maxLength: 3000
    type: string
  projectId:
    default: '##default'
    description: Represents a project identifier across the system.
    type: string
  taskId:
    default: '##default'
    description: Represents a task identifier across the system.
    type: string
  userId:
    default: '##default'
    description: Represents a user identifier across the system.
    minLength: 1
    type: string
required:
- amount
- categoryId
- changeFields
- date
- userId
type: object
```

<a id="schema-expenseweeklytotalsdtov1"></a>
### `ExpenseWeeklyTotalsDtoV1`

```yaml
description: Represents an expense weekly total data transfer object.
properties:
  date:
    description: Date in yyyy-MM-dd format.
    example: '2020-01-01'
    type: string
  total:
    description: Represents expense total.
    format: double
    type: number
type: object
```

<a id="schema-expensesgroupby"></a>
### `ExpensesGroupBy`

```yaml
enum:
- CATEGORY
- PROJECT
- USER
type: string
```

<a id="schema-expensesgrouptype"></a>
### `ExpensesGroupType`

```yaml
enum:
- GROUPED
- DETAILED
type: string
```

<a id="schema-expenseswithcountdtov1"></a>
### `ExpensesWithCountDtoV1`

```yaml
description: Represents an expense with count data transfer object.
properties:
  count:
    description: Represents result count.
    format: int32
    type: integer
  expenses:
    items:
      $ref: '#/components/schemas/ExpenseHydratedDtoV1'
    type: array
type: object
```

<a id="schema-gettimeentriesbyidsrequest"></a>
### `GetTimeEntriesByIdsRequest`

```yaml
properties:
  hydrated:
    default: false
    description: Flag to set whether to include additional information of time entries or not.
    example: false
    type: boolean
  timeEntryIds:
    description: Represents time entry identifiers across the system.
    example:
    - 64c777ddd3fcab07cfbb210c
    items:
      description: Represents time entry identifiers across the system.
      example: '["64c777ddd3fcab07cfbb210c"]'
      type: string
    minItems: 1
    type: array
required:
- timeEntryIds
type: object
```

<a id="schema-grouponedto"></a>
### `GroupOneDto`

```yaml
additionalProperties: true
properties:
  amount:
    description: Group amount.
    type: number
  children:
    description: Nested child groups.
    items:
      $ref: '#/components/schemas/GroupOneDto'
    type: array
  clientName:
    description: Client name.
    type: string
  days:
    description: Daily totals for the group.
    items:
      $ref: '#/components/schemas/DailyTotalDto'
    type: array
  duration:
    description: Duration.
    type: number
  id:
    description: Group identifier.
    type: string
  name:
    description: Name.
    type: string
  nameLowerCase:
    description: Lowercase name.
    type: string
type: object
```

<a id="schema-halfdayperiod"></a>
### `HalfDayPeriod`

```yaml
description: Represents the half day period.
enum:
- FIRST_HALF
- SECOND_HALF
- NOT_DEFINED
type: string
```

<a id="schema-holidaydetailsdto"></a>
### `HolidayDetailsDto`

```yaml
description: Represents a holiday with detailed user and user group assignments.
properties:
  automaticTimeEntryCreation:
    $ref: '#/components/schemas/AutomaticTimeEntryCreationDto'
  color:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  datePeriod:
    $ref: '#/components/schemas/DatePeriod'
  everyoneIncludingNew:
    default: false
    description: Indicates whether the holiday is shown to new users.
    type: boolean
  id:
    description: Represents holiday identifier across the system.
    type: string
  name:
    description: Represents the name of the holiday.
    type: string
  occursAnnually:
    default: false
    description: Indicates whether the holiday occurs annually.
    type: boolean
  userGroupIds:
    description: Indicates which user groups are included.
    items:
      type: string
    type: array
    uniqueItems: true
  userGroups:
    description: Contains names of user groups that are assigned to holiday.
    items:
      $ref: '#/components/schemas/EntityIdNameDto'
    type: array
  userIds:
    description: Indicates which users are included.
    items:
      type: string
    type: array
    uniqueItems: true
  users:
    description: Contains names of users that are assigned to holiday.
    items:
      $ref: '#/components/schemas/EntityIdNameDto'
    type: array
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-holidaydto"></a>
### `HolidayDto`

```yaml
description: Represents a holiday on a workspace.
properties:
  automaticTimeEntryCreation:
    default: false
    description: Indicates that time entries will be automatically created for this holiday.
    type: boolean
  datePeriod:
    $ref: '#/components/schemas/DatePeriod'
  everyoneIncludingNew:
    default: false
    description: Indicates whether the holiday is shown to new users.
    type: boolean
  id:
    description: Represents holiday identifier across the system.
    type: string
  name:
    description: Represents the name of the holiday.
    type: string
  occursAnnually:
    default: false
    description: Indicates whether the holiday occurs annually.
    type: boolean
  projectId:
    description: Represents projectId for automatic time entry creation.
    type: string
  taskId:
    description: Represents taskId for automatic time entry creation.
    type: string
  userGroupIds:
    description: Indicates which user groups are included.
    items:
      type: string
    type: array
    uniqueItems: true
  userIds:
    description: Indicates which users are included.
    items:
      type: string
    type: array
    uniqueItems: true
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-hourlyratedtov1"></a>
### `HourlyRateDtoV1`

```yaml
description: Represents an hourly rate object.
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    type: integer
  currency:
    description: Represents a currency.
    type: string
type: object
```

<a id="schema-imageuploadresponse"></a>
### `ImageUploadResponse`

```yaml
properties:
  name:
    description: File name of the uploaded image.
    type: string
  url:
    description: The URL of the uploaded image in the server.
    type: string
type: object
```

<a id="schema-importinvoiceitemsrequest"></a>
### `ImportInvoiceItemsRequest`

```yaml
example:
  expenseFieldsForDetailedGroup:
  - NOTE
  expensesGroupBy: CATEGORY
  expensesGroupType: GROUPED
  from: '2025-06-01T00:00:00Z'
  importExpenses: false
  projectFilter:
    contains: CONTAINS
    ids:
    - 25b687e29ae1f428e7ebe123
    status: ACTIVE
  roundTimeEntryDuration: false
  timeEntryFieldsForDetailedGroup:
  - PROJECT
  - DESCRIPTION
  timeEntryGroupType: GROUPED
  timeEntryPrimaryGroupBy: PROJECT
  timeEntrySecondaryGroupBy: TASK
  to: '2025-06-07T00:00:00Z'
properties:
  expenseFieldsForDetailedGroup:
    default:
    - NOTE
    description: A set of expense fields to include when using the DETAILED expense grouping type.
    items:
      $ref: '#/components/schemas/ExpenseFieldsForDetailedGroup'
    type: array
    uniqueItems: true
  expensesGroupBy:
    allOf:
    - $ref: '#/components/schemas/ExpensesGroupBy'
    default: PROJECT
    description: Represents a group field when using the GROUPED expense group type.
  expensesGroupType:
    allOf:
    - $ref: '#/components/schemas/ExpensesGroupType'
    default: DETAILED
    description: Represents an expense group type.
  from:
    default: '##default'
    description: Represents date and time in the yyyy-MM-ddThh:mm:ssZ format.
    example: '2025-06-01T00:00:00Z'
    type: string
  importExpenses:
    default: false
    description: Indicates if billable expenses should be imported alongside time entries.
    type: boolean
  projectFilter:
    $ref: '#/components/schemas/ContainsArchivedFilterRequest'
  roundTimeEntryDuration:
    default: false
    description: Indicates if imported time entry durations should be rounded to the nearest 15 minute interval.
    type: boolean
  timeEntryFieldsForDetailedGroup:
    description: A set of time entry fields to include when using DETAILED time entry grouping type.
    items:
      $ref: '#/components/schemas/TimeEntryFieldsForDetailedGroup'
    type: array
    uniqueItems: true
  timeEntryGroupType:
    $ref: '#/components/schemas/TimeEntryGroupType'
  timeEntryPrimaryGroupBy:
    $ref: '#/components/schemas/TimeEntryPrimaryGroupBy'
  timeEntrySecondaryGroupBy:
    $ref: '#/components/schemas/TimeEntrySecondaryGroupBy'
  to:
    default: '##default'
    description: Represents date and time in the yyyy-MM-ddThh:mm:ssZ format.
    example: '2025-06-07T00:00:00Z'
    type: string
required:
- from
- importExpenses
- projectFilter
- timeEntryGroupType
- to
type: object
```

<a id="schema-invoicecreaterequest"></a>
### `InvoiceCreateRequest`

```yaml
example:
  clientId: 34p687e29ae1f428e7ebe562
  currency: USD
  dueDate: '2020-06-01T08:00:00Z'
  issuedDate: '2020-01-01T08:00:00Z'
  number: '202306121129'
  timeViewMode: AGGREGATED_TIME_VIEW
properties:
  clientId:
    default: '##default'
    description: Represents a client identifier across the system.
    minLength: 1
    type: string
  currency:
    default: '##default'
    description: Represents the currency used by the invoice.
    minLength: 1
    type: string
  dueDate:
    description: Represents an invoice due date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  issuedDate:
    description: Represents an invoice issued date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  number:
    default: '##default'
    description: Represents an invoice number.
    minLength: 1
    type: string
  timeViewMode:
    $ref: '#/components/schemas/TimeViewMode'
required:
- clientId
- currency
- dueDate
- issuedDate
- number
type: object
```

<a id="schema-invoicecreateresponse"></a>
### `InvoiceCreateResponse`

```yaml
properties:
  billFrom:
    default: '##default'
    description: Represents to whom the invoice should be billed from.
    type: string
  clientId:
    default: '##default'
    description: Represents client identifier across the system.
    type: string
  currency:
    default: '##default'
    description: Represents the currency used by the invoice.
    type: string
  dueDate:
    description: Represents an invoice due date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  id:
    default: '##default'
    description: Represents invoice identifier across the system.
    type: string
  issuedDate:
    description: Represents an invoice issued date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  number:
    default: '##default'
    description: Represents an invoice number.
    type: string
type: object
```

<a id="schema-invoicedefaultsettingsrequestv1"></a>
### `InvoiceDefaultSettingsRequestV1`

```yaml
description: Represents an invoice default settings request object.
properties:
  companyId:
    default: '##default'
    description: Represents company identifier across the system.
    type: string
  dueDays:
    description: Represents an invoice number of due days.
    format: int32
    type: integer
  itemTypeId:
    default: '##default'
    description: Represents item type identifier across the system.
    type: string
  notes:
    default: '##default'
    description: Represents an invoice note.
    type: string
  subject:
    default: '##default'
    description: Represents an invoice subject.
    type: string
  tax2Percent:
    description: Represents a tax amount in percentage.
    format: double
    type: number
  taxPercent:
    description: Represents a tax amount in percentage.
    format: double
    type: number
  taxType:
    $ref: '#/components/schemas/TaxType'
required:
- notes
- subject
type: object
```

<a id="schema-invoicedtofull"></a>
### `InvoiceDtoFull`

```yaml
description: Represents a complete invoice object.
example:
  amount: 100
  balance: 50
  billFrom: Business X
  calculationType: INVOICE_BASED
  clientAddress: Ground Floor, ABC Bldg., Palo Alto, California, USA 94020
  clientId: 98h687e29ae1f428e7ebe707
  clientName: Client X
  companyId: 04g687e29ae1f428e7ebe123
  containsImportedExpenses: false
  containsImportedTimes: false
  currency: USD
  discount: 10.5
  discountAmount: 11
  dueDate: '2020-06-01T08:00:00Z'
  id: 78a687e29ae1f428e7ebe303
  issuedDate: '2020-01-01T08:00:00Z'
  items: []
  note: This is a sample note for this invoice.
  number: '202306121129'
  paid: 50
  status: PAID
  subject: January salary
  subtotal: 5000
  tax: 1.5
  tax2: 0
  tax2Amount: 0
  taxAmount: 1
  taxType: SIMPLE
  userId: 12t687e29ae1f428e7ebe202
  visibleZeroFields:
  - TAX
  - TAX_2
  - DISCOUNT
properties:
  amount:
    description: Represents an invoice amount as long.
    format: int64
    type: integer
  balance:
    description: Represents an invoice balance amount as long.
    format: int64
    type: integer
  billFrom:
    default: '##default'
    description: Represents to whom the invoice should be billed from.
    type: string
  calculationType:
    $ref: '#/components/schemas/CalculationType'
  clientAddress:
    default: '##default'
    description: Represents client address.
    type: string
  clientId:
    default: '##default'
    description: Represents client identifier across the system.
    type: string
  clientName:
    default: '##default'
    description: Represents client name for an invoice.
    type: string
  companyId:
    default: '##default'
    description: Represents company identifier across the system.
    type: string
  containsImportedExpenses:
    default: false
    description: Indicates whether invoice contains imported expenses.
    type: boolean
  containsImportedTimes:
    default: false
    description: Indicates whether invoice contains imported items.
    type: boolean
  currency:
    default: '##default'
    description: Represents the currency used by the invoice.
    type: string
  discount:
    description: Represents an invoice discount amount as double.
    format: double
    type: number
  discountAmount:
    description: Represents an invoice discount amount as long.
    format: int64
    type: integer
  dueDate:
    description: Represents an invoice due date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  id:
    default: '##default'
    description: Represents invoice identifier across the system.
    type: string
  issuedDate:
    description: Represents an invoice issued date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  items:
    description: Represents a list of invoice item datatransfer objects.
    items:
      $ref: '#/components/schemas/InvoiceItemDto'
    type: array
    x-sourceDefault: '##default'
  note:
    default: '##default'
    description: Represents an invoice note.
    type: string
  number:
    default: '##default'
    description: Represents an invoice number.
    type: string
  paid:
    description: Represents an invoice paid amount as long.
    format: int64
    type: integer
  status:
    $ref: '#/components/schemas/InvoiceStatus'
  subject:
    default: '##default'
    description: Represents an invoice subject.
    type: string
  subtotal:
    description: Represents an invoice subtotal as long.
    format: int64
    type: integer
  tax:
    description: Represents an invoice tax amount as double.
    format: double
    type: number
  tax2:
    description: Represents an invoice tax amount as double.
    format: double
    type: number
  tax2Amount:
    description: Represents an invoice tax amount as long.
    format: int64
    type: integer
  taxAmount:
    description: Represents an invoice tax amount as long.
    format: int64
    type: integer
  taxType:
    $ref: '#/components/schemas/TaxType'
  userId:
    default: '##default'
    description: Represents user identifier across the system.
    type: string
  visibleZeroFields:
    description: Represents a list of zero value invoice fields that will be visible.
    items:
      $ref: '#/components/schemas/VisibleZeroFieldsInvoice'
    type: array
type: object
```

<a id="schema-invoicedtov1"></a>
### `InvoiceDtoV1`

```yaml
description: Represents an invoice summary.
properties:
  amount:
    description: Represents an invoice amount as long.
    format: int64
    type: integer
  balance:
    description: Represents an invoice balance amount as long.
    format: int64
    type: integer
  clientId:
    default: '##default'
    description: Represents client identifier across the system.
    type: string
  clientName:
    default: '##default'
    description: Represents client name for an invoice.
    type: string
  currency:
    default: '##default'
    description: Represents the currency used by the invoice.
    type: string
  dueDate:
    description: Represents an invoice due date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  id:
    default: '##default'
    description: Represents invoice identifier across the system.
    type: string
  issuedDate:
    description: Represents an invoice issued date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  number:
    default: '##default'
    description: Represents an invoice number.
    type: string
  paid:
    description: Represents an invoice paid amount as long.
    format: int64
    type: integer
  status:
    $ref: '#/components/schemas/InvoiceStatus'
type: object
```

<a id="schema-invoiceexportfieldsrequest"></a>
### `InvoiceExportFieldsRequest`

```yaml
description: Represents an invoice export fields request object.
properties:
  itemType:
    default: false
    description: Indicates whether to export item type.
    type: boolean
  quantity:
    default: false
    description: Indicates whether to export quantity.
    type: boolean
  rtl:
    default: false
    description: Indicates whether to export RTL.
    type: boolean
  tax:
    default: false
    description: Indicates whether to export tax.
    type: boolean
  tax2:
    default: false
    description: Indicates whether to export tax2.
    type: boolean
  unitPrice:
    default: false
    description: Indicates whether to export unit price.
    type: boolean
type: object
```

<a id="schema-invoicefilterrequest"></a>
### `InvoiceFilterRequest`

```yaml
description: Request body for filtering invoices.
example:
  clients:
    contains: CONTAINS
    ids:
    - 44a687e29ae1f428e7ebe305
    status: ACTIVE
  companies:
    contains: CONTAINS
    ids:
    - 04g687e29ae1f428e7ebe123
  exactAmount: 1000
  exactBalance: 1000
  greaterThanAmount: 500
  greaterThanBalance: 500
  invoiceNumber: Invoice-01
  issueDate:
    issue-date-end: '2024-12-31'
    issue-date-start: '2024-01-01'
  lessThanAmount: 500
  lessThanBalance: 500
  page: 1
  pageSize: 50
  sortColumn: ID
  sortOrder: ASCENDING
  statuses:
  - SENT
  - PAID
  - PARTIALLY_PAID
  strictSearch: false
properties:
  clients:
    $ref: '#/components/schemas/ContainsArchivedFilterRequest'
  companies:
    $ref: '#/components/schemas/BaseFilterRequest'
  exactAmount:
    description: If provided, filters invoices with the exact amount.
    format: int64
    type: integer
  exactBalance:
    description: If provided, filters invoices with the exact balance.
    format: int64
    type: integer
  greaterThanAmount:
    description: If provided, filters invoices with amount greater than specified.
    format: int64
    type: integer
  greaterThanBalance:
    description: If provided, filters invoices with balance greater than specified.
    format: int64
    type: integer
  invoiceNumber:
    default: '##default'
    description: If provided, filters invoices that contain the provided string in their invoice number.
    type: string
  issueDate:
    $ref: '#/components/schemas/TimeRangeRequestDtoV1'
  lessThanAmount:
    description: If provided, filters invoices with amount less than specified.
    format: int64
    type: integer
  lessThanBalance:
    description: If provided, filters invoices with balance less than specified.
    format: int64
    type: integer
  page:
    default: 1
    description: Page number.
    format: int32
    type: integer
  pageSize:
    default: 50
    description: Page size.
    format: int32
    type: integer
  sortColumn:
    $ref: '#/components/schemas/InvoiceSortColumn'
  sortOrder:
    $ref: '#/components/schemas/InvoicesSortOrder'
  statuses:
    description: Represents a list of invoice statuses.
    items:
      $ref: '#/components/schemas/InvoiceStatus'
    type: array
  strictSearch:
    default: false
    description: When true, search by invoice number only returns invoices whose number exactly matches the provided
      string.
    type: boolean
type: object
```

<a id="schema-invoiceimporttype"></a>
### `InvoiceImportType`

```yaml
description: Represents the invoice item import type.
enum:
- NOT_IMPORTED
- TIME_ENTRY_IMPORT
- EXPENSE_IMPORT
type: string
```

<a id="schema-invoiceinfolistresponse"></a>
### `InvoiceInfoListResponse`

```yaml
properties:
  invoices:
    description: Represents a list of invoice info.
    items:
      $ref: '#/components/schemas/InvoiceInfoV1'
    type: array
    x-sourceDefault: '##default'
  total:
    description: Represents the total invoice count.
    format: int64
    type: integer
type: object
```

<a id="schema-invoiceinfov1"></a>
### `InvoiceInfoV1`

```yaml
description: Represents invoice info returned by filtered invoice search.
properties:
  amount:
    description: Represents an invoice amount as long.
    format: int64
    type: integer
  balance:
    description: Represents an invoice balance amount as long.
    format: int64
    type: integer
  billFrom:
    default: '##default'
    description: Represents to whom an invoice is billed from.
    type: string
  clientId:
    default: '##default'
    description: Represents client identifier across the system.
    type: string
  clientName:
    default: '##default'
    description: Represents client name for an invoice.
    type: string
  currency:
    default: '##default'
    description: Represents the currency used by the invoice.
    type: string
  daysOverdue:
    description: Represents the number of days an invoice is overdue.
    format: int64
    type: integer
  dueDate:
    description: Represents an invoice due date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  id:
    default: '##default'
    description: Represents invoice identifier across the system.
    type: string
  issuedDate:
    description: Represents an invoice issued date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  number:
    default: '##default'
    description: Represents an invoice number.
    type: string
  paid:
    description: Represents an invoice paid amount as long.
    format: int64
    type: integer
  status:
    $ref: '#/components/schemas/InvoiceStatus'
  visibleZeroFields:
    description: Represents a list of zero value invoice fields that will be visible.
    items:
      $ref: '#/components/schemas/VisibleZeroFieldsInvoice'
    type: array
type: object
```

<a id="schema-invoiceitemdto"></a>
### `InvoiceItemDto`

```yaml
description: Represents an invoice item data transfer object.
properties:
  amount:
    description: Represents item amount.
    format: int64
    type: integer
  applyTaxes:
    $ref: '#/components/schemas/ApplyTaxes'
  description:
    default: '##default'
    description: Represents an invoice item description.
    type: string
  expenseIds:
    description: Represents a list of imported expense ids.
    items:
      type: string
    type: array
  importType:
    $ref: '#/components/schemas/InvoiceImportType'
  itemType:
    default: '##default'
    description: Represents item type.
    type: string
  order:
    description: Represents an integer.
    format: int32
    type: integer
  quantity:
    description: Represents item quantity.
    format: int64
    type: integer
  timeEntryIds:
    description: Represents a list of imported time entry ids.
    items:
      type: string
    type: array
  unitPrice:
    description: Represents item unit price.
    format: int64
    type: integer
type: object
```

<a id="schema-invoicelistresponse"></a>
### `InvoiceListResponse`

```yaml
properties:
  invoices:
    description: Represents a list of invoices.
    items:
      $ref: '#/components/schemas/InvoiceDtoV1'
    type: array
    x-sourceDefault: '##default'
  total:
    description: Represents the total invoice count.
    format: int64
    type: integer
type: object
```

<a id="schema-invoicepaymentdto"></a>
### `InvoicePaymentDto`

```yaml
description: Represents an invoice payment.
properties:
  amount:
    description: Represents an invoice payment amount as long.
    format: int64
    type: integer
  author:
    default: '##default'
    description: Represents an invoice payment author.
    type: string
  date:
    description: Represents an invoice payment date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  id:
    default: '##default'
    description: Represents invoice payment identifier across the system.
    type: string
  note:
    default: '##default'
    description: Represents an invoice payment note.
    type: string
type: object
```

<a id="schema-invoicesettingsrequest"></a>
### `InvoiceSettingsRequest`

```yaml
description: Request body for updating invoice settings/language labels.
example:
  defaults: {}
  exportFields: {}
  labels:
    amount: amount
    billFrom: billFrom
    billTo: billTo
    description: description
    discount: discount
    dueDate: dueDate
    issueDate: issueDate
    itemType: itemType
    notes: notes
    paid: paid
    quantity: quantity
    subtotal: subtotal
    tax: tax
    tax2: tax2
    total: total
    totalAmountDue: totalAmountDue
    unitPrice: unitPrice
properties:
  defaults:
    $ref: '#/components/schemas/InvoiceDefaultSettingsRequestV1'
  exportFields:
    $ref: '#/components/schemas/InvoiceExportFieldsRequest'
  labels:
    $ref: '#/components/schemas/LabelsCustomizationRequest'
required:
- labels
type: object
```

<a id="schema-invoicesettingsresponse"></a>
### `InvoiceSettingsResponse`

```yaml
properties:
  defaults:
    $ref: '#/components/schemas/OpenapiInvoiceDefaultSettingsDto'
  exportFields:
    $ref: '#/components/schemas/OpenapiInvoiceExportFields'
  labels:
    $ref: '#/components/schemas/OpenapiLabelsCustomization'
type: object
```

<a id="schema-invoicesortcolumn"></a>
### `InvoiceSortColumn`

```yaml
description: Invoice sorting column.
enum:
- ID
- CLIENT
- DUE_ON
- ISSUE_DATE
- AMOUNT
- BALANCE
type: string
```

<a id="schema-invoicestatus"></a>
### `InvoiceStatus`

```yaml
description: Represents the live status of an invoice. DRAFT is rejected by Clockify; use UNSENT for draft-like
  invoices.
enum:
- UNSENT
- SENT
- PAID
- PARTIALLY_PAID
- VOID
- OVERDUE
type: string
```

<a id="schema-invoicestatusrequest"></a>
### `InvoiceStatusRequest`

```yaml
example:
  invoiceStatus: PAID
properties:
  invoiceStatus:
    $ref: '#/components/schemas/InvoiceStatus'
required:
- invoiceStatus
type: object
```

<a id="schema-invoicessortorder"></a>
### `InvoicesSortOrder`

```yaml
description: Sorting order.
enum:
- ASCENDING
- DESCENDING
type: string
```

<a id="schema-labelscustomizationrequest"></a>
### `LabelsCustomizationRequest`

```yaml
description: Represents a label customization request object.
properties:
  amount:
    default: '##default'
    description: Represents invoice amount label.
    maxLength: 20
    minLength: 0
    type: string
  billFrom:
    default: '##default'
    description: Represents invoice billFrom label.
    maxLength: 20
    minLength: 0
    type: string
  billTo:
    default: '##default'
    description: Represents invoice billTo label.
    maxLength: 20
    minLength: 0
    type: string
  description:
    default: '##default'
    description: Represents invoice description label.
    maxLength: 20
    minLength: 0
    type: string
  discount:
    default: '##default'
    description: Represents invoice discount label.
    maxLength: 20
    minLength: 0
    type: string
  dueDate:
    default: '##default'
    description: Represents invoice dueDate label.
    maxLength: 20
    minLength: 0
    type: string
  issueDate:
    default: '##default'
    description: Represents invoice issueDate label.
    maxLength: 20
    minLength: 0
    type: string
  itemType:
    default: '##default'
    description: Represents invoice itemType label.
    maxLength: 20
    minLength: 0
    type: string
  notes:
    default: '##default'
    description: Represents invoice notes label.
    maxLength: 20
    minLength: 0
    type: string
  paid:
    default: '##default'
    description: Represents invoice paid label.
    maxLength: 20
    minLength: 0
    type: string
  quantity:
    default: '##default'
    description: Represents invoice quantity label.
    maxLength: 20
    minLength: 0
    type: string
  subtotal:
    default: '##default'
    description: Represents invoice subtotal label.
    maxLength: 20
    minLength: 0
    type: string
  tax:
    default: '##default'
    description: Represents invoice tax label.
    maxLength: 20
    minLength: 0
    type: string
  tax2:
    default: '##default'
    description: Represents invoice tax2 label.
    maxLength: 20
    minLength: 0
    type: string
  total:
    default: '##default'
    description: Represents invoice total label.
    maxLength: 20
    minLength: 0
    type: string
  totalAmountDue:
    default: '##default'
    description: Represents invoice totalAmountDue label.
    maxLength: 20
    minLength: 0
    type: string
  unitPrice:
    default: '##default'
    description: Represents invoice unitPrice label.
    maxLength: 20
    minLength: 0
    type: string
required:
- amount
- billFrom
- billTo
- description
- discount
- dueDate
- issueDate
- itemType
- notes
- paid
- quantity
- subtotal
- tax
- tax2
- total
- totalAmountDue
- unitPrice
type: object
```

<a id="schema-limiteduserrequest"></a>
### `LimitedUserRequest`

```yaml
properties:
  costRate:
    format: int32
    minimum: 0
    type: integer
  hourlyRate:
    format: int32
    minimum: 0
    type: integer
  name:
    minLength: 1
    type: string
  userCustomFields:
    items:
      $ref: '#/components/schemas/UpsertUserCustomFieldRequest'
    type: array
  userGroups:
    items:
      minLength: 1
      type: string
    type: array
    uniqueItems: true
  weekStart:
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  workCapacity:
    type: string
  workingDays:
    items:
      enum:
      - MONDAY
      - TUESDAY
      - WEDNESDAY
      - THURSDAY
      - FRIDAY
      - SATURDAY
      - SUNDAY
      type: string
    type: array
required:
- name
type: object
```

<a id="schema-managerrolerequest"></a>
### `ManagerRoleRequest`

```yaml
description: Request body used to add or remove a user's manager role.
properties:
  entityId:
    description: Represents an entity identifier across the system.
    minLength: 1
    type: string
  role:
    description: Represents a valid role.
    enum:
    - WORKSPACE_ADMIN
    - TEAM_MANAGER
    - PROJECT_MANAGER
    type: string
  sourceType:
    description: Optional field used to indicate that the target of the operation is a user group.
    enum:
    - USER_GROUP
    type: string
required:
- entityId
- role
type: object
```

<a id="schema-memberprofiledtov1"></a>
### `MemberProfileDtoV1`

```yaml
description: Represents a member profile.
properties:
  email:
    description: Represents email address of the user.
    format: email
    type: string
  hasPassword:
    default: false
    description: Indicates whether user has password or none.
    type: boolean
  hasPendingApprovalRequest:
    default: false
    description: Indicates whether user has pending approval request.
    type: boolean
  imageUrl:
    description: Represents an image url.
    type: string
  name:
    description: Represents name of the user.
    type: string
  userCustomFieldValues:
    description: Represents a list of value objects for user’s custom fields.
    items:
      $ref: '#/components/schemas/UserCustomFieldValueFullDtoV1'
    type: array
  weekStart:
    $ref: '#/components/schemas/UsersDayOfWeek'
  workCapacity:
    description: Represents work capacity as a time duration in the ISO-8601 format.
    type: string
  workingDays:
    description: Live Clockify serializes working days as an array of day enum strings; JSON-encoded strings are
      rejected.
    items:
      type: string
      enum:
      - MONDAY
      - TUESDAY
      - WEDNESDAY
      - THURSDAY
      - FRIDAY
      - SATURDAY
      - SUNDAY
    type: array
  workspaceNumber:
    description: Represents the number of workspace(s) the user is associated to.
    format: int32
    type: integer
type: object
```

<a id="schema-memberprofileupdaterequest"></a>
### `MemberProfileUpdateRequest`

```yaml
description: Request body for updating a member profile.
properties:
  imageUrl:
    description: Represents an image url. A field that can only be updated for limited users.
    type: string
  name:
    deprecated: true
    description: Deprecated. Represents name of the user and can only be updated for limited users.
    maxLength: 100
    minLength: 1
    type: string
  removeProfileImage:
    default: false
    description: Indicates whether to remove profile image or not.
    type: boolean
  userCustomFields:
    description: Represents a list of upsert user custom field objects.
    items:
      $ref: '#/components/schemas/UpsertUserCustomFieldRequest'
    type: array
  weekStart:
    $ref: '#/components/schemas/UsersDayOfWeek'
  workCapacity:
    description: Represents work capacity as a time duration in ISO-8601 format. For example, PT7H.
    type: string
  workingDays:
    description: Live Clockify serializes working days as an array of day enum strings; JSON-encoded strings are
      rejected.
    items:
      type: string
      enum:
      - MONDAY
      - TUESDAY
      - WEDNESDAY
      - THURSDAY
      - FRIDAY
      - SATURDAY
      - SUNDAY
    type: array
type: object
```

<a id="schema-membershipdtov1"></a>
### `MembershipDtoV1`

```yaml
additionalProperties: false
description: Represents a membership object.
properties:
  costRate:
    $ref: '#/components/schemas/RateDtoV1'
  hourlyRate:
    $ref: '#/components/schemas/RateDtoV1'
  membershipStatus:
    description: Represents a membership status enum.
    enum:
    - PENDING
    - ACTIVE
    - DECLINED
    - INACTIVE
    - ALL
    type: string
  membershipType:
    description: Represents membership type enum.
    enum:
    - WORKSPACE
    - PROJECT
    - USERGROUP
    type: string
  targetId:
    description: Represents target identifier across the system.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
type: object
```

<a id="schema-membershiprequest"></a>
### `MembershipRequest`

```yaml
additionalProperties: false
description: Represents a membership request object.
properties:
  hourlyRate:
    $ref: '#/components/schemas/RateRequest'
  membershipStatus:
    enum:
    - PENDING
    - ACTIVE
    - DECLINED
    - INACTIVE
    - ALL
    type: string
  membershipType:
    enum:
    - WORKSPACE
    - PROJECT
    - USERGROUP
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
type: object
```

<a id="schema-membershipstatus"></a>
### `MembershipStatus`

```yaml
enum:
- PENDING
- ACTIVE
- DECLINED
- INACTIVE
- ALL
type: string
```

<a id="schema-milestonedto"></a>
### `MilestoneDto`

```yaml
additionalProperties: false
description: Represents a milestone object.
properties:
  date:
    description: Represents a date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  id:
    description: Represents milestone identifier across the system.
    type: string
  name:
    description: Represents milestone name.
    type: string
  projectId:
    description: Represents project identifier across the system.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-negativebalancedto"></a>
### `NegativeBalanceDto`

```yaml
description: Represents negative balance data including amount, time unit, and period.
properties:
  amount:
    format: double
    type: number
  period:
    type: string
  shouldReset:
    type: boolean
  timeUnit:
    type: string
type: object
```

<a id="schema-negativebalancerequest"></a>
### `NegativeBalanceRequest`

```yaml
description: Negative balance data to use for creating or updating the policy.
properties:
  amount:
    description: Represents negative balance amount.
    format: double
    minimum: 0
    type: number
  amountValidForTimeUnit:
    type: boolean
  period:
    description: Represents negative balance period.
    enum:
    - MONTH
    - YEAR
    type: string
  shouldReset:
    default: false
    description: Indicates whether negative balance should reset at the end of the period.
    type: boolean
  timeUnit:
    description: Represents negative balance time unit.
    enum:
    - DAYS
    - HOURS
    type: string
type: object
```

<a id="schema-openapiinvoicedefaultsettingsdto"></a>
### `OpenapiInvoiceDefaultSettingsDto`

```yaml
description: Represents an invoice default settings object.
properties:
  companyId:
    description: Represents company identifier across the system.
    example: 34a687e29ae1f428e7ebe101
    type: string
  defaultImportExpenseItemTypeId:
    description: Represents item type identifier across the system.
    example: 88a687e29ae1f428e7ebe303
    type: string
  defaultImportTimeItemTypeId:
    description: Represents item type identifier across the system.
    example: 18a687e29ae1f428e7ebe303
    type: string
  dueDays:
    description: Represents an invoice number of due days.
    example: 2
    format: int32
    type: integer
  itemType:
    type: string
    writeOnly: true
  itemTypeId:
    description: Represents item type identifier across the system.
    example: 78a687e29ae1f428e7ebe303
    type: string
  notes:
    description: Represents an invoice note.
    example: This is a sample note for this invoice.
    type: string
  subject:
    description: Represents an invoice subject.
    example: January salary
    type: string
  tax:
    deprecated: true
    format: int64
    type: integer
  tax2:
    deprecated: true
    format: int64
    type: integer
  tax2Percent:
    description: Represents a tax amount in percentage.
    example: 1
    format: double
    type: number
  taxPercent:
    description: Represents a tax amount in percentage.
    example: 5
    format: double
    type: number
  taxType:
    description: Represents a tax type.
    enum:
    - COMPOUND
    - SIMPLE
    - NONE
    example: COMPOUND
    type: string
type: object
```

<a id="schema-openapiinvoiceexportfields"></a>
### `OpenapiInvoiceExportFields`

```yaml
description: Represents an invoice export fields object.
properties:
  RTL:
    type: boolean
    writeOnly: true
  itemType:
    type: boolean
  quantity:
    type: boolean
  rtl:
    type: boolean
  tax:
    type: boolean
  tax2:
    type: boolean
  unitPrice:
    type: boolean
type: object
```

<a id="schema-openapilabelscustomization"></a>
### `OpenapiLabelsCustomization`

```yaml
description: Represents a label customization object.
properties:
  amount:
    description: Represents invoice amount.
    example: '1000'
    type: string
  billFrom:
    description: Represents a string an invoice is billed from.
    example: Entity A
    type: string
  billTo:
    description: Represents a string an invoice is billed to.
    example: Entity B
    type: string
  description:
    description: Represents a description of an invoice.
    example: This is a sample description for this invoice.
    type: string
  discount:
    description: Represents invoice discount amount.
    example: '0'
    type: string
  dueDate:
    description: Represents a due date in yyyy-MM-dd format.
    example: '2020-01-01'
    type: string
  issueDate:
    description: Represents an issue date in yyyy-MM-dd format.
    example: '2020-01-01'
    type: string
  itemType:
    description: Represents an item type.
    example: Service
    type: string
  notes:
    description: Represents notes for an invoice.
    example: This is a sample note for this invoice.
    type: string
  paid:
    description: Represents invoice paid amount.
    example: '1000'
    type: string
  quantity:
    description: Represents quantity.
    example: '10'
    type: string
  subtotal:
    description: Represents invoice subtotal.
    example: '1000'
    type: string
  tax:
    description: Represents invoice tax amount.
    example: '10'
    type: string
  tax2:
    description: Represents invoice tax amount.
    example: '0'
    type: string
  total:
    description: Represents invoice total amount.
    example: '1010'
    type: string
  totalAmount:
    description: Represents invoice total amount.
    example: '1010'
    type: string
  unitPrice:
    description: Represents unit price.
    example: '100'
    type: string
type: object
```

<a id="schema-openapiratedto"></a>
### `OpenapiRateDto`

```yaml
properties:
  amount:
    description: Rate in minor units (cents). e.g. 12000 = 120.00
    type: integer
  currency:
    $ref: '#/components/schemas/Currency'
type: object
```

<a id="schema-openapiratedto2"></a>
### `OpenapiRateDto2`

```yaml
description: Represents hourly rate object.
properties:
  amount:
    description: Represents an amount as integer.
    example: 10500
    format: int32
    type: integer
  currency:
    description: Represents a currency.
    example: USD
    type: string
type: object
```

<a id="schema-period"></a>
### `Period`

```yaml
description: Represents a period with date-time start and end values.
properties:
  end:
    format: date-time
    type: string
  start:
    format: date-time
    type: string
type: object
```

<a id="schema-periodv1request"></a>
### `PeriodV1Request`

```yaml
description: Represents period of time off request including start and end date.
properties:
  days:
    description: Provide number of days.
    format: int32
    maximum: 999
    minimum: 1
    type: integer
  end:
    description: Provide end date in YYYY-MM-DD format.
    format: date
    type: string
    x-clockify-default: '##default'
  start:
    description: Provide start date in YYYY-MM-DD format.
    format: date
    type: string
    x-clockify-default: '##default'
type: object
```

<a id="schema-policiesautomatictimeentrycreationdto"></a>
### `PoliciesAutomaticTimeEntryCreationDto`

```yaml
description: Represents automatic time entry creation settings.
properties:
  defaultEntities:
    $ref: '#/components/schemas/PoliciesDefaultEntitiesDto'
  enabled:
    description: Indicates that automatic time entry creation is enabled.
    type: boolean
type: object
```

<a id="schema-policiesdefaultentitiesdto"></a>
### `PoliciesDefaultEntitiesDto`

```yaml
description: Default project and task for automatically created time entries.
properties:
  projectId:
    type: string
  taskId:
    type: string
type: object
```

<a id="schema-policiesdefaultentitiesrequest"></a>
### `PoliciesDefaultEntitiesRequest`

```yaml
description: Default project and task for automatically created time entries.
properties:
  projectId:
    description: Default project for automatically created time entries.
    type: string
  taskId:
    description: Default task for automatically created time entries.
    type: string
type: object
```

<a id="schema-policiesusergroupidsschema"></a>
### `PoliciesUserGroupIdsSchema`

```yaml
description: User group filter with identifiers and status.
properties:
  contains:
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    type: string
  ids:
    description: Identifiers used for filtering.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Represents user status.
    enum:
    - ALL
    - ACTIVE
    - INACTIVE
    type: string
type: object
```

<a id="schema-policiesuseridsschema"></a>
### `PoliciesUserIdsSchema`

```yaml
description: User filter with identifiers and status.
properties:
  contains:
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    type: string
  ids:
    description: Identifiers used for filtering.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Represents user status.
    enum:
    - ALL
    - ACTIVE
    - INACTIVE
    type: string
type: object
```

<a id="schema-policy"></a>
### `Policy`

```yaml
description: Represents a time off policy.
properties:
  allowHalfDay:
    default: false
    description: Indicates whether half day is allowed.
    type: boolean
  allowNegativeBalance:
    default: false
    description: Indicates whether negative balance is allowed.
    type: boolean
  approve:
    $ref: '#/components/schemas/PolicyApprovalDto'
  archived:
    default: false
    description: Indicates whether the policy is archived.
    type: boolean
  automaticAccrual:
    $ref: '#/components/schemas/AutomaticAccrualDto'
  automaticTimeEntryCreation:
    $ref: '#/components/schemas/PoliciesAutomaticTimeEntryCreationDto'
  color:
    description: Policy color as a hex RGB value.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  everyoneIncludingNew:
    default: false
    description: Indicates whether the policy is applied to future new users.
    type: boolean
  icon:
    description: Policy icon.
    enum:
    - UMBRELLA
    - SNOWFLAKE
    - FAMILY
    - PLANE
    - STETHOSCOPE
    - HEALTH_METRICS
    - CHILDCARE
    - LUGGAGE
    - MONETIZATION
    - CALENDAR
    type: string
  id:
    description: Represents policy identifier across the system.
    type: string
  name:
    description: Represents the name of the policy.
    type: string
  negativeBalance:
    $ref: '#/components/schemas/NegativeBalanceDto'
  projectId:
    description: Represents project identifier across the system.
    type: string
  timeUnit:
    description: Represents the time unit of the policy.
    enum:
    - DAYS
    - HOURS
    type: string
  userGroupIds:
    description: User group identifiers included in the policy.
    items:
      type: string
    type: array
    uniqueItems: true
  userIds:
    description: User identifiers included in the policy.
    items:
      type: string
    type: array
    uniqueItems: true
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-policyapprovaldto"></a>
### `PolicyApprovalDto`

```yaml
description: Represents policy approval settings.
properties:
  requiresApproval:
    default: false
    description: Indicates whether approval is required.
    type: boolean
  specificMembers:
    default: false
    description: Indicates whether specific members are required to approve.
    type: boolean
  teamManagers:
    default: false
    description: Indicates whether team manager's approval is required.
    type: boolean
  userIds:
    description: Set of user identifiers across the system.
    items:
      type: string
    type: array
    uniqueItems: true
type: object
```

<a id="schema-policystatuschangerequest"></a>
### `PolicyStatusChangeRequest`

```yaml
description: Request body for changing a policy status.
properties:
  status:
    description: Status to use for changing the policy.
    enum:
    - ACTIVE
    - ARCHIVED
    type: string
required:
- status
type: object
```

<a id="schema-policytimeunit"></a>
### `PolicyTimeUnit`

```yaml
description: Represents policy time unit.
enum:
- DAYS
- HOURS
type: string
```

<a id="schema-project"></a>
### `Project`

```yaml
additionalProperties: false
description: Represents a Clockify project.
properties:
  archived:
    default: false
    description: Indicates whether project is archived or not.
    type: boolean
  billable:
    default: false
    description: Indicates whether project is billable or not.
    type: boolean
  budgetEstimate:
    $ref: '#/components/schemas/EstimateWithOptionsDto'
  clientId:
    description: Represents client identifier across the system.
    type: string
  clientName:
    description: Represents client name.
    type: string
  color:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  costRate:
    $ref: '#/components/schemas/RateDtoV1'
  duration:
    description: Represents project duration in milliseconds.
    type: string
  estimate:
    $ref: '#/components/schemas/EstimateDtoV1'
  estimateReset:
    $ref: '#/components/schemas/EstimateResetDto'
  hourlyRate:
    $ref: '#/components/schemas/RateDtoV1'
  id:
    description: Represents project identifier across the system.
    type: string
  memberships:
    description: Represents a list of membership objects.
    items:
      $ref: '#/components/schemas/MembershipDtoV1'
    type: array
  name:
    description: Represents a project name.
    type: string
  note:
    description: Represents project note.
    type: string
  public:
    default: false
    description: Indicates whether project is public or not.
    type: boolean
  template:
    default: false
    description: Indicates whether project is a template or not.
    type: boolean
  timeEstimate:
    $ref: '#/components/schemas/TimeEstimateDto'
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
required:
- id
- name
- workspaceId
- billable
- color
- archived
- public
- template
```

<a id="schema-projectassignmentstotal"></a>
### `ProjectAssignmentsTotal`

```yaml
additionalProperties: false
description: Represents scheduled assignment totals for a project.
properties:
  assignments:
    description: Represents a list of assignment per day objects.
    items:
      $ref: '#/components/schemas/AssignmentPerDayDto'
    type: array
  clientName:
    description: Represents project name.
    type: string
  milestones:
    description: Represents a list of milestone objects.
    items:
      $ref: '#/components/schemas/MilestoneDto'
    type: array
  projectArchived:
    default: false
    description: Indicates whether project is archived or not.
    type: boolean
  projectBillable:
    default: false
    description: Indicates whether project is billable or not.
    type: boolean
  projectColor:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  projectId:
    description: Represents project identifier across the system.
    type: string
  projectName:
    description: Represents project name.
    type: string
  taskId:
    description: Represents task identifier across the system.
    type: string
  taskName:
    description: Represents task name.
    type: string
  totalHours:
    description: Represents project total hours as double.
    format: double
    type: number
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-projectinfodto"></a>
### `ProjectInfoDto`

```yaml
description: Represents a project info object.
properties:
  clientId:
    description: Represents client identifier across the system.
    type: string
  clientName:
    description: Represents client name.
    type: string
  color:
    description: RGB hexadecimal color code.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  id:
    description: Represents project identifier across the system.
    type: string
  name:
    description: Represents a project name.
    type: string
type: object
```

<a id="schema-projecttotalsrequest"></a>
### `ProjectTotalsRequest`

```yaml
additionalProperties: false
description: Request for scheduled assignments per project.
properties:
  end:
    description: Represents an end date in the yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  page:
    default: 1
    description: Page number.
    format: int32
    type: integer
  pageSize:
    default: 50
    description: Page size.
    format: int32
    maximum: 200
    type: integer
  search:
    description: Represents a term for searching projects and clients by name.
    type: string
  start:
    description: Represents a start date in the yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  statusFilter:
    $ref: '#/components/schemas/StatusFilter'
required:
- start
- end
type: object
```

<a id="schema-projectsusergroupidsschema"></a>
### `ProjectsUserGroupIdsSchema`

```yaml
additionalProperties: false
description: Provide list with user group ids and corresponding status.
properties:
  contains:
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    type: string
  ids:
    description: Represents ids upon which filtering is performed.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Represents user status.
    enum:
    - ALL
    - ACTIVE
    - INACTIVE
    type: string
type: object
```

<a id="schema-publishassignmentsrequest"></a>
### `PublishAssignmentsRequest`

```yaml
additionalProperties: false
description: Request for publishing assignments.
properties:
  end:
    description: Represents end date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  notifyUsers:
    default: false
    description: Indicates whether to notify users when assignment is published.
    type: boolean
  search:
    description: Represents a search string.
    type: string
  start:
    description: Represents start date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  userFilter:
    $ref: '#/components/schemas/ContainsUsersFilterRequestV1'
  userGroupFilter:
    $ref: '#/components/schemas/ContainsUserGroupFilterRequestV1'
  viewType:
    $ref: '#/components/schemas/SchedulingViewType'
required:
- start
- end
type: object
```

<a id="schema-ratedto"></a>
### `RateDto`

```yaml
description: Represents hourly rate object.
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    type: integer
  currency:
    description: Represents a currency.
    type: string
type: object
```

<a id="schema-ratedtov1"></a>
### `RateDtoV1`

```yaml
additionalProperties: false
description: Represents an hourly or cost rate object.
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    type: integer
  currency:
    description: Represents a currency.
    type: string
type: object
```

<a id="schema-raterequest"></a>
### `RateRequest`

```yaml
additionalProperties: false
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    minimum: 0
    type: integer
  since:
    description: Represents a date and time in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
required:
- amount
type: object
```

<a id="schema-rateupdaterequest"></a>
### `RateUpdateRequest`

```yaml
example:
  amount: 20000
  since: '2020-01-01T00:00:00Z'
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    minimum: 0
    type: integer
  since:
    description: Represents a date and time in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
required:
- amount
type: object
```

<a id="schema-recurringassignmentdto"></a>
### `RecurringAssignmentDto`

```yaml
additionalProperties: false
description: Represents recurring assignment object.
properties:
  repeat:
    default: false
    description: Indicates whether assignment is recurring or not.
    type: boolean
  seriesId:
    description: Represents series identifier.
    type: string
  weeks:
    description: Represents number of weeks for this assignment.
    format: int32
    type: integer
type: object
```

<a id="schema-recurringassignmentrequestv1"></a>
### `RecurringAssignmentRequestV1`

```yaml
additionalProperties: false
description: Recurring assignment settings.
properties:
  repeat:
    default: false
    description: Indicates whether assignment is recurring or not.
    type: boolean
  weeks:
    description: Indicates number of weeks for assignment.
    format: int32
    maximum: 99
    minimum: 1
    type: integer
required:
- weeks
type: object
```

<a id="schema-reporttagdto"></a>
### `ReportTagDto`

```yaml
additionalProperties: true
properties:
  id:
    description: Tag identifier.
    type: string
  name:
    description: Tag name.
    type: string
type: object
```

<a id="schema-reporttimeintervaldto"></a>
### `ReportTimeIntervalDto`

```yaml
additionalProperties: true
properties:
  duration:
    description: Duration of interval.
    format: int32
    type: integer
  end:
    description: End datetime in format YYYY-MM-DDTHH:MM:SS.ssssssZ.
    type: string
  start:
    description: Start datetime in format YYYY-MM-DDTHH:MM:SS.ssssssZ.
    type: string
type: object
```

<a id="schema-requeststatustype"></a>
### `RequestStatusType`

```yaml
enum:
- PENDING
- APPROVED
- REJECTED
- ALL
type: string
```

<a id="schema-roleassignmentdtov1"></a>
### `RoleAssignmentDtoV1`

```yaml
properties:
  role:
    description: Represents a valid role.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-rounddto"></a>
### `RoundDto`

```yaml
additionalProperties: true
description: Represents a time rounding object.
properties:
  minutes:
    type: string
  round:
    type: string
type: object
```

<a id="schema-schedulingassignment"></a>
### `SchedulingAssignment`

```yaml
additionalProperties: false
description: Represents a scheduled assignment.
properties:
  billable:
    default: false
    description: Indicates whether assignment is billable or not.
    type: boolean
  excludeDays:
    description: Represents a list of excluded days objects.
    items:
      $ref: '#/components/schemas/SchedulingExcludeDay'
    type: array
    uniqueItems: true
  hoursPerDay:
    description: Represents assignment total hours per day.
    format: double
    type: number
  id:
    description: Represents assignment identifier across the system.
    type: string
  includeNonWorkingDays:
    default: false
    description: Indicates whether assignment should include non-working days or not.
    type: boolean
  note:
    description: Represents assignment note.
    type: string
  period:
    $ref: '#/components/schemas/SchedulingDateRangeDto'
  projectId:
    description: Represents project identifier across the system.
    type: string
  published:
    default: false
    description: Indicates whether assignment is published or not.
    type: boolean
  recurring:
    $ref: '#/components/schemas/RecurringAssignmentDto'
  startTime:
    description: Represents start time in hh:mm:ss format.
    example: '10:00:00'
    type: string
  taskId:
    description: Represents task identifier across the system.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-schedulingdaterangedto"></a>
### `SchedulingDateRangeDto`

```yaml
additionalProperties: false
description: Represents date range object.
properties:
  end:
    format: date-time
    type: string
  start:
    format: date-time
    type: string
type: object
```

<a id="schema-schedulingexcludeday"></a>
### `SchedulingExcludeDay`

```yaml
additionalProperties: false
description: Represents a scheduling excluded day.
properties:
  date:
    description: Represents a datetime in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  type:
    $ref: '#/components/schemas/SchedulingExcludeDayType'
type: object
```

<a id="schema-schedulingexcludedaytype"></a>
### `SchedulingExcludeDayType`

```yaml
enum:
- WEEKEND
- HOLIDAY
- TIME_OFF
type: string
```

<a id="schema-schedulingviewtype"></a>
### `SchedulingViewType`

```yaml
enum:
- PROJECTS
- TEAM
- ALL
type: string
```

<a id="schema-seriesupdateoption"></a>
### `SeriesUpdateOption`

```yaml
enum:
- THIS_ONE
- THIS_AND_FOLLOWING
- ALL
type: string
```

<a id="schema-sharedattendancefilter"></a>
### `SharedAttendanceFilter`

```yaml
description: 'VERIFIED: only `attendanceFilter` accepted on attendance endpoint.'
properties:
  page:
    default: 1
    type: integer
  pageSize:
    default: 50
    type: integer
  users:
    properties:
      contains:
        enum:
        - CONTAINS
        - DOES_NOT_CONTAIN
        - CONTAINS_ONLY
        type: string
      ids:
        items:
          type: string
        type: array
      status:
        enum:
        - ALL
        - ACTIVE
        - INACTIVE
        type: string
    type: object
type: object
```

<a id="schema-shareddetailedfilter"></a>
### `SharedDetailedFilter`

```yaml
description: 'VERIFIED: only `detailedFilter` accepted on detailed endpoint.'
properties:
  auditFilter:
    additionalProperties: true
    type: object
  options:
    additionalProperties: true
    type: object
  page:
    default: 1
    type: integer
  pageSize:
    default: 50
    type: integer
  sortColumn:
    type: string
  sortOrder:
    enum:
    - ASCENDING
    - DESCENDING
    type: string
type: object
```

<a id="schema-sharedreport"></a>
### `SharedReport`

```yaml
properties:
  filter:
    $ref: '#/components/schemas/SharedReportFilter'
  fixedDate:
    nullable: true
    type: boolean
  id:
    type: string
  isPublic:
    type: boolean
  link:
    nullable: true
    type: string
  name:
    type: string
  reportAuthor:
    nullable: true
    type: string
  type:
    $ref: '#/components/schemas/SharedReportCreate/properties/type'
  userId:
    nullable: true
    type: string
  visibleToUserGroups:
    items:
      additionalProperties: true
      type: object
    nullable: true
    type: array
  visibleToUsers:
    items:
      additionalProperties: true
      type: object
    nullable: true
    type: array
  workspaceId:
    nullable: true
    type: string
type: object
```

<a id="schema-sharedreportcreate"></a>
### `SharedReportCreate`

```yaml
description: "Body keys: `type` (NOT reportType) and `filter` (NOT filters,\nsingular). Required nested fields:\n\
  \  filter.exportType, filter.dateRangeStart, filter.dateRangeEnd.\n"
properties:
  filter:
    $ref: '#/components/schemas/SharedReportFilter'
  isPublic:
    type: boolean
  name:
    type: string
  type:
    enum:
    - SUMMARY
    - DETAILED
    - WEEKLY
    - EXPENSE_DETAILED
    - INVOICE_TIME
    - KIOSK_PIN_LIST
    - ATTENDANCE_DETAILED
    - ATTENDANCE_SUMMARY
    - ASSIGNMENT_LIST
    - ASSIGNMENT_SCHEDULE
    - APPROVAL_DETAILED
    - APPROVAL_SUMMARY
    - BALANCE_LIST
    - INVOICE_AMOUNT_LIST
    - INVOICE_DETAILED
    - TIMEOFF_DETAILED
    - TIMEOFF_HOLIDAY
    - TIMEOFF_BALANCE
    - EXPENSE_SUMMARY
    type: string
required:
- name
- type
- filter
type: object
```

<a id="schema-sharedreportdata"></a>
### `SharedReportData`

```yaml
description: 'Rendered payload of a shared report. `groupOne` and `donutChart` rows

  follow the saved report''s grouping, so their properties vary; the keys

  listed here are the ones observed for a SUMMARY report grouped by

  project.

  '
properties:
  donutChart:
    items:
      additionalProperties: true
      type: object
    type: array
  filters:
    additionalProperties: true
    description: 'The saved shared-report configuration echoed back. Carries every

      `SharedReport` field plus the viewer presentation context

      (`workspace`, `subscriptionPlan`, `isAdminOrOwner`, `timezone`,

      `dateFormat`, `timeFormat`, `weekStart`, `originalLang`, `notes`).

      '
    type: object
  groupOne:
    items:
      $ref: '#/components/schemas/SharedReportGroupRow'
    type: array
  groupTotals:
    properties:
      groupOneTotalCount:
        type: integer
    type: object
  totals:
    items:
      $ref: '#/components/schemas/SharedReportTotals'
    type: array
type: object
```

<a id="schema-sharedreportfilter"></a>
### `SharedReportFilter`

```yaml
properties:
  attendanceFilter:
    $ref: '#/components/schemas/SharedAttendanceFilter'
  dateRangeEnd:
    format: date-time
    type: string
  dateRangeStart:
    format: date-time
    type: string
  detailedFilter:
    $ref: '#/components/schemas/SharedDetailedFilter'
  exportType:
    enum:
    - JSON_V1
    - JSON
    - CSV
    - XLSX
    - PDF
    type: string
  summaryFilter:
    $ref: '#/components/schemas/SharedSummaryFilter'
  weeklyFilter:
    $ref: '#/components/schemas/SharedWeeklyFilter'
required:
- exportType
- dateRangeStart
- dateRangeEnd
type: object
```

<a id="schema-sharedreportgrouprow"></a>
### `SharedReportGroupRow`

```yaml
additionalProperties: true
properties:
  _id:
    type: string
  amount:
    type: number
  amounts:
    items:
      additionalProperties: true
      type: object
    type: array
  clientName:
    nullable: true
    type: string
  color:
    nullable: true
    type: string
  currency:
    type: string
  duration:
    description: Seconds.
    type: integer
  name:
    type: string
  nameLowerCase:
    type: string
  workspaceCurrencyCode:
    type: string
type: object
```

<a id="schema-sharedreportlistenvelope"></a>
### `SharedReportListEnvelope`

```yaml
properties:
  count:
    type: integer
  reports:
    items:
      $ref: '#/components/schemas/SharedReport'
    type: array
type: object
```

<a id="schema-sharedreporttotals"></a>
### `SharedReportTotals`

```yaml
additionalProperties: true
properties:
  _id:
    type: string
  amounts:
    items:
      additionalProperties: true
      type: object
    type: array
  entriesCount:
    type: integer
  numOfCurrencies:
    type: integer
  totalAmount:
    type: number
  totalAmountByCurrency:
    items:
      additionalProperties: true
      type: object
    type: array
  totalBillableTime:
    description: Seconds.
    type: integer
  totalTime:
    description: Seconds.
    type: integer
type: object
```

<a id="schema-sharedsummaryfilter"></a>
### `SharedSummaryFilter`

```yaml
description: 'VERIFIED: only `summaryFilter` is accepted on the summary

  endpoint (NOT `detailedFilter`/`weeklyFilter`/`attendanceFilter`).

  '
properties:
  groups:
    items:
      enum:
      - CLIENT
      - PROJECT
      - TASK
      - DATE
      - WEEK
      - MONTH
      - TIMEENTRY
      - USER
      - TAG
      type: string
    maxItems: 3
    type: array
  sortColumn:
    type: string
required:
- groups
type: object
```

<a id="schema-sharedweeklyfilter"></a>
### `SharedWeeklyFilter`

```yaml
description: 'VERIFIED: only `weeklyFilter` accepted on weekly endpoint.

  Date range MUST be exactly 7 days or upstream returns

  `{code:501, message:"Please select date range of exactly 7 days for weekly report"}`.

  '
properties:
  group:
    enum:
    - PROJECT
    - USER
    type: string
  subgroup:
    enum:
    - TIME
    type: string
required:
- group
- subgroup
type: object
```

<a id="schema-sortorder"></a>
### `SortOrder`

```yaml
enum:
- ASCENDING
- DESCENDING
type: string
```

<a id="schema-statusfilter"></a>
### `StatusFilter`

```yaml
enum:
- PUBLISHED
- UNPUBLISHED
- ALL
type: string
```

<a id="schema-submitapprovalrequestrequest"></a>
### `SubmitApprovalRequestRequest`

```yaml
properties:
  period:
    $ref: '#/components/schemas/ApprovalPeriod'
  periodStart:
    description: Approval period start date in yyyy-MM-ddThh:mm:ssZ format.
    example: '2020-01-01T00:00:00.000Z'
    minLength: 1
    type: string
required:
- period
- periodStart
type: object
```

<a id="schema-summaryfilter"></a>
### `SummaryFilter`

```yaml
additionalProperties: false
description: Summary report filter. Valid only on /reports/summary. At most three groups are allowed.
properties:
  groups:
    description: Summary report grouping levels. Maximum 3 groups.
    items:
      $ref: '#/components/schemas/SummaryGroup'
    maxItems: 3
    minItems: 1
    type: array
    uniqueItems: true
  sortColumn:
    description: Column used for sorting summary report rows.
    enum:
    - GROUP
    - DURATION
    - AMOUNT
    - EARNED
    - COST
    - PROFIT
    type: string
  summaryChartType:
    description: Summary chart type.
    enum:
    - BILLABILITY
    - PROJECT
    type: string
required:
- groups
type: object
x-clockify-max-groups: 3
x-clockify-report-filter: summary
```

<a id="schema-summarygroup"></a>
### `SummaryGroup`

```yaml
description: 'Allowed summary grouping key.

  Live reports also accept TAG grouping.'
enum:
- CLIENT
- PROJECT
- USER
- WEEK
- DATE
- MONTH
- TIMEENTRY
- TASK
- TAG
type: string
```

<a id="schema-summaryreportrequest"></a>
### `SummaryReportRequest`

```yaml
additionalProperties: false
description: Request payload for generating summary reports. Only summaryFilter is accepted as the report-specific
  filter.
properties:
  amountShown:
    description: If provided, returns reports with the provided amount shown.
    enum:
    - EARNED
    - COST
    - PROFIT
    - HIDE_AMOUNT
    - EXPORT
    type: string
  amounts:
    description: Amount columns to include.
    items:
      $ref: '#/components/schemas/AmountType'
    type: array
  approvalState:
    description: If provided, returns reports with the provided approval state.
    enum:
    - APPROVED
    - UNAPPROVED
    - ALL
    type: string
  archived:
    description: Indicates whether the report is archived.
    type: boolean
  billable:
    description: Indicates whether the report is billable.
    type: boolean
  clients:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  currency:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  customFields:
    description: Time entry custom field filters.
    items:
      $ref: '#/components/schemas/CustomFieldFilter'
    type: array
  dateFormat:
    description: Provide date in format YYYY-MM-DD.
    example: '2018-11-01'
    type: string
  dateRangeEnd:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. Interpreted using the user's timezone or the
      provided timeZone.
    example: '2018-11-30T23:59:59.999'
    minLength: 1
    type: string
  dateRangeStart:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. Interpreted using the user's timezone or the
      provided timeZone.
    example: '2018-11-01T00:00:00'
    minLength: 1
    type: string
  dateRangeType:
    description: Date range preset.
    enum:
    - ABSOLUTE
    - TODAY
    - YESTERDAY
    - THIS_WEEK
    - LAST_WEEK
    - PAST_TWO_WEEKS
    - THIS_MONTH
    - LAST_MONTH
    - THIS_YEAR
    - LAST_YEAR
    type: string
  description:
    description: Search term for filtering report entries by description.
    type: string
  exportType:
    description: Export format requested for the report.
    enum:
    - JSON
    - JSON_V1
    - PDF
    - CSV
    - XLSX
    - ZIP
    type: string
  invoicingState:
    description: If provided, returns reports with the provided invoicing state.
    enum:
    - INVOICED
    - UNINVOICED
    - ALL
    type: string
  projects:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  rounding:
    description: Indicates whether report filter rounding is enabled.
    type: boolean
  sortOrder:
    description: Sort order.
    enum:
    - ASCENDING
    - DESCENDING
    type: string
  summaryFilter:
    $ref: '#/components/schemas/SummaryFilter'
  tags:
    $ref: '#/components/schemas/ContainsTagFilter'
  tasks:
    $ref: '#/components/schemas/ContainsTaskFilter'
  timeFormat:
    description: Provide time in format THH:MM:SS.ssssss.
    example: T00:00:00
    type: string
  timeZone:
    description: Timezone used to interpret dates and times.
    example: Europe/Belgrade
    type: string
  userCustomFields:
    description: User custom field filters.
    items:
      $ref: '#/components/schemas/CustomFieldFilter'
    type: array
  userGroups:
    $ref: '#/components/schemas/ContainsUsersFilter'
  userLocale:
    description: Locale used for report formatting.
    example: en
    type: string
  users:
    $ref: '#/components/schemas/ContainsUsersFilter'
  weekStart:
    description: Configured week start day.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  withoutDescription:
    description: If true, report includes only entries with empty description.
    type: boolean
  zoomLevel:
    description: Report zoom level.
    enum:
    - WEEK
    - MONTH
    - YEAR
    type: string
required:
- dateRangeStart
- dateRangeEnd
- summaryFilter
type: object
```

<a id="schema-summaryreportresponse"></a>
### `SummaryReportResponse`

```yaml
additionalProperties: true
description: Summary report response.
properties:
  groupOne:
    description: List of top-level groups.
    items:
      $ref: '#/components/schemas/GroupOneDto'
    type: array
  totals:
    description: List of totals.
    items:
      $ref: '#/components/schemas/TimeEntryReportTotals'
    type: array
  donutChart:
    description: Live summary reports return donutChart instead of the stale chart key.
    items:
      type: object
      additionalProperties: true
    type: array
  groupTotals:
    description: Live summary report group total counters.
    additionalProperties: true
    properties:
      groupOneTotalCount:
        type: integer
      groupTwoTotalCount:
        type: integer
    type: object
type: object
```

<a id="schema-summaryreportsettingsdtov1"></a>
### `SummaryReportSettingsDtoV1`

```yaml
description: Represents a summary report settings object.
properties:
  group:
    type: string
  subgroup:
    type: string
required:
- group
- subgroup
type: object
```

<a id="schema-tag"></a>
### `Tag`

```yaml
properties:
  archived:
    type: boolean
  id:
    type: string
  name:
    type: string
  workspaceId:
    type: string
type: object
required:
- id
- name
- workspaceId
- archived
```

<a id="schema-tagcreate"></a>
### `TagCreate`

```yaml
properties:
  name:
    type: string
required:
- name
type: object
```

<a id="schema-tagdto"></a>
### `TagDto`

```yaml
description: Represents a tag object.
properties:
  archived:
    default: false
    description: Indicates whether tag is archived or not.
    type: boolean
  id:
    description: Represents tag identifier across the system.
    type: string
  name:
    description: Represents tag name.
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-task"></a>
### `Task`

```yaml
description: Represents a Clockify task on a project.
example:
  assigneeId: string
  assigneeIds:
  - 45b687e29ae1f428e7ebe123
  - 67s687e29ae1f428e7ebe678
  billable: false
  budgetEstimate: 10000
  costRate:
    amount: 20000
    currency: USD
  duration: PT1H30M
  estimate: PT1H30M
  hourlyRate:
    amount: 20000
    currency: USD
  id: 57a687e29ae1f428e7ebe107
  name: Bugfixing
  projectId: 25b687e29ae1f428e7ebe123
  status: DONE
  userGroupIds:
  - 67b687e29ae1f428e7ebe123
  - 12s687e29ae1f428e7ebe678
properties:
  active:
    description: Indicates whether the task is active.
    type: boolean
  assigneeId:
    deprecated: true
    description: Deprecated task assignee identifier.
    type: string
  assigneeIds:
    description: Represents list of assignee ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
  billable:
    default: false
    description: Indicates whether a task is billable or not.
    type: boolean
  budgetEstimate:
    description: Represents a task budget estimate as long.
    format: int64
    type: integer
  costRate:
    $ref: '#/components/schemas/TasksRateDtoV1'
  duration:
    description: Represents a task duration.
    type: string
  estimate:
    description: Represents a task duration estimate.
    type: string
  hourlyRate:
    $ref: '#/components/schemas/TasksRateDtoV1'
  id:
    description: Represents task identifier across the system.
    type: string
  name:
    description: Represents task name.
    type: string
  projectId:
    description: Represents project identifier across the system.
    type: string
  status:
    $ref: '#/components/schemas/TaskStatus'
  userGroupIds:
    description: Represents list of user group ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
type: object
required:
- id
- name
- projectId
- status
- billable
```

<a id="schema-taskcreaterequest"></a>
### `TaskCreateRequest`

```yaml
example:
  assigneeId: '##default'
  assigneeIds:
  - 45b687e29ae1f428e7ebe123
  - 67s687e29ae1f428e7ebe678
  billable: false
  budgetEstimate: 10000
  estimate: PT1H30M
  id: 57a687e29ae1f428e7ebe107
  name: Bugfixing
  status: DONE
  userGroupIds:
  - 67b687e29ae1f428e7ebe123
  - 12s687e29ae1f428e7ebe678
properties:
  assigneeId:
    default: '##default'
    deprecated: true
    description: Deprecated task assignee identifier.
    type: string
  assigneeIds:
    description: Represents list of assignee ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
  billable:
    default: false
    description: Indicates whether a task is billable or not.
    type: boolean
  budgetEstimate:
    description: Represents a task budget estimate as long.
    format: int64
    minimum: 0
    type: integer
  estimate:
    description: Represents a task duration estimate in ISO-8601 format.
    type: string
  id:
    description: Represents task identifier across the system.
    type: string
  name:
    description: Represents task name.
    maxLength: 1000
    minLength: 1
    type: string
  status:
    $ref: '#/components/schemas/TaskStatus'
  userGroupIds:
    description: Represents list of user group ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
required:
- name
type: object
```

<a id="schema-taskinfodto"></a>
### `TaskInfoDto`

```yaml
description: Represents a task info object.
properties:
  id:
    description: Represents task identifier across the system.
    type: string
  name:
    description: Represents task name.
    type: string
type: object
```

<a id="schema-taskrequest"></a>
### `TaskRequest`

```yaml
additionalProperties: false
description: Represents a task request object used when creating a project.
properties:
  assigneeId:
    deprecated: true
    type: string
  assigneeIds:
    description: Represents list of assignee ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
  billable:
    default: false
    description: Flag to set whether task is billable or not.
    type: boolean
  budgetEstimate:
    format: int64
    minimum: 0
    type: integer
  costRate:
    $ref: '#/components/schemas/RateRequest'
  estimate:
    description: Represents a task duration estimate.
    type: string
  hourlyRate:
    $ref: '#/components/schemas/RateRequest'
  id:
    description: Represents task identifier across the system.
    type: string
  name:
    description: Represents task name.
    type: string
  projectId:
    description: Represents project identifier across the system.
    type: string
  status:
    description: Represents task status.
    enum:
    - ACTIVE
    - DONE
    - ALL
    type: string
  userGroupIds:
    description: Represents list of user group ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
required:
- name
type: object
```

<a id="schema-taskstatus"></a>
### `TaskStatus`

```yaml
description: Represents task status.
enum:
- ACTIVE
- DONE
- ALL
type: string
```

<a id="schema-taskupdaterequest"></a>
### `TaskUpdateRequest`

```yaml
example:
  assigneeId: '##default'
  assigneeIds:
  - 45b687e29ae1f428e7ebe123
  - 67s687e29ae1f428e7ebe678
  billable: false
  budgetEstimate: 10000
  estimate: PT1H30M
  name: Bugfixing
  status: DONE
  userGroupIds:
  - 67b687e29ae1f428e7ebe123
  - 12s687e29ae1f428e7ebe678
properties:
  assigneeId:
    default: '##default'
    deprecated: true
    description: Deprecated task assignee identifier.
    type: string
  assigneeIds:
    description: Represents list of assignee ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
  billable:
    default: false
    description: Indicates whether a task is billable or not.
    type: boolean
  budgetEstimate:
    description: Represents a task budget estimate as integer.
    format: int64
    minimum: 0
    type: integer
  estimate:
    description: Represents a task duration estimate.
    type: string
  name:
    description: Represents task name.
    maxLength: 1000
    minLength: 1
    type: string
  status:
    $ref: '#/components/schemas/TaskStatus'
  userGroupIds:
    description: Represents list of user group ids for the task.
    items:
      type: string
    type: array
    uniqueItems: true
required:
- name
type: object
```

<a id="schema-tasksratedtov1"></a>
### `TasksRateDtoV1`

```yaml
description: Represents hourly or cost rate object.
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    type: integer
  currency:
    description: Represents a currency.
    type: string
type: object
```

<a id="schema-taxtype"></a>
### `TaxType`

```yaml
description: Represents an invoice taxation type.
enum:
- COMPOUND
- SIMPLE
- NONE
type: string
```

<a id="schema-timeentriescustomfieldvaluedto"></a>
### `TimeEntriesCustomFieldValueDto`

```yaml
properties:
  customFieldId:
    type: string
  name:
    type: string
  timeEntryId:
    type: string
  type:
    enum:
    - WORKSPACE
    - PROJECT
    - TIMEENTRY
    type: string
  value:
    nullable: true
    type: string
type: object
```

<a id="schema-timeentriestimeentry"></a>
### `TimeEntriesTimeEntry`

```yaml
properties:
  billable:
    type: boolean
  customFieldValues:
    items:
      $ref: '#/components/schemas/TimeEntriesCustomFieldValueDto'
    type: array
  description:
    type: string
  id:
    type: string
  isLocked:
    type: boolean
  kioskId:
    nullable: true
    type: string
  projectId:
    nullable: true
    type: string
  tagIds:
    items:
      type: string
    nullable: true
    type: array
  taskId:
    nullable: true
    type: string
  timeInterval:
    $ref: '#/components/schemas/TimeEntriesTimeIntervalDto'
  type:
    enum:
    - REGULAR
    - BREAK
    - HOLIDAY
    - TIME_OFF
    type: string
  userId:
    type: string
  workspaceId:
    type: string
type: object
```

<a id="schema-timeentriestimeintervaldto"></a>
### `TimeEntriesTimeIntervalDto`

```yaml
properties:
  duration:
    type: string
  end:
    format: date-time
    nullable: true
    type: string
  start:
    format: date-time
    type: string
type: object
```

<a id="schema-timeentry"></a>
### `TimeEntry`

```yaml
properties:
  approvalRequestId:
    nullable: true
    type: string
  billable:
    type: boolean
  costRate:
    $ref: '#/components/schemas/OpenapiRateDto'
    nullable: true
  customFieldValues:
    items:
      additionalProperties: true
      type: object
    type: array
  description:
    type: string
  hourlyRate:
    $ref: '#/components/schemas/OpenapiRateDto'
    nullable: true
  id:
    type: string
  isLocked:
    type: boolean
  kioskId:
    nullable: true
    type: string
  projectId:
    nullable: true
    type: string
  tagIds:
    items:
      type: string
    nullable: true
    type: array
  taskId:
    nullable: true
    type: string
  timeInterval:
    $ref: '#/components/schemas/DateTimeInterval'
  type:
    enum:
    - REGULAR
    - BREAK
    - TIMEOFF
    - HOLIDAY
    - OVERTIME
    type: string
  userId:
    type: string
  workspaceId:
    type: string
type: object
required:
- id
- description
- userId
- billable
- workspaceId
- timeInterval
- type
- isLocked
```

<a id="schema-timeentrycreate"></a>
### `TimeEntryCreate`

```yaml
properties:
  billable:
    type: boolean
  customFields:
    items:
      properties:
        customFieldId:
          type: string
        sourceType:
          enum:
          - WORKSPACE
          - PROJECT
          type: string
        value:
          description: Polymorphic — string/number/array depending on custom-field type
      type: object
    type: array
  description:
    type: string
  end:
    description: Omit to start a running timer
    format: date-time
    type: string
  projectId:
    type: string
  start:
    description: Required ISO 8601
    format: date-time
    type: string
  tagIds:
    items:
      type: string
    type: array
  taskId:
    type: string
  type:
    enum:
    - REGULAR
    - BREAK
    type: string
required:
- start
type: object
```

<a id="schema-timeentrydto"></a>
### `TimeEntryDto`

```yaml
additionalProperties: true
properties:
  approvalRequestId:
    description: Approval request identifier.
    type: string
  billable:
    description: Indicates whether the time entry is billable.
    type: boolean
  clientId:
    description: Client identifier.
    type: string
  clientName:
    description: Client name.
    type: string
  description:
    description: Time entry description.
    type: string
  get_id:
    description: Time entry identifier as shown in the source documentation.
    type: string
  id:
    description: Time entry identifier.
    type: string
  locked:
    description: Indicates whether the time entry is locked.
    type: boolean
  projectColor:
    description: Project color.
    type: string
  projectId:
    description: Project identifier.
    type: string
  projectName:
    description: Project name.
    type: string
  tags:
    description: List of tags.
    items:
      $ref: '#/components/schemas/ReportTagDto'
    type: array
  taskId:
    description: Task identifier.
    type: string
  taskName:
    description: Task name.
    type: string
  timeInterval:
    $ref: '#/components/schemas/ReportTimeIntervalDto'
  userEmail:
    description: User email.
    type: string
  userId:
    description: User identifier.
    type: string
  userName:
    description: User name.
    type: string
type: object
```

<a id="schema-timeentrydtoimplv1"></a>
### `TimeEntryDtoImplV1`

```yaml
properties:
  billable:
    default: false
    description: Indicates whether a time entry is billable.
    type: boolean
  customFieldValues:
    description: Represents a list of custom field value objects.
    items:
      $ref: '#/components/schemas/CustomFieldValueDtoV1'
    type: array
  description:
    description: Represents time entry description.
    example: This is a sample time entry description.
    type: string
  id:
    description: Represents time entry identifier across the system.
    example: 64c777ddd3fcab07cfbb210c
    type: string
  isLocked:
    default: false
    description: Represents whether time entry is locked for modification.
    type: boolean
  kioskId:
    description: Represents kiosk identifier across the system.
    example: 94c777ddd3fcab07cfbb210d
    type: string
  projectId:
    description: Represents project identifier across the system.
    example: 25b687e29ae1f428e7ebe123
    type: string
  tagIds:
    description: Represents a list of tag identifiers across the system.
    example:
    - 321r77ddd3fcab07cfbb567y
    - 44x777ddd3fcab07cfbb88f
    items:
      description: Represents a list of tag identifiers across the system.
      example: '["321r77ddd3fcab07cfbb567y","44x777ddd3fcab07cfbb88f"]'
      type: string
    type: array
  taskId:
    description: Represents task identifier across the system.
    example: 54m377ddd3fcab07cfbb432w
    type: string
  timeInterval:
    $ref: '#/components/schemas/TimeIntervalDtoV1'
  type:
    description: Represents a time entry type enum.
    enum:
    - REGULAR
    - BREAK
    - HOLIDAY
    - TIME_OFF
    example: BREAK
    type: string
  userId:
    description: Represents user identifier across the system.
    example: 5a0ab5acb07987125438b60f
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    example: 64a687e29ae1f428e7ebe303
    type: string
type: object
```

<a id="schema-timeentryfieldsfordetailedgroup"></a>
### `TimeEntryFieldsForDetailedGroup`

```yaml
enum:
- PROJECT
- TASK
- TAGS
- DESCRIPTION
- DATE
- USER
type: string
```

<a id="schema-timeentrygrouptype"></a>
### `TimeEntryGroupType`

```yaml
enum:
- SINGLE_ITEM
- GROUPED
- DETAILED
type: string
```

<a id="schema-timeentryinfodto"></a>
### `TimeEntryInfoDto`

```yaml
description: Represents a time entry info data transfer object.
properties:
  approvalRequestId:
    description: Represents approval identifier across the system.
    type: string
  billable:
    default: false
    description: Indicates whether time entry is billable or not.
    type: boolean
  costRate:
    $ref: '#/components/schemas/RateDto'
  customFieldValues:
    items:
      $ref: '#/components/schemas/CustomFieldValueDto'
    type: array
  description:
    description: Represents a time entry description.
    type: string
  hourlyRate:
    $ref: '#/components/schemas/RateDto'
  id:
    description: Represents time entry identifier across the system.
    type: string
  isLocked:
    default: false
    description: Indicates whether time entry is locked or not.
    type: boolean
  project:
    $ref: '#/components/schemas/ProjectInfoDto'
  tags:
    items:
      $ref: '#/components/schemas/TagDto'
    type: array
  task:
    $ref: '#/components/schemas/TaskInfoDto'
  timeInterval:
    $ref: '#/components/schemas/TimeIntervalDto'
  type:
    $ref: '#/components/schemas/TimeEntryType'
type: object
```

<a id="schema-timeentryprimarygroupby"></a>
### `TimeEntryPrimaryGroupBy`

```yaml
enum:
- USER
- PROJECT
- DATE
type: string
```

<a id="schema-timeentryreporttotals"></a>
### `TimeEntryReportTotals`

```yaml
additionalProperties: true
properties:
  amounts:
    description: List of amounts.
    items:
      $ref: '#/components/schemas/AmountDto'
    type: array
  entriesCount:
    description: Entries count.
    format: int32
    type: integer
  id:
    description: Time entry report identifier.
    type: string
  totalBillableTime:
    description: Total billable time.
    type: number
  totalTime:
    description: Total time.
    type: number
type: object
```

<a id="schema-timeentrysecondarygroupby"></a>
### `TimeEntrySecondaryGroupBy`

```yaml
enum:
- PROJECT
- USER
- TASK
- DATE
- DESCRIPTION
- NONE
type: string
```

<a id="schema-timeentrytype"></a>
### `TimeEntryType`

```yaml
enum:
- REGULAR
- BREAK
- HOLIDAY
- TIME_OFF
type: string
```

<a id="schema-timeentryupdate"></a>
### `TimeEntryUpdate`

```yaml
allOf:
- $ref: '#/components/schemas/TimeEntryCreate'
```

<a id="schema-timeentrywithratesdtov1"></a>
### `TimeEntryWithRatesDtoV1`

```yaml
properties:
  billable:
    default: false
    description: Indicates whether a time entry is billable.
    type: boolean
  costRate:
    $ref: '#/components/schemas/OpenapiRateDto2'
  customFieldValues:
    description: Represents a list of custom field value objects.
    items:
      $ref: '#/components/schemas/CustomFieldValueDtoV1'
    type: array
  description:
    description: Represents time entry description.
    example: This is a sample time entry description.
    type: string
  hourlyRate:
    $ref: '#/components/schemas/OpenapiRateDto2'
  id:
    description: Represents time entry identifier across the system.
    example: 64c777ddd3fcab07cfbb210c
    type: string
  isLocked:
    default: false
    description: Represents whether time entry is locked for modification.
    type: boolean
  kioskId:
    description: Represents kiosk identifier across the system.
    example: 94c777ddd3fcab07cfbb210d
    type: string
  projectId:
    description: Represents project identifier across the system.
    example: 25b687e29ae1f428e7ebe123
    type: string
  tagIds:
    description: Represents a list of tag identifiers across the system.
    example:
    - 321r77ddd3fcab07cfbb567y
    - 44x777ddd3fcab07cfbb88f
    items:
      description: Represents a list of tag identifiers across the system.
      example: '["321r77ddd3fcab07cfbb567y","44x777ddd3fcab07cfbb88f"]'
      type: string
    type: array
  taskId:
    description: Represents task identifier across the system.
    example: 54m377ddd3fcab07cfbb432w
    type: string
  timeInterval:
    $ref: '#/components/schemas/TimeIntervalDtoV1'
  type:
    description: Represents a time entry type enum.
    enum:
    - REGULAR
    - BREAK
    - HOLIDAY
    - TIME_OFF
    example: BREAK
    type: string
  userId:
    description: Represents user identifier across the system.
    example: 5a0ab5acb07987125438b60f
    type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    example: 64a687e29ae1f428e7ebe303
    type: string
type: object
```

<a id="schema-timeestimatedto"></a>
### `TimeEstimateDto`

```yaml
additionalProperties: false
description: Represents a project time estimate object.
properties:
  active:
    type: boolean
  estimate:
    description: Represents project duration in milliseconds or ISO-8601 duration.
    type: string
  includeNonBillable:
    type: boolean
  resetOption:
    enum:
    - WEEKLY
    - MONTHLY
    - YEARLY
    type: string
  type:
    enum:
    - AUTO
    - MANUAL
    type: string
type: object
```

<a id="schema-timeestimaterequest"></a>
### `TimeEstimateRequest`

```yaml
additionalProperties: false
description: Represents project time estimate request object.
properties:
  active:
    default: false
    description: Flag whether to include only active or inactive estimates.
    type: boolean
  estimate:
    description: Represents a time duration in ISO-8601 format.
    type: string
  includeNonBillable:
    default: false
    description: Flag whether to include non-billable expenses.
    type: boolean
  resetOption:
    enum:
    - WEEKLY
    - MONTHLY
    - YEARLY
    type: string
  type:
    enum:
    - AUTO
    - MANUAL
    type: string
type: object
```

<a id="schema-timeintervaldto"></a>
### `TimeIntervalDto`

```yaml
description: Represents a time interval object.
properties:
  duration:
    $ref: '#/components/schemas/DurationString'
  end:
    format: date-time
    type: string
  offsetEnd:
    format: int32
    type: integer
  offsetStart:
    format: int32
    type: integer
  start:
    format: date-time
    type: string
  timeZone:
    type: string
  zonedEnd:
    format: date-time
    type: string
  zonedStart:
    format: date-time
    type: string
type: object
```

<a id="schema-timeintervaldtov1"></a>
### `TimeIntervalDtoV1`

```yaml
description: Represents a time interval object.
properties:
  duration:
    description: Represents a time duration.
    example: '8000'
    type: string
  end:
    description: Represents an end date in yyyy-MM-ddThh:mm:ssZ format.
    example: '2021-01-01T00:00:00Z'
    format: date-time
    type: string
  start:
    description: Represents a start date in yyyy-MM-ddThh:mm:ssZ format.
    example: '2020-01-01T00:00:00Z'
    format: date-time
    type: string
type: object
```

<a id="schema-timeoffrequestdto"></a>
### `TimeOffRequestDto`

```yaml
description: Represents a time off request response.
example:
  balanceDiff: 1
  createdAt: '2022-08-26T08:32:01.640708Z'
  id: 5b715612b079875110791111
  note: Time Off Request Note
  policyId: 5b715612b079875110792333
  status:
    statusType: PENDING
  timeOffPeriod:
    halfDay: false
    period:
      end: '2022-08-26T17:00:00Z'
      start: '2022-08-26T08:00:00Z'
  userId: 5b715612b079875110794444
  workspaceId: 5b715612b079875110792222
properties:
  balanceDiff:
    description: Represents the balance difference.
    format: double
    type: number
  createdAt:
    description: Represents the date when time off request is created. Date is in format YYYY-MM-DDTHH:MM:SS.ssssssZ
    format: date-time
    type: string
  id:
    description: Represents time off requester identifier across the system.
    type: string
    x-clockify-default: '##default'
  note:
    description: Represents the note of the time off request.
    type: string
    x-clockify-default: '##default'
  policyId:
    description: Represents policy identifier across the system.
    type: string
    x-clockify-default: '##default'
  status:
    $ref: '#/components/schemas/TimeOffRequestStatus'
  timeOffPeriod:
    $ref: '#/components/schemas/TimeOffRequestPeriodDto'
  userId:
    description: Represents user identifier across the system.
    type: string
    x-clockify-default: '##default'
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
    x-clockify-default: '##default'
type: object
```

<a id="schema-timeoffrequestfullv1dto"></a>
### `TimeOffRequestFullV1Dto`

```yaml
description: Represents a full time off request response.
example:
  balance: 10
  balanceDiff: 1
  createdAt: '2022-08-26T08:32:01.640708Z'
  id: 5b715612b079875110791111
  note: Time Off Request Note
  policyId: 5b715612b079875110792333
  policyName: Days
  requesterUserId: 5b715612b079875110794444
  requesterUserName: John Doe
  status:
    statusType: PENDING
  timeOffPeriod:
    halfDay: false
    halfDayPeriod: NOT_DEFINED
    period:
      end: '2022-08-26T17:00:00Z'
      start: '2022-08-26T08:00:00Z'
  timeUnit: DAYS
  userEmail: <EMAIL>
  userId: 5b715612b079875110794444
  userName: John Doe
  userTimeZone: UTC
  workspaceId: 5b715612b079875110792222
properties:
  balance:
    description: Represents the time off balance.
    format: double
    type: number
  balanceDiff:
    description: Represents the balance difference.
    format: double
    type: number
  createdAt:
    description: Represents the date when time off request is created. It is in format YYYY-MM-DDTHH:MM:SS.ssssssZ
    format: date-time
    type: string
  id:
    description: Represents time off requester identifier across the system.
    type: string
    x-clockify-default: '##default'
  note:
    description: Represents the note of the time off request.
    type: string
    x-clockify-default: '##default'
  policyId:
    description: Represents policy identifier across the system.
    type: string
    x-clockify-default: '##default'
  policyName:
    description: Represents the policy name of the time off request.
    type: string
    x-clockify-default: '##default'
  requesterUserId:
    description: Represents requester user's id.
    type: string
    x-clockify-default: '##default'
  requesterUserName:
    description: Represents requester user's username.
    type: string
    x-clockify-default: '##default'
  status:
    $ref: '#/components/schemas/TimeOffRequestStatus'
  timeOffPeriod:
    $ref: '#/components/schemas/TimeOffRequestPeriodDto'
  timeUnit:
    $ref: '#/components/schemas/TimeUnit'
  userEmail:
    description: Represents user's email
    type: string
    x-clockify-default: '##default'
  userId:
    description: Represents user identifier across the system.
    type: string
    x-clockify-default: '##default'
  userName:
    description: Represents user's username.
    type: string
    x-clockify-default: '##default'
  userTimeZone:
    description: Represents user's time zone
    type: string
    x-clockify-default: '##default'
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
    x-clockify-default: '##default'
type: object
```

<a id="schema-timeoffrequestperioddto"></a>
### `TimeOffRequestPeriodDto`

```yaml
description: Represents the period of the time off request.
properties:
  halfDay:
    type: boolean
  halfDayHours:
    $ref: '#/components/schemas/Period'
  halfDayPeriod:
    $ref: '#/components/schemas/HalfDayPeriod'
  period:
    $ref: '#/components/schemas/Period'
type: object
```

<a id="schema-timeoffrequestperiodv1request"></a>
### `TimeOffRequestPeriodV1Request`

```yaml
description: Provide the period you would like to use for creating the time off request. If timeZone isn't set,
  should be aligned with time zone for user in settings. Can be shifted from user time zone with explicit setting
  of timeZone.
properties:
  halfDayPeriod:
    allOf:
    - $ref: '#/components/schemas/HalfDayPeriod'
    x-clockify-default: '##default'
  isHalfDay:
    default: false
    description: Indicates whether time off is half day.
    type: boolean
  period:
    $ref: '#/components/schemas/PeriodV1Request'
  timeOffHalfDayPeriod:
    $ref: '#/components/schemas/HalfDayPeriod'
required:
- period
type: object
```

<a id="schema-timeoffrequestsearchrequest"></a>
### `TimeOffRequestSearchRequest`

```yaml
description: Filters used to return time off requests on a workspace.
example:
  end: '2022-08-26T23:55:06.281873Z'
  page: 1
  pageSize: 50
  start: '2022-08-26T08:00:06.281873Z'
  statuses:
  - APPROVED
  - PENDING
  userGroups:
  - 5b715612b079875110791342
  - 5b715612b079875110791324
  - 5b715612b079875110793142
  users:
  - 5b715612b079875110791432
  - b715612b079875110791234
properties:
  end:
    description: Return time off requests created before the specified time in requester's time zone. Provide end
      in format YYYY-MM-DDTHH:MM:SS.ssssssZ
    format: date-time
    type: string
  page:
    default: 1
    description: Page number.
    format: int32
    maximum: 1000
    type: integer
  pageSize:
    default: 50
    description: Page size.
    format: int32
    maximum: 200
    minimum: 1
    type: integer
  start:
    description: Return time off requests created after the specified time in requester's time zone. Provide start
      in format YYYY-MM-DDTHH:MM:SS.ssssssZ
    format: date-time
    type: string
  statuses:
    description: Filters time off requests by status.
    items:
      $ref: '#/components/schemas/RequestStatusType'
    type: array
    uniqueItems: true
    x-clockify-default: '##default'
  userGroups:
    description: Provide the user group ids of time off requests.
    items:
      type: string
    type: array
    uniqueItems: true
    x-clockify-default: '##default'
  users:
    description: Provide the user ids of time off requests. If empty, will return time off requests of all users
      (with a maximum of 5000 users).
    items:
      type: string
    type: array
    uniqueItems: true
    x-clockify-default: '##default'
type: object
```

<a id="schema-timeoffrequeststatus"></a>
### `TimeOffRequestStatus`

```yaml
description: Represents the status of the time off request.
properties:
  changedAt:
    format: date-time
    type: string
  changedByUserId:
    type: string
  changedByUserName:
    type: string
  changedForUserName:
    type: string
  note:
    type: string
  statusType:
    $ref: '#/components/schemas/RequestStatusType'
type: object
```

<a id="schema-timeoffrequestsresponse"></a>
### `TimeOffRequestsResponse`

```yaml
example:
  count: 1
  requests: []
properties:
  count:
    description: Total count of time off requests.
    format: int32
    type: integer
  requests:
    items:
      $ref: '#/components/schemas/TimeOffRequestFullV1Dto'
    type: array
    x-clockify-default: '##default'
type: object
```

<a id="schema-timerangerequestdtov1"></a>
### `TimeRangeRequestDtoV1`

```yaml
description: Represents a time range object for invoice issue dates.
properties:
  issue-date-end:
    default: '##default'
    description: Represents a date in yyyy-MM-dd format.
    example: '2024-12-31'
    type: string
  issue-date-start:
    default: '##default'
    description: Represents a date in yyyy-MM-dd format.
    example: '2024-01-01'
    type: string
type: object
```

<a id="schema-timeunit"></a>
### `TimeUnit`

```yaml
description: Represents the time unit of the time off request.
enum:
- DAYS
- HOURS
type: string
```

<a id="schema-timeviewmode"></a>
### `TimeViewMode`

```yaml
enum:
- TIME_SENSITIVE_VIEW
- AGGREGATED_TIME_VIEW
type: string
```

<a id="schema-totalsperdaydto"></a>
### `TotalsPerDayDto`

```yaml
additionalProperties: false
description: Represents total hours per day object.
properties:
  date:
    format: date-time
    type: string
  totalHours:
    format: double
    type: number
type: object
```

<a id="schema-updateapprovalrequestrequest"></a>
### `UpdateApprovalRequestRequest`

```yaml
properties:
  note:
    description: Additional notes for the approval request.
    type: string
  state:
    $ref: '#/components/schemas/ApprovalRequestState'
required:
- state
type: object
```

<a id="schema-updatebalanceassignmentv1request"></a>
### `UpdateBalanceAssignmentV1Request`

```yaml
properties:
  balanceChange:
    description: Represents the change in balance of the balance assignment
    example: 12
    format: double
    maximum: 10000
    minimum: -10000
    type: number
  dateRange:
    $ref: '#/components/schemas/DateRangeV1Request'
  note:
    description: Represents note attached to updating balance.
    example: Bonus days added.
    type: string
required:
- balanceChange
type: object
```

<a id="schema-updatebalancerequest"></a>
### `UpdateBalanceRequest`

```yaml
example:
  note: Bonus days added.
  userIds:
  - 5b715448b079875110792222
  - 5b715448b079875110791111
  value: 22
properties:
  note:
    default: '##default'
    description: Represents a new balance note value.
    type: string
  userIds:
    description: Represents the list of users' identifiers whose balance is to be updated.
    items:
      type: string
    minItems: 1
    type: array
    uniqueItems: true
  value:
    description: Represents a new balance value.
    format: double
    maximum: 10000
    minimum: -10000
    type: number
required:
- note
- userIds
- value
type: object
```

<a id="schema-updatecostraterequest"></a>
### `UpdateCostRateRequest`

```yaml
additionalProperties: false
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    minimum: 0
    type: integer
  since:
    description: Represents a date and time in yyyy-MM-ddThh:mm:ssZ format.
    example: '2020-01-01T00:00:00Z'
    type: string
required:
- amount
type: object
```

<a id="schema-updatecustomfieldrequest"></a>
### `UpdateCustomFieldRequest`

```yaml
example:
  allowedValues:
  - New York
  - London
  - Manila
  - Sydney
  - Belgrade
  description: This field contains a location.
  name: location
  onlyAdminCanEdit: false
  placeholder: Location
  required: false
  status: VISIBLE
  type: DROPDOWN_MULTIPLE
  workspaceDefaultValue:
  - Manila
properties:
  allowedValues:
    description: Represents a list of custom field allowed values.
    items:
      type: string
    type: array
  description:
    description: Represents a custom field description.
    type: string
  name:
    description: Represents a custom field name.
    maxLength: 250
    minLength: 2
    type: string
  onlyAdminCanEdit:
    default: false
    description: Flag to set whether custom field is modifiable only by admin users.
    type: boolean
  placeholder:
    description: Represents a custom field placeholder value.
    type: string
  required:
    default: false
    description: Flag to set whether custom field is mandatory or not.
    type: boolean
  status:
    $ref: '#/components/schemas/CustomFieldStatus'
  type:
    $ref: '#/components/schemas/CustomFieldType'
  workspaceDefaultValue:
    $ref: '#/components/schemas/CustomFieldValue'
required:
- name
- type
type: object
```

<a id="schema-updateholidayrequest"></a>
### `UpdateHolidayRequest`

```yaml
properties:
  automaticTimeEntryCreation:
    $ref: '#/components/schemas/AutomaticTimeEntryCreationRequest'
  color:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  datePeriod:
    $ref: '#/components/schemas/DatePeriodRequest'
  everyoneIncludingNew:
    default: false
    description: Indicates whether the holiday is shown to new users.
    type: boolean
  name:
    description: Provide the name you would like to use for updating the holiday.
    minLength: 1
    type: string
  occursAnnually:
    default: false
    description: Indicates whether the holiday occurs annually.
    type: boolean
  userGroups:
    $ref: '#/components/schemas/ContainsUserGroupFilterRequest'
  users:
    $ref: '#/components/schemas/ContainsUsersFilterRequestForHoliday'
required:
- datePeriod
- name
- occursAnnually
type: object
```

<a id="schema-updateinvoicerequest"></a>
### `UpdateInvoiceRequest`

```yaml
example:
  billFrom: Business X
  clientAddress: Ground Floor, ABC Bldg., Palo Alto, California, USA 94020
  clientId: 98h687e29ae1f428e7ebe707
  companyId: 04g687e29ae1f428e7ebe123
  currency: USD
  discountPercent: 10.5
  dueDate: '2020-06-01T08:00:00Z'
  issuedDate: '2020-01-01T08:00:00Z'
  note: This is a sample note for this invoice.
  number: '202306121129'
  subject: January salary
  tax2Percent: 0
  taxPercent: 1.5
  taxType: SIMPLE
  visibleZeroFields:
  - TAX
  - TAX_2
  - DISCOUNT
properties:
  billFrom:
    default: '##default'
    description: Represents to whom the invoice should be billed from.
    type: string
  clientAddress:
    default: '##default'
    description: Represents client address.
    type: string
  clientId:
    default: '##default'
    description: Represents client identifier across the system.
    type: string
  companyId:
    default: '##default'
    description: Represents company identifier across the system.
    type: string
  currency:
    default: '##default'
    description: Represents the currency used by the invoice.
    maxLength: 100
    minLength: 1
    type: string
  discountPercent:
    description: Represents an invoice discount percent as double.
    format: double
    type: number
  dueDate:
    description: Represents an invoice due date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  issuedDate:
    description: Represents an invoice issued date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  note:
    default: '##default'
    description: Represents an invoice note.
    type: string
  number:
    default: '##default'
    description: Represents an invoice number.
    minLength: 1
    type: string
  subject:
    default: '##default'
    description: Represents an invoice subject.
    type: string
  tax2Percent:
    description: Represents an invoice tax 2 percent as double.
    format: double
    type: number
  taxPercent:
    description: Represents an invoice tax percent as double.
    format: double
    type: number
  taxType:
    $ref: '#/components/schemas/TaxType'
  visibleZeroFields:
    description: Represents one or more zero value invoice fields that will be visible.
    oneOf:
    - $ref: '#/components/schemas/VisibleZeroFieldsInvoice'
    - items:
        $ref: '#/components/schemas/VisibleZeroFieldsInvoice'
      type: array
required:
- currency
- discountPercent
- dueDate
- issuedDate
- number
- tax2Percent
- taxPercent
type: object
```

<a id="schema-updateprojectcustomfieldrequest"></a>
### `UpdateProjectCustomFieldRequest`

```yaml
example:
  defaultValue: Manila
  status: VISIBLE
properties:
  defaultValue:
    $ref: '#/components/schemas/CustomFieldValue'
  status:
    $ref: '#/components/schemas/CustomFieldStatus'
type: object
```

<a id="schema-updateprojectestimaterequest"></a>
### `UpdateProjectEstimateRequest`

```yaml
additionalProperties: false
properties:
  budgetEstimate:
    $ref: '#/components/schemas/EstimateWithOptionsRequest'
  estimateReset:
    $ref: '#/components/schemas/EstimateResetRequest'
  timeEstimate:
    $ref: '#/components/schemas/TimeEstimateRequest'
type: object
```

<a id="schema-updateprojectmembershipsrequest"></a>
### `UpdateProjectMembershipsRequest`

```yaml
additionalProperties: false
properties:
  memberships:
    description: Represents a list of users with id and rates request objects.
    items:
      $ref: '#/components/schemas/UserIdWithRatesRequest'
    type: array
  userGroups:
    $ref: '#/components/schemas/ProjectsUserGroupIdsSchema'
required:
- memberships
type: object
```

<a id="schema-updateprojectrequest"></a>
### `UpdateProjectRequest`

```yaml
additionalProperties: false
properties:
  archived:
    default: false
    description: Indicates whether project is archived or not.
    type: boolean
  billable:
    default: false
    description: Indicates whether project is billable or not.
    type: boolean
  clientId:
    description: Represents client identifier across the system.
    type: string
  color:
    description: Color value in standard RGB hexadecimal format.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  costRate:
    $ref: '#/components/schemas/RateRequest'
  hourlyRate:
    $ref: '#/components/schemas/RateRequest'
  isPublic:
    default: false
    description: Indicates whether project is public or not.
    type: boolean
  name:
    description: Represents a project name.
    maxLength: 250
    minLength: 2
    type: string
  note:
    description: Represents project note.
    maxLength: 16384
    type: string
type: object
```

<a id="schema-updateprojecttemplaterequest"></a>
### `UpdateProjectTemplateRequest`

```yaml
additionalProperties: false
properties:
  isTemplate:
    default: false
    description: Indicates whether project is a template or not.
    type: boolean
required:
- isTemplate
type: object
```

<a id="schema-updaterecurringassignmentrequest"></a>
### `UpdateRecurringAssignmentRequest`

```yaml
additionalProperties: false
description: Request for updating a recurring assignment.
properties:
  billable:
    default: false
    description: Indicates whether assignment is billable or not.
    type: boolean
  end:
    description: Represents an end date in the yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  hoursPerDay:
    description: Represents assignment total hours per day.
    format: double
    type: number
  includeNonWorkingDays:
    default: false
    description: Indicates whether to include non-working days or not.
    type: boolean
  note:
    description: Represents an assignment note.
    maxLength: 100
    type: string
  seriesUpdateOption:
    $ref: '#/components/schemas/SeriesUpdateOption'
  start:
    description: Represents start date in yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  startTime:
    description: Represents a start time in the hh:mm:ss format.
    example: '10:00:00'
    type: string
  taskId:
    description: Represents task identifier across the system.
    type: string
required:
- start
- end
type: object
```

<a id="schema-updatetimeoffpolicyrequest"></a>
### `UpdateTimeOffPolicyRequest`

```yaml
description: Request body for updating a time off policy.
properties:
  allowHalfDay:
    default: false
    description: Indicates whether policy allows half day.
    type: boolean
  allowNegativeBalance:
    default: false
    description: Indicates whether policy allows negative balance.
    type: boolean
  approve:
    $ref: '#/components/schemas/PolicyApprovalDto'
  archived:
    default: false
    description: Indicates whether policy is archived.
    type: boolean
  automaticAccrual:
    $ref: '#/components/schemas/AutomaticAccrualRequest'
  automaticTimeEntryCreation:
    $ref: '#/components/schemas/AutomaticTimeEntryCreationRequest'
  color:
    description: Policy color as a hex RGB value.
    pattern: ^#(?:[0-9a-fA-F]{6}){1}$
    type: string
  everyoneIncludingNew:
    default: false
    description: Indicates whether the policy is shown to new users.
    type: boolean
  hasExpiration:
    default: false
    description: Indicates whether the policy has expiration.
    type: boolean
  icon:
    description: Policy icon.
    enum:
    - UMBRELLA
    - SNOWFLAKE
    - FAMILY
    - PLANE
    - STETHOSCOPE
    - HEALTH_METRICS
    - CHILDCARE
    - LUGGAGE
    - MONETIZATION
    - CALENDAR
    type: string
  name:
    description: Name to use for updating the policy.
    maxLength: 100
    minLength: 2
    type: string
  negativeBalance:
    $ref: '#/components/schemas/NegativeBalanceRequest'
  userGroups:
    $ref: '#/components/schemas/PoliciesUserGroupIdsSchema'
  users:
    $ref: '#/components/schemas/PoliciesUserIdsSchema'
required:
- allowHalfDay
- allowNegativeBalance
- approve
- archived
- everyoneIncludingNew
- hasExpiration
- name
- userGroups
- users
type: object
```

<a id="schema-updateusercustomfieldvaluerequest"></a>
### `UpdateUserCustomFieldValueRequest`

```yaml
properties:
  value:
    description: Represents custom field value.
    nullable: true
required:
- value
type: object
```

<a id="schema-updateuserhourlyraterequest"></a>
### `UpdateUserHourlyRateRequest`

```yaml
additionalProperties: false
properties:
  amount:
    description: Represents an hourly rate amount as integer.
    format: int32
    minimum: 0
    type: integer
  since:
    description: Represents a date and time in yyyy-MM-ddThh:mm:ssZ format.
    example: '2020-01-01T00:00:00Z'
    type: string
required:
- amount
type: object
```

<a id="schema-updateuserstatusrequest"></a>
### `UpdateUserStatusRequest`

```yaml
additionalProperties: false
properties:
  status:
    description: Represents membership status.
    enum:
    - ACTIVE
    - INACTIVE
    type: string
required:
- status
type: object
```

<a id="schema-updateworkspacebillableraterequest"></a>
### `UpdateWorkspaceBillableRateRequest`

```yaml
additionalProperties: false
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    minimum: 0
    type: integer
  currency:
    default: USD
    description: Represents a currency.
    maxLength: 100
    minLength: 1
    type: string
  since:
    description: Represents a date and time in yyyy-MM-ddThh:mm:ssZ format.
    example: '2020-01-01T00:00:00Z'
    type: string
required:
- amount
- currency
type: object
```

<a id="schema-upsertusercustomfieldrequest"></a>
### `UpsertUserCustomFieldRequest`

```yaml
properties:
  customFieldId:
    description: Represents custom field identifier across the system.
    type: string
  value:
    description: Represents custom field value.
    nullable: true
required:
- customFieldId
type: object
```

<a id="schema-usercapacitytotal"></a>
### `UserCapacityTotal`

```yaml
additionalProperties: false
description: Represents capacity totals for a user.
properties:
  capacityPerDay:
    description: Represents capacity per day in seconds. For a 7hr work day, value is 25200.
    format: double
    type: number
  totalHoursPerDay:
    description: Represents total hours per day object.
    items:
      $ref: '#/components/schemas/TotalsPerDayDto'
    type: array
  userId:
    description: Represents user identifier across the system.
    type: string
  userImage:
    description: Represents url path to user image.
    type: string
  userName:
    description: Represents user name.
    type: string
  userStatus:
    description: Represents user status.
    type: string
  workingDays:
    description: Represents list of days of the week. The source sample shows a JSON-stringified array, so this
      schema allows both an array and a string representation.
    example:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    oneOf:
    - items:
        $ref: '#/components/schemas/DayOfWeek'
      type: array
    - type: string
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
type: object
```

<a id="schema-usercapacitytotalsrequest"></a>
### `UserCapacityTotalsRequest`

```yaml
additionalProperties: false
description: Request for total capacity of users on a workspace.
properties:
  end:
    description: Represents an end date in the yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  page:
    default: 1
    description: Page number.
    format: int32
    type: integer
  pageSize:
    default: 50
    description: Page size.
    format: int32
    maximum: 200
    type: integer
  search:
    description: Represents the keyword for searching users by name or email.
    type: string
  start:
    description: Represents a start date in the yyyy-MM-ddThh:mm:ssZ format.
    format: date-time
    type: string
  statusFilter:
    $ref: '#/components/schemas/StatusFilter'
  userFilter:
    $ref: '#/components/schemas/ContainsUsersFilterRequestV1'
  userGroupFilter:
    $ref: '#/components/schemas/ContainsUserGroupFilterRequestV1'
required:
- start
- end
type: object
```

<a id="schema-usercustomfieldvaluedtov1"></a>
### `UserCustomFieldValueDtoV1`

```yaml
description: Represents a user custom field value object.
properties:
  customFieldId:
    description: Represents custom field identifier across the system.
    type: string
  customFieldName:
    description: Represents custom field name.
    type: string
  customFieldType:
    $ref: '#/components/schemas/UsersCustomFieldType'
  userId:
    description: Represents user identifier across the system.
    type: string
  value:
    description: Represents custom field value.
    nullable: true
type: object
```

<a id="schema-usercustomfieldvaluefulldtov1"></a>
### `UserCustomFieldValueFullDtoV1`

```yaml
description: Represents a full user custom field value object.
properties:
  customField:
    $ref: '#/components/schemas/CustomFieldDtoV1'
  customFieldId:
    description: Represents custom field identifier across the system.
    type: string
  name:
    description: Represents user custom field name.
    type: string
  sourceType:
    description: Represents user custom field source type.
    enum:
    - WORKSPACE
    - USER
    type: string
  type:
    $ref: '#/components/schemas/UsersCustomFieldType'
  userId:
    description: Represents user identifier across the system.
    type: string
  value:
    description: Represents user custom field value.
    nullable: true
type: object
```

<a id="schema-userdto"></a>
### `UserDto`

```yaml
additionalProperties: true
properties:
  dateFormat:
    description: Date format.
    type: string
  email:
    description: Email.
    type: string
  id:
    description: User identifier.
    type: string
  name:
    description: Name.
    type: string
  timeFormat:
    description: Time format.
    type: string
  timeZone:
    description: Time zone.
    type: string
  weekStart:
    description: Week start day.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
type: object
```

<a id="schema-userdtov1"></a>
### `UserDtoV1`

```yaml
description: Represents a user.
properties:
  activeWorkspace:
    description: Represents user's active workspace identifier across the system.
    type: string
  customFields:
    description: Represents a list of value objects for user’s custom fields.
    items:
      $ref: '#/components/schemas/UserCustomFieldValueDtoV1'
    type: array
  defaultWorkspace:
    description: Represents user default workspace identifier across the system.
    type: string
  email:
    description: Represents email address of the user.
    format: email
    type: string
  id:
    description: Represents user identifier across the system.
    type: string
  memberships:
    description: Represents a list of membership objects.
    items:
      $ref: '#/components/schemas/UsersMembershipDtoV1'
    type: array
  name:
    description: Represents name of the user.
    type: string
  profilePicture:
    description: Represents profile image path of the user.
    type: string
  settings:
    $ref: '#/components/schemas/UserSettingsDtoV1'
  status:
    $ref: '#/components/schemas/AccountStatus'
  roles:
    description: Included when user responses request role details; shape varies by workspace role surface.
    items:
      type: object
      additionalProperties: true
    type: array
type: object
required:
- id
- email
- name
- status
```

<a id="schema-userfilterrequest"></a>
### `UserFilterRequest`

```yaml
description: Request body for filtering workspace users.
properties:
  accountStatuses:
    description: Filters users with the corresponding account status filter.
    items:
      $ref: '#/components/schemas/AccountStatus'
    type: array
    uniqueItems: true
  email:
    description: Filters users by email substring.
    type: string
  includeRoles:
    default: false
    description: If true, each user's detailed manager roles are included.
    type: boolean
  memberships:
    default: NONE
    description: Returns users along with workspaces, groups, or projects they have access to.
    enum:
    - ALL
    - NONE
    - WORKSPACE
    - PROJECT
    - USERGROUP
    type: string
  name:
    description: Filters users by name substring.
    type: string
  page:
    default: 1
    description: Page number.
    format: int32
    type: integer
  pageSize:
    default: 50
    description: Page size.
    format: int32
    minimum: 1
    type: integer
  projectId:
    description: If provided, returns users that have access to the project.
    type: string
  roles:
    description: Filters users that have any of the specified roles.
    items:
      enum:
      - WORKSPACE_ADMIN
      - OWNER
      - TEAM_MANAGER
      - PROJECT_MANAGER
      type: string
    type: array
    uniqueItems: true
  sortColumn:
    description: Sorting criteria.
    enum:
    - ID
    - EMAIL
    - NAME
    - NAME_LOWERCASE
    - ACCESS
    - HOURLYRATE
    - COSTRATE
    type: string
  sortOrder:
    description: Sorting mode.
    enum:
    - ASCENDING
    - DESCENDING
    type: string
  status:
    description: Filters users with the corresponding status.
    enum:
    - PENDING
    - ACTIVE
    - DECLINED
    - INACTIVE
    - ALL
    type: string
  userGroups:
    description: Filters users that belong to the specified user group IDs.
    items:
      type: string
    type: array
    uniqueItems: true
type: object
```

<a id="schema-usergroupdtov1"></a>
### `UserGroupDtoV1`

```yaml
description: Represents a user group.
example:
  id: 76a687e29ae1f428e7ebe101
  name: development_team
  teamManagers:
  - id: 672323eb0024343a1585e8a7
    name: Jane Doe
  userIds:
  - 5a0ab5acb07987125438b60f
  - 98j4b5acb07987125437y32
  workspaceId: 64a687e29ae1f428e7ebe303
properties:
  id:
    description: Represents a user group identifier across the system.
    type: string
    x-clockify-default: '##default'
  name:
    description: Represents a user group name.
    type: string
    x-clockify-default: '##default'
  teamManagers:
    description: Represents a list of assigned team managers for this user group.
    items:
      $ref: '#/components/schemas/UserRedactedDtoV1'
    type: array
    x-clockify-default: '##default'
  userIds:
    description: Represents a list of users' identifiers across the system.
    items:
      type: string
    type: array
    x-clockify-default: '##default'
  workspaceId:
    description: Represents a workspace identifier across the system.
    type: string
    x-clockify-default: '##default'
type: object
```

<a id="schema-usergroupidsschema"></a>
### `UserGroupIdsSchema`

```yaml
description: Provide list with user group ids and corresponding status.
properties:
  contains:
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    type: string
  ids:
    description: Represents ids upon which filtering is performed.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Represents user status.
    enum:
    - ALL
    - ACTIVE
    - INACTIVE
    type: string
type: object
```

<a id="schema-usergrouprequest"></a>
### `UserGroupRequest`

```yaml
description: Request body for creating or updating a user group.
example:
  name: development_team
properties:
  name:
    description: Represents a user group name.
    maxLength: 100
    minLength: 0
    type: string
    x-clockify-default: '##default'
required:
- name
type: object
```

<a id="schema-usergroupsortcolumn"></a>
### `UserGroupSortColumn`

```yaml
description: Column to be used as the sorting criteria.
enum:
- ID
- NAME
type: string
```

<a id="schema-usergroupssortorder"></a>
### `UserGroupsSortOrder`

```yaml
description: Sorting mode.
enum:
- ASCENDING
- DESCENDING
type: string
```

<a id="schema-useridwithratesrequest"></a>
### `UserIdWithRatesRequest`

```yaml
additionalProperties: false
description: Represents a user id with cost and hourly rates.
properties:
  costRate:
    $ref: '#/components/schemas/RateRequest'
  hourlyRate:
    $ref: '#/components/schemas/RateRequest'
  userId:
    description: Represents user identifier across the system.
    type: string
required:
- userId
type: object
```

<a id="schema-useridsschema"></a>
### `UserIdsSchema`

```yaml
description: Provide list with user ids and corresponding status.
properties:
  contains:
    enum:
    - CONTAINS
    - DOES_NOT_CONTAIN
    type: string
  ids:
    description: Represents ids upon which filtering is performed.
    items:
      type: string
    type: array
    uniqueItems: true
  status:
    description: Represents user status.
    enum:
    - ALL
    - ACTIVE
    - INACTIVE
    type: string
type: object
```

<a id="schema-userredacteddtov1"></a>
### `UserRedactedDtoV1`

```yaml
description: Represents a redacted user object.
example:
  id: 672323eb0024343a1585e8a7
  name: Jane Doe
properties:
  id:
    description: Represents a user identifier across the system.
    type: string
  name:
    description: Represents a user name.
    type: string
type: object
```

<a id="schema-usersettingsdtov1"></a>
### `UserSettingsDtoV1`

```yaml
description: Represents user settings object.
properties:
  alerts:
    default: false
    type: boolean
  approval:
    default: false
    type: boolean
  collapseAllProjectLists:
    default: false
    type: boolean
  dashboardPinToTop:
    default: false
    type: boolean
  dashboardSelection:
    enum:
    - ME
    - TEAM
    type: string
  dashboardViewType:
    enum:
    - PROJECT
    - BILLABILITY
    type: string
  dateFormat:
    description: Represents a date format.
    type: string
  groupSimilarEntriesDisabled:
    default: false
    type: boolean
  invoiceReminders:
    default: false
    type: boolean
  isCompactViewOn:
    default: false
    type: boolean
  lang:
    type: string
  longRunning:
    default: false
    type: boolean
  multiFactorEnabled:
    default: false
    type: boolean
  myStartOfDay:
    type: string
  onboarding:
    default: false
    type: boolean
  projectListCollapse:
    format: int32
    type: integer
  projectPickerTaskFilter:
    default: false
    type: boolean
  pto:
    default: false
    type: boolean
  reminders:
    default: false
    type: boolean
  scheduledReports:
    default: false
    type: boolean
  scheduling:
    default: false
    type: boolean
  sendNewsletter:
    default: false
    type: boolean
  showOnlyWorkingDays:
    default: false
    type: boolean
  summaryReportSettings:
    $ref: '#/components/schemas/SummaryReportSettingsDtoV1'
  theme:
    enum:
    - DARK
    - DEFAULT
    type: string
  timeFormat:
    description: Represents a time format enum.
    enum:
    - HOUR12
    - HOUR24
    type: string
  timeTrackingManual:
    default: false
    type: boolean
  timeZone:
    description: Represents a valid timezone ID.
    type: string
  weekStart:
    $ref: '#/components/schemas/UsersDayOfWeek'
  weeklyUpdates:
    default: false
    type: boolean
required:
- dateFormat
- timeFormat
- timeZone
type: object
```

<a id="schema-userscustomfieldtype"></a>
### `UsersCustomFieldType`

```yaml
description: Represents custom field type.
enum:
- TXT
- NUMBER
- DROPDOWN_SINGLE
- DROPDOWN_MULTIPLE
- CHECKBOX
- LINK
type: string
```

<a id="schema-usersdayofweek"></a>
### `UsersDayOfWeek`

```yaml
description: Represents a day of the week.
enum:
- MONDAY
- TUESDAY
- WEDNESDAY
- THURSDAY
- FRIDAY
- SATURDAY
- SUNDAY
type: string
```

<a id="schema-usersmembershipdtov1"></a>
### `UsersMembershipDtoV1`

```yaml
description: Represents a membership object.
properties:
  costRate:
    $ref: '#/components/schemas/RateDto'
  hourlyRate:
    $ref: '#/components/schemas/HourlyRateDtoV1'
  membershipStatus:
    description: Represents a membership status enum.
    enum:
    - PENDING
    - ACTIVE
    - DECLINED
    - INACTIVE
    - ALL
    type: string
  membershipType:
    description: Represents membership type enum.
    enum:
    - WORKSPACE
    - PROJECT
    - USERGROUP
    type: string
  targetId:
    description: Represents target identifier across the system.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
type: object
```

<a id="schema-visiblezerofieldsinvoice"></a>
### `VisibleZeroFieldsInvoice`

```yaml
description: Represents a zero-value invoice field that will be visible.
enum:
- TAX
- TAX_2
- DISCOUNT
type: string
```

<a id="schema-webhookcollectiondtov1"></a>
### `WebhookCollectionDtoV1`

```yaml
properties:
  webhooks:
    description: Represents a list of webhook objects for the workspace.
    items:
      $ref: '#/components/schemas/WebhookDtoV1'
    type: array
    x-sourceDefault: '##default'
  workspaceWebhookCount:
    description: Represents number of webhooks for the workspace.
    example: 5
    format: int32
    type: integer
type: object
```

<a id="schema-webhookdtov1"></a>
### `WebhookDtoV1`

```yaml
properties:
  authToken:
    description: Represents an authentication token.
    type: string
    x-sourceDefault: '##default'
  deliveryEnabled:
    default: false
    description: Indicates whether webhook delivery is enabled or not. It can be disabled if delivery failed for
      too many times.
    type: boolean
  enabled:
    default: false
    description: Indicates whether webhook is enabled or not.
    type: boolean
  id:
    description: Represents webhook identifier across the system.
    type: string
    x-sourceDefault: '##default'
  name:
    description: Represents webhook name.
    type: string
    x-sourceDefault: '##default'
  planEnabled:
    default: false
    description: Indicates whether webhook is supported by current plan. It can be disabled if number of webhooks
      exceeds plan limit or if the feature is not supported on current plan.
    type: boolean
  triggerSource:
    description: Represents a list of trigger sources.
    items:
      type: string
    type: array
    x-sourceDefault: '##default'
  triggerSourceType:
    $ref: '#/components/schemas/WebhookEventTriggerSourceType'
  url:
    description: Represents a webhook target URL.
    format: uri
    type: string
    x-sourceDefault: '##default'
  userId:
    description: Represents user identifier across the system.
    type: string
    x-sourceDefault: '##default'
  webhookEvent:
    $ref: '#/components/schemas/WebhookEventType'
  workspaceId:
    description: Represents workspace identifier across the system.
    type: string
    x-sourceDefault: '##default'
type: object
description: Live webhook records do not return entityType, feature, payloadType, or validSourceTypes.
```

<a id="schema-webhookeventstatuswithlatestlogdtov1"></a>
### `WebhookEventStatusWithLatestLogDtoV1`

```yaml
properties:
  id:
    description: Represents log identifier across the system.
    example: 69807d47b209426e67302a42
    type: string
  requestBody:
    description: Represents request body.
    example: '{"id":"65df50f5d2dd8f23a685374e","name":"Webhook"}'
    type: string
  respondedAt:
    description: Represents date and time of response.
    example: 2025-02-02 12:02:28 +0000
    type: string
  responseBody:
    description: Represents response body.
    example: '{"id":"h73210f5d2dd8f23685374e","response":"Webhook response"}'
    type: string
  retryCount:
    description: Represents how many times we tried to deliver the webhook event.
    example: 2
    format: int32
    type: integer
  status:
    description: Represents delivery status of the webhook event.
    example: FAILED
    type: string
  statusCode:
    description: Represents response status code.
    example: 400
    format: int32
    type: integer
  webhookId:
    description: Represents log identifier across the system.
    example: 6973710805e44c5a46763239
    type: string
  webhookLogId:
    description: Represents log identifier across the system.
    example: 69807e04b209426e67302a57
    type: string
type: object
```

<a id="schema-webhookeventtriggersourcetype"></a>
### `WebhookEventTriggerSourceType`

```yaml
enum:
- PROJECT_ID
- USER_ID
- TAG_ID
- TASK_ID
- WORKSPACE_ID
- ASSIGNMENT_ID
- EXPENSE_ID
type: string
```

<a id="schema-webhookeventtype"></a>
### `WebhookEventType`

```yaml
enum:
- NEW_PROJECT
- NEW_TASK
- NEW_CLIENT
- NEW_TIMER_STARTED
- TIMER_STOPPED
- TIME_ENTRY_UPDATED
- TIME_ENTRY_DELETED
- TIME_ENTRY_SPLIT
- NEW_TIME_ENTRY
- TIME_ENTRY_RESTORED
- NEW_TAG
- USER_DELETED_FROM_WORKSPACE
- USER_JOINED_WORKSPACE
- USER_DEACTIVATED_ON_WORKSPACE
- USER_ACTIVATED_ON_WORKSPACE
- USER_EMAIL_CHANGED
- USER_UPDATED
- NEW_INVOICE
- INVOICE_UPDATED
- NEW_APPROVAL_REQUEST
- APPROVAL_REQUEST_STATUS_UPDATED
- TIME_OFF_REQUESTED
- TIME_OFF_REQUEST_UPDATED
- TIME_OFF_REQUEST_APPROVED
- TIME_OFF_REQUEST_REJECTED
- TIME_OFF_REQUEST_STARTED
- TIME_OFF_REQUEST_WITHDRAWN
- BALANCE_UPDATED
- TAG_UPDATED
- TAG_DELETED
- TASK_UPDATED
- CLIENT_UPDATED
- TASK_DELETED
- CLIENT_DELETED
- EXPENSE_RESTORED
- ASSIGNMENT_CREATED
- ASSIGNMENT_DELETED
- ASSIGNMENT_PUBLISHED
- ASSIGNMENT_UPDATED
- EXPENSE_CREATED
- EXPENSE_DELETED
- EXPENSE_UPDATED
- PROJECT_UPDATED
- PROJECT_DELETED
- USER_GROUP_CREATED
- USER_GROUP_UPDATED
- USER_GROUP_DELETED
- USERS_INVITED_TO_WORKSPACE
- LIMITED_USERS_ADDED_TO_WORKSPACE
- COST_RATE_UPDATED
- BILLABLE_RATE_UPDATED
type: string
```

<a id="schema-webhooklogdtov1"></a>
### `WebhookLogDtoV1`

```yaml
properties:
  id:
    description: Represents log identifier across the system.
    type: string
    x-sourceDefault: '##default'
  requestBody:
    description: Represents request body.
    type: string
    x-sourceDefault: '##default'
  respondedAt:
    description: Represents date and time of response.
    format: date-time
    type: string
    x-sourceDefault: '##default'
  responseBody:
    description: Represents response body.
    type: string
    x-sourceDefault: '##default'
  statusCode:
    description: Represents response status code.
    format: int32
    type: integer
  webhookEventStatusId:
    description: Represents webhook event status identifier across the system.
    type: string
    x-sourceDefault: '##default'
  webhookId:
    description: Represents webhook identifier across the system.
    type: string
    x-sourceDefault: '##default'
type: object
```

<a id="schema-webhooklogsrequest"></a>
### `WebhookLogsRequest`

```yaml
properties:
  from:
    description: Represents date and time in yyyy-MM-ddThh:mm:ssZ format. If provided, results will include logs
      which occurred after this value.
    format: date-time
    type: string
  sortByNewest:
    default: false
    description: If set to true, logs will be sorted with most recent first.
    type: boolean
  status:
    description: Filters logs by status.
    enum:
    - ALL
    - SUCCEEDED
    - FAILED
    type: string
    x-sourceDefault: '##default'
  to:
    description: Represents date and time in yyyy-MM-ddThh:mm:ssZ format. If provided, results will include logs
      which occurred before this value.
    format: date-time
    type: string
type: object
```

<a id="schema-webhookrequest"></a>
### `WebhookRequest`

```yaml
properties:
  name:
    description: Represents a webhook name.
    maxLength: 30
    minLength: 2
    type: string
    x-sourceDefault: '##default'
  triggerSource:
    description: 'Represents a list of trigger sources.

      USER_EMAIL_CHANGED and USER_UPDATED require at least one user id.'
    items:
      type: string
    type: array
    x-sourceDefault: '##default'
  triggerSourceType:
    $ref: '#/components/schemas/WebhookEventTriggerSourceType'
    description: USER_EMAIL_CHANGED and USER_UPDATED require USER_ID.
  url:
    description: Represents a webhook target url.
    format: uri
    minLength: 1
    type: string
    x-sourceDefault: '##default'
  webhookEvent:
    $ref: '#/components/schemas/WebhookEventType'
required:
- name
- triggerSource
- triggerSourceType
- url
- webhookEvent
type: object
description: For USER_EMAIL_CHANGED and USER_UPDATED, live Clockify requires triggerSourceType USER_ID and a nonempty
  triggerSource user id.
```

<a id="schema-webhooktype"></a>
### `WebhookType`

```yaml
enum:
- USER_CREATED
- SYSTEM
- ADDON
type: string
```

<a id="schema-webhooksclockifyerror"></a>
### `WebhooksClockifyError`

```yaml
properties:
  code:
    description: Observed 501 for validation, 3000 for unsupported method.
    type: integer
  message:
    type: string
type: object
```

<a id="schema-webhookswebhook2"></a>
### `WebhooksWebhook2`

```yaml
properties:
  authToken:
    description: 32-char shared secret sent in webhook delivery headers.
    type: string
  deliveryEnabled:
    type: boolean
  enabled:
    type: boolean
  id:
    type: string
  name:
    type: string
  planEnabled:
    type: boolean
  triggerSource:
    items:
      type: string
    type: array
  triggerSourceType:
    type: string
  url:
    type: string
  userId:
    description: Present on create/update/regenerate responses (not documented in WEBHOOKDOC.md for list).
    type: string
  webhookEvent:
    type: string
  workspaceId:
    type: string
type: object
```

<a id="schema-weeklyfilter"></a>
### `WeeklyFilter`

```yaml
additionalProperties: false
description: Weekly report filter. Valid only on /reports/weekly. The group is USER or PROJECT, and subgroup is
  always TIME.
properties:
  group:
    description: Weekly report top-level group. Valid values are USER or PROJECT.
    enum:
    - USER
    - PROJECT
    type: string
  subgroup:
    default: TIME
    description: Weekly report subgroup. Clockify weekly report subgroup is always TIME.
    enum:
    - TIME
    type: string
required:
- group
- subgroup
type: object
x-clockify-report-filter: weekly
```

<a id="schema-weeklyreportrequest"></a>
### `WeeklyReportRequest`

```yaml
additionalProperties: false
description: Request payload for generating weekly reports. Only weeklyFilter is accepted as the report-specific
  filter.
properties:
  amountShown:
    description: If provided, returns reports with the provided amount shown.
    enum:
    - EARNED
    - COST
    - PROFIT
    - HIDE_AMOUNT
    - EXPORT
    type: string
  amounts:
    description: Amount columns to include.
    items:
      $ref: '#/components/schemas/AmountType'
    type: array
  approvalState:
    description: If provided, returns reports with the provided approval state.
    enum:
    - APPROVED
    - UNAPPROVED
    - ALL
    type: string
  archived:
    description: Indicates whether the report is archived.
    type: boolean
  billable:
    description: Indicates whether the report is billable.
    type: boolean
  clients:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  currency:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  customFields:
    description: Time entry custom field filters.
    items:
      $ref: '#/components/schemas/CustomFieldFilter'
    type: array
  dateFormat:
    description: Provide date in format YYYY-MM-DD.
    example: '2018-11-01'
    type: string
  dateRangeEnd:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. Interpreted using the user's timezone or the
      provided timeZone.
    example: '2018-11-30T23:59:59.999'
    minLength: 1
    type: string
  dateRangeStart:
    description: Provide date in format YYYY-MM-DDTHH:MM:SS.ssssss. Interpreted using the user's timezone or the
      provided timeZone.
    example: '2018-11-01T00:00:00'
    minLength: 1
    type: string
  dateRangeType:
    description: Date range preset.
    enum:
    - ABSOLUTE
    - TODAY
    - YESTERDAY
    - THIS_WEEK
    - LAST_WEEK
    - PAST_TWO_WEEKS
    - THIS_MONTH
    - LAST_MONTH
    - THIS_YEAR
    - LAST_YEAR
    type: string
  description:
    description: Search term for filtering report entries by description.
    type: string
  exportType:
    description: Export format requested for the report.
    enum:
    - JSON
    - JSON_V1
    - PDF
    - CSV
    - XLSX
    - ZIP
    type: string
  invoicingState:
    description: If provided, returns reports with the provided invoicing state.
    enum:
    - INVOICED
    - UNINVOICED
    - ALL
    type: string
  projects:
    $ref: '#/components/schemas/ContainsArchivedFilter'
  rounding:
    description: Indicates whether report filter rounding is enabled.
    type: boolean
  sortOrder:
    description: Sort order.
    enum:
    - ASCENDING
    - DESCENDING
    type: string
  tags:
    $ref: '#/components/schemas/ContainsTagFilter'
  tasks:
    $ref: '#/components/schemas/ContainsTaskFilter'
  timeFormat:
    description: Provide time in format THH:MM:SS.ssssss.
    example: T00:00:00
    type: string
  timeZone:
    description: Timezone used to interpret dates and times.
    example: Europe/Belgrade
    type: string
  userCustomFields:
    description: User custom field filters.
    items:
      $ref: '#/components/schemas/CustomFieldFilter'
    type: array
  userGroups:
    $ref: '#/components/schemas/ContainsUsersFilter'
  userLocale:
    description: Locale used for report formatting.
    example: en
    type: string
  users:
    $ref: '#/components/schemas/ContainsUsersFilter'
  weekStart:
    description: Configured week start day.
    enum:
    - MONDAY
    - TUESDAY
    - WEDNESDAY
    - THURSDAY
    - FRIDAY
    - SATURDAY
    - SUNDAY
    type: string
  weeklyFilter:
    $ref: '#/components/schemas/WeeklyFilter'
  withoutDescription:
    description: If true, report includes only entries with empty description.
    type: boolean
  zoomLevel:
    description: Report zoom level.
    enum:
    - WEEK
    - MONTH
    - YEAR
    type: string
required:
- dateRangeStart
- dateRangeEnd
- weeklyFilter
type: object
```

<a id="schema-weeklyreportresponse"></a>
### `WeeklyReportResponse`

```yaml
additionalProperties: true
description: Weekly report response.
properties:
  decimalFormat:
    description: Indicates whether the time entry report is in decimal format.
    type: boolean
  groupOne:
    description: List of groups.
    items:
      $ref: '#/components/schemas/GroupOneDto'
    type: array
  includeUsersWithoutTime:
    description: Indicates whether the report includes users without time.
    type: boolean
  totals:
    description: 'List of totals.

      Live empty weeks may contain a literal null item.'
    items:
      $ref: '#/components/schemas/TimeEntryReportTotals'
      nullable: true
    type: array
  totalsByDay:
    description: Daily totals.
    items:
      $ref: '#/components/schemas/DailyTotalDto'
    type: array
  trackTimeDownToSeconds:
    description: Indicates whether time is tracked down to seconds.
    type: boolean
  usersWithoutTime:
    description: Users without time.
    items:
      $ref: '#/components/schemas/UserDto'
    type: array
type: object
```

<a id="schema-workspace"></a>
### `Workspace`

```yaml
additionalProperties: true
description: Workspace object.
properties:
  cakeOrganizationId:
    description: Represents the Cake organization identifier across the system.
    type: string
  costRate:
    $ref: '#/components/schemas/WorkspacesRateDtoV1'
  currencies:
    items:
      $ref: '#/components/schemas/CurrencyWithDefaultInfoDtoV1'
    type: array
  featureSubscriptionType:
    description: Represents a feature plan type enum.
    example: STANDARD_2021
    type: string
  features:
    description: Represents a list of features.
    items:
      $ref: '#/components/schemas/WorkspacesFeature'
    type: array
  hourlyRate:
    $ref: '#/components/schemas/WorkspacesRateDtoV1'
  id:
    description: Represents workspace identifier across the system.
    type: string
  imageUrl:
    description: Represents an image url.
    type: string
  memberships:
    items:
      $ref: '#/components/schemas/WorkspacesMembershipDtoV1'
    type: array
  name:
    description: Represents workspace name.
    type: string
  subdomain:
    $ref: '#/components/schemas/WorkspaceSubdomainDtoV1'
  workspaceSettings:
    $ref: '#/components/schemas/WorkspaceSettingsDtoV1'
type: object
```

<a id="schema-workspaceexpensesdtov1"></a>
### `WorkspaceExpensesDtoV1`

```yaml
description: Response returned by the workspace expenses endpoint.
example:
  dailyTotals:
  - date: '2020-01-01'
    dateAsInstant: '2020-01-01T00:00:00Z'
    total: 10500.5
  expenses:
    count: 1
    expenses:
    - billable: false
      categoryId: 45y687e29ae1f428e7ebe890
      date: '2020-01-01'
      fileId: 745687e29ae1f428e7ebe890
      id: 64c777ddd3fcab07cfbb210c
      locked: true
      notes: This is a sample note for this expense.
      projectId: 25b687e29ae1f428e7ebe123
      quantity: 0.1
      taskId: 25b687e29ae1f428e7ebe123
      total: 10500.5
      userId: 89b687e29ae1f428e7ebe912
      workspaceId: 64a687e29ae1f428e7ebe303
  weeklyTotals:
  - date: '2020-01-01'
    total: 10500.5
properties:
  dailyTotals:
    items:
      $ref: '#/components/schemas/ExpenseDailyTotalsDtoV1'
    type: array
  expenses:
    $ref: '#/components/schemas/ExpensesWithCountDtoV1'
  weeklyTotals:
    items:
      $ref: '#/components/schemas/ExpenseWeeklyTotalsDtoV1'
    type: array
type: object
```

<a id="schema-workspacesettingsdtov1"></a>
### `WorkspaceSettingsDtoV1`

```yaml
additionalProperties: true
description: Workspace settings. Time Duration Format can be set by durationFormat; the decimalFormat and trackTimeDownToSecond
  booleans are deprecated in the source documentation.
properties:
  activeBillableHours:
    default: false
    description: Indicates whether billable hours is active.
    type: boolean
  adminOnlyPages:
    description: Represents a unique list of protected page enums.
    items:
      enum:
      - PROJECT
      - TEAM
      - REPORTS
      type: string
    type: array
    uniqueItems: true
  automaticLock:
    $ref: '#/components/schemas/AutomaticLockDtoV1'
  canSeeTimeSheet:
    default: false
    description: Indicates whether timesheets are visible or not.
    type: boolean
  canSeeTracker:
    default: false
    description: Indicates whether time trackers are visible or not.
    type: boolean
  currencyFormat:
    description: Represents a clockify currency format enum.
    enum:
    - CURRENCY_SPACE_VALUE
    - VALUE_SPACE_CURRENCY
    - CURRENCY_VALUE
    - VALUE_CURRENCY
    type: string
  defaultBillableProjects:
    default: false
    description: Indicates whether projects are billable by default.
    type: boolean
  durationFormat:
    description: Used to set Duration format instead of setting decimalFormat and trackTimeDownToSecond.
    enum:
    - FULL
    - COMPACT
    - DECIMAL
    type: string
  entityCreationPermissions:
    $ref: '#/components/schemas/EntityCreationPermissionsDtoV1'
  forceDescription:
    default: false
    description: Indicates whether description are forced or not.
    type: boolean
  forceProjects:
    default: false
    description: Indicates whether projects are forced or not.
    type: boolean
  forceTags:
    default: false
    description: Indicates whether tags are forced or not.
    type: boolean
  forceTasks:
    default: false
    description: Indicates whether tasks are forced or not.
    type: boolean
  isProjectPublicByDefault:
    type: boolean
  lockTimeEntries:
    type: string
  lockTimeZone:
    type: string
  multiFactorEnabled:
    default: false
    description: Indicates whether two-factor authentication is enabled or not.
    type: boolean
  numberFormat:
    description: Represents a clockify number format enum.
    enum:
    - COMMA_PERIOD
    - PERIOD_COMMA
    - QUOTATION_MARK_PERIOD
    - SPACE_COMMA
    type: string
  onlyAdminsCanChangeBillableStatus:
    default: false
    description: Indicates whether only admins can change billable status.
    type: boolean
  onlyAdminsCreateProject:
    default: false
    description: Indicates whether only admins can create projects.
    type: boolean
  onlyAdminsCreateTag:
    default: false
    description: Indicates whether only admins can create tags.
    type: boolean
  onlyAdminsCreateTask:
    default: false
    description: Indicates whether only admins can create task.
    type: boolean
  onlyAdminsSeeAllTimeEntries:
    default: false
    description: Indicates whether only admins can see all time entries.
    type: boolean
  onlyAdminsSeeBillableRates:
    default: false
    description: Indicates whether only admins can see billable rates.
    type: boolean
  onlyAdminsSeeDashboard:
    default: false
    description: Indicates whether only admins can see dashboard.
    type: boolean
  onlyAdminsSeePublicProjectsEntries:
    default: false
    description: Indicates whether only admins can see public project entries.
    type: boolean
  projectFavorites:
    default: false
    description: Indicates whether project favorites are allowed.
    type: boolean
  projectGroupingLabel:
    description: Represents a project grouping label.
    type: string
  projectLabel:
    description: Represents a project label.
    type: string
  projectPickerSpecialFilter:
    default: false
    description: Indicates whether project picker special filter is enabled.
    type: boolean
  round:
    $ref: '#/components/schemas/RoundDto'
  taskLabel:
    description: Represents a task label.
    type: string
  timeRoundingInReports:
    default: false
    description: Indicates whether time rounding is enabled in reports.
    type: boolean
  timeTrackingMode:
    description: Represents a time tracking mode enum.
    enum:
    - DEFAULT
    - STOPWATCH_ONLY
    type: string
  trackTimeDownToSecond:
    default: false
    deprecated: true
    description: Indicates whether time tracking is seconds-accurate. Deprecated; durationFormat can now be used
      to manage Time Duration Format.
    type: boolean
  workingDays:
    description: Represents a list of working days.
    items:
      enum:
      - MONDAY
      - TUESDAY
      - WEDNESDAY
      - THURSDAY
      - FRIDAY
      - SATURDAY
      - SUNDAY
      type: string
    type: array
    uniqueItems: true
type: object
```

<a id="schema-workspacesubdomaindtov1"></a>
### `WorkspaceSubdomainDtoV1`

```yaml
additionalProperties: true
description: Represents the workspace subdomain.
properties:
  enabled:
    default: false
    description: Indicates whether subdomain is enabled on workspace.
    type: boolean
  name:
    description: Represents subdomain name.
    type: string
type: object
```

<a id="schema-workspacesfeature"></a>
### `WorkspacesFeature`

```yaml
description: Workspace feature identifier.
enum:
- ADD_TIME_FOR_OTHERS
- ADMIN_PANEL
- ALERTS
- APPROVAL
- AUDIT_LOG
- AUTOMATIC_LOCK
- BRANDED_REPORTS
- BULK_EDIT
- CUSTOM_FIELDS
- CUSTOM_REPORTING
- CUSTOM_SUBDOMAIN
- CREATION_PERMISSIONS
- DECIMAL_FORMAT
- DISABLE_MANUAL_MODE
- EDIT_MEMBER_PROFILE
- EXCLUDE_NON_BILLABLE_FROM_ESTIMATE
- EXPENSES
- FILE_IMPORT
- TIMESHEET_IMPORT
- USER_IMPORT
- HIDE_PAGES
- HISTORIC_RATES
- INVOICING
- INVOICE_EMAILS
- INVOICE_REMINDERS
- LABOR_COST
- LOCATIONS
- MANAGER_ROLE
- MULTI_FACTOR_AUTHENTICATION
- PROJECT_BUDGET
- PROJECT_TEMPLATES
- GRANT_PROJECT_MANAGER_ROLE
- PRIVATE_PROJECT_ACCESS
- QUICKBOOKS_INTEGRATION
- RECURRING_ESTIMATES
- RECURRING_INVOICES
- REQUIRED_FIELDS
- SCHEDULED_REPORTS
- SCHEDULING
- SCREENSHOTS
- SSO
- SUMMARY_ESTIMATE
- TARGETS_AND_REMINDERS
- TASK_RATES
- TIME_OFF
- UNLIMITED_REPORTS
- USER_CUSTOM_FIELDS
- WHO_CAN_CHANGE_TIMEENTRY_BILLABILITY
- BREAKS
- KIOSK_SESSION_DURATION
- KIOSK_PIN_REQUIRED
- WHO_CAN_SEE_ALL_TIME_ENTRIES
- WHO_CAN_SEE_PROJECT_STATUS
- WHO_CAN_SEE_PUBLIC_PROJECTS_ENTRIES
- WHO_CAN_SEE_TEAMS_DASHBOARD
- WORKSPACE_LOCK_TIMEENTRIES
- WORKSPACE_TIME_AUDIT
- WORKSPACE_TIME_ROUNDING
- KIOSK
- KIOSK_SIX_DIGIT_PIN
- KIOSK_QR_CODE
- LIMITED_USERS
- FORECASTING
- TIME_TRACKING
- ATTENDANCE_REPORT
- WORKSPACE_TRANSFER
- FAVORITE_ENTRIES
- SPLIT_TIME_ENTRY
- CLIENT_CURRENCY
- SCHEDULING_FORECASTING
- SCIM
- UNLIMITED_USER_SEATS
- BILLABLE_HOURS
- PROJECT_ESTIMATE
- CSV_EXPORT
- XLSX_EXPORT
- ONE_MONTH_RANGE_REPORTS
- ONE_YEAR_RANGE_REPORTS
- SHARED_REPORTS
type: string
```

<a id="schema-workspacesmembershipdtov1"></a>
### `WorkspacesMembershipDtoV1`

```yaml
additionalProperties: true
description: Represents a membership object.
properties:
  costRate:
    $ref: '#/components/schemas/WorkspacesRateDtoV1'
  hourlyRate:
    $ref: '#/components/schemas/WorkspacesRateDtoV1'
  membershipStatus:
    description: Represents a membership status enum.
    enum:
    - PENDING
    - ACTIVE
    - DECLINED
    - INACTIVE
    - ALL
    type: string
  membershipType:
    description: Represents membership type enum.
    enum:
    - WORKSPACE
    - PROJECT
    - USERGROUP
    type: string
  targetId:
    description: Represents target identifier across the system.
    type: string
  userId:
    description: Represents user identifier across the system.
    type: string
type: object
```

<a id="schema-workspacesratedtov1"></a>
### `WorkspacesRateDtoV1`

```yaml
additionalProperties: true
description: Represents hourly rate object.
properties:
  amount:
    description: Represents an amount as integer.
    format: int32
    type: integer
  currency:
    description: Represents a currency.
    type: string
type: object
```

<a id="schema-invoicinginfo"></a>
### `invoicingInfo`

```yaml
description: Expense's invoicing info.
properties:
  invoiceId:
    type: string
  manuallyInvoiced:
    type: boolean
type: object
```

## Manifest invariants

- Exactly 168 unique authoritative operation IDs are present.
- Exactly 168 unique `(resource, method)` Python mappings are present; no collision and no Python keyword is used as a method name.
- Exactly 62 operations are non-mutating and 106 are mutating.
- Exactly 49 non-mutating operations use GET and 13 use POST.
- Exactly 60 raw read operations are eligible for MCP registration; two binary-only reads are SDK-only.
- Every operation records path/query/body/response information from the corrected OpenAPI and every transitive reachable component-schema root is present in the appendix.
- Historical: writes were deferred by this manifest until 0.2.0 shipped them through the sealed gate.
