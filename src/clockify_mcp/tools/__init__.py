"""Raw read tool registration (populated in Phase 6)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient


def register_read_tools(server: MCPServer, client: ClockifyClient) -> None:
    """Register the 60 raw read tools. Populated in Phase 6."""
