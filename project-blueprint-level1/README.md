# Project Blueprint — Level 2 Architecture Map

## Compatibility rules

- **Level 1 files are unchanged, byte for byte.** Their schema and example are shipped for reference.
- Level 2 keeps `meta.schemaVersion = "1.0"` and the identical `meta` shape and feature core fields.
- Level 2 extends feature objects only with **optional** `entities`, `apis`, `screens`, `dependsOn`, `businessRules`.
- Level 2 adds only **optional** root sections `entities`, `apis`, `screens`, `businessRules`.
- All valid Level 1 *data payloads* validate against the Level 2 schema. Existing `$schema` pointers may remain pointing at Level 1, but a Level 2 payload must change `$schema` to the Level 2 schema to enable editor validation of the new fields.
- The Level 1 schema intentionally **does not validate** Level 2-only properties (it sets `additionalProperties:false`). This is not backward data-compatibility in the reverse direction. Do not validate Level 2 documents using the Level 1 schema.
- Level numbers are validation profiles. `meta.schemaVersion` stays `1.0` because no existing field's meaning/representation changes; when the document contract eventually changes incompatibly, increment it deliberately and migrate.

## What Level 2 adds

Feature → Entity, API, Screen, Feature dependency, Business Rule; API → Entity; Screen → API; entity fields can remain short strings or use optional detailed definitions with `ref`.

A single source of truth is maintained in the typed references. A graph can be generated from the references; no duplicate `relations[]` is stored.

## Validation

```bash
pip install jsonschema
python validate_references.py project-architecture.example.json
python validate_references.py project-overview.example.json
```

JSON Schema validates shapes and ID formats, while `validate_references.py` additionally checks that referenced IDs exist. It does not detect multi-feature dependency cycles or prove runtime relationships from source code.
