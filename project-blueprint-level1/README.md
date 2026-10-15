# Frontend / Backend Source Blueprints (v1)

Purpose: separate source-derived facts from architecture reconciliation. Files `*.example.json` illustrate *hypothetical* ShopNow source trees; paths are examples, not verified repositories.

## Contents

- `frontend-blueprint.schema.json` + `.example.json`: routes/screens, components, forms/validation, API calls, UI states, UI flows, source evidence.
- `backend-blueprint.schema.json` + `.example.json`: controllers/endpoints, DTOs, services, entities/ORM, migrations, implemented rules, source evidence.
- `project-overview.schema.json`, `project-architecture.schema.json`, `project-specification.schema.json`: retained prior Level 1–3 project schemas, unchanged.
- `merge_blueprints.py`: minimal conservative merge script; outputs `project-merged.example.json` + `merge-report.example.json`.
- `test_blueprints.py`: schema and matching checks.

## Extraction policy

1. Extract only facts discoverable in the relevant repository; do not fabricate frontend screens from backend APIs or backend rules from frontend UI.
2. Record `evidence[].path` (and symbol/line when available), confidence `verified | inferred | unknown`; `verified` requires actual inspection.
3. `features` are *candidates inferred from implementation*, not automatically verified business requirements. A working-looking code path is not proof of `done` across product/UAT.
4. API matching is only a **candidate** if method and effective path match. Verify API base paths, versioning, proxies, dynamic parameters and environment settings before calling it confirmed.
5. Namespaced local IDs are valid within a source blueprint. Matching feature IDs across repositories is NOT a semantic contract.
6. Missing frontend/backend information belongs in `unknowns`; do not fill with guesses. Requirements, acceptance criteria and test cases cannot be treated as verified merely because code exists.
7. Keep external source references, confidence, component structure, DTOs, services and evidence in source blueprints. Project Level 3 cannot represent all these fields; the merge is deliberately lossy and the sources remain canonical evidence.
8. When a fact conflicts across repos, produce a reconciliation finding; do not silently overwrite. Never auto-merge two entity objects by name if collisions exist.

## Usage

```bash
python -m pip install jsonschema
python merge_blueprints.py
python test_blueprints.py
```

`merge_blueprints.py` currently uses the included example filenames and writes examples; it is an **illustrative implementation**, not a repository scanner or full production merge system. It only joins exact method+path and carries Frontend feature mappings forward; review report before acceptance. The merged JSON validates against the existing Level 3 schema, and uses only fields supported by it. Level 1/2 source JSON continues to work under the Level 3 project schema; source-specific JSON files have separate schemas because their object structure serves a different purpose.
