"""Exactly-one-credential invariant."""

from clockify.errors import ClockifyConfigurationError


class Credential:
    """Holds the single configured Clockify credential.

    The secret never appears in `repr`/`str`; it is read only at header-attach
    time, after final-host validation.
    """

    __slots__ = ("_secret", "header_name")

    def __init__(self, *, api_key: str | None = None, addon_token: str | None = None) -> None:
        if bool(api_key) == bool(addon_token):
            raise ClockifyConfigurationError("configure exactly one of api_key or addon_token")
        self.header_name = "X-Api-Key" if api_key else "X-Addon-Token"
        self._secret = api_key or addon_token or ""

    def attach(self, headers: dict[str, str]) -> None:
        headers[self.header_name] = self._secret

    def sensitive_values(self) -> tuple[str, ...]:
        """Return values that the internal error boundary must redact."""
        return (self._secret,)

    def __repr__(self) -> str:
        return f"Credential(header_name={self.header_name!r}, secret=<redacted>)"
