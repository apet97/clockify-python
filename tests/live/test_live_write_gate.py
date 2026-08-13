# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false
"""Safety Phase G live proof: one gated write against the sacrificial workspace.

The full production path runs for real: plan build via ReadOnlyExecutor,
deterministic preview, elicitation approval, atomic nonce consumption,
ControlledWriteExecutor dispatch, direct read-back — then SDK cleanup to zero
residue.
"""

import json as jsonlib
import os
import uuid
from typing import Any

import pytest
from mcp.types import ElicitResult

from clockify import ClockifyClient
from clockify_mcp.context import ServerConfig
from clockify_mcp.full_server import build_full_server
from mcp import Client

pytestmark = pytest.mark.live


def result_json(call_result: Any) -> Any:
    if call_result.structured_content is not None:
        return call_result.structured_content
    return jsonlib.loads(call_result.content[0].text)


async def test_gated_tag_create_live_zero_residue() -> None:
    api_key = os.environ.get("CLOCKIFY_API_KEY")
    workspace_id = os.environ.get("CLOCKIFY_WORKSPACE_ID")
    if not api_key or not workspace_id:
        pytest.skip("CLOCKIFY_API_KEY / CLOCKIFY_WORKSPACE_ID not set")

    name = f"py115-gate-{uuid.uuid4().hex[:8]}"
    config = ServerConfig(api_key=api_key, addon_token=None, workspace_id=workspace_id)
    server = build_full_server(config)
    previews: list[str] = []

    async def approve(context: Any, params: Any) -> ElicitResult:
        previews.append(params.message)
        return ElicitResult(action="accept", content={"decision": "approve"})

    created_id: str | None = None
    try:
        async with Client(server, elicitation_callback=approve) as client:
            result = await client.call_tool("clockify_tags_create", {"name": name})
        payload = result_json(result)
        assert payload["state"] == "reconciled", payload
        created_id = payload["data"]["id"]
        assert payload["data"]["name"] == name
        # The human-facing preview showed the exact bound body before dispatch.
        assert f'"name":"{name}"' in previews[0]
    finally:
        async with ClockifyClient(api_key=api_key, workspace_id=workspace_id) as sdk:
            if created_id is not None:
                deleted = await sdk.tags.delete(created_id)
                assert deleted.id == created_id
            residue = await sdk.tags.list(name="py115-gate-", page=1, page_size=50)
            assert [t.id for t in residue] == [], "gated live write left residue"
