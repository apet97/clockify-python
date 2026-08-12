"""Live sacrificial-workspace tests (marker: live; excluded from ordinary runs).

Rules (docs/port + CLAUDE.md): unique run prefix, create-then-clean own
artifacts only, cleanup in finally preserving the primary failure, zero
residue, never print credentials.
"""

import os
import secrets
import uuid

import pytest

from clockify import ClockifyClient
from clockify.errors import ClockifyAPIError

pytestmark = pytest.mark.live

RUN_PREFIX = f"py115-{uuid.uuid4().hex[:8]}"


def require_env() -> tuple[str, str]:
    api_key = os.environ.get("CLOCKIFY_API_KEY")
    workspace_id = os.environ.get("CLOCKIFY_WORKSPACE_ID")
    if not api_key or not workspace_id:
        pytest.skip("CLOCKIFY_API_KEY / CLOCKIFY_WORKSPACE_ID not set")
    return api_key, workspace_id


@pytest.fixture()
async def client():  # type: ignore[no-untyped-def]
    api_key, workspace_id = require_env()
    async with ClockifyClient(api_key=api_key, workspace_id=workspace_id) as instance:
        yield instance


async def test_me_and_workspace_identity(client: ClockifyClient) -> None:
    me = await client.users.me()
    assert me.id
    workspace = await client.workspaces.get()
    # Confirm the configured workspace is the workspace actually reached.
    assert workspace.id == os.environ["CLOCKIFY_WORKSPACE_ID"]
    memberships = me.memberships or []
    assert me.default_workspace or me.active_workspace or memberships is not None


async def test_read_surface_smoke(client: ClockifyClient) -> None:
    tags = await client.tags.list(page=1, page_size=5)
    projects = await client.projects.list(page=1, page_size=5)
    users = await client.users.list(page=1, page_size=5)
    assert isinstance(tags, list)
    assert isinstance(projects, list)
    assert users, "sacrificial workspace should contain at least the owner"


async def test_last_page_header_on_tags_list(client: ClockifyClient) -> None:
    response = await client.raw.call(
        "getWorkspacesWorkspaceIdTags",
        path={"workspaceId": os.environ["CLOCKIFY_WORKSPACE_ID"]},
        query={"page": 1, "page_size": 1},
    )
    assert response.last_page in (True, False)  # header present and parseable


async def test_tag_create_read_back_delete_zero_residue(client: ClockifyClient) -> None:
    """The additive-write proof: create, read back directly, archive+delete, verify gone."""
    name = f"{RUN_PREFIX}-{secrets.token_hex(3)}"
    created_id: str | None = None
    try:
        created = await client.tags.create({"name": name})
        created_id = created.id
        assert created_id is not None
        assert created.name == name

        read_back = await client.tags.get(created_id)
        assert read_back.id == created_id

        # Full-replace update: archived must be resent (proven replacement risk).
        updated = await client.tags.update(created_id, {"name": name, "archived": True})
        assert updated.archived is True
    finally:
        if created_id is not None:
            deleted = await client.tags.delete(created_id)
            assert deleted.id == created_id

    assert created_id is not None
    with pytest.raises(ClockifyAPIError):
        await client.tags.get(created_id)

    residue = await client.tags.list(name=RUN_PREFIX, page=1, page_size=50)
    assert [t.id for t in residue] == [], "live run left residue"


async def test_project_archive_before_delete_lifecycle(client: ClockifyClient) -> None:
    """Proves the archive_before_delete prerequisite and cleans up completely."""
    name = f"{RUN_PREFIX}-proj-{secrets.token_hex(3)}"
    project_id: str | None = None
    try:
        created = await client.projects.create({"name": name})
        project_id = created.id

        # Direct delete of an active project must fail (lifecycle prerequisite).
        with pytest.raises(ClockifyAPIError):
            await client.projects.delete(project_id)
    finally:
        if project_id is not None:
            current = await client.projects.get(project_id)
            await client.projects.update(
                project_id,
                {
                    "name": current.name,
                    "archived": True,
                    "isPublic": bool(current.public),
                    "billable": bool(current.billable),
                },
            )
            deleted = await client.projects.delete(project_id)
            assert deleted.id == project_id

    remaining = await client.projects.list(name=RUN_PREFIX, page=1, page_size=50)
    assert [p.id for p in remaining] == [], "live run left residue"
