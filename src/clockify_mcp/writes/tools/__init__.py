"""Write tool registration, one module per domain.

Mirrors ``clockify_mcp.tools``: every domain module defines
``register(server, deps)`` and is imported explicitly by name here.
``tests/mcp/test_full_surface.py`` asserts the resulting tool set, so a
missing or extra registration is a test failure.
"""

from mcp.server import MCPServer

from clockify_mcp.writes.runner import WriteDeps
from clockify_mcp.writes.tools import tags

_DOMAIN_MODULES = (tags,)


def register_write_tools(server: MCPServer, deps: WriteDeps) -> None:
    for module in _DOMAIN_MODULES:
        module.register(server, deps)
