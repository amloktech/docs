import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { AmlokClient, runJourney } from '../downloads/amlok-journey.mjs';
const fixtures=JSON.parse(await readFile(new URL('../data/product-api-examples.json',import.meta.url)));
const spec=JSON.parse(await readFile(new URL('../openapi/amlok.json',import.meta.url)));
const index=JSON.parse(await readFile(new URL('../data/api-reference-index.json',import.meta.url)));
const clone=structuredClone;
const captured=[];
const json=(body,status=200,headers={})=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json',...headers}});

test('client retries a rate limit using the same command identity',async()=>{
 const calls=[],delays=[];
 const client=new AmlokClient({baseUrl:'https://api.example.com',apiKey:'synthetic',sleep:async n=>delays.push(n),fetcher:async(url,opts)=>{calls.push(opts);return calls.length===1?json({error:{code:'rate_limited',retryable:true,message:'Wait'}},429,{'Retry-After':'2'}):json({data:{id:'one'}});}});
 await client.request('POST','/v1/borrowers',{type:'business'},{'Idempotency-Key':'same'});
 assert.equal(calls.length,2);assert.equal(calls[0].headers['Idempotency-Key'],calls[1].headers['Idempotency-Key']);assert.equal(calls[0].body,calls[1].body);assert.ok(delays[0]>=2000);
});
test('validation and authorization failures never retry',async()=>{
 let calls=0;const client=new AmlokClient({baseUrl:'https://api.example.com',apiKey:'synthetic',fetcher:async()=>{calls++;return json({error:{code:'forbidden',retryable:false,message:'Denied'}},403);}});
 await assert.rejects(()=>client.request('GET','/v1/billing/summary'));assert.equal(calls,1);
});
test('pagination retains filters and follows every page',async()=>{
 const urls=[];const client=new AmlokClient({baseUrl:'https://api.example.com',apiKey:'synthetic',fetcher:async url=>{urls.push(url);return json({data:[urls.length],page:{has_more:urls.length===1,next_cursor:urls.length===1?'next':null}});}});
 const values=[];for await(const batch of client.pages('/v1/data/records?borrower_id=bor_a&resource_type=invoice'))values.push(...batch.data);
 assert.deepEqual(values,[1,2]);assert.equal(new URL(urls[1]).searchParams.get('borrower_id'),'bor_a');assert.equal(new URL(urls[1]).searchParams.get('cursor'),'next');
});
test('origin validation prevents cross-origin API key transmission',()=>{
 assert.throws(()=>new AmlokClient({baseUrl:'https://api.example.com/v1',apiKey:'synthetic'}));
 assert.throws(()=>new AmlokClient({baseUrl:'http://external.example.com',apiKey:'synthetic'}));
});

for(const kind of ['business','person'])test(kind+' complete journey uses schema-valid calls and returned IDs',async()=>{
 const inputs=JSON.parse(await readFile(new URL('../downloads/'+(kind==='person'?'consumer-journey-inputs.json':'journey-inputs.json'),import.meta.url)));
 const state={runId:'offline-'+kind,commands:{},scenario:'happy_path',embeddingVersionId:'embed_synthetic',returnUrl:'https://institution.example.com/connected'};
 let sessionCompleted=false,saves=0;
 const fetcher=async(url,opts)=>{
  const parsed=new URL(url);const op=index.find(row=>row.method===opts.method && new RegExp('^'+row.path.replace('{id}','[^/]+')+'$').test(parsed.pathname));
  assert.ok(op,'Undocumented operation '+opts.method+' '+parsed.pathname);
  let request;
  if(opts.body instanceof FormData){request={};for(const [k,v] of opts.body)request[k]=typeof v==='string'?v:'<binary file bytes>';}
  else if(opts.body)request=JSON.parse(opts.body);
  if(request)captured.push({kind,operationId:op.id,request});
  const d=clone(fixtures[op.response]);
  if(op.id==='createBorrower'){d.profile=request;d.client_reference=request[kind].client_reference;}
  if(op.id==='createEmbeddingSession'||op.id==='getEmbeddingSession'){d.expires_at=new Date(Date.now()+900000).toISOString();d.status=sessionCompleted?'completed':'created';d.connection_ids=sessionCompleted?['con_synthetic']:[];}
  if(op.id==='createExport'||op.id==='getExport'){d.status='completed';d.expires_at=new Date(Date.now()+86400000).toISOString();d.artifact=clone(spec.paths['/v1/exports/{id}'].get.responses['200'].content['application/json']['x-response-views'].completed.example.data.artifact);}
  const definition=spec.paths[op.path][op.method.toLowerCase()];
  const [status,response]=Object.entries(definition.responses).find(([code])=>code.startsWith('2'));
  const out=clone(response.content['application/json'].example);out.data=op.many?[d]:d;
  if(op.id==='createOrigination'){out.data.status='accepted';out.data.risk_package_id=null;}
  if(op.id==='createMonitor'){out.data.status='initializing';out.data.latest_package_id=null;out.data.next_evaluation_at=null;}
  captured.push({kind,operationId:op.id,status,response:out});
  return json(out,Number(status));
 };
 const client=new AmlokClient({baseUrl:'https://api.example.com',apiKey:'synthetic-offline',fetcher,sleep:async()=>{}});
 const options={client,state,inputs,persist:async()=>{saves++;},launch:url=>assert.match(url,/^https:/),documentBytes:new Uint8Array([37,80,68,70])};
 assert.equal((await runJourney({...options,phase:'prepare'})).phase,'awaiting_borrower');sessionCompleted=true;
 const result=await runJourney({...options,phase:'complete'});assert.equal(result.phase,'completed');assert.equal(result.monitor_id,'mon_synthetic');assert.equal(result.deal_snapshot_id,'ds_synthetic');assert.ok(saves>5);
 const countBefore=captured.filter(c=>c.operationId==='createOrigination'&&c.request).length;
 await runJourney({...options,phase:'complete'});
 assert.equal(captured.filter(c=>c.operationId==='createOrigination'&&c.request).length,countBefore,'Resume must not resubmit completed origination');
 await writeFile(new URL('../artifacts/client-contract-calls.json',import.meta.url),JSON.stringify(captured,null,2));
});

test('Hub helper rejects spoofed origins, wrong frames, duplicate IDs and expired sessions',async()=>{
 const listeners=new Map();globalThis.window={location:{origin:'https://institution.example.com'},addEventListener:(n,f)=>listeners.set(n,f),removeEventListener:n=>listeners.delete(n)};
 const {mountAmlokHub}=await import('../downloads/hub-embed.js');
 const frame={contentWindow:{},setAttribute(){},removeAttribute(){}};let verified=0,states=0;
 const session={...fixtures.EmbeddingSession,embed_origin:window.location.origin,expires_at:new Date(Date.now()+90000).toISOString()};
 const cleanup=mountAmlokHub({iframe:frame,session,hubOrigin:'https://borrower.example.com',fetchSession:async()=>{verified++;return {...session,status:'completed'};},onState:()=>states++});
 const data={protocol_version:'1',event_id:'message-1',session_id:session.id,type:'amlok.hub.completed'};
 await listeners.get('message')({origin:'https://evil.example',source:frame.contentWindow,data});
 await listeners.get('message')({origin:'https://borrower.example.com',source:{},data});assert.equal(verified,0);
 await listeners.get('message')({origin:'https://borrower.example.com',source:frame.contentWindow,data});
 await listeners.get('message')({origin:'https://borrower.example.com',source:frame.contentWindow,data});assert.equal(verified,1);assert.equal(states,1);
 cleanup();assert.equal(listeners.size,0);
 assert.throws(()=>mountAmlokHub({iframe:frame,session:{...session,expires_at:'2000-01-01T00:00:00Z'},hubOrigin:'https://borrower.example.com'}));
});
