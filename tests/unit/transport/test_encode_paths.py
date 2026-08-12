"""Path-argument boundary: dot segments must never reach URL construction.

Review finding F4: `"."` and `".."` survived `render_path`, and httpx
normalizes dot segments, so a request could target a different endpoint on
the same service. The literal dot values are rejected at the rendering
boundary; everything else keeps its exact percent-encoded form.
"""

import pytest

from clockify._transport.encode import render_path
from clockify.errors import ClockifyConfigurationError
from clockify.operations.registry import BY_ID

OP = BY_ID["getWorkspacesWorkspaceIdTags"]


@pytest.mark.parametrize("value", [".", ".."])
def test_dot_segments_rejected(value: str) -> None:
    with pytest.raises(ClockifyConfigurationError, match="path parameter"):
        render_path(OP, {"workspaceId": value})


def test_normal_id_renders() -> None:
    assert render_path(OP, {"workspaceId": "64ad1305c701cc5be7c26fe4"}) == (
        "/workspaces/64ad1305c701cc5be7c26fe4/tags"
    )


def test_embedded_slash_is_percent_encoded() -> None:
    # A slash can never create a new path segment.
    assert render_path(OP, {"workspaceId": "a/b"}) == "/workspaces/a%2Fb/tags"
    assert render_path(OP, {"workspaceId": "../x"}) == "/workspaces/..%2Fx/tags"


def test_encoded_dot_like_input_stays_inert() -> None:
    # Pre-encoded input is data, not structure: "%2e%2e" is re-quoted, so the
    # server sees the literal characters, never a traversal segment.
    assert render_path(OP, {"workspaceId": "%2e%2e"}) == "/workspaces/%252e%252e/tags"
    # Three dots are a valid opaque id, not a dot segment.
    assert render_path(OP, {"workspaceId": "..."}) == "/workspaces/.../tags"
