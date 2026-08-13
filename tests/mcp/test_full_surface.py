"""Full-server surface contract: names, risk coverage, read-only separation."""

import subprocess
import sys

from clockify_mcp.context import ServerConfig
from clockify_mcp.full_server import build_full_server
from clockify_mcp.risk import GUARDED_RISKS, RISK_BY_TOOL, Risk
from clockify_mcp.server import build_read_only_server

from .conftest import MockBackend, make_mock_client

CONFIG = ServerConfig(api_key="test-key", addon_token=None, workspace_id="w-test")


def full_server():  # type: ignore[no-untyped-def]
    return build_full_server(CONFIG, read_client=make_mock_client(MockBackend()))


async def registered_names(server) -> set[str]:  # type: ignore[no-untyped-def]
    return {tool.name for tool in await server.list_tools()}


async def test_full_server_matches_risk_map_exactly() -> None:
    assert await registered_names(full_server()) == set(RISK_BY_TOOL)


async def test_read_only_server_has_no_write_tools() -> None:
    server = build_read_only_server(CONFIG, client=make_mock_client(MockBackend()))
    names = await registered_names(server)
    assert len(names) == 65
    write_names = {name for name, risk in RISK_BY_TOOL.items() if risk is not Risk.READ}
    assert names.isdisjoint(write_names)


async def test_guarded_tools_are_not_marked_read_only() -> None:
    server = full_server()
    for tool in await server.list_tools():
        risk = RISK_BY_TOOL[tool.name]
        assert tool.annotations is not None
        if risk is Risk.READ:
            assert tool.annotations.read_only_hint is True
        else:
            assert tool.annotations.read_only_hint is False
        if risk in GUARDED_RISKS:
            assert tool.annotations.destructive_hint is (risk is Risk.DESTRUCTIVE)


def test_read_only_server_import_loads_no_write_modules() -> None:
    """The structural boundary: `clockify_mcp.server` never pulls in writes."""
    code = (
        "import sys, clockify_mcp.server, clockify_mcp.tools;"
        "bad = [m for m in sys.modules if m.startswith('clockify_mcp.writes')"
        " or m == 'clockify_mcp.full_server'];"
        "raise SystemExit(1 if bad else 0)"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert proc.returncode == 0, proc.stderr.decode()
