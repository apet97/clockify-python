"""Generated from the corrected Clockify OpenAPI — do not edit by hand.

Source SHA-256: 38b6dcda5e6c1cf27c7f1f483c0cb77126bff28d59bedf5a6b6556c5016c3d94
Regenerate with scripts/import_openapi.py.
"""

from __future__ import annotations

from clockify.models.base import ClockifyResponseModel


class ImageUploadResponse(ClockifyResponseModel):
    name: str | None = None
    url: str | None = None
