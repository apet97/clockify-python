"""Full-surface MCP server: reads, workflows, and gated writes.

This is the default `clockify-mcp` build. The read-only build stays in
`clockify_mcp.server`, which never imports this module or anything under
`clockify_mcp.writes` — set ``CLOCKIFY_MCP_READ_ONLY=true`` to select it.

Every guarded write requires explicit user approval of the exact bound
request through the sealed request-state gate; routine writes execute
directly, single attempt, never retried.
"""

import httpx
from mcp.server import MCPServer
from mcp.server.request_state import RequestStateSecurity

from clockify._transport.auth import Credential
from clockify._transport.executor import HttpExecutor
from clockify.client import ClockifyClient
from clockify.config import DEFAULT_TIMEOUT
from clockify_mcp.context import ServerConfig, build_read_only_client
from clockify_mcp.prompts import register_prompts
from clockify_mcp.resources import register_resources
from clockify_mcp.tools import register_read_tools
from clockify_mcp.tools.orientation import register_orientation
from clockify_mcp.tools.workflows import register_workflows
from clockify_mcp.tools.write_workflows import register_write_workflows
from clockify_mcp.writes.gate import WriteGate
from clockify_mcp.writes.principal import AUDIENCE, new_process_secret
from clockify_mcp.writes.runner import WriteDeps, make_step_sender
from clockify_mcp.writes.tools import register_write_tools


def build_full_server(
    config: ServerConfig | None = None,
    *,
    read_client: ClockifyClient | None = None,
    write_http_client: httpx.AsyncClient | None = None,
) -> MCPServer:
    """Construct the full server. Client injection exists for tests."""
    resolved_config = config or ServerConfig.from_env()
    resolved_config.require_credential()
    if read_client is None:
        read_client = build_read_only_client(resolved_config)
    credential = Credential(
        api_key=resolved_config.api_key, addon_token=resolved_config.addon_token
    )
    process_secret = new_process_secret()
    gate = WriteGate(process_secret=process_secret, credential=credential)
    write_executor = HttpExecutor(
        client=write_http_client or httpx.AsyncClient(timeout=DEFAULT_TIMEOUT),
        credential=credential,
    )
    security = RequestStateSecurity(
        keys=[process_secret],
        ttl=300.0,
        bind_principal=lambda _ctx: gate.principal_id,
        audience=AUDIENCE,
    )
    server = MCPServer(
        name="clockify",
        instructions=(
            "Clockify tools: raw clockify_<resource>_<method> tools mirror the "
            "Clockify API; workflows compose them. Guarded writes require "
            "explicit user approval of the exact request; routine writes "
            "execute directly and are never retried."
        ),
        log_level="WARNING",
        request_state_security=security,
    )
    register_read_tools(server, read_client)
    register_workflows(server, read_client, resolved_config)
    register_orientation(server)
    register_resources(server)
    register_prompts(server)
    deps = WriteDeps(read_client=read_client, gate=gate, sender=make_step_sender(write_executor))
    register_write_tools(server, deps)
    register_write_workflows(server, deps)
    return server
