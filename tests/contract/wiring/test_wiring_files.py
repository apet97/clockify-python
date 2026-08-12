"""Public-method wiring: files (1 operation)."""

from clockify.files import Upload
from clockify.models import ImageUploadResponse

from ._harness import assert_wired, make_client

COVERED = {"uploadImage"}


async def test_upload_image_multipart() -> None:
    client, capture = make_client(
        json={"name": "shot.png", "url": "https://img.clockify.me/shot.png"}
    )
    result = await client.files.upload_image(
        Upload(filename="shot.png", content=b"\x89PNG", content_type="image/png")
    )
    assert_wired(
        capture,
        resource="files",
        method="upload_image",
        url="https://api.clockify.me/api/v1/file/image",
    )
    assert capture.request.headers["Content-Type"].startswith("multipart/form-data")
    body = capture.request.content
    assert b'name="file"; filename="shot.png"' in body
    assert b"\x89PNG" in body
    assert isinstance(result, ImageUploadResponse)
    assert result.url == "https://img.clockify.me/shot.png"


async def test_upload_image_no_workspace_in_path() -> None:
    client, capture = make_client(json={"name": "a.png", "url": "u"}, workspace_id=None)
    await client.files.upload_image(Upload(filename="a.png", content=b"x"))
    assert "/workspaces/" not in str(capture.request.url)
