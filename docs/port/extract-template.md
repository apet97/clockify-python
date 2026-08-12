# Operation-module extraction template (internal working note; deleted after Phase 2)

For each assigned resource, write `src/clockify/operations/<resource>.py` exactly in this
shape, transcribing `docs/port/OPERATION_PORT_MANIFEST.md`:

```python
"""Operation records for the `<resource>` resource.

Hand-authored from docs/port/OPERATION_PORT_MANIFEST.md; verify against it, not
against the raw OpenAPI alone.
"""

from clockify.operations.model import (
    MutationEffect,
    Operation,
    OperationSemantics,
    PaginationSpec,
    QueryParameter,
    ReplacementSemantics,
    RequestEncoding,
    ResponseKind,
    Service,
)

APPROVALS_LIST = Operation(
    operation_id="getApprovalRequests",
    resource="approvals",
    sdk_method="list",
    http_method="GET",
    service=Service.REGULAR,
    path="/workspaces/{workspaceId}/approval-requests",
    path_parameters=("workspaceId",),
    query_parameters=(
        QueryParameter("status", "status"),
        QueryParameter("sort_column", "sort-column"),
        QueryParameter("types", "types"),  # repeated query key -> explode=True (default)
        QueryParameter("sort_order", "sort-order"),
        QueryParameter("page", "page"),
        QueryParameter("page_size", "page-size"),
    ),
    request_encoding=RequestEncoding.NONE,
    response_kind=ResponseKind.JSON,
    pagination=PaginationSpec(
        page_parameter="page",
        page_size_parameter="page-size",
        items_path=None,  # bare array
        last_page_header=True,
    ),
    semantics=OperationSemantics(
        mutates=False,
        effect=MutationEffect.NONE,
        replacement=ReplacementSemantics.NOT_APPLICABLE,
    ),
)

# ... one constant per operation, named <RESOURCE>_<METHOD> in manifest order ...

OPERATIONS = (APPROVALS_LIST, ...)
```

Rules:

- `operation_id`, `path`, wire names: byte-exact from the manifest tables.
- `path_parameters`: wire names in the order they appear in the path template.
- `query_parameters`: one per query row, manifest order. `python_name` from the Python
  column, `wire_name` from Wire. "repeated query key" -> default explode=True.
  "comma-joined"/"comma-separated single key" -> `style="form", explode=False`.
- `request_encoding`: NONE (no body), JSON, or MULTIPART per the Request body table.
- `response_kind`: decoder column -> JSON/BYTES/TEXT/NONE/CONTENT_NEGOTIATED.
- `pagination`: only when the record has a **Pagination:** line. `items_path` is None for a
  bare array, else the tuple path to the item list inside the envelope
  (e.g. `("clients",)` or `("timeentries",)`). `count_path` likewise when a count field is
  named. `last_page_header=True` only when the record says the `Last-Page` header is
  authoritative.
- `semantics.mutates`: from the Mutation row (`non-mutating` -> False).
- `semantics.effect` (mutating only): CREATE / REPLACE / PATCH / TRANSITION / DELETE / BULK,
  judged from the record's behavior + corrected-behavior notes. Reads use
  `MutationEffect.NONE`. Status/archival toggles are TRANSITION. Multi-entity writes are BULK.
- `semantics.replacement`: PATCH for partial updates; FULL_REPLACE_PROVEN or MIXED_PROVEN
  only when the corrected-behavior notes prove it; UNKNOWN_CONSERVATIVE when the record
  says omission behavior is unproven; NOT_APPLICABLE otherwise.
- `semantics.lifecycle`: `"archive_before_delete"`, `"done_before_delete"`, or
  `"pending_only"` when the record states the prerequisite; else omit.
- `semantics.replacement_required_fields`: exact wire field names when the record
  enumerates fields that a replacement must resend to avoid data loss; else omit.
- Add a short trailing `#` comment on a record only for a non-obvious wire quirk stated in
  the manifest (e.g. money units, weird envelope, payment-ID recovery). No prose blocks.

Also write `tests/fixtures/wiring/<resource>.json` (one file per resource):

```json
{
  "resource": "approvals",
  "operations": {
    "getApprovalRequests": {
      "request_model": null,
      "response": {"shape": "list", "model": "ApprovalRequestListItem", "items_path": null},
      "notes": []
    }
  }
}
```

- `request_model`: the component-schema class name of the JSON/multipart body, else null.
- `response.shape`: "model" | "list" | "none" | "bytes" | "text" | "negotiated".
- `response.model`: component-schema class name of the (item) payload, null for
  none/bytes/text. If the manifest names an inline/envelope shape with no component name,
  use null and add a note.
- `response.items_path`: envelope path array for list responses, null for bare arrays.
- `notes`: short strings for corrected-behavior facts a later implementer must not miss
  (money units, lifecycle prerequisites, payment-ID recovery, absent single-get, exact
  weekly interval, wall-clock semantics, replace-risk fields). Empty list when none.
