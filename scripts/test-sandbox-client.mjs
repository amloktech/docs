import test from 'node:test';
import assert from 'node:assert/strict';
import { SandboxScenarioClient, runSandboxScenario } from '../downloads/run-sandbox-scenario.mjs';
const json=(data,status=200,headers={})=>new Response(JSON.stringify(status<300?{data,meta:{environment:'sandbox'}}:data),{status,headers:{'Content-Type':'application/json',...headers}});

test('lost command response retries the same saved identity and resumed execution never creates a second run',async()=>{
  const state={},commands=[],persisted=[];let attempts=0,polls=0;
  const client=new SandboxScenarioClient({baseUrl:'https://api.example.com',apiKey:'amlok_test_fixture',sleep:async()=>{},fetcher:async(url,options)=>{
    const path=new URL(url).pathname;
    if(path==='/v1/sandbox/catalog')return json({version:'catalog-1',businesses:[{id:'maple-retail'}]});
    if(options.method==='POST'){
      assert.ok(persisted.length,'Intent must be saved before the network write');
      commands.push({key:options.headers['Idempotency-Key'],body:options.body});
      if(++attempts===1)throw TypeError('Socket closed after acceptance');
      return json({id:'srun_1',status:'queued'},202);
    }
    polls++;return json({id:'srun_1',status:'completed',resources:[]});
  }});
  const options={client,state,input:{scenario:'healthy'},persist:async value=>persisted.push(structuredClone(value)),sleep:async()=>{}};
  assert.equal((await runSandboxScenario(options)).status,'completed');
  assert.equal(commands.length,2);assert.deepEqual(commands[0],commands[1]);
  assert.equal(state.runId,'srun_1');
  assert.equal((await runSandboxScenario({...options,input:{scenario:'outside_policy'}})).id,'srun_1');
  assert.equal(commands.length,2);assert.equal(polls,2);
  assert.ok(!JSON.stringify(state).includes('amlok_test_fixture'));
});

test('process restart recovers the persisted request and does not fetch a changed catalog',async()=>{
  const state={origin:'https://api.example.com',command:{key:'fixed-key',body:{scenario_id:'healthy',fixture_id:'maple-retail',catalog_version:'catalog-1'}}};
  const calls=[];
  const client=new SandboxScenarioClient({baseUrl:state.origin,apiKey:'amlok_test_fixture',fetcher:async(url,options)=>{calls.push({url,options});return json({id:'srun_1',status:'completed'},202);}});
  await runSandboxScenario({client,state,input:{scenario:'provider_failure'},persist:async()=>{}});
  assert.equal(calls.length,1);assert.equal(calls[0].options.headers['Idempotency-Key'],'fixed-key');
  assert.equal(JSON.parse(calls[0].options.body).scenario_id,'healthy');
});

test('expired response replay recovers the accepted scenario through its durable receipt',async()=>{
  const state={origin:'https://api.example.com',command:{key:'accepted-key',body:{scenario_id:'healthy'}}};const urls=[];
  const client=new SandboxScenarioClient({baseUrl:state.origin,apiKey:'amlok_test_fixture',fetcher:async(url,options)=>{
    urls.push(url);
    if(options.method==='POST')return json({error:{code:'idempotency_result_expired',message:'Use receipt',retryable:false}},409);
    if(url.includes('/request-receipts/lookup'))return json({resource_id:'srun_accepted'});
    return json({id:'srun_accepted',status:'completed'});
  }});
  assert.equal((await runSandboxScenario({client,state,input:{},persist:async()=>{}})).id,'srun_accepted');
  assert.match(urls[1],/operation_id=createSandboxRun&idempotency_key=accepted-key/);
});

test('authentication, Live keys and unsafe origins fail without network retries',async()=>{
  for(const baseUrl of ['http://api.example.com','https://api.example.com/v1','https://user:secret@api.example.com','https://api.example.com/?token=x'])assert.throws(()=>new SandboxScenarioClient({baseUrl,apiKey:'amlok_test_fixture'}));
  assert.throws(()=>new SandboxScenarioClient({baseUrl:'https://api.example.com',apiKey:'amlok_live_fixture'}));
  let attempts=0;
  const client=new SandboxScenarioClient({baseUrl:'https://api.example.com',apiKey:'amlok_test_fixture',fetcher:async()=>{attempts++;return json({error:{code:'forbidden',message:'Denied',retryable:false}},403);}});
  await assert.rejects(()=>client.request('/v1/sandbox/catalog'),/403/);assert.equal(attempts,1);
  await assert.rejects(()=>runSandboxScenario({client,state:{origin:'https://staging-api.example.com'},input:{},persist:async()=>{}}),/different API deployment/);
});

test('retry delay respects Retry-After and polling returns resumable queued work at its deadline',async()=>{
  let calls=0;const sleeps=[];
  const client=new SandboxScenarioClient({baseUrl:'https://api.example.com',apiKey:'amlok_test_fixture',sleep:async ms=>sleeps.push(ms),fetcher:async()=>++calls===1?json({error:{code:'rate_limited',message:'Wait',retryable:true}},429,{'Retry-After':'3'}):json({id:'srun_1',status:'queued'})});
  const state={origin:client.origin,runId:'srun_1',command:{key:'k',body:{}}};
  const run=await runSandboxScenario({client,state,input:{},persist:async()=>{},now:()=>0,maxWaitMs:1000});
  assert.equal(run.status,'queued');assert.equal(sleeps.length,1);assert.ok(sleeps[0]>=3000);assert.equal(calls,2);
});
