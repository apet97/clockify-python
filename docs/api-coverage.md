# API coverage

The `0.1.0` release candidate contains:

| Contract | Count |
|---|---:|
| Operations | 168 |
| Resource classes | 29 |
| Explicit public methods | 168 |
| Semantic reads | 62 |
| GET reads | 49 |
| POST reads | 13 |
| Writes | 106 |
| Regular / reports / audit-log operations | 157 / 10 / 1 |
| Multipart operations | 3 |
| Reachable component-schema roots | 339 |
| MCP raw reads / workflows / total | 60 / 5 / 65 |
| Registered MCP writes | 0 |

`tests/contract/test_complete_surface.py` reconciles the runtime registry with
the corrected OpenAPI at the pinned sibling commit. The 168-case wiring suite
proves each public method's route and encoding.
