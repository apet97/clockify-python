"""Review finding F5: runtime annotation introspection must work everywhere.

Under PEP 649 (Python 3.14) a deferred annotation like ``-> list[X]``
evaluates in class scope, where a sibling method named ``list`` shadows the
builtin and `inspect.signature` raises. Every public resource method must
introspect cleanly on every supported interpreter; this file is also executed
against the installed wheel on Python 3.14.
"""

import importlib
import inspect

from clockify.operations.registry import BY_PUBLIC_METHOD


def test_inspect_signature_succeeds_on_all_168_public_methods() -> None:
    introspected: list[tuple[str, str]] = []
    resources = sorted({resource for resource, _ in BY_PUBLIC_METHOD})
    assert len(resources) == 29
    for resource in resources:
        module = importlib.import_module(f"clockify.resources.{resource}")
        classes = [
            cls
            for _, cls in inspect.getmembers(module, inspect.isclass)
            if cls.__name__.endswith("Resource") and cls.__module__ == module.__name__
        ]
        assert len(classes) == 1, f"expected one resource class in {resource}"
        (cls,) = classes
        for method_name, method in inspect.getmembers(cls, inspect.iscoroutinefunction):
            if method_name.startswith("_"):
                continue
            signature = inspect.signature(method)  # must not raise (F5)
            assert signature.parameters, f"{resource}.{method_name} lost its parameters"
            introspected.append((resource, method_name))
    assert sorted(introspected) == sorted(BY_PUBLIC_METHOD)
    assert len(introspected) == 168
