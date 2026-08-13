"""Focused release-documentation and packaging invariants."""

import tomllib
from pathlib import Path

from clockify.config import USER_AGENT

ROOT = Path(__file__).parents[2]


def test_readme_states_independence_and_read_only_mcp_contract() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(readme.split())
    assert "independent community project" in readme
    assert "not affiliated with, endorsed by, or sponsored by CAKE.com or Clockify" in normalized
    assert "registers zero writes" in readme
    quickstart = readme.split("## Read-only SDK quickstart", 1)[1].split("## MCP quickstart", 1)[0]
    assert ".create(" not in quickstart
    assert ".update(" not in quickstart
    assert ".delete(" not in quickstart


def test_release_files_and_pep561_markers_exist() -> None:
    required = [
        "CONTRIBUTING.md",
        "NOTICE.md",
        "docs/quickstart.md",
        "docs/sdk-guide.md",
        "docs/mcp.md",
        "docs/api-coverage.md",
        "examples/sdk_list_projects.py",
        "examples/sdk_iterate_time_entries.py",
        "examples/sdk_generate_report.py",
        "examples/sdk_create_tag_sacrificial.py",
        "examples/sdk_error_handling.py",
        "examples/mcp_config.example.json",
        "src/clockify/py.typed",
        "src/clockify_mcp/py.typed",
    ]
    assert [path for path in required if not (ROOT / path).is_file()] == []


def test_active_guide_has_no_completed_campaign_continuation() -> None:
    guide = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Next exact action" not in guide
    assert "continue from" not in guide.lower()
    assert not (ROOT / "CLAUDE_CODE_CLOCKIFY_PYTHON_IMPLEMENTATION_PROMPT.md").exists()


def test_ci_verifies_the_built_artifact_on_every_supported_python() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert '["3.11", "3.12", "3.13", "3.14"]' in workflow
    assert "actions/download-artifact" in workflow
    assert "scripts/verify_artifact.py" in workflow
    assert "wheels=(dist/*.whl)" in workflow
    assert "sdists=(dist/*.tar.gz)" in workflow
    assert "${#wheels[@]} -eq 1" in workflow
    assert "${#sdists[@]} -eq 1" in workflow
    assert "clockify_python_115-0.1.0" not in workflow


def test_user_agent_version_matches_project_version() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert f"clockify-python-115/{project['project']['version']}" == USER_AGENT


def test_release_docs_use_the_project_version_and_private_security_route() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = str(project["project"]["version"])
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    quickstart = (ROOT / "docs/quickstart.md").read_text(encoding="utf-8")
    coverage = (ROOT / "docs/api-coverage.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")

    assert f"Documentation version: `{version}`" in readme
    assert f"clockify-python-115=={version}" in quickstart
    assert f"clockify-python-115[mcp]=={version}" in quickstart
    assert f"Version `{version}` contains" in coverage
    assert "https://github.com/apet97/clockify-python/security/advisories/new" in security
