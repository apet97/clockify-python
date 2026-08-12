"""Importer fixture tests: supported constructs render; unsupported fail closed."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

_SPEC_PATH = Path(__file__).resolve().parents[2] / "scripts" / "import_openapi.py"
_spec = importlib.util.spec_from_file_location("import_openapi", _SPEC_PATH)
assert _spec and _spec.loader
_module = importlib.util.module_from_spec(_spec)
sys.modules["import_openapi"] = _module
_spec.loader.exec_module(_module)

Importer = _module.Importer
UnsupportedSchema = _module.UnsupportedSchema
snake = _module.snake


def make_importer(schemas: dict[str, Any]) -> Any:
    spec = {"components": {"schemas": schemas}, "paths": {}}
    return Importer(spec, source_sha="test")


class TestSnake:
    def test_camel_case(self) -> None:
        assert snake("workspaceId") == "workspace_id"

    def test_kebab_case(self) -> None:
        assert snake("page-size") == "page_size"

    def test_acronym_run(self) -> None:
        assert snake("ccEmails") == "cc_emails"
        assert snake("XYZValue") == "xyz_value"

    def test_python_keyword_gets_suffix(self) -> None:
        assert snake("from") == "from_"


class TestRenderType:
    def test_primitives(self) -> None:
        imp = make_importer({})
        assert imp.render_type({"type": "string"}, "p") == "str"
        assert imp.render_type({"type": "integer", "format": "int64"}, "p") == "int"
        assert imp.render_type({"type": "number", "format": "double"}, "p") == "float"
        assert imp.render_type({"type": "boolean"}, "p") == "bool"

    def test_binary_string_is_bytes(self) -> None:
        imp = make_importer({})
        assert imp.render_type({"type": "string", "format": "binary"}, "p") == "bytes"

    def test_datetime_stays_str(self) -> None:
        imp = make_importer({})
        assert imp.render_type({"type": "string", "format": "date-time"}, "p") == "str"

    def test_nullable(self) -> None:
        imp = make_importer({})
        assert imp.render_type({"type": "string", "nullable": True}, "p") == "str | None"

    def test_array(self) -> None:
        imp = make_importer({})
        assert imp.render_type({"type": "array", "items": {"type": "string"}}, "p") == "list[str]"

    def test_inline_string_enum_is_literal(self) -> None:
        imp = make_importer({})
        assert imp.render_type({"type": "string", "enum": ["A", "B"]}, "p") == "Literal['A', 'B']"

    def test_ref(self) -> None:
        imp = make_importer({})
        node = {"$ref": "#/components/schemas/Other"}
        assert imp.render_type(node, "p") == "Other"

    def test_nullable_ref(self) -> None:
        imp = make_importer({})
        node = {"$ref": "#/components/schemas/Other", "nullable": True}
        assert imp.render_type(node, "p") == "Other | None"

    def test_typed_additional_properties(self) -> None:
        imp = make_importer({})
        node = {"type": "object", "additionalProperties": {"type": "integer"}}
        assert imp.render_type(node, "p") == "dict[str, int]"

    def test_one_of_union(self) -> None:
        imp = make_importer({})
        node = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        assert imp.render_type(node, "p") == "str | int"

    def test_array_without_items_fails_closed(self) -> None:
        imp = make_importer({})
        with pytest.raises(UnsupportedSchema, match="array without items"):
            imp.render_type({"type": "array"}, "path/here")

    def test_unknown_construct_fails_closed(self) -> None:
        imp = make_importer({})
        with pytest.raises(UnsupportedSchema, match="unsupported object keys"):
            imp.render_type({"type": "object", "patternProperties": {}}, "p")

    def test_non_string_enum_fails_closed(self) -> None:
        imp = make_importer({})
        with pytest.raises(UnsupportedSchema):
            imp.render_type({"type": "integer", "enum": [1, 2]}, "p")


class TestRenderRoot:
    def test_object_request_model(self) -> None:
        imp = make_importer(
            {
                "Req": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "clientId": {"type": "string"},
                    },
                }
            }
        )
        source, is_class = imp.render_root("Req", request_only=True)
        assert is_class
        assert "class Req(ClockifyRequestModel):" in source
        assert "name: str" in source
        assert 'client_id: str | None = Field(default=None, alias="clientId")' in source

    def test_object_response_model(self) -> None:
        imp = make_importer({"Resp": {"type": "object", "properties": {"id": {"type": "string"}}}})
        source, _ = imp.render_root("Resp", request_only=False)
        assert "class Resp(ClockifyResponseModel):" in source

    def test_enum_root_becomes_literal_alias(self) -> None:
        imp = make_importer({"Color": {"type": "string", "enum": ["RED", "BLUE"]}})
        source, is_class = imp.render_root("Color", request_only=False)
        assert not is_class
        assert "Color = Literal['RED', 'BLUE']" in source

    def test_array_root_becomes_list_alias(self) -> None:
        imp = make_importer(
            {
                "Items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/Thing"},
                },
                "Thing": {"type": "object", "properties": {}},
            }
        )
        source, is_class = imp.render_root("Items", request_only=False)
        assert not is_class
        assert "Items = list[Thing]" in source

    def test_all_of_merges_properties(self) -> None:
        imp = make_importer(
            {
                "Base": {
                    "type": "object",
                    "required": ["a"],
                    "properties": {"a": {"type": "string"}},
                },
                "Combined": {
                    "allOf": [
                        {"$ref": "#/components/schemas/Base"},
                        {"type": "object", "properties": {"b": {"type": "integer"}}},
                    ]
                },
            }
        )
        source, _ = imp.render_root("Combined", request_only=False)
        assert "class Combined(" in source
        assert "a: str" in source
        assert "b: int | None = None" in source

    def test_inline_object_synthesizes_named_class(self) -> None:
        imp = make_importer(
            {
                "Doc": {
                    "type": "object",
                    "properties": {
                        "auditMetadata": {
                            "type": "object",
                            "properties": {"actor": {"type": "string"}},
                        }
                    },
                }
            }
        )
        source, _ = imp.render_root("Doc", request_only=False)
        assert "audit_metadata: DocAuditMetadata | None" in source
        joined = "".join(imp.pending_inline)
        assert "class DocAuditMetadata(" in joined

    def test_case_collision_gets_upper_suffix(self) -> None:
        imp = make_importer(
            {
                "Fields": {
                    "type": "object",
                    "properties": {"rtl": {"type": "boolean"}, "RTL": {"type": "boolean"}},
                }
            }
        )
        source, _ = imp.render_root("Fields", request_only=False)
        assert "rtl: bool | None = None" in source
        assert 'rtl_upper: bool | None = Field(default=None, alias="RTL")' in source
