"""Curated read workflow registration (populated in Phase 7)."""

from mcp.server import MCPServer

from clockify.client import ClockifyClient


def register_workflows(server: MCPServer, client: ClockifyClient) -> None:
    """Register the five curated workflows. Populated in Phase 7."""
