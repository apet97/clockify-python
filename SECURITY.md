# Security

Do not open a public issue that contains a credential, private workspace data,
or an unpatched vulnerability. Report a vulnerability through the repository's
[private security advisory form](https://github.com/apet97/clockify-python/security/advisories/new).

Current guarantees:

- The SDK sends exactly one `X-Api-Key` or `X-Addon-Token` value.
- It validates the final destination before it attaches the credential.
- It rejects caller-supplied `Host`, `:authority`, `X-Api-Key`, and
  `X-Addon-Token` headers before network access.
- It does not follow redirects.
- It sanitizes and bounds upstream error data before it constructs public errors.
- It never automatically retries a write.
- The default MCP server registers zero writes.

The dormant MCP write-safety code is not a public write capability. Do not
enable it until every condition in `docs/port/MCP_WRITE_SAFETY_PLAN.md` passes,
including independent review and approval-UI evidence from two intended hosts.
