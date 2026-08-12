"""Public-method wiring: member_profiles (2 operations)."""

from clockify.models import MemberProfileDtoV1

from ._harness import assert_wired, make_client

COVERED = {
    "getMemberProfile",
    "updateMemberProfile",
}

PROFILE_JSON = {"email": "a@example.com", "name": "Ana", "weekStart": "MONDAY"}


async def test_get() -> None:
    client, capture = make_client(json=PROFILE_JSON)
    profile = await client.member_profiles.get("u1", workspace_id="w1")
    assert_wired(
        capture,
        resource="member_profiles",
        method="get",
        url="https://api.clockify.me/api/v1/workspaces/w1/member-profile/u1",
    )
    assert isinstance(profile, MemberProfileDtoV1)
    assert profile.name == "Ana"


async def test_get_default_workspace() -> None:
    client, capture = make_client(json=PROFILE_JSON)
    await client.member_profiles.get("u1")
    assert "/workspaces/w-default/member-profile/u1" in str(capture.request.url)


async def test_update_sends_exact_body() -> None:
    client, capture = make_client(json=PROFILE_JSON)
    profile = await client.member_profiles.update(
        "u1", {"name": "Ana", "weekStart": "MONDAY"}, workspace_id="w1"
    )
    assert_wired(
        capture,
        resource="member_profiles",
        method="update",
        url="https://api.clockify.me/api/v1/workspaces/w1/member-profile/u1",
    )
    assert capture.sent_json() == {"name": "Ana", "weekStart": "MONDAY"}
    assert isinstance(profile, MemberProfileDtoV1)
