# Direction A final adversarial review

Date: 2026-08-12. Release-candidate code commit: `e755016`.

## Verdict

**DIRECTION A RELEASE READY — MCP WRITES REMAIN DISABLED**

This verdict applies to the local `0.1.0` release candidate. No push, tag,
public release, or PyPI publication occurred.

## Verified product contract

- Independent package: `clockify-python-115`.
- Python 3.11 through 3.14.
- 168 explicit SDK operations on 29 resources: 62 reads and 106 SDK writes.
- Default MCP server: 60 raw reads, five workflows, 65 total tools, zero writes.
- `clockify_mcp.server` imports no dormant write module.
- Sibling specification checkout remained clean at
  `d7091a44a1b95d4918fa17a7f9b174bf668a9136`.

## Final gates

| Evidence | Result |
|---|---|
| `uv run ruff check .` | Pass |
| `uv run ruff format --check .` | Pass |
| `uv run pyright` | 0 errors |
| `uv run pytest -q -m "not live"` | 459 passed, 6 deselected |
| `uv run pytest -q -m live` | 6 passed, 459 deselected; zero residue |
| Exact wheel, core-only and `[mcp]` | Pass on Python 3.11, 3.12, 3.13, 3.14 |
| Exact sdist | Pass on Python 3.14 |
| Official MCP stdio client | Initialize; exact 65 tools; zero writes; controlled rejection; protocol-only stdout |
| Deterministic build | Wheel and sdist byte-identical across two builds |

The live run used unique names and cleanup in `finally`. It proved workspace
identity, tag and project lifecycles, and one explicitly approved dormant
write-gate flow. It did not change the default server or register MCP writes.

## Second-opinion closure

- SO-01: protected authority and Clockify credential headers are rejected at
  compile and final dispatch boundaries, case-insensitively.
- SO-02: API and MCP errors redact configured secrets and auth-like fields and
  bound strings, nesting, collections, and bodies.
- SO-03: one shared parser supports both `Retry-After` forms.
- SO-04: both packages contain PEP 561 markers; installed negative type proof
  rejects an invalid SDK call.
- SO-05: CI builds once and proves the downloaded artifact on all supported
  Python versions; release publication is a separate least-privilege job.
- SO-06: the plan limit measures canonical UTF-8 bytes for all retained fields.
- SO-07: pending records and tombstones share one bounded capacity.
- SO-08: user docs state independence, lead with reads, and isolate writes in a
  unique-name sacrificial example.
- SO-09: no configured secret match exists in tracked files, reachable refs, or
  artifacts. One local reflog-only unreachable blob remains an owner action.
- SO-10: active guidance is maintenance-oriented; stale campaign ceremony is
  removed.

## Required mutant campaign

All mutants were introduced one at a time in one disposable worktree. Each
focused test failed, the mutation was restored, and the worktree was deleted.

| # | Mutant | Killing evidence |
|---:|---|---|
| 1 | Allow caller authority headers | protected-header case matrix |
| 2 | Expose raw reflected error data | configured-secret public-view test |
| 3 | Remove HTTP-date retry parsing | actual retry-delay matrix |
| 4 | Omit `py.typed` from the wheel | exact installed-artifact verifier |
| 5 | Replace artifact CI proof with source tests | CI workflow contract test |
| 6 | Disable `ReadOnlyExecutor` refusal | pre-network mutation boundary test |
| 7 | Retry mutating operations | POST-write and semantic GET-trap tests |
| 8 | Remove consumed-nonce tombstones | replay and 100-consumer tests |
| 9 | Remove principal binding | principal-mismatch consume test |
| 10 | Remove workspace binding | stored-record workspace test |
| 11 | Dispatch the caller-owned step | stored-step identity test |
| 12 | Omit a retained plan field | structural field and oversized-warning tests |
| 13 | Exclude tombstones from capacity | sequential and concurrent capacity tests |
| 14 | Import write modules in default server | fresh-interpreter import test |
| 15 | Allow MCP PDF/XLSX output | in-memory and spawned-stdio rejection tests |

## Artifacts

| File | Size | SHA-256 |
|---|---:|---|
| `clockify_python_115-0.1.0-py3-none-any.whl` | 188,562 bytes | `ea85c93fb6108d828576fea9eec6433f48e8ae8210df4d33d317d971d4dfb60c` |
| `clockify_python_115-0.1.0.tar.gz` | 367,153 bytes | `259afe53aa3bfc1480211664b21bfd7f535db4f7293edc24899d350a8440905d` |

## Residual owner and external actions

1. Rotate or revoke the credential that matched local unreachable blob
   `88ab0df5bfd36815c7073531cbd54f3b73f826d6`.
2. Remove the stale shell-profile value. Only then consider reflog expiry and
   garbage collection. Git cleanup is not revocation.
3. Configure the protected GitHub `pypi` environment and PyPI Trusted
   Publisher before publication.
4. Push, tag, publish, and verify immutable public artifacts only when the
   owner authorizes those external actions.
5. Before registering any MCP write, obtain a separate approval and real
   approval-UI evidence from two intended hosts.
