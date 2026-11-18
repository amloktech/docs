// Node.js 22+. Run only with a dedicated Sandbox key. No dependencies required.
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
const base=new URL(process.env.AMLOK_API_BASE_URL || 'https://api.amlok.io');
assert.ok(['https://api.amlok.io','https://staging-api.amlok.io'].includes(base.origin),'Use a documented API origin');
assert.equal(base.pathname,'/','Do not include /v1 in the base URL');
const key=process.env.AMLOK_API_KEY;assert.ok(key?.startsWith('amlok_test_'),'Supply a dedicated Sandbox key through AMLOK_API_KEY');
const checks=[];
async function call(method,path,body,command=randomUUID(),authorization=key){
  for(let attempt=0;attempt<4;attempt++){
    const response=await fetch(base.origin+path,{method,headers:{authorization:'Bearer '+authorization,'content-type':'application/json','idempotency-key':command},body:body===undefined?undefined:JSON.stringify(body),redirect:'error',signal:AbortSignal.timeout(20000)});
    const value=await response.json();assert.ok(response.headers.get('x-request-id'),'Response must include a request ID');
    if(response.status===429){
      const seconds=Number(response.headers.get('retry-after'));assert.ok(Number.isFinite(seconds)&&seconds>0,'429 must include Retry-After');
      assert.equal(value.error.retryable,true);if(attempt===3||seconds>60)throw Error('Rate limit persists. Stop and retry later using the same command key.');
      await new Promise(r=>setTimeout(r,seconds*1000+Math.random()*250));continue;
    }
    return {status:response.status,body:value,headers:response.headers};
  }
}
function success(r,status){assert.equal(r.status,status,JSON.stringify({status:r.status,error:r.body.error?.code,requestId:r.headers.get('x-request-id')}));assert.equal(r.body.meta.environment,'sandbox');return r.body.data;}
const denied=await call('GET','/v1/borrowers',undefined,randomUUID(),'invalid');assert.equal(denied.status,401);checks.push('Invalid key rejected');
const config=success(await call('GET','/v1/configuration'),200);assert.ok(config.operational_profile.rate_limits.length);checks.push('Authenticated Sandbox configuration');
const command=randomUUID(), body={type:'business',business:{legal_name:'API client check '+command.slice(0,8),client_reference:'client-check-'+command,incorporation_country:'CA'}};
const first=success(await call('POST','/v1/borrowers',body,command),201);
const retried=await Promise.all([call('POST','/v1/borrowers',body,command),call('POST','/v1/borrowers',body,command)]);
for(const r of retried){assert.equal(success(r,201).id,first.id);assert.equal(r.headers.get('idempotency-replayed'),'true');}
checks.push('Concurrent retries return one borrower');
const receipt=success(await call('GET','/v1/request-receipts/lookup?operation_id=createBorrower&idempotency_key='+encodeURIComponent(command)),200);assert.equal(receipt.resource_id,first.id);checks.push('Accepted request recovered by command key');
const conflict=await call('POST','/v1/borrowers',{...body,business:{...body.business,legal_name:'Changed retry body'}},command);assert.equal(conflict.status,409);checks.push('Changed retry payload rejected');
assert.equal(success(await call('GET','/v1/borrowers/'+first.id),200).id,first.id);checks.push('Created borrower is retrievable');
console.log(JSON.stringify({passed:true,borrowerId:first.id,clientReference:body.business.client_reference,commandReference:command,checks,next:'Find this borrower in Console > Borrowers using the same workspace and Sandbox environment.'},null,2));
