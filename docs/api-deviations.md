# Known Clockify API deviations

Encoded as ordinary implementation plus focused regression tests
(`tests/contract/test_known_deviations.py`, wiring tests, live suite).

- Three hosts: regular (`api.clockify.me/api/v1`), reports
  (`reports.api.clockify.me/v1`), audit log (`auditlog-api.api.clockify.me/v1`).
- 13 POST operations are semantic reads (reports, filters, searches, batch get).
- Pagination names vary (`page-size`, `pageSize`, `size`); the `Last-Page`
  response header is authoritative where live-audited.
- Money scales differ by operation: rates and expense totals are minor units
  (cents); expense `amount` on create/update is major units; invoice
  `unitPrice`/tax percents are minor-units-times-100. See `clockify.money`.
- `PUT` is not uniformly "replace": clients/tags/projects and others are proven
  full replacements (omitting `ccEmails`/`archived` destroys data); several PUT
  omission rules remain unproven and are marked conservative.
- Lifecycle prerequisites: archive-before-delete (projects, clients),
  DONE-before-delete (tasks), pending-only withdrawal (time-off requests).
- Invoice payment create returns the updated invoice, not the payment; recover
  the payment ID by list diff.
- Some flat routes are phantoms (404): stop-timer lives at the user-scoped
  PATCH; time-off status/delete are policy-scoped.
- `getProjectById`/`getInvoiceById` return 400 code 501 for missing entities,
  never 404.
- Weekly reports require an exact seven-day interval; several ranges evaluate as
  wall-clock values in a supplied or account timezone.
- Idempotency keys are unsupported/no-op: no write is ever automatically
  retried; a transport failure after dispatch is `MutationOutcomeUnknownError`.
- Live 2026-08-12: workspace `features` contains enum values missing from the
  spec, and `entityCreationPermissions` values arrive as plain strings; response
  models accept both shapes.
- Live 2026-08-13: the official spec marks `submitApprovalRequest`
  (`POST /approval-requests`) and `submitApprovalRequestForUser`
  (`POST /approval-requests/users/{userId}`) as deprecated. The typed variants
  (`approvals.submit_with_type`, `approvals.submit_for_user_with_type`) are the
  successors. This SDK keeps both deprecated operations; the routes still work.
- Live 2026-08-13: the official spec renamed the typed-submit path parameter
  from `{approvalRequestId}` to `{type}`, confirming what this SDK already
  documents: the segment is the approval type (`TIMESHEET` | `EXPENSE`), not an
  approval request ID.
