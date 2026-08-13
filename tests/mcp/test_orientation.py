# pyright: reportMissingParameterType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false
"""Orientation tools, guide resources, and prompts on the full server."""

import json
from typing import Any

from mcp.types import TextContent

from clockify_mcp.context import ServerConfig
from clockify_mcp.full_server import build_full_server
from mcp import Client

from .conftest import MockBackend, make_mock_client

CONFIG = ServerConfig(api_key="test-key", addon_token=None, workspace_id="w-test")


def make_server():  # type: ignore[no-untyped-def]
    return build_full_server(CONFIG, read_client=make_mock_client(MockBackend()))


def data_of(result: Any) -> dict[str, Any]:
    if isinstance(result.structured_content, dict):
        return result.structured_content
    first = result.content[0]
    assert isinstance(first, TextContent)
    return json.loads(first.text)


async def test_orientation_tools_answer_without_network() -> None:
    async with Client(make_server()) as client:
        guide = data_of(await client.call_tool("clockify_tools_guide", {}))
        assert "write_doctrine" in guide
        plan = data_of(await client.call_tool("clockify_plan_change", {"intent": "track time"}))
        assert plan["plans"]["track time"][0]["tool"] == "clockify_start_work"
        unknown = data_of(await client.call_tool("clockify_plan_change", {"intent": "juggle"}))
        assert unknown["plan"] == [] and "known_intents" in unknown


async def test_operation_guide_answers_from_the_registry() -> None:
    async with Client(make_server()) as client:
        result = data_of(
            await client.call_tool("clockify_operation_guide", {"query": "deleteProject"})
        )
    top = result["operations"][0]
    assert top["operation_id"] == "deleteProject"
    assert top["method"] == "DELETE"
    assert top["mutates"] is True
    assert top["mcp_tool"] == "clockify_projects_delete"


async def test_resources_and_prompts_are_served() -> None:
    async with Client(make_server()) as client:
        resources = await client.list_resources()
        uris = {str(resource.uri) for resource in resources.resources}
        assert len(uris) == 6
        assert "clockify://guide/safety" in uris
        content = await client.read_resource("clockify://guide/axioms")
        assert "sacrificial" in content.contents[0].text
        prompts = await client.list_prompts()
        names = {prompt.name for prompt in prompts.prompts}
        assert names == {"clockify-getting-started", "clockify-workflow-plan"}
        prompt = await client.get_prompt("clockify-workflow-plan", {"goal": "invoice Acme"})
        assert "invoice Acme" in prompt.messages[0].content.text
