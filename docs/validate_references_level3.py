#!/usr/bin/env python3
"""Validate L1/L2/L3 documents against L3 schema and check graph references."""
import json, pathlib, sys
from jsonschema import Draft202012Validator, FormatChecker
base=pathlib.Path(__file__).resolve().parent
schema=json.loads((base/'project-specification.schema.json').read_text(encoding='utf8'))
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base/'project-specification.example.json'
data=json.loads(path.read_text(encoding='utf8'))
errors=[f'{".".join(map(str,e.absolute_path))}: {e.message}' for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(data)]
def ref(catalog,value,location):
    if value not in data.get(catalog,{}): errors.append(f'{location}: missing {value} in {catalog}')
def refs(obj,key,catalog,loc):
    for v in obj.get(key,[]): ref(catalog,v,f'{loc}.{key}')
for fid,f in data.get('features',{}).items():
    loc=f'features.{fid}'
    for k,c in [('entities','entities'),('apis','apis'),('screens','screens'),('dependsOn','features'),('businessRules','businessRules'),('requirements','requirements'),('acceptanceCriteria','acceptanceCriteria'),('flows','flows'),('testCases','testCases')]:refs(f,k,c,loc)
    if fid in f.get('dependsOn',[]): errors.append(f'{loc}: self-dependency')
for a,obj in data.get('apis',{}).items():refs(obj,'entities','entities',f'apis.{a}')
for sid,obj in data.get('screens',{}).items():
    loc=f'screens.{sid}';refs(obj,'apis','apis',loc)
    for action in obj.get('spec',{}).get('actions',[]):
        if 'api' in action:ref('apis',action['api'],loc+'.spec.actions')
for eid,obj in data.get('entities',{}).items():
    loc=f'entities.{eid}';refs(obj,'databaseSpecs','databaseSpecs',loc)
    for name,field in obj.get('fields',{}).items():
        if isinstance(field,dict) and 'ref' in field:ref('entities',field['ref'],loc+'.fields.'+name)
for rid,obj in data.get('requirements',{}).items():
    loc=f'requirements.{rid}';refs(obj,'acceptanceCriteria','acceptanceCriteria',loc);refs(obj,'businessRules','businessRules',loc)
    if 'feature' in obj:ref('features',obj['feature'],loc+'.feature')
for acid,obj in data.get('acceptanceCriteria',{}).items():
    loc=f'acceptanceCriteria.{acid}';refs(obj,'testCases','testCases',loc)
    if 'requirement' in obj:ref('requirements',obj['requirement'],loc+'.requirement')
for flid,obj in data.get('flows',{}).items():
    loc=f'flows.{flid}'
    if 'feature' in obj:ref('features',obj['feature'],loc+'.feature')
    step_ids=[step['id'] for step in obj.get('steps',[]) if 'id' in step]
    if len(step_ids)!=len(set(step_ids)): errors.append(loc+': duplicate flow step id')
    for step in obj.get('steps',[]):
        sloc=loc+'.steps.'+step.get('id','?')
        for k,c in [('screen','screens'),('api','apis')]:
            if k in step: ref(c,step[k],sloc+'.'+k)
        for nxt in step.get('next',[]):
            if nxt not in step_ids:errors.append(sloc+': missing next step '+nxt)
for tcid,obj in data.get('testCases',{}).items():
    loc=f'testCases.{tcid}';refs(obj,'requirements','requirements',loc);refs(obj,'acceptanceCriteria','acceptanceCriteria',loc)
for dbid,obj in data.get('databaseSpecs',{}).items():
    if 'entity' in obj:ref('entities',obj['entity'],f'databaseSpecs.{dbid}.entity')
for bid,obj in data.get('businessRules',{}).items():
    refs(obj,'acceptanceCriteria','acceptanceCriteria','businessRules.'+bid);refs(obj,'testCases','testCases','businessRules.'+bid)
if errors:
    print('FAIL: '+path.name+'\n'+'\n'.join(' - '+x for x in errors));sys.exit(1)
print('PASS: '+path.name+' (schema + references + flow steps)')
