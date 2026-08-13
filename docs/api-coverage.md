# API coverage

Version `0.2.0` contains:

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
| MCP raw reads / raw writes / workflows / orientation / total | 60 / 104 / 18 / 4 / 186 |
| MCP write tiers | 5 routine time-entry tools + 7 routine workflows; all other writes gated |

`tests/contract/test_complete_surface.py` reconciles the runtime registry with
the corrected OpenAPI at the pinned sibling commit. The 168-case wiring suite
proves each public method's route and encoding.
