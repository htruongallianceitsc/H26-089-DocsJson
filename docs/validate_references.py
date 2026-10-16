#!/usr/bin/env python3
"""Validate Level 2 JSON Schema and cross-catalog ID existence (standard JSON Schema cannot do dynamic ID lookups)."""
import json, pathlib, sys
from jsonschema import Draft202012Validator, FormatChecker
base=pathlib.Path(__file__).resolve().parent
schema=json.loads((base/'project-architecture.schema.json').read_text(encoding='utf-8'))
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base/'project-architecture.example.json'
data=json.loads(path.read_text(encoding='utf-8'))
errors=[f'{list(e.path)}: {e.message}' for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(data)]
sections={'entities':'E','apis':'A','screens':'S','dependsOn':'F','businessRules':'BR'}
for feature_id,feature in data.get('features',{}).items():
    for key,prefix in sections.items():
        catalog='features' if key=='dependsOn' else key
        for ref in feature.get(key,[]):
            if ref not in data.get(catalog,{}): errors.append(f'features.{feature_id}.{key}: missing {ref} in {catalog}')
            if key=='dependsOn' and ref==feature_id: errors.append(f'features.{feature_id}: cannot depend on itself')
for api_id,api in data.get('apis',{}).items():
    for ref in api.get('entities',[]):
        if ref not in data.get('entities',{}): errors.append(f'apis.{api_id}.entities: missing {ref}')
for screen_id,screen in data.get('screens',{}).items():
    for ref in screen.get('apis',[]):
        if ref not in data.get('apis',{}): errors.append(f'screens.{screen_id}.apis: missing {ref}')
for ent_id,entity in data.get('entities',{}).items():
    for name,field in entity.get('fields',{}).items():
        if isinstance(field,dict) and 'ref' in field and field['ref'] not in data.get('entities',{}): errors.append(f'entities.{ent_id}.fields.{name}.ref: missing {field["ref"]}')
if errors:
    print('FAIL\n'+'\n'.join('- '+e for e in errors)); sys.exit(1)
print(f'PASS: {path.name} (schema + reference existence)')
