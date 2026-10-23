"""Verify exact report/request custody and author-response map completeness.

No economics, optimizer, original risk primitive or protected experiment is
read or executed. This is a source-map check, not scientific issue closure.
"""
from pathlib import Path
import datetime, hashlib, json

REV = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((REV/name).read_bytes())

def digest(name):
    return hashlib.sha256((REV/name).read_bytes()).hexdigest()

def run():
    current=read('response_inputs/CURRENT_RESPONSE125.json')
    history=read('response_inputs/HISTORICAL_ITEM_ROUTES125.json')
    catalogue=read('response_inputs/HISTORICAL_REQUEST_CATALOGUE125.json')
    bodies=read('provenance/unique_reports.json')
    byid={r['id']:r for r in catalogue['records']}
    assert len(byid)==684
    seen=set()
    major=parent=0
    old=(REV/'new119/historical_response119_body.tex').read_text()
    more=(REV/'new119/additional_response119_body.tex').read_text()
    for r in history['records']:
        key=r['id'];assert key not in seen;seen.add(key)
        original=byid[key]
        assert r['report_sha256']==original['report_sha256']
        assert r['exact_original_body_sha256']==hashlib.sha256(original['exact_body'].encode()).hexdigest()
        assert r['closure_claim'] is False
        assert r['r125_current_response_ids'] and r['r125_current_chapter_labels']
        if r['record_kind']=='explicit_major_block':
            major+=1
            assert r['exact_inherited_response_latex'] in old
        else:
            parent+=1
            if r.get('exact_inherited_response_latex'):
                assert r['exact_inherited_response_latex'] in more
    assert seen==set(byid) and major==620 and parent==64
    report=(REV/'provenance/review_sources/2026-10-14-econometrica-numerical-methods-r97/referee_report.md').read_text()
    expected={f'B{i}' for i in range(1,11)}|{f'M{i}' for i in range(1,11)}|{f'Minor {i}' for i in range(1,11)}
    assert {r['request_id'] for r in current['records']}==expected
    for r in current['records']:
        assert r['exact_original_request'] in report
        assert r['exact_request_sha256']==hashlib.sha256(r['exact_original_request'].encode()).hexdigest()
        assert r['closure_claim'] is False
        assert r['r125_author_amendment'] and r['r125_remaining_scientific_requirement']
        assert r.get('status')
    report_checks=[]
    for r in bodies:
        data=(REV/'provenance'/r['local_path']).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert blob==r['git_blob_sha1']
        report_checks.append(blob)
    assert len(set(report_checks))==35
    inputs=['response_inputs/CURRENT_RESPONSE125.json','response_inputs/HISTORICAL_ITEM_ROUTES125.json',
            'response_inputs/HISTORICAL_ITEM_ROUTES125.md','response_inputs/HISTORICAL_REQUEST_CATALOGUE125.json',
            'new125/response125_body.tex','new119/historical_response119_body.tex',
            'new119/additional_response119_body.tex']
    result={
      'schema':'r125-response-map-verification-v1',
      'executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'status':'passed',
      'scope':'Exact source custody and response-route completeness only; no scientific claim or issue closure is inferred.',
      'source_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'genuine_report_bodies_verified':35,'current_original_requests_verified':30,
      'historical_index_records_verified':684,'major_individual_responses_verified':620,
      'overlapping_parent_sections':64,
      'all_closure_claims_false':True,
      'current_evidence_status':current['numerical_evidence_status_at_generation'],
      'inputs_sha256':{name:digest(name) for name in inputs},
    }
    (REV/'provenance/RESPONSE_MAP_VERIFICATION125.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inputs_sha256'}))

if __name__=='__main__':
    run()
