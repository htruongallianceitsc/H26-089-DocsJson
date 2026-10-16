"""Conservative join: FE route/API calls and BE endpoints; no speculative business requirements."""
import json, sys, re
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parent

def load(name):return json.loads((ROOT/name).read_text(encoding='utf8'))
def slug(s):return re.sub(r'[^A-Z0-9]+','-',s.upper()).strip('-') or 'UNKNOWN'
def merge(fe,be):
    out={'meta':{'schemaVersion':'1.0','name':'ShopNow','description':'Dự án được tổng hợp từ frontend và backend; cần xác minh nghiệp vụ','stack':{'frontend':fe['meta']['framework'],'backend':be['meta']['framework']}},'features':{},'screens':{},'apis':{},'entities':{},'businessRules':{}}
    report={'matchedApiCalls':[],'unmatchedFrontendCalls':[],'unmatchedBackendEndpoints':[],'featureCandidates':[],'unresolved':fe.get('unknowns',[])+be.get('unknowns',[]),'sourceRefs':{'frontend':fe['meta']['repo'],'backend':be['meta']['repo']}}
    entity_map={}
    for k,v in be.get('entities',{}).items():
        dest='E-'+slug(v.get('name',k))
        if dest in out['entities']:
            raise ValueError('Entity naming collision; explicit mapping required: '+dest)
        entity_map[k]=dest
        out['entities'][dest]={'name':v['name'],'fields':v.get('fields',{})}
    endpoint_map={}; sigmap={}
    for k,v in be.get('endpoints',{}).items():
        api='A-'+slug(k.removeprefix('EP-'))
        if api in out['apis']:raise ValueError('API ID collision: '+api)
        endpoint_map[k]=api
        out['apis'][api]={'name':v['name'],'method':v['method'],'path':v['path'],'entities':[entity_map[x] for x in v.get('entities',[]) if x in entity_map]}
        sig=(v['method'],v['path'])
        sigmap.setdefault(sig,[]).append(k)
    call_map={}
    matched_be=set()
    for k,v in fe.get('apiCalls',{}).items():
        sig=v['method'],v['path'];choices=sigmap.get(sig,[])
        if len(choices)==1:
            endpoint=choices[0];call_map[k]=endpoint_map[endpoint];matched_be.add(endpoint)
            report['matchedApiCalls'].append({'frontendCall':k,'backendEndpoint':endpoint,'projectApi':endpoint_map[endpoint],'basis':'exact HTTP method + path; verify base URL and reverse proxy'})
        else:
            report['unmatchedFrontendCalls'].append({'call':k,'method':v['method'],'path':v['path'],'reason':'not found' if not choices else 'ambiguous'})
    report['unmatchedBackendEndpoints']=[k for k in be.get('endpoints',{}) if k not in matched_be]
    for k,v in fe.get('screens',{}).items():
        out['screens'][k]={'name':v['name'],'route':v['route'],'apis':list(dict.fromkeys(call_map[x] for x in v.get('calls',[]) if x in call_map))}
    for k,v in be.get('businessRules',{}).items():
        out['businessRules']['BR-'+slug(k.removeprefix('RULE-'))]={'description':v['name'],'details':{'condition':v['condition'],'effect':v['effect']}}
    # FE features stay distinct. BE-only feature mappings need human review, unless exactly matching FE key.
    for k,v in fe.get('features',{}).items():
        ss=[x for x in v.get('screens',[]) if x in out['screens']]
        apis=list(dict.fromkeys(x for screen in ss for x in out['screens'][screen].get('apis',[])))
        entities=list(dict.fromkeys(x for api in apis for x in out['apis'][api].get('entities',[])))
        out['features'][k]={'name':v['name'],'status':v.get('status','planned'),'screens':ss,'apis':apis,'entities':entities}
    for k,v in be.get('features',{}).items():
        if k not in out['features']:
            report['featureCandidates'].append({'backendFeature':k,'name':v['name'],'endpointRefs':v.get('endpoints',[]),'action':'Review and map to existing FE feature or create new feature manually'})
        else:
            report['featureCandidates'].append({'backendFeature':k,'name':v['name'],'possibleFrontendFeature':k,'action':'Review semantic match; same ID is not sufficient evidence'})
    return out,report

def main():
 fe=load('frontend-blueprint.example.json');be=load('backend-blueprint.example.json')
 for kind,d in [('frontend',fe),('backend',be)]:
  Draft202012Validator(load(f'{kind}-blueprint.schema.json'),format_checker=FormatChecker()).validate(d)
 merged,report=merge(fe,be)
 Draft202012Validator(load('project-specification.schema.json'),format_checker=FormatChecker()).validate(merged)
 (ROOT/'project-merged.example.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (ROOT/'merge-report.example.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('PASS: FE and BE schemas; merged Project Level 3 schema; matches:',len(report['matchedApiCalls']))
if __name__=='__main__':main()
