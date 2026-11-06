"""Conservative structural compatibility check for two AMLOK OpenAPI files.
Usage: python check-contract-compatibility.py previous.json candidate.json
Exit 1 means review is required; this does not validate business semantics.
"""
import json
import sys

ANNOTATIONS={'description','summary','title','example','examples','externalDocs','x-codeSamples'}

def compare(old,new):
    issues=[]
    def walk(a,b,path):
        if isinstance(a,dict) and isinstance(b,dict):
            for key,value in a.items():
                if key in ANNOTATIONS or key.startswith('x-'):
                    continue
                if key not in b:
                    issues.append(path+'/'+key+': removed');continue
                if key=='required' and set(value)<=set(b[key]):
                    additions=set(b[key])-set(value)
                    new_fields=set(b.get('properties',{}))-set(a.get('properties',{}))
                    if additions and (path.startswith('/request') or not additions<=new_fields):
                        issues.append(path+'/required: stricter requirement')
                    continue
                walk(value,b[key],path+'/'+key)
            # New constraints and security requirements can narrow an existing schema.
            for key in set(b)-set(a):
                if key in {'required','enum','const','pattern','minimum','maximum','minLength','maxLength','minItems','maxItems','additionalProperties','oneOf','anyOf','allOf','not','security'}:
                    issues.append(path+'/'+key+': new constraint')
        elif a!=b:
            issues.append(path+': changed')
    old_paths=old.get('paths',{});new_paths=new.get('paths',{})
    for path,methods in old_paths.items():
        for method,op in methods.items():
            candidate=new_paths.get(path,{}).get(method)
            if candidate is None:
                issues.append(method.upper()+' '+path+': removed');continue
            walk(op,candidate,'/operations/'+op.get('operationId',path))
    old_schemas=old.get('components',{}).get('schemas',{})
    new_schemas=new.get('components',{}).get('schemas',{})
    request_names=set()
    def request_refs(value):
        if isinstance(value,dict):
            if '$ref' in value:
                name=value['$ref'].split('/')[-1]
                if name in request_names:return
                request_names.add(name);request_refs(new_schemas.get(name,{}))
            for key,child in value.items():
                if key!='$ref':request_refs(child)
        elif isinstance(value,list):
            for child in value:request_refs(child)
    for methods in new_paths.values():
        for op in methods.values():
            request_refs(op.get('requestBody',{}));request_refs(op.get('parameters',[]))
    for name,schema in old_schemas.items():
        if name not in new_schemas:issues.append('/schemas/'+name+': removed')
        else:walk(schema,new_schemas[name],('/request' if name in request_names else '/response')+'/schemas/'+name)
    return issues

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: python check-contract-compatibility.py previous.json candidate.json')
    with open(sys.argv[1]) as stream:old=json.load(stream)
    with open(sys.argv[2]) as stream:new=json.load(stream)
    issues=compare(old,new)
    print(json.dumps({'structural_changes_requiring_review':issues,'semantic_review_required':True},indent=2))
    raise SystemExit(bool(issues))
