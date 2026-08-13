# clockify-python-115

`clockify-python-115` is an independent community project. It is not affiliated
with, endorsed by, or sponsored by CAKE.com or Clockify. The project uses the
Clockify name only to identify the service that it supports.

The distribution contains:

- `clockify`: a typed async SDK with all 168 known Clockify operations on 29 resources.
- `clockify_mcp`: a full-featured Model Context Protocol (MCP) server with a
  sealed approval gate for guarded writes.

Documentation version: `0.2.0`. The distribution is available from public
PyPI. The default MCP server registers 186 tools: 60 raw reads, 104 guarded
or routine writes, 18 workflows, and 4 orientation tools. Set
`CLOCKIFY_MCP_READ_ONLY=true` for the structurally read-only 65-tool build.

## Install

Install the SDK or the SDK with the optional MCP server:

```bash
uv add clockify-python-115
uv add "clockify-python-115[mcp]"
```

Python 3.11, 3.12, 3.13, and 3.14 are supported and tested.

## SDK quickstart

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
clockify-mcp                    # stdio (default)
clockify-mcp --http --port 8000 # Streamable HTTP, stateful sessions
```

Configure exactly one of `CLOCKIFY_API_KEY` or `CLOCKIFY_ADDON_TOKEN`. You can
also configure `CLOCKIFY_WORKSPACE_ID`.

The MCP contract is exact:

- 60 raw read tools and 104 raw write tools;
- 18 workflows (5 read, 7 routine write, 6 gated write) and 4 orientation
  tools: 186 tools in total;
- routine writes (personal time entries, daily tracking) execute directly and
  are never retried;
- every other write is guarded: the user approves a deterministic preview of
  the exact request before anything is sent, bound by a single-use
  confirmation;
- `CLOCKIFY_MCP_READ_ONLY=true` serves the read-only build (65 tools, zero
  writes, structurally unable to mutate).

See [docs/mcp.md](docs/mcp.md) and
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
