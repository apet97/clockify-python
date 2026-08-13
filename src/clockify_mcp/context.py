"""Restricted server context: configuration plus the read-only Clockify client."""

import os
from dataclasses import dataclass

import httpx

from clockify._transport.auth import Credential
from clockify._transport.executor import HttpExecutor
from clockify.client import ClockifyClient
from clockify.config import DEFAULT_TIMEOUT
from clockify.errors import ClockifyConfigurationError
from clockify_mcp.read_executor import ReadOnlyExecutor


@dataclass(frozen=True, slots=True)
class ServerConfig:
    """Read from the environment; never logs credential values."""

    api_key: str | None
    addon_token: str | None
    workspace_id: str | None

    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            api_key=os.environ.get("CLOCKIFY_API_KEY") or None,
            addon_token=os.environ.get("CLOCKIFY_ADDON_TOKEN") or None,
            workspace_id=os.environ.get("CLOCKIFY_WORKSPACE_ID") or None,
        )

    def require_credential(self) -> None:
        if bool(self.api_key) == bool(self.addon_token):
            raise ClockifyConfigurationError(
                "set exactly one of CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN"
            )


def build_read_only_client(config: ServerConfig) -> ClockifyClient:
    """A ClockifyClient whose every call passes the ReadOnlyExecutor boundary.

    No Clockify request happens here; construction is network-free.
    """
    config.require_credential()
    credential = Credential(api_key=config.api_key, addon_token=config.addon_token)
    http_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
    executor = ReadOnlyExecutor(HttpExecutor(client=http_client, credential=credential))
    return ClockifyClient(
        workspace_id=config.workspace_id, http_client=http_client, _executor=executor
    )
