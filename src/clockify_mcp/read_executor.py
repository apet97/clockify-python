"""The final read-only boundary, re-exported for the MCP layer.

The implementation lives beside the HTTP executor so the SDK can guarantee the
invariant without importing MCP code.
"""

from clockify._transport.executor import ReadOnlyExecutor

__all__ = ["ReadOnlyExecutor"]
