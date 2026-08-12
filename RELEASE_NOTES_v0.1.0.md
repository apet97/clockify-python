# clockify-python-115 0.1.0

## GitHub release body

First release of the independent `clockify-python-115` project.

- Complete typed async SDK: 168 operations on 29 resources.
- Read-only MCP server: 60 raw reads and five workflows.
- Zero registered MCP writes.
- Protected authenticated headers, bounded sanitized errors, no write retries,
  and HTTP-date `Retry-After` support.
- Python 3.11 through 3.14.

This project is not affiliated with, endorsed by, or sponsored by CAKE.com or
Clockify.

## PyPI summary

Independent typed async Clockify SDK with 168 operations and a 65-tool
read-only MCP server for Python 3.11 through 3.14.

## Install

```bash
uv add clockify-python-115
uv add "clockify-python-115[mcp]"
```

## 60-second SDK demo

```python
import asyncio, os
from clockify import ClockifyClient


async def main():
    async with ClockifyClient(api_key=os.environ["CLOCKIFY_API_KEY"]) as client:
        me = await client.users.me()
        print(me.name)


asyncio.run(main())
```

## 60-second MCP demo

Install the `[mcp]` extra. Configure one credential and run:

```bash
clockify-mcp
```

The server lists 65 tools. It exposes 60 raw reads and five workflows. It
exposes no writes.

## Limitations

- The project is unofficial and not yet publicly published at the time of this receipt.
- The MCP server is read-only.
- Some `PUT` omission rules remain conservative and require full replacement care.
- Real human approval for future MCP writes still requires evidence from two intended hosts.

## Artifacts

Two independent builds produced byte-identical files:

| File | Size | SHA-256 |
|---|---:|---|
| `clockify_python_115-0.1.0-py3-none-any.whl` | 188,562 bytes | `ea85c93fb6108d828576fea9eec6433f48e8ae8210df4d33d317d971d4dfb60c` |
| `clockify_python_115-0.1.0.tar.gz` | 367,153 bytes | `259afe53aa3bfc1480211664b21bfd7f535db4f7293edc24899d350a8440905d` |

## Owner release steps

1. Rotate or revoke the reflog-only credential and remove the stale shell-profile value.
2. Create or select the GitHub remote.
3. Configure the protected `pypi` GitHub environment.
4. Configure the PyPI Trusted Publisher for `.github/workflows/release.yml`.
5. Review the release commit and create the `v0.1.0` tag.
6. Push the branch and tag. The release workflow builds, verifies, and publishes once.
7. Verify names, hashes, metadata, imports, typing, and MCP behavior from PyPI.

## Developer announcement

`clockify-python-115` 0.1.0 provides a typed async API for all 168 reconciled
Clockify operations. It includes installed PEP 561 typing, explicit resources,
three-host routing, safe bounded errors, and exact artifact verification.

## Clockify user announcement

Use Python or a read-only MCP host to inspect Clockify users, projects, time
entries, reports, and other workspace data. MCP writes remain disabled. The
separate SDK write example is for verified sacrificial workspaces only.
