# Direction A release-candidate receipt

## Release mode

`0.1.0` local release candidate. The Python SDK is complete. The default MCP
server is read-only. No push, tag, release, or publication has occurred.

## Contract

- 168 operations, 29 resources, and 168 explicit public methods.
- 62 reads: 49 GET and 13 POST.
- 106 SDK writes.
- 157 regular, 10 reports, and one audit-log operation.
- Three multipart operations and 339 reachable schema roots.
- 60 raw MCP reads, five workflows, 65 total tools, zero registered writes.

## Final gates and artifacts

The release-candidate code is commit `e755016`. Final evidence-only documents
follow that commit.

- Ruff check and format check: pass.
- Pyright strict mode: 0 errors.
- Offline suite: 459 passed, 6 deselected.
- Authorized live sacrificial suite: 6 passed, 459 deselected, zero residue.
- Installed wheel: pass on Python 3.11, 3.12, 3.13, and 3.14.
- Installed sdist: pass on Python 3.14.
- Official MCP client: initialize, exact 65 tools, exact 60 raw reads plus five
  workflows, zero writes, controlled pre-network rejection, protocol-only stdout.
- Mutant campaign: all 15 required mutants killed in one disposable worktree.
- Deterministic build: both wheel and sdist matched byte-for-byte across two builds.

Artifact hashes:

- wheel: `ea85c93fb6108d828576fea9eec6433f48e8ae8210df4d33d317d971d4dfb60c`
- sdist: `259afe53aa3bfc1480211664b21bfd7f535db4f7293edc24899d350a8440905d`

## Live proof

The current remediation ran the marked suite against the configured
sacrificial workspace. It proved identity, read behavior, tag and project
lifecycle cleanup, one explicitly approved dormant write-gate path, and zero
residue. This does not enable or register MCP writes in the default server.

## Owner and external actions

1. Rotate or revoke the credential identified by the internal value-aware scan.
2. Remove the stale shell-profile value.
3. Optionally expire reflogs and run Git garbage collection only after rotation
   and after preserving required recovery history.
4. Create or select the GitHub remote and protect the release environment.
5. Configure the PyPI Trusted Publisher for `.github/workflows/release.yml` and
   environment `pypi`.
6. Push, tag, publish, and verify the immutable public artifacts.
7. Before any MCP write registration, obtain independent review and approval-UI
   evidence from two intended hosts.

The next legitimate in-repository milestone is a separately approved MCP write
wave or a versioned maintenance change. There is no completed-campaign
continuation task.
