"""Files resource: explicit methods over the file operations."""

from clockify.files import Upload
from clockify.models import ImageUploadResponse
from clockify.operations.files import FILES_UPLOAD_IMAGE
from clockify.resources._base import ResourceBase


class FilesResource(ResourceBase):
    async def upload_image(self, file: Upload) -> ImageUploadResponse:
        response = await self._call(FILES_UPLOAD_IMAGE, path={}, files={"file": file})
        return self._adapt(FILES_UPLOAD_IMAGE, response, ImageUploadResponse)
