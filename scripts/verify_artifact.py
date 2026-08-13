"""Verify one built wheel from isolated installed environments."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path

from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent

from mcp import ClientSession

WORKFLOWS = {
    "clockify_status",
    "clockify_workspace_overview",
    "clockify_review_day",
    "clockify_review_week",
    "clockify_doctor",
}


def run(
    *args: str, check: bool = True, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, cwd=cwd, text=True, capture_output=True)


def inspect_names(names: set[str]) -> None:
    forbidden = (".env", ".mcp.json", "__pycache__", ".pyc", ".pytest_cache")
    bad = sorted(name for name in names if any(part in name for part in forbidden))
    if bad:
        raise AssertionError(f"artifact contains forbidden files: {bad}")


def inspect_wheel(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    inspect_names(names)
    required = {"clockify/py.typed", "clockify_mcp/py.typed"}
    missing = required - names
    if missing:
        raise AssertionError(f"wheel is missing PEP 561 markers: {sorted(missing)}")


def inspect_sdist(sdist: Path) -> None:
    with tarfile.open(sdist, "r:gz") as archive:
        names = {member.name for member in archive.getmembers()}
    inspect_names(names)
    required_suffixes = {
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "NOTICE.md",
        "docs/quickstart.md",
        "examples/sdk_list_projects.py",
    }
    missing = {
        suffix for suffix in required_suffixes if not any(name.endswith(suffix) for name in names)
    }
    if missing:
        raise AssertionError(f"sdist is missing release material: {sorted(missing)}")


def create_venv(path: Path, python_version: str) -> Path:
    run("uv", "venv", "--python", python_version, str(path))
    return path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def install(python: Path, requirement: str) -> None:
    run("uv", "pip", "install", "--python", str(python), requirement)


def prove_core_only(python: Path, expected_version: str) -> None:
    code = (
        "import importlib.metadata as m; "
        "from clockify import ClockifyClient; "
        "assert ClockifyClient.__name__ == 'ClockifyClient'; "
        f"assert m.version('clockify-python-115') == {expected_version!r}; "
        "assert not any(d.metadata['Name'].lower() == 'mcp' for d in m.distributions())"
    )
    run(str(python), "-I", "-c", code, cwd=python.parent)


def prove_sdist(sdist: Path, python_version: str, scratch: Path, expected_version: str) -> None:
    python = create_venv(scratch / "sdist", python_version)
    install(python, str(sdist))
    prove_core_only(python, expected_version)


def prove_console(python: Path) -> None:
    result = run(str(python), "-I", "-m", "clockify_mcp", "--help", cwd=python.parent)
    if result.stdout:
        raise AssertionError("clockify-mcp --help wrote non-protocol text to stdout")
    if "read-only Clockify MCP server" not in result.stderr:
        raise AssertionError("clockify-mcp --help did not describe the installed server")


def prove_installed_typing(python: Path, scratch: Path) -> None:
    checker = shutil.which("pyright")
    if checker is None:
        raise RuntimeError("pyright is required for installed typing proof")
    consumer = scratch / "invalid_consumer.py"
    consumer.write_text(
        "from clockify import ClockifyClient\n"
        "client: ClockifyClient\n"
        "async def invalid() -> None:\n"
        "    await client.projects.list(archived='not-a-bool')\n",
        encoding="utf-8",
    )
    result = run(
        checker,
        "--pythonpath",
        str(python),
        str(consumer),
        check=False,
        cwd=scratch,
    )
    output = result.stdout + result.stderr
    if result.returncode == 0 or "archived" not in output or "bool" not in output:
        raise AssertionError(f"installed typing did not reject the invalid call:\n{output}")


def installed_expected_tools(python: Path) -> set[str]:
    code = (
        "import json; "
        "from clockify.operations.model import ResponseKind; "
        "from clockify.operations.registry import ALL_OPERATIONS; "
        "print(json.dumps(sorted('clockify_' + op.resource + '_' + op.sdk_method "
        "for op in ALL_OPERATIONS if not op.semantics.mutates "
        "and op.response_kind is not ResponseKind.BYTES)))"
    )
    result = run(str(python), "-I", "-c", code, cwd=python.parent)
    return set(json.loads(result.stdout)) | WORKFLOWS


async def prove_stdio(python: Path) -> None:
    expected = installed_expected_tools(python)
    if len(expected - WORKFLOWS) != 60 or len(expected) != 65:
        raise AssertionError("installed operation registry does not define the 60/5/65 contract")
    env = {
        **os.environ,
        "CLOCKIFY_API_KEY": "artifact-test-key",
        "CLOCKIFY_WORKSPACE_ID": "artifact-workspace",
    }
    env.pop("CLOCKIFY_ADDON_TOKEN", None)
    params = StdioServerParameters(command=str(python), args=["-I", "-m", "clockify_mcp"], env=env)
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        initialized = await session.initialize()
        if initialized.server_info.name != "clockify":
            raise AssertionError("installed stdio server returned the wrong identity")
        tools = await session.list_tools()
        names = {tool.name for tool in tools.tools}
        if names != expected:
            raise AssertionError(
                f"installed tool contract mismatch: missing={sorted(expected - names)}, "
                f"extra={sorted(names - expected)}"
            )
        result = await session.call_tool(
            "clockify_shared_reports_view_public",
            {"shared_report_id": "artifact-report", "format": "PDF"},
        )
        first = result.content[0]
        if (
            not result.is_error
            or not isinstance(first, TextContent)
            or "JSON or CSV" not in first.text
        ):
            raise AssertionError("installed controlled pre-network rejection failed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path)
    parser.add_argument("--python", required=True, dest="python_version")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )
    expected_version = str(project["project"]["version"])
    wheel = args.wheel.resolve()
    inspect_wheel(wheel)
    sdist = args.sdist.resolve() if args.sdist else None
    if sdist is not None:
        inspect_sdist(sdist)
    with tempfile.TemporaryDirectory(prefix="clockify-artifact-") as temp:
        scratch = Path(temp)
        core_python = create_venv(scratch / "core", args.python_version)
        install(core_python, str(wheel))
        prove_core_only(core_python, expected_version)
        prove_installed_typing(core_python, scratch)

        mcp_python = create_venv(scratch / "mcp", args.python_version)
        install(mcp_python, f"{wheel}[mcp]")
        prove_console(mcp_python)
        asyncio.run(prove_stdio(mcp_python))
        if sdist is not None:
            prove_sdist(sdist, args.python_version, scratch, expected_version)
    print(f"verified {wheel.name} on Python {args.python_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
