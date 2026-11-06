/* Sandbox reference client. No SDK, provider credentials or payment processor required.
   Run prepare, complete the returned Hub URL, then run complete. See runnable-example. */
import { readFile, writeFile, chmod } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { pathToFileURL } from 'node:url';

export class AmlokClient {
  constructor({ baseUrl, apiKey, fetcher = fetch, sleep = ms => new Promise(r => setTimeout(r, ms)) }) {
    const url = new URL(baseUrl);
    if (url.protocol !== 'https:' && !(url.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(url.hostname))) throw new Error('HTTPS API origin required');
    if (url.pathname !== '/' || url.search || url.hash || url.username || url.password) throw new Error('Supply the API origin without /v1');
    if (!apiKey) throw new Error('Server-side API key required');
    this.base = url.origin; this.key = apiKey; this.fetcher = fetcher; this.sleep = sleep;
  }
  async request(method, path, body, extraHeaders = {}) {
    if (!path.startsWith('/v1/')) throw new Error('Only the configured API origin is allowed');
    let last;
    for (let attempt = 0; attempt < 4; attempt++) {
      try {
        const multipart = body instanceof FormData;
        const response = await this.fetcher(this.base + path, { method, redirect: 'error', signal: AbortSignal.timeout(30000),
          headers: { Authorization: `Bearer ${this.key}`, Accept: 'application/json', ...(body && !multipart ? {'Content-Type':'application/json'} : {}), ...extraHeaders },
          ...(body ? { body: multipart ? body : JSON.stringify(body) } : {}) });
        const payload = await response.json();
        if (response.ok) return payload;
        const error = new Error(`${response.status} ${payload.error?.code}: ${payload.error?.message}`);
        error.status = response.status; error.detail = payload.error;
        if (![429,503].includes(response.status) || payload.error?.retryable !== true) throw error;
        last = error;
        if (attempt < 3) {
          const retry = Number(response.headers.get('Retry-After') ?? 2 ** attempt);
          if (!Number.isFinite(retry) || retry > 60) throw error; // Durable caller retries later, never before Retry-After.
          await this.sleep(Math.max(0, retry) * 1000 + Math.floor(Math.random()*250));
        }
      } catch (error) {
        if (error.status) throw error;
        last = error;
        if (attempt < 3) await this.sleep(1000 * 2 ** attempt);
      }
    }
    throw last;
  }
  async *pages(path) {
    let cursor;
    do {
      const target = new URL(path, this.base);
      if (cursor) target.searchParams.set('cursor', cursor);
      const response = await this.request('GET', target.pathname + target.search);
      yield response;
      if (response.page.has_more && !response.page.next_cursor) throw new Error('Invalid pagination contract');
      cursor = response.page.has_more ? response.page.next_cursor : null;
    } while (cursor);
  }
  async wait(path, profile, maxWaitMs = 120000) {
    const stop = Date.now() + maxWaitMs;
    let delay = profile.poll_min_interval_seconds;
    while (true) {
      const result = await this.request('GET', path);
      if (!['accepted','collecting','processing','initializing','queued'].includes(result.data.status)) return result.data;
      if (Date.now() + delay*1000 > stop) throw new Error('Still processing: retain the resource ID and resume later; do not create duplicate work');
      await this.sleep(delay*1000);
      delay = Math.min(profile.poll_max_interval_seconds, delay*2);
    }
  }
}

export async function runJourney({ phase, client, state, inputs, persist, launch, documentBytes }) {
  const config = (await client.request('GET','/v1/configuration')).data;
  if (!config.sandbox) throw new Error('This reference journey runs only in Sandbox');
  const profile = config.operational_profile;
  async function command(label, operationId, path, body, readPath, headers={}) {
    // Persist intended request and key before sending. Retain the same identity after interruption.
    const previous = state.commands[label];
    if (previous?.id) return (await client.request('GET', readPath(previous.id))).data;
    if (!previous) { state.commands[label]={key:state.runId+'-'+label,body}; await persist(state); }
    const saved=state.commands[label];
    let result;
    try { result=await client.request('POST',path,saved.body,{'Idempotency-Key':saved.key,...headers}); }
    catch (error) {
      if (error.status && error.detail?.code!=='idempotency_result_expired') throw error;
      const receipt=await client.request('GET','/v1/request-receipts/lookup?operation_id='+operationId+'&idempotency_key='+encodeURIComponent(saved.key));
      result=await client.request('GET',readPath(receipt.data.resource_id));
    }
    saved.id=result.data.id; await persist(state); return result.data;
  }
  if (phase==='prepare') {
    const borrower=await command('borrower','createBorrower','/v1/borrowers',{...inputs.CreateBorrower,[inputs.CreateBorrower.type]:{...inputs.CreateBorrower[inputs.CreateBorrower.type],client_reference:state.runId}},id=>'/v1/borrowers/'+id,{'X-AMLOK-Sandbox-Scenario':state.scenario});
    const product=structuredClone(inputs.LendingProductInput);product.external_id=state.runId; product.pricing_schema_id=config.pricing_schemas[0].id;
    const policy=structuredClone(inputs.RiskPolicyInput);policy.external_id=state.runId;
    await command('product','createLendingProductVersion','/v1/lending-product-versions',product,id=>'/v1/lending-product-versions/'+id);
    await command('policy','createRiskPolicyVersion','/v1/risk-policy-versions',policy,id=>'/v1/risk-policy-versions/'+id);
    const hub=config.embedding_versions.find(h=>h.id===state.embeddingVersionId);
    if (!hub || !hub.integration_ids.includes(config.sandbox.test_integration_id)) throw new Error('Publish/select a Hub containing the synthetic integration');
    const session=await command('session','createEmbeddingSession','/v1/embedding-sessions',{borrower_id:borrower.id,embedding_version_id:hub.id,purpose:'connect',return_url:state.returnUrl,consent_purposes:['credit_assessment','continuous_monitoring']},id=>'/v1/embedding-sessions/'+id);
    if (!session.launch_url || Date.parse(session.expires_at)<=Date.now()) throw new Error('Session expired; prepare a new journey with a new state file');
    launch(session.launch_url);return {phase:'awaiting_borrower',session_id:session.id};
  }
  if (phase!=='complete' || !state.commands.session?.id) throw new Error('Run prepare first');
  const session=(await client.request('GET','/v1/embedding-sessions/'+state.commands.session.id)).data;
  if (session.status!=='completed') throw new Error('Complete the Hub first; session is '+session.status);
  const borrowerId=state.commands.borrower.id;
  if (!state.documentId) {
    const form=new FormData();form.append('file',new Blob([documentBytes],{type:'application/pdf'}),'synthetic-statement.pdf');form.append('context','borrower');form.append('borrower_id',borrowerId);form.append('document_type','financial_statement');
    const upload=await client.request('POST','/v1/documents',form,{'Idempotency-Key':state.runId+'-document'});
    state.documentId=upload.data.id;await persist(state);
  }
  const doc=await client.wait('/v1/documents/'+state.documentId,profile);
  if (doc.status!=='available') throw new Error('Document unavailable: '+JSON.stringify(doc.failure));
  const request=structuredClone(inputs.CreateOrigination);Object.assign(request,{borrower_id:borrowerId,lending_product_version_id:state.commands.product.id,risk_policy_version_id:state.commands.policy.id,connection_ids:session.connection_ids,document_ids:[doc.id]});
  request.application.institution_reference=state.runId;if(!config.application_schemas.some(s=>s.id===request.application.application_schema_id))throw new Error('Provision the input application schema before running this fixture');
  const origination=await command('origination','createOrigination','/v1/originations',request,id=>'/v1/originations/'+id);
  const completed=await client.wait('/v1/originations/'+origination.id,profile);
  if (completed.status!=='completed') return {phase:completed.status,origination_id:completed.id,requirements:completed.requirements,failure:completed.failure};
  const pkg=(await client.request('GET','/v1/risk-packages/'+completed.risk_package_id)).data;
  let evidenceCount=0;for await(const batch of client.pages('/v1/evidence?evidence_set_id='+encodeURIComponent(pkg.evidence_set.id)))evidenceCount+=batch.data.length;
  let dataCount=0,changesCursor;for await(const batch of client.pages('/v1/data/records?borrower_id='+borrowerId)){dataCount+=batch.data.length;changesCursor??=batch.page.changes_cursor;}
  const changes=await client.request('GET','/v1/data/changes?cursor='+encodeURIComponent(changesCursor));
  // A real consumer applies each batch and checkpoints atomically in its database.
  state.dataResumeCursor=changes.page.resume_cursor;await persist(state);
  const monitorBody=structuredClone(inputs.CreateMonitor);Object.assign(monitorBody,{borrower_id:borrowerId,baseline:{risk_package_id:pkg.id},risk_policy_version_id:state.commands.policy.id,cadence_id:config.cadences[0].id,connection_ids:session.connection_ids});monitorBody.deal.institution_reference=state.runId;
  const monitor=await command('monitor','createMonitor','/v1/monitors',monitorBody,id=>'/v1/monitors/'+id);
  const active=await client.wait('/v1/monitors/'+monitor.id,profile);
  if (active.status!=='active') return {phase:active.status,monitor_id:active.id,requirements:active.requirements,failure:active.failure};
  const snapshotBody={previous_snapshot_id:active.latest_deal_snapshot_id,effective_at:new Date().toISOString(),deal:{...active.deal,outstanding_amount:{...active.deal.outstanding_amount,amount:'48000.00'}},performance:null};
  const snapshot=await command('snapshot','createDealSnapshot','/v1/monitors/'+active.id+'/deal-snapshots',snapshotBody,id=>'/v1/deal-snapshots/'+id);
  const runs=[];for await(const batch of client.pages('/v1/monitoring-runs?monitor_id='+active.id))runs.push(...batch.data);
  const alerts=[];for await(const batch of client.pages('/v1/alerts?monitor_id='+active.id))alerts.push(...batch.data);
  const preparedExport=await command('export','createExport','/v1/exports',{kind:'risk_package',risk_package_id:pkg.id,format:'json'},id=>'/v1/exports/'+id);
  const exportResult=await client.wait('/v1/exports/'+preparedExport.id,profile);
  if(exportResult.status!=='completed')return {phase:'export_'+exportResult.status,export_id:exportResult.id,failure:exportResult.failure};
  // Capability URLs are not printed or persisted. Stream/hash file bytes in your own secure downloader.
  const link=await client.request('POST','/v1/exports/'+exportResult.id+'/download-links',{purpose:'Sandbox integration acceptance'},{'Idempotency-Key':state.runId+'-download-'+randomUUID()});
  if(!link.data.sha256 || !link.data.expires_at)throw new Error('Incomplete download capability');
  const summary=(await client.request('GET','/v1/billing/summary')).data;
  const totals={payments:0,transactions:0,usage:0};
  for(const kind of Object.keys(totals))for await(const batch of client.pages('/v1/billing/'+kind+'?snapshot_id='+summary.snapshot_id))totals[kind]+=batch.data.length;
  return {phase:'completed',monitoring_runs:runs.length,alerts:alerts.length,export_id:exportResult.id,origination_id:completed.id,risk_package_id:pkg.id,evidenceCount,dataCount,monitor_id:active.id,deal_snapshot_id:snapshot.id,billing_snapshot_id:summary.snapshot_id,available_credits:summary.available_credits,...totals};
}

async function main(){
  const phase=process.argv[2]; const statePath=process.argv[3] || 'amlok-journey-state.json';
  if(!['prepare','complete'].includes(phase))throw new Error('Usage: node amlok-journey.mjs prepare|complete state.json');
  let state;try{state=JSON.parse(await readFile(statePath,'utf8'));}catch(error){if(error.code!=='ENOENT')throw error;state={runId:randomUUID(),commands:{},scenario:process.env.AMLOK_SCENARIO||'happy_path',embeddingVersionId:process.env.AMLOK_EMBEDDING_VERSION_ID,returnUrl:process.env.AMLOK_RETURN_URL};}
  const inputs=JSON.parse(await readFile(new URL(process.env.AMLOK_BORROWER_TYPE==='person'?'./consumer-journey-inputs.json':'./journey-inputs.json',import.meta.url),'utf8'));
  const client=new AmlokClient({baseUrl:process.env.AMLOK_API_BASE_URL,apiKey:process.env.AMLOK_API_KEY});
  const result=await runJourney({phase,client,state,inputs,persist:async value=>{await writeFile(statePath,JSON.stringify(value,null,2),{mode:0o600});await chmod(statePath,0o600);},launch:url=>process.stdout.write('Open this short-lived borrower URL privately: '+url+'\n'),documentBytes:await readFile(new URL('./synthetic-statement.pdf',import.meta.url))});
  console.log(JSON.stringify(result,null,2));
}
if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(error=>{console.error(error.message);process.exitCode=1;});
