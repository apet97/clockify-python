"""Registry contract: exact counts and byte-exact agreement with the corrected OpenAPI.

The corrected spec is read from the sibling evidence repository. Count/uniqueness
tests never need it. The spec cross-check REQUIRES the evidence: a missing sibling
repository fails the test by default so completeness evidence cannot silently
disappear. Only an explicit CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE=1 permits an
intentional evidence-less run (one clearly explained skip). Release CI clones
apet97/clockify-ts-sdk at the pinned commit and never sets the opt-out.
"""

import keyword
import os
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from clockify.operations.model import RequestEncoding, ResponseKind, Service
from clockify.operations.registry import ALL_OPERATIONS, BY_ID, BY_PUBLIC_METHOD

SPEC_PATH = (
    Path(__file__).resolve().parents[2].parent
    / "clockify-ts-sdk"
    / "spec"
    / "corrected"
    / "clockify.corrected.openapi.yaml"
)
EVIDENCE_PIN = "d7091a44a1b95d4918fa17a7f9b174bf668a9136"
EVIDENCE_OPT_OUT = "CLOCKIFY_ALLOW_MISSING_TS_SDK_EVIDENCE"


def evidence_gate(spec_exists: bool, environ: dict[str, str]) -> str:
    """Decide how the spec cross-check runs: 'run', 'skip', or 'fail'.

    Missing evidence fails by default; only the explicit opt-out variable set to
    exactly "1" converts it into one clearly explained skip.
    """
    if spec_exists:
        return "run"
    if environ.get(EVIDENCE_OPT_OUT) == "1":
        return "skip"
    return "fail"


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
    verdict = evidence_gate(SPEC_PATH.exists(), dict(os.environ))
    if verdict == "skip":
        pytest.skip(
            "corrected OpenAPI evidence intentionally absent: "
            f"{EVIDENCE_OPT_OUT}=1 was set explicitly, so the spec cross-check "
            "is skipped for this run only. Never set this in development or "
            "release CI."
        )
    if verdict == "fail":
        pytest.fail(
            f"corrected OpenAPI evidence missing at {SPEC_PATH}. Clone "
            f"https://github.com/apet97/clockify-ts-sdk at commit {EVIDENCE_PIN} "
            "as a sibling directory of this repository, or — only for an "
            f"intentional evidence-less run — set {EVIDENCE_OPT_OUT}=1."
        )
    yaml = pytest.importorskip("yaml")
    spec = yaml.safe_load(SPEC_PATH.read_bytes())

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
