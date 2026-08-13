# SDK guide

`ClockifyClient` is asynchronous and owns one reused `httpx.AsyncClient` unless
you inject a client. Use it as an async context manager.

## Resources and operations

The client has 29 explicit resource attributes and 168 explicit methods. The
operation registry routes calls to regular, reports, or audit-log hosts. The
raw escape hatch accepts registered operation IDs only. It cannot call an
arbitrary URL or method.

## Pagination

Resource list methods fetch one page. Use `Page`, `iter_pages`, and `iter_all`
when you need bounded iteration. Page-size wire names differ by operation.
`Last-Page` is authoritative when the operation declares it.

Use `Page.from_response(...)` when the iterator fetches a raw `ClockifyResponse`.
This constructor keeps the `Last-Page` header, request ID, and response headers.
It prevents a short page from ending iteration when `Last-Page: false` says that
another page exists.

See `examples/sdk_iterate_time_entries.py`.

## Reports

Report methods are semantic reads even though they use `POST`. They can use the
optional read retry policy. A write cannot use that retry policy.

See `examples/sdk_generate_report.py`.

## Errors

Catch broad public categories such as `ClockifyAPIError`,
`ClockifyTransportError`, and `MutationOutcomeUnknownError`. API errors retain
only bounded sanitized fields. Use `operation_id`, `status_code`, `request_id`,
`api_code`, `retry_after`, and `detail` for diagnostics.

See `examples/sdk_error_handling.py`.

## Writes

The Python SDK exposes 106 writes to explicit callers. Verify the workspace
before each live write. Use unique names, capture created IDs, and clean up in
`finally`. A deleted tag, project, or client name can remain reserved. Always
use a new name for a later run.

See `examples/sdk_create_tag_sacrificial.py`.
