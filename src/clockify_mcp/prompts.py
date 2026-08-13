# pyright: reportUnusedFunction=false
"""Prompts served by the full server."""

from mcp.server import MCPServer


def register_prompts(server: MCPServer) -> None:
    @server.prompt(name="clockify-getting-started")
    def getting_started() -> str:
        """First-session orientation for the Clockify MCP server."""
        return (
            "You are connected to the Clockify MCP server.\n"
            "1. Call clockify_status to confirm the credential, workspace, and "
            "any running timer.\n"
            "2. Call clockify_tools_guide for the tool map and write doctrine.\n"
            "3. Read clockify://guide/which-tool to pick the right tool per task.\n"
            "Guarded writes preview the exact request and wait for the user's "
            "approval; never assume a write happened without a receipt."
        )

    @server.prompt(name="clockify-workflow-plan")
    def workflow_plan(goal: str) -> str:
        """Plan the tool calls for a Clockify goal before executing them."""
        return (
            f"Goal: {goal}\n"
            "Plan the Clockify tool calls before executing:\n"
            "1. Call clockify_plan_change with this goal's intent.\n"
            "2. List the reads first, then each write with its approval "
            "requirement.\n"
            "3. Execute step by step, reusing ids from previous receipts.\n"
            "4. Finish with a verification read (status or review_day)."
        )
