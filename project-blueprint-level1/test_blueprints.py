from merge_blueprints import load,merge
from jsonschema import Draft202012Validator,FormatChecker

def test():
 f=load('frontend-blueprint.example.json');b=load('backend-blueprint.example.json')
 for kind,value in [('frontend',f),('backend',b)]:
  Draft202012Validator(load(kind+'-blueprint.schema.json'),format_checker=FormatChecker()).validate(value)
 p,r=merge(f,b)
 Draft202012Validator(load('project-specification.schema.json'),format_checker=FormatChecker()).validate(p)
 assert len(r['matchedApiCalls'])==2
 assert p['screens']['S-CHECKOUT']['apis']==['A-ORDER-CREATE']
 assert p['features']['F-ORDER']['entities']==['E-ORDER','E-PRODUCT']
 b['endpoints']['EP-ORDER-CREATE']['path']='/api/v2/orders'
 _,r=merge(f,b)
 assert any(i['call']=='CALL-ORDER-CREATE' for i in r['unmatchedFrontendCalls'])
 print('PASS: 2 source schemas, project L3 schema, exact match, mismatch detection')
if __name__=='__main__':test()
