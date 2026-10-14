import copy,json,pathlib
from jsonschema import Draft202012Validator,FormatChecker
from validate_references_level3 import base # module executes default example validation
s=json.loads((base/'project-specification.schema.json').read_text())
Draft202012Validator.check_schema(s)
v=Draft202012Validator(s,format_checker=FormatChecker())
for name in ['project-overview.example.json','project-architecture.example.json','project-specification.example.json']:
    obj=json.loads((base/name).read_text());assert v.is_valid(obj),name;print('SCHEMA PASS',name)
obj=json.loads((base/'project-specification.example.json').read_text())
for title,edit in [('invalid status',lambda o:o['features']['F-ORDER'].update(status='unknown')),('invalid API method',lambda o:o['apis']['A-LOGIN'].update(method='FETCH')),('unknown top-level',lambda o:o.update(garbage=1))]:
    bad=copy.deepcopy(obj);edit(bad);assert not v.is_valid(bad),title;print('NEGATIVE PASS',title)
print('ALL COMPATIBILITY TESTS PASSED')
