"""Console entry point for the Clockify MCP server.

Default: the full server (reads, workflows, gated writes) over stdio.
``CLOCKIFY_MCP_READ_ONLY=true`` selects the structurally read-only build.
``--http`` serves Streamable HTTP with stateful sessions (required for the
write-approval round trip); stdio keeps stdout protocol-only.
"""

import os
import sys

_HELP = """clockify-mcp: Clockify MCP server.
Environment: CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN (exactly one),
optional CLOCKIFY_WORKSPACE_ID.
CLOCKIFY_MCP_READ_ONLY=true serves only the 65 read tools.
Options:
  --http         serve Streamable HTTP instead of stdio
  --host HOST    HTTP bind host (default 127.0.0.1)
  --port PORT    HTTP bind port (default 8000)
"""


def _parse_args(argv: list[str]) -> tuple[bool, str, int]:
    """Minimal flag parsing; argparse would print help to stdout."""
    http = False
    host = "127.0.0.1"
    port = 8000
    index = 0
    while index < len(argv):
        flag = argv[index]
        if flag == "--http":
            http = True
        elif flag == "--host" and index + 1 < len(argv):
            index += 1
            host = argv[index]
        elif flag == "--port" and index + 1 < len(argv):
            index += 1
            port = int(argv[index])
        else:
            raise ValueError(f"unknown argument: {flag}")
        index += 1
    return http, host, port


def main() -> int:
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        print(_HELP, file=sys.stderr, end="")
        return 0
    try:
        http, host, port = _parse_args(argv)
    except ValueError as exc:
        print(f"clockify-mcp: {exc}", file=sys.stderr)
        return 2
    read_only = os.environ.get("CLOCKIFY_MCP_READ_ONLY", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    try:
        if read_only:
            from clockify_mcp.server import build_read_only_server as build_server
        else:
            from clockify_mcp.full_server import build_full_server as build_server
    except ImportError as exc:
        print(
            f"clockify-mcp: MCP dependencies missing ({exc}). "
            'Install with: uv add "clockify-python-115[mcp]"',
            file=sys.stderr,
        )
        return 1
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    try:
        server = build_server()
    except Exception as exc:  # configuration errors must not corrupt stdout
        print(f"clockify-mcp: {exc}", file=sys.stderr)
        return 1
    if http:
        server.run(transport="streamable-http", host=host, port=port)
    else:
        server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
