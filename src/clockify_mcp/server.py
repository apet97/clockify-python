"""Read-only MCP server construction.

Building the server performs no Clockify request. Stdout carries only MCP
protocol traffic; logs go to stderr. No write module is imported here — the
default server is structurally read-only, not read-only-by-flag.
"""

import logging
import sys

from mcp.server import MCPServer

from clockify.client import ClockifyClient
from clockify_mcp.context import ServerConfig, build_read_only_client
from clockify_mcp.tools import register_read_tools
from clockify_mcp.tools.workflows import register_workflows

logger = logging.getLogger("clockify_mcp")


def build_read_only_server(
    config: ServerConfig | None = None,
    *,
    client: ClockifyClient | None = None,
) -> MCPServer:
    """Construct the read-only server. `client` injection exists for tests."""
    resolved_config = config or ServerConfig.from_env()
    if client is None:
        client = build_read_only_client(resolved_config)
    server = MCPServer(
        name="clockify",
        instructions=(
            "Read-only Clockify tools. Raw clockify_<resource>_<method> tools mirror "
            "the Clockify API; clockify_status/workspace_overview/review_day/"
            "review_week/doctor are curated workflows. No tool can modify Clockify data."
        ),
        log_level="WARNING",
    )
    register_read_tools(server, client)
    register_workflows(server, client, resolved_config)
    return server


def main() -> int:
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    try:
        server = build_read_only_server()
    except Exception as exc:  # configuration errors must not corrupt stdout
        print(f"clockify-mcp: {exc}", file=sys.stderr)
        return 1
    server.run(transport="stdio")
    return 0
