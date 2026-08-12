"""WriteGate: the only path from an approved preview to an ExecutionPermit."""

import time
from typing import Any

from clockify._transport.auth import Credential
from clockify_mcp.writes.canonical import digest_of
from clockify_mcp.writes.nonce_store import ExecutionPermit, InMemoryNonceStore
from clockify_mcp.writes.plan import PreparedWrite, WritePlan, arguments_digest_of
from clockify_mcp.writes.principal import derive_key, derive_principal_id


class WriteGate:
    """Owns principal derivation, pending issuance, and atomic consumption."""

    def __init__(
        self,
        *,
        process_secret: bytes,
        credential: Credential,
        store: InMemoryNonceStore | None = None,
    ) -> None:
        self._process_secret = process_secret
        self.principal_id = derive_principal_id(process_secret, credential)
        self.store = store or InMemoryNonceStore()

    async def prepare(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        workspace_id: str | None,
        plan: WritePlan,
    ) -> PreparedWrite:
        """Issue (or re-fetch) the pending confirmation for these exact arguments."""
        arguments_digest = arguments_digest_of(arguments)
        key = derive_key(
            self._process_secret, self.principal_id, tool_name, arguments_digest, workspace_id
        )
        return await self.store.get_or_issue(
            key=key,
            principal_id=self.principal_id,
            tool_name=tool_name,
            workspace_id=workspace_id,
            arguments_digest=arguments_digest,
            plan=plan,
        )

    async def consume(self, prepared: PreparedWrite) -> ExecutionPermit:
        """Atomically consume; called only after an explicit user approval."""
        return await self.store.consume(
            nonce=prepared.nonce,
            principal_id=prepared.principal_id,
            tool_name=prepared.tool_name,
            arguments_digest=prepared.arguments_digest,
            plan_digest=prepared.plan_digest,
        )

    async def cancel(self, prepared: PreparedWrite) -> None:
        await self.store.cancel(prepared.nonce)


def is_approved(elicitation_result: Any) -> bool:
    """True only for an accepted elicitation whose decision is literally 'approve'."""
    action = getattr(elicitation_result, "action", None)
    if action != "accept":
        return False
    data = getattr(elicitation_result, "data", None)
    return getattr(data, "decision", None) == "approve"


def fingerprint_state(fields: dict[str, Any]) -> str:
    """Canonical precondition fingerprint of the minimum relevant fields."""
    return digest_of(fields)


def now() -> float:
    return time.monotonic()
