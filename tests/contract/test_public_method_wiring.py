"""Completeness of the public surface and the wiring suite itself."""

import importlib
import inspect
import pkgutil
from pathlib import Path

from clockify.operations.registry import ALL_OPERATIONS, BY_PUBLIC_METHOD

WIRING_DIR = Path(__file__).parent / "wiring"


def test_every_operation_has_a_public_resource_method() -> None:
    """168 methods exist with exact (resource, sdk_method) names — checked on classes,
    so no client construction or network is involved."""
    import clockify.resources as resources_pkg

    method_owner: dict[tuple[str, str], str] = {}
    for module_info in pkgutil.iter_modules(resources_pkg.__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"clockify.resources.{module_info.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if not cls.__name__.endswith("Resource") or cls.__module__ != module.__name__:
                continue
            for method_name, _member in inspect.getmembers(cls, inspect.iscoroutinefunction):
                if not method_name.startswith("_"):
                    method_owner[(module_info.name, method_name)] = cls.__name__

    missing = [key for key in BY_PUBLIC_METHOD if key not in method_owner]
    assert missing == [], f"operations without public methods: {missing}"

    extra = [key for key in method_owner if key not in BY_PUBLIC_METHOD]
    assert extra == [], f"public methods without operation records: {extra}"


def test_client_exposes_all_29_resources() -> None:
    from clockify.client import ClockifyClient

    resources = {op.resource for op in ALL_OPERATIONS}
    parameters = inspect.signature(ClockifyClient.__init__).parameters
    assert "api_key" in parameters and "addon_token" in parameters
    source = inspect.getsource(ClockifyClient.__init__)
    for resource in resources:
        assert f"self.{resource} =" in source, f"client missing resource {resource}"


def test_wiring_suite_covers_all_168_operations() -> None:
    covered: set[str] = set()
    for test_file in sorted(WIRING_DIR.glob("test_wiring_*.py")):
        module_name = f"tests.contract.wiring.{test_file.stem}"
        module = importlib.import_module(module_name)
        assert hasattr(module, "COVERED"), f"{test_file.name} lacks COVERED"
        covered |= module.COVERED

    all_ids = {op.operation_id for op in ALL_OPERATIONS}
    missing = sorted(all_ids - covered)
    assert missing == [], f"operations without wiring tests: {missing}"
    unknown = sorted(covered - all_ids)
    assert unknown == [], f"wiring tests claim unknown operations: {unknown}"
