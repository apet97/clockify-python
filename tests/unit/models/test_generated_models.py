"""Generated model surface: imports, rebuild, request/response contracts."""

import pydantic
import pytest
from pydantic import BaseModel

import clockify.models as models
from clockify.models.base import ClockifyRequestModel, ClockifyResponseModel


def model_classes() -> list[type[BaseModel]]:
    out: list[type[BaseModel]] = []
    for name in models.__all__:
        value = getattr(models, name)
        if isinstance(value, type) and issubclass(value, BaseModel):
            out.append(value)
    return out


def test_every_exported_model_is_complete() -> None:
    classes = model_classes()
    assert len(classes) > 280
    incomplete = [c.__name__ for c in classes if not c.__pydantic_complete__]
    assert incomplete == []


def test_request_models_reject_unknown_fields() -> None:
    with pytest.raises(pydantic.ValidationError):
        models.TagCreate.model_validate({"name": "x", "bogus": 1})


def test_response_models_preserve_unknown_fields() -> None:
    tag = models.TagDto.model_validate({"id": "t1", "name": "n", "futureField": True})
    assert tag.model_extra == {"futureField": True}


def test_aliases_round_trip_wire_names() -> None:
    tag = models.Tag.model_validate({"archived": False, "id": "t", "name": "n", "workspaceId": "w"})
    assert tag.workspace_id == "w"
    assert tag.model_dump(by_alias=True)["workspaceId"] == "w"


def test_leading_underscore_wire_field_is_a_real_model_field() -> None:
    row = models.SharedReportGroupRow.model_validate({"_id": "group-1"})
    assert row.id_ == "group-1"
    assert row.model_extra == {}
    assert row.model_dump(by_alias=True)["_id"] == "group-1"


def test_no_model_field_is_silently_any() -> None:
    """`Any` may appear only where the spec genuinely has an unconstrained node."""
    for cls in model_classes():
        for field_name, field in cls.model_fields.items():
            assert field.annotation is not None, (cls.__name__, field_name)


def test_every_generated_class_uses_a_clockify_base() -> None:
    for cls in model_classes():
        if cls in (ClockifyRequestModel, ClockifyResponseModel):
            continue
        assert issubclass(cls, ClockifyRequestModel | ClockifyResponseModel), cls.__name__


def test_datetime_fields_stay_strings() -> None:
    entry = models.TimeEntryDtoImplV1.model_validate(
        {
            "id": "e1",
            "timeInterval": {"start": "2026-08-12T10:00:00Z", "end": None, "duration": None},
        }
    )
    interval = entry.time_interval
    assert interval is not None
    assert interval.start == "2026-08-12T10:00:00Z"


def test_unset_optional_fields_are_excluded_from_wire_dump() -> None:
    body = models.TagCreate(name="only-name")
    assert body.model_dump(by_alias=True, exclude_unset=True) == {"name": "only-name"}


def test_workspace_survives_live_shapes() -> None:
    """Live evidence 2026-08-12: features contain enum values missing from the
    spec, and entityCreationPermissions values are plain strings."""
    workspace = models.Workspace.model_validate(
        {
            "id": "w1",
            "name": "Sandbox",
            "features": ["TIME_TRACKING", "WEEKLY_OVERTIME_CALCULATION_PERIOD"],
            "workspaceSettings": {
                "entityCreationPermissions": {
                    "whoCanCreateProjectsAndClients": "ADMINS_AND_PROJECT_MANAGERS",
                    "whoCanCreateTags": "EVERYONE",
                    "whoCanCreateTasks": "EVERYONE",
                }
            },
        }
    )
    assert workspace.id == "w1"
