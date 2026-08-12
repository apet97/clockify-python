"""Process-local principal binding for stdio.

The principal is derived from the configured Clockify credential via HMAC with
a per-process secret; the credential value itself is never stored or exposed.
A restart changes the secret, invalidating pending confirmations — the safe
stdio behavior.
"""

import hmac
import secrets

from clockify._transport.auth import Credential

_CONTEXT = b"clockify-principal-v1"
AUDIENCE = "clockify-python-mcp"


def new_process_secret() -> bytes:
    return secrets.token_bytes(32)


def derive_principal_id(process_secret: bytes, credential: Credential) -> str:
    header: dict[str, str] = {}
    credential.attach(header)
    ((scheme, secret_value),) = header.items()
    material = _CONTEXT + b"\x00" + scheme.encode() + b"\x00" + secret_value.encode()
    return hmac.new(process_secret, material, "sha256").hexdigest()


def derive_key(
    process_secret: bytes, principal_id: str, tool_name: str, arguments_digest: str
) -> str:
    """Stable pending-record key across MRTR rounds; reveals no secret."""
    material = b"\x00".join(
        (
            b"clockify-write-key-v1",
            principal_id.encode(),
            tool_name.encode(),
            arguments_digest.encode(),
        )
    )
    return hmac.new(process_secret, material, "sha256").hexdigest()
