# Quickstart

## 1. Install

For version `0.1.2`, create an environment and install the package:

```bash
uv venv .venv
uv pip install --python .venv/bin/python clockify-python-115==0.1.2
```

Install `clockify-python-115[mcp]==0.1.2` when you need the MCP server.

## 2. Configure one credential

```bash
export CLOCKIFY_API_KEY="..."
export CLOCKIFY_WORKSPACE_ID="..."
```

Use `CLOCKIFY_ADDON_TOKEN` instead of `CLOCKIFY_API_KEY` for an add-on token.
Do not configure both.

## 3. Run a read

```bash
.venv/bin/python examples/sdk_list_projects.py
```

The example reads the current user and active projects. It does not mutate the workspace.

## 4. Run MCP

Install the `[mcp]` extra, copy `examples/mcp_config.example.json` into your
host configuration, and replace the executable path. Keep credentials in the
host environment or a secret store. Do not put a credential in the JSON file.
