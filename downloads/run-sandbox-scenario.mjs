import { randomUUID } from 'node:crypto';
const base=process.env.AMLOK_API_BASE_URL,key=process.env.AMLOK_API_KEY;
if(!base||!key?.startsWith('amlok_test_'))throw Error('Set AMLOK_API_BASE_URL and a Sandbox AMLOK_API_KEY.');
const call=async(path,body,commandKey=randomUUID())=>{
 for(let attempt=0;attempt<6;attempt++){
  const response=await fetch(base.replace(/\/$/,'')+path,{method:body===undefined?'GET':'POST',headers:{Authorization:'Bearer '+key,...(body===undefined?{}:{'Content-Type':'application/json','Idempotency-Key':commandKey})},body:body===undefined?undefined:JSON.stringify(body),redirect:'error',signal:AbortSignal.timeout(30000)});
  if(response.status===429||response.status===503){await new Promise(r=>setTimeout(r,Math.max(1,Number(response.headers.get('retry-after'))||5)*1000));continue;}
  const result=await response.json();if(!response.ok)throw Error(`${response.status}: ${result.error?.message||'Request failed'}`);return result.data;
 }
 throw Error('Retry budget exhausted. Retry the command with the same idempotency key.');
};
const catalog=await call('/v1/sandbox/catalog');
const endpoint=process.env.AMLOK_SANDBOX_ENDPOINT_ID;
let run=await call('/v1/sandbox/runs',{scenario_id:process.env.AMLOK_SANDBOX_SCENARIO||'healthy',fixture_id:process.env.AMLOK_SANDBOX_FIXTURE||catalog.businesses[0].id,catalog_version:catalog.version,...(endpoint?{endpoint_id:endpoint,send_webhooks:true}:{})});
console.log('Run:',run.id);
const deadline=Date.now()+15*60*1000;
while(['queued','running'].includes(run.status)&&Date.now()<deadline){await new Promise(r=>setTimeout(r,2000));run=await call('/v1/sandbox/runs/'+run.id);}
console.log(JSON.stringify({id:run.id,status:run.status,error:run.error,assertions:run.assertions,resources:run.resources},null,2));
if(run.status!=='completed')process.exitCode=1;
