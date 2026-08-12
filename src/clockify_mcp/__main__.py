"""Console entry point for the Clockify MCP server (stdio)."""

import sys


def main() -> int:
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(
            "clockify-mcp: read-only Clockify MCP server over stdio.\n"
            "Environment: CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN (exactly one),\n"
            "optional CLOCKIFY_WORKSPACE_ID.",
            file=sys.stderr,
        )
        return 0
    try:
        from clockify_mcp.server import main as server_main
    except ImportError as exc:
        print(
            f"clockify-mcp: MCP dependencies missing ({exc}). "
            'Install with: uv add "clockify-python-115[mcp]"',
            file=sys.stderr,
        )
        return 1
    return server_main()


if __name__ == "__main__":
    sys.exit(main())
