"""Registry contract: exact counts and agreement with the pinned corrected OpenAPI.

The corrected spec is read from the pinned Git object in the sibling evidence
repository. Count/uniqueness tests never need it. The spec cross-check REQUIRES
the evidence: a missing sibling repository fails the test by default so
completeness evidence cannot silently disappear. Only an explicit
CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE=1 permits an intentional evidence-less run
(one clearly explained skip). Release CI clones apet97/clockify-ts-sdk at the
pinned commit and never sets the opt-out.
"""

import importlib
import inspect
import keyword
import os
import subprocess
import types
from collections import Counter
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

import pytest

from clockify.operations.model import RequestEncoding, ResponseKind, Service
from clockify.operations.registry import ALL_OPERATIONS, BY_ID, BY_PUBLIC_METHOD
from clockify.resources._base import ResourceBase

EVIDENCE_REPO = Path(__file__).resolve().parents[2].parent / "clockify-ts-sdk"
EVIDENCE_SPEC_PATH = "spec/corrected/clockify.corrected.openapi.yaml"
EVIDENCE_PIN = "d7091a44a1b95d4918fa17a7f9b174bf668a9136"
EVIDENCE_OPT_OUT = "CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE"


def evidence_gate(evidence_exists: bool, environ: dict[str, str]) -> str:
    """Decide how the spec cross-check runs: 'run', 'skip', or 'fail'.

    Missing evidence fails by default; only the explicit opt-out variable set to
    exactly "1" converts it into one clearly explained skip.
    """
    if evidence_exists:
        return "run"
    if environ.get(EVIDENCE_OPT_OUT) == "1":
        return "skip"
    return "fail"


def _load_corrected_spec() -> dict[str, Any]:
    verdict = evidence_gate(EVIDENCE_REPO.is_dir(), dict(os.environ))
    if verdict == "skip":
        pytest.skip(
            "corrected OpenAPI evidence intentionally absent: "
            f"{EVIDENCE_OPT_OUT}=1 was set explicitly, so the spec cross-check "
            "is skipped for this run only. Never set this in development or "
            "release CI."
        )
    if verdict == "fail":
        pytest.fail(
            f"corrected OpenAPI evidence repository missing at {EVIDENCE_REPO}. Clone "
            f"https://github.com/apet97/clockify-ts-sdk at commit {EVIDENCE_PIN} "
            "as a sibling directory of this repository, or — only for an "
            f"intentional evidence-less run — set {EVIDENCE_OPT_OUT}=1.",
            pytrace=False,
        )

    object_name = f"{EVIDENCE_PIN}:{EVIDENCE_SPEC_PATH}"
    try:
        result = subprocess.run(
            ["git", "-C", str(EVIDENCE_REPO), "show", object_name],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        pytest.fail(
            f"cannot read pinned corrected OpenAPI object {object_name}: "
            "the git executable was not found.",
            pytrace=False,
        )
    except subprocess.CalledProcessError:
        pytest.fail(
            f"cannot read pinned corrected OpenAPI object {object_name} from "
            f"{EVIDENCE_REPO}. Confirm that the sibling repository contains "
            f"commit {EVIDENCE_PIN}.",
            pytrace=False,
        )

    yaml = pytest.importorskip("yaml")
    return yaml.safe_load(result.stdout)


def test_evidence_gate_states() -> None:
    assert evidence_gate(True, {}) == "run"
    assert evidence_gate(True, {EVIDENCE_OPT_OUT: "1"}) == "run"
    assert evidence_gate(False, {}) == "fail"
    assert evidence_gate(False, {EVIDENCE_OPT_OUT: "0"}) == "fail"
    assert evidence_gate(False, {EVIDENCE_OPT_OUT: ""}) == "fail"
    assert evidence_gate(False, {EVIDENCE_OPT_OUT: "1"}) == "skip"


def test_exactly_168_operations() -> None:
    assert len(ALL_OPERATIONS) == 168
    assert len(BY_ID) == 168
    assert len(BY_PUBLIC_METHOD) == 168


def test_semantic_read_write_split() -> None:
    reads = [op for op in ALL_OPERATIONS if not op.semantics.mutates]
    writes = [op for op in ALL_OPERATIONS if op.semantics.mutates]
    assert len(reads) == 62
    assert len(writes) == 106
    read_verbs = Counter(op.http_method for op in reads)
    assert read_verbs == {"GET": 49, "POST": 13}


def test_service_routing_counts() -> None:
    counts = Counter(op.service for op in ALL_OPERATIONS)
    assert counts == {Service.REGULAR: 157, Service.REPORTS: 10, Service.AUDIT_LOG: 1}


def test_exactly_three_multipart_operations() -> None:
    multipart = sorted(
        op.operation_id for op in ALL_OPERATIONS if op.request_encoding is RequestEncoding.MULTIPART
    )
    assert multipart == ["createExpense", "updateExpense", "uploadImage"]


def test_29_resources_and_no_python_keywords() -> None:
    resources = {op.resource for op in ALL_OPERATIONS}
    assert len(resources) == 29
    for op in ALL_OPERATIONS:
        assert not keyword.iskeyword(op.sdk_method), op.operation_id
        assert op.sdk_method.isidentifier(), op.operation_id


def test_binary_reads_are_the_two_known_sdk_only_operations() -> None:
    binary_reads = sorted(
        op.operation_id
        for op in ALL_OPERATIONS
        if not op.semantics.mutates and op.response_kind is ResponseKind.BYTES
    )
    assert binary_reads == ["downloadExpenseReceipt", "exportInvoice"]


def test_path_parameters_match_path_template() -> None:
    import re

    for op in ALL_OPERATIONS:
        in_path = tuple(re.findall(r"\{(\w+)\}", op.path))
        assert in_path == op.path_parameters, op.operation_id


def test_mutating_operations_never_paginate() -> None:
    for op in ALL_OPERATIONS:
        if op.semantics.mutates:
            assert op.pagination is None, op.operation_id


def test_registry_agrees_with_corrected_openapi() -> None:
    spec = _load_corrected_spec()

    service_by_url = {
        "https://api.clockify.me/api/v1": Service.REGULAR,
        "https://reports.api.clockify.me/v1": Service.REPORTS,
        "https://auditlog-api.api.clockify.me/v1": Service.AUDIT_LOG,
    }
    spec_ops: dict[str, tuple[str, str, Service, dict[str, Any]]] = {}
    for path, item in spec["paths"].items():
        for verb in ("get", "post", "put", "patch", "delete"):
            if verb not in item:
                continue
            node = item[verb]
            servers = node.get("servers") or spec.get("servers")
            assert servers is not None, node["operationId"]
            service = service_by_url[servers[0]["url"]]
            spec_ops[node["operationId"]] = (verb.upper(), path, service, node)

    assert set(spec_ops) == set(BY_ID)

    for op in ALL_OPERATIONS:
        verb, path, service, node = spec_ops[op.operation_id]
        assert op.http_method == verb, op.operation_id
        assert op.path == path, op.operation_id
        assert op.service == service, op.operation_id

        # Query wire names: registry must not invent parameters absent from the
        # corrected spec + manifest-stamped pagination params.
        spec_query = set()
        for parameter in node.get("parameters", []):
            if "$ref" in parameter:
                kind, name = parameter["$ref"].split("/")[2:4]
                parameter = spec["components"][kind][name]
            if parameter.get("in") == "query":
                spec_query.add(parameter["name"])
        registry_query = {q.wire_name for q in op.query_parameters}
        extra = registry_query - spec_query - {"page", "page-size"}
        assert not extra, (op.operation_id, extra)

        has_body = "requestBody" in node
        if op.request_encoding is RequestEncoding.NONE:
            assert not has_body or not node["requestBody"].get("required", True), op.operation_id
        # createExpense/updateExpense are multipart per manifest despite the spec
        # omitting their request bodies; only they may disagree with the spec here.
        elif not has_body:
            assert op.operation_id in ("createExpense", "updateExpense"), op.operation_id


def _resolve_component(spec: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    while "$ref" in node:
        resolved: Any = spec
        for part in node["$ref"][2:].split("/"):
            resolved = resolved[part]
        node = resolved
    return node


def _annotation_shape(annotation: Any) -> str:
    origin = get_origin(annotation)
    if origin in (Union, types.UnionType):
        shapes = {
            _annotation_shape(item) for item in get_args(annotation) if item is not type(None)
        }
        assert len(shapes) == 1, annotation
        return shapes.pop()
    if origin is list:
        return "array"
    if origin is Literal:
        literal_types = {type(value) for value in get_args(annotation)}
        assert len(literal_types) == 1, annotation
        return _annotation_shape(literal_types.pop())
    if annotation is str:
        return "string"
    if annotation is bool:
        return "boolean"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    raise AssertionError(f"unsupported public query annotation {annotation!r}")


def _resource_method(resource: str, method: str) -> Any:
    module = importlib.import_module(f"clockify.resources.{resource}")
    candidates = [
        value
        for value in vars(module).values()
        if inspect.isclass(value)
        and value is not ResourceBase
        and issubclass(value, ResourceBase)
        and value.__module__ == module.__name__
        and hasattr(value, method)
    ]
    assert len(candidates) == 1, (resource, method, candidates)
    return getattr(candidates[0], method)


def test_query_contract_matches_corrected_openapi_and_public_signatures() -> None:
    spec = _load_corrected_spec()
    spec_operations: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for item in spec["paths"].values():
        for verb in ("get", "post", "put", "patch", "delete"):
            if verb in item:
                node = item[verb]
                spec_operations[node["operationId"]] = (item, node)

    for operation in ALL_OPERATIONS:
        item, node = spec_operations[operation.operation_id]
        query_parameters: dict[str, dict[str, Any]] = {}
        for raw_parameter in [*item.get("parameters", []), *node.get("parameters", [])]:
            parameter = _resolve_component(spec, raw_parameter)
            if parameter.get("in") == "query":
                query_parameters[parameter["name"]] = parameter

        registry_parameters = {
            parameter.wire_name: parameter for parameter in operation.query_parameters
        }
        assert set(registry_parameters) == set(query_parameters), operation.operation_id

        method = _resource_method(operation.resource, operation.sdk_method)
        signature = inspect.signature(method)
        annotations = get_type_hints(method)
        for wire_name, query_parameter in query_parameters.items():
            registry_parameter = registry_parameters[wire_name]
            public_parameter = signature.parameters[registry_parameter.python_name]
            schema = _resolve_component(spec, query_parameter["schema"])

            assert registry_parameter.required is bool(query_parameter.get("required")), (
                operation.operation_id,
                wire_name,
            )
            assert (
                _annotation_shape(annotations[registry_parameter.python_name]) == schema["type"]
            ), (
                operation.operation_id,
                wire_name,
            )

            if registry_parameter.required:
                expected_default = schema.get("default", inspect.Parameter.empty)
                assert public_parameter.default == expected_default, (
                    operation.operation_id,
                    wire_name,
                )
