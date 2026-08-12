"""Base classes for all generated Clockify models.

Requests reject unknown fields so misspelled or stale keys fail before a
destructive call. Responses keep additive unknown Clockify fields in
`model_extra` instead of discarding them.
"""

from pydantic import BaseModel, ConfigDict


class ClockifyRequestModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )


class ClockifyResponseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )
