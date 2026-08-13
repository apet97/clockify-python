"""Request encoding boundary tests."""

import pytest

from clockify._transport.encode import serialize_query
from clockify.errors import ClockifyConfigurationError
from clockify.operations.model import Operation, QueryParameter, Service

REQUIRED_QUERY_OPERATION = Operation(
    operation_id="testRequiredQuery",
    resource="tests",
    sdk_method="required_query",
    http_method="GET",
    service=Service.REGULAR,
    path="/required-query",
    path_parameters=(),
    query_parameters=(QueryParameter("user_id", "userId", required=True),),
)


@pytest.mark.parametrize(
    "query",
    [
        {},
        {"user_id": None},
        {"user_id": []},
        {"user_id": ()},
        {"user_id": set()},
        {"user_id": frozenset()},
    ],
)
def test_required_query_parameter_must_have_a_value(query: dict[str, object]) -> None:
    with pytest.raises(ClockifyConfigurationError, match="required query parameter"):
        serialize_query(REQUIRED_QUERY_OPERATION, query)


def test_required_query_parameter_uses_its_wire_name() -> None:
    assert serialize_query(REQUIRED_QUERY_OPERATION, {"user_id": "u1"}) == (("userId", "u1"),)
