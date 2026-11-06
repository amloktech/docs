"""Synthetic verification fixtures. Never copy customer report values into public examples."""
from copy import deepcopy
from verification_contract import empty_assessment, SECTIONS

NOW='2026-11-06T12:00:00Z'

def examples(s):
 def default(schema):
  if '$ref' in schema:return default(s[schema['$ref'].split('/')[-1]])
  if any(v.get('type')=='null' for v in schema.get('anyOf',[])):return None
  if 'const' in schema:return schema['const']
  if 'enum' in schema:return schema['enum'][0]
  t=schema.get('type')
  if isinstance(t,list) and 'null' in t:return None
  if t=='array':return []
  if t=='object':return {k:default(v) for k,v in schema['properties'].items()}
  if t=='boolean':return False
  if t in ['integer','number']:return 0
  if schema.get('format')=='date-time':return NOW
  if schema.get('format')=='date':return '2026-11-06'
  return 'synthetic'
 def evidence(page=None,path=None):return {'evidence_id':'ev_verification_synthetic','data_record_id':'dr_verification_source_synthetic','source_path':path,'document_id':'doc_registry_synthetic' if page else None,'page':page}
 def item(schema_name,id,subject='biz_synthetic',page=None,basis='registry',**values):
  result=default(s[schema_name]);result.update(id=id,subject_id=subject,**values)
  result['provenance']={'basis':basis,'source_id':'src_verification_synthetic','observed_at':NOW,'retrieved_at':NOW,'evidence':[evidence(page)],'field_evidence':[]}
  for key,value in result.items():
   if value is None:result['missing_fields'].append({'path':'/'+key,'reason':'not_provided','description':'This synthetic source does not supply this field.'})
  return result
 def coverage(scopes,status='complete'):return {'status':status,'requested_scopes':scopes,'completed_scopes':scopes if status=='complete' else [],'limitations':[] if status=='complete' else ['This example does not establish complete coverage.']}
 def put(a,key,items):a[key]={'status':'available','reason':None,'explanation':'Synthetic observations; availability does not mean a passing result.','coverage':coverage(['synthetic_requested_scope']),'items':items}
 def score(value=100,direction='higher_is_stronger_match'):return {'value':value,'scale_min':0,'scale_max':100,'direction':direction,'label':'Synthetic similarity only','method':'synthetic-method-1'}
 def identifier(scheme,value,country='CA'):return {'scheme':scheme,'value':value,'masked_value':None,'country':country,'jurisdiction':None,'disclosure':'full','reason':None}
 business=empty_assessment('bor_synthetic',NOW);business.update(id='verify_business_synthetic',status='partial',outcome='review_required',summary='Synthetic business has a selected registry record. Required related-party checks and ownership resolution remain incomplete; an active registration is not a verified pass.')
 business['sources']=[{'id':'src_verification_synthetic','kind':'business_verification','display_name':'Synthetic licensed registry source','jurisdictions':['CA-AB'],'reference':'report_synthetic','reported_status':'not_verified','requested_at':NOW,'completed_at':NOW,'as_of':NOW,'coverage':coverage(['business_registry','licence_registry','related_people'],'partial'),'document_ids':['doc_registry_synthetic'],'warnings':['Required people not supplied.'],'errors':[]}]
 business['documents']=[{'document_id':'doc_registry_synthetic','kind':'registry_report','access':'available','reason':None,'source_id':'src_verification_synthetic'}]
 business['ownership_resolution'].update(status='partial',reason='Corporate shareholder chain and remaining voting interests are unresolved.',unresolved_subject_ids=['owner_company_synthetic'],ownership_basis='voting',known_share='0.65',unknown_share='0.35')
 put(business,'checks',[item('VerificationResult','check_registry_synthetic',kind='business_registration',state='completed',outcome='review_required',provider_status='not_verified',summary='Registry found; required people have not been submitted.',required=True,completed_at=NOW,item_ids=['business_selected_synthetic','compare_people_synthetic'])])
 put(business,'businesses',[item('VerificationBusiness','business_selected_synthetic',page=1,resolution='selected',legal_name='Synthetic Example Manufacturing Inc.',entity_type='corporation',country='CA',jurisdiction='CA-AB',identifiers=[identifier('corporation_number','SYNTHETIC-CA-001')],incorporation_date='2018-04-10',nature_of_business='Synthetic manufacturing business',registry_status='Active',address_ids=['address_registered_synthetic','address_records_synthetic'],match_score=score())])
 put(business,'registrations',[item('VerificationRegistration','registration_synthetic',page=4,authority='Synthetic provincial registry',registration_number='SYNTHETIC-CA-001',country='CA',jurisdiction='CA-AB',registered_name='Synthetic Example Manufacturing Inc.',status='Active',last_annual_return_year=2024,last_annual_return_filed_on='2025-03-01',annual_return_status='overdue',outstanding_return_years=[2025],document_ids=['doc_registry_synthetic'])])
 put(business,'addresses',[item('VerificationAddress','address_'+role+'_synthetic',page=1,roles=[role+'_office'],street='100 Synthetic Example Street',unit='Suite 3',city='Calgary',region='AB',postal_code='T2P 1J9',country='CA',validation='not_validated') for role in ['registered','records']])
 put(business,'relationships',[item('VerificationRelationship','relationship_owner_synthetic',page=3,related_subject_id='owner_company_synthetic',related_entity_type='business',name='Synthetic Holding Company Inc.',roles=['shareholder'],role_labels=['Voting shareholder'],verification_required=True,verification_state='pending'),item('VerificationRelationship','relationship_agent_synthetic',page=1,related_subject_id='agent_synthetic',related_entity_type='person',name='Synthetic Service Agent',roles=['agent_for_service'],role_labels=['Primary agent for service'],verification_state='not_requested')])
 put(business,'ownership',[item('VerificationOwnership','ownership_synthetic',page=3,owner_subject_id='owner_company_synthetic',owned_subject_id='biz_synthetic',interest_type='voting',voting_share='0.65',chain_subject_ids=['owner_company_synthetic','biz_synthetic'],chain_complete=False,unresolved_reason='No source establishes the corporate owner ultimate beneficial owners.',reported_interest='65% of Voting Shares')])
 put(business,'field_comparisons',[item('VerificationFieldComparison','compare_name_synthetic',field='business.legal_name',provided='SYNTHETIC EXAMPLE MANUFACTURING INC.',observed='Synthetic Example Manufacturing Inc.',normalized_provided='SYNTHETIC EXAMPLE MANUFACTURING INC',normalized_observed='SYNTHETIC EXAMPLE MANUFACTURING INC',result='matched',score=score(),threshold=95,required=True,affects_outcome=True,normalization='Case and terminal punctuation folded; source names retained.'),item('VerificationFieldComparison','compare_people_synthetic',field='business.related_people',result='not_submitted',required=True,affects_outcome=True)])
 put(business,'licences',[item('VerificationLicence','licence_synthetic',registry='Synthetic municipal business licence registry',authority='Synthetic municipality',country='CA',jurisdiction='CA-AB',identifier='SYNTHETIC-LIC-1',legal_name='Synthetic Example Manufacturing Inc.',licence_types=['Manufacturing'],status='Renewal licensed',issued_on='2018-04-10',expires_on='2027-04-10',match_score=score())])
 put(business,'filings',[item('VerificationFiling','filing_synthetic',page=4,kind='Annual return',filed_on='2025-03-01',period_year=2024,status='Filed',document_ids=['doc_registry_synthetic'])])
 put(business,'corporate_structure',[item('VerificationCorporateStructure','structure_synthetic',page=4,share_classes=[{'name':'Synthetic Class A','description':'Common voting shares','authorized_quantity':None,'unlimited':True,'issued_quantity':None,'voting_rights':'One vote per share','votes_per_share':'1','nominal_value':None,'dividend_rights':'As declared, subject to senior rights.','liquidation_rights':None,'redemption_terms':None,'evidence':[evidence(6)]}],minimum_directors=1,maximum_directors=10,share_transfer_restrictions=['See the source articles schedule.'],document_ids=['doc_registry_synthetic'])])
 put(business,'tax_checks',[item('VerificationTaxCheck','tax_synthetic',identifier={'scheme':'BN','value':None,'masked_value':'*****0001','country':'CA','jurisdiction':None,'disclosure':'masked','reason':'Synthetic example masks the taxpayer identifier.'},result='unavailable',unavailable_reason='Registry identifier reported; no tax-authority validation result supplied.')])
 put(business,'source_scores',[item('VerificationSourceScore','score_synthetic',kind='entity_match',score=score(),limitations=['Similarity is not an AMLOK credit score or a verified beneficial-owner conclusion.'])])
 person=empty_assessment('bor_consumer_synthetic',NOW,'person');person.update(id='verify_person_synthetic',status='partial',outcome='review_required',summary='Synthetic identity document matched; a screening candidate remains unreviewed. No lender decision is made.')
 person['sources']=deepcopy(business['sources']);person['sources'][0].update(kind='identity_verification',display_name='Synthetic identity source',reported_status='in_review',document_ids=[],coverage=coverage(['identity','sanctions']))
 subject='person_synthetic'
 put(person,'checks',[item('VerificationResult','check_id_synthetic',subject,basis='provider_verified',kind='identity',state='completed',outcome='passed',provider_status='approved',summary='Synthetic document comparison completed.',completed_at=NOW,item_ids=['id_document_synthetic']),item('VerificationResult','check_aml_synthetic',subject,basis='provider_verified',kind='sanctions',state='completed',outcome='review_required',provider_status='in_review',summary='A candidate match requires review.',completed_at=NOW,item_ids=['screening_synthetic'])])
 put(person,'persons',[item('VerificationPerson','person_synthetic',subject,basis='document_extracted',full_name='Synthetic Example Person',given_names='Synthetic',family_name='Person',identity_assurance='documentary',identity_check_ids=['check_id_synthetic'])])
 put(person,'identity_documents',[item('VerificationIdentityDocument','id_document_synthetic',subject,basis='provider_verified',document_type='Passport',identifier={'scheme':'passport','value':None,'masked_value':'*****0123','country':'CA','jurisdiction':None,'disclosure':'masked','reason':'Personal document identifiers are minimized.'},issuing_country='CA',issued_on='2024-01-01',expires_on='2034-01-01',holder_subject_id=subject,method='document',assurance='documentary',authenticity='passed')])
 put(person,'biometrics',[item('VerificationBiometric','liveness_synthetic',subject,basis='provider_verified',kind='liveness',method='passive',outcome='passed',score=score(96,'higher_is_more_assurance'),threshold=80)])
 put(person,'screenings',[item('VerificationScreening','screening_synthetic',subject,basis='provider_verified',kind='sanctions',state='completed',result='potential_match',coverage=coverage(['synthetic_sanctions_dataset']),hits=[{'id':'hit_synthetic','category':'sanctions','matched_name':'Synthetic Similar Name','aliases':[],'list_name':'Synthetic screening dataset','list_authority':None,'source_record_reference':'source_hit_synthetic','source_url':None,'match_score':score(82),'risk_score':None,'disposition':'unreviewed','reviewed_at':None,'review_reason':None,'first_seen_at':None,'last_seen_at':None,'properties':[],'evidence':[evidence(path='/aml_screenings/0/hits/0')]}],reported_hit_count=1,returned_hit_count=1,screened_at=NOW)])
 put(person,'contact_checks',[item('VerificationContactCheck','contact_synthetic',subject,basis='provider_verified',kind='email',value='synthetic@example.com',method='otp',outcome='passed',verified_at=NOW,attempts=1,deliverable=True)])
 put(person,'bank_account_checks',[item('VerificationBankAccountCheck','bank_owner_synthetic',subject,basis='provider_verified',masked_account_number='*****0123',institution_name='Synthetic Bank',country='CA',holder_names=['Synthetic Example Person'],reference_identity_name='Synthetic Example Person',method='account_check',result='matched',verified_at=NOW)])
 return {'business':business,'consumer':person}


def normalized_record(assessment):
 return {'id':assessment['id'],'object':'verification_assessment','subject_id':assessment['subject_id'],'record_version':1,'created_at':assessment['as_of'],'updated_at':assessment['as_of'],'observed_at':assessment['as_of'],'schema_version':'1.0.0','assessment':deepcopy(assessment)}
