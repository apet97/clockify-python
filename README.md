# clockify-python-115

`clockify-python-115` is an independent community project. It is not affiliated
with, endorsed by, or sponsored by CAKE.com or Clockify. The project uses the
Clockify name only to identify the service that it supports.

The distribution contains:

- `clockify`: a typed async SDK with all 168 known Clockify operations on 29 resources.
- `clockify_mcp`: a structurally read-only Model Context Protocol (MCP) server.

Release status: `0.1.0` is a local release candidate. It is not published to
PyPI yet. The default MCP server registers 60 raw reads and five workflows. It
registers zero writes.

## Install

Install the local release candidate after `uv build`:

```bash
uv pip install dist/clockify_python_115-0.1.0-py3-none-any.whl
uv pip install "dist/clockify_python_115-0.1.0-py3-none-any.whl[mcp]"
```

After publication, use:

```bash
uv add clockify-python-115
uv add "clockify-python-115[mcp]"
```

Python 3.11, 3.12, 3.13, and 3.14 are supported and tested.

## Read-only SDK quickstart

```python
import asyncio
import os

from clockify import ClockifyClient


async def main() -> None:
    async with ClockifyClient(
        api_key=os.environ["CLOCKIFY_API_KEY"],
        workspace_id=os.environ.get("CLOCKIFY_WORKSPACE_ID"),
    ) as clockify:
        me = await clockify.users.me()
        projects = await clockify.projects.list(archived=False, page_size=25)
        print(me.name, len(projects))


asyncio.run(main())
```

See [docs/quickstart.md](docs/quickstart.md) and
[examples/sdk_list_projects.py](examples/sdk_list_projects.py).

## MCP quickstart

```bash
clockify-mcp
```

Configure exactly one of `CLOCKIFY_API_KEY` or `CLOCKIFY_ADDON_TOKEN`. You can
also configure `CLOCKIFY_WORKSPACE_ID`.

The MCP contract is exact:

- 60 raw read tools;
- five workflows: `clockify_status`, `clockify_workspace_overview`,
  `clockify_review_day`, `clockify_review_week`, and `clockify_doctor`;
- 65 tools in total;
- zero registered writes.

The SDK exposes writes to explicit Python callers. MCP does not. See
[docs/mcp-guide.md](docs/mcp-guide.md) and
[examples/mcp_config.example.json](examples/mcp_config.example.json).

## SDK behavior

- Configure exactly one credential. The SDK rejects caller-supplied authority
  and Clockify credential headers before network access.
- Ordinary caller headers and `X-Request-Id` are preserved.
- Read retries support delay-seconds and HTTP-date `Retry-After` values.
- No write is automatically retried. An ambiguous write transport failure
  raises `MutationOutcomeUnknownError`. Read state before a manual retry.
- Pagination names vary by operation. Use `iter_pages` or `iter_all` and honor
  the operation's `Last-Page` behavior.
- Reports and audit-log operations use their required service hosts automatically.
- Some `PUT` operations replace the complete entity. Resend each field that
  must remain. See [docs/api-deviations.md](docs/api-deviations.md).
- API errors expose bounded sanitized detail, status, operation ID, request ID,
  safe API code, and safe retry timing.

The direct write example is intentionally separate. It mutates only a verified
sacrificial workspace and uses a unique name:
[examples/sdk_create_tag_sacrificial.py](examples/sdk_create_tag_sacrificial.py).

## Develop

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q -m "not live"
uv build
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md),
[NOTICE.md](NOTICE.md), and [LICENSE](LICENSE).
