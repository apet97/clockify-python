# Live tests

`tests/live/` runs against a sacrificial Clockify workspace only. Never point it
at a customer workspace.

```bash
export CLOCKIFY_API_KEY=…           # exactly one credential
export CLOCKIFY_WORKSPACE_ID=…      # sacrificial workspace
uv run pytest -q -m live
```

Rules the suite follows (and any new live test must follow):

1. Confirm the configured workspace is the workspace actually reached.
2. Resolve the current user via the API; no user IDs in source.
3. One unique run prefix (`py115-<random>`); every created entity carries it.
4. Create prerequisites in-run, capture returned IDs, clean up in `finally`;
   a cleanup failure is an additional failure, never a replacement error.
5. Apply proven lifecycle prerequisites before deletion (archive/DONE/pending).
6. Never mass-delete by broad filter — exact created IDs only.
7. After the run, query the prefix and require zero residue.
8. Plan/permission rejections are environment evidence, not SDK bugs.

Ordinary CI never runs live tests (`-m "not live"`).
