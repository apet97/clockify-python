# pyright: reportMissingParameterType=false, reportUnknownParameterType=false, reportAttributeAccessIssue=false, reportUnusedImport=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""Real spawned-stdio smoke: protocol integrity with stderr logging."""

import os
import sys

from mcp.client.stdio import StdioServerParameters, stdio_client

from mcp import ClientSession


async def test_stdio_lists_and_calls_a_tool() -> None:
    env = {
        **os.environ,
        "CLOCKIFY_API_KEY": "stdio-test-key",
        "CLOCKIFY_WORKSPACE_ID": "w-stdio",
    }
    env.pop("CLOCKIFY_ADDON_TOKEN", None)
    params = StdioServerParameters(command=sys.executable, args=["-m", "clockify_mcp"], env=env)
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        names = {tool.name for tool in tools.tools}
        assert len(names) == 65
        assert "clockify_tags_list" in names
        assert "clockify_doctor" in names
        # A tool that fails before network still answers over the protocol
        # (fake credentials; view_public rejects the format pre-network).
        result = await session.call_tool(
            "clockify_shared_reports_view_public",
            {"shared_report_id": "sr1", "format": "PDF"},
        )
        assert result.is_error
        assert "JSON or CSV" in result.content[0].text


async def test_stdio_missing_credentials_exits_with_stderr_message() -> None:
    import asyncio

    env = {k: v for k, v in os.environ.items() if not k.startswith("CLOCKIFY_")}
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "clockify_mcp",
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
    assert process.returncode == 1
    assert stdout == b""  # stdout stays protocol-clean even on failure
    assert b"CLOCKIFY_API_KEY" in stderr
