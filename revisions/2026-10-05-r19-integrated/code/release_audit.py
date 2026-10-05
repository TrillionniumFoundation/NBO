"""Bind complete evidence, exact certificate replay, source retention and native PDFs."""
from pathlib import Path
import hashlib,json,re,sys,subprocess
from study import verify_freeze
R=Path(__file__).resolve().parents[1]
ROOT=R.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    frozen=verify_freeze()
    report=json.loads((R/'results/REPORT_AUDIT.json').read_text())
    preservation=json.loads((R/'results/PRESERVATION.json').read_text())
    compilation=json.loads((R/'results/COMPILATION.json').read_text())
    replay=json.loads((R/'results/CERTIFICATE_REPLAY.json').read_text())
    summary=R/'results/registered/SUMMARY.json'
    data=json.loads(summary.read_text())
    assert report['completed']==report['expected']==252 and not report['failures']
    assert report['all_record_checks'] and preservation['all_preserved']
    assert replay['summary_sha256']==digest(summary)
    assert replay['freeze_sha256']==frozen and replay['complete_services']==252
    assert replay['all_certificate_fields_exactly_reproduced']
    expected_stages=sum(len(row['stages']) for row in data['records'])
    expected_points=sum(row['queries']*len(row['stages']) for row in data['records'])
    assert replay['stages_replayed']==expected_stages and replay['task_certificates_replayed']==expected_points
    nbo=[row for row in data['records'] if row['method']=='NBO']
    assert len(nbo)==36 and all(row['status']=='certified' for row in nbo)
    response=json.loads((R/'RESPONSE_MAP.json').read_text())
    assert len(response['comments'])==18
    assert {x['id'] for x in response['comments']}=={f'B{i}' for i in range(1,9)}|{f'M{i}' for i in range(1,11)}
    units=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(R/'code'),'-p','test*.py','-v'],cwd=ROOT,capture_output=True,text=True)
    log=units.stdout+units.stderr
    (R/'results/UNIT_TESTS.log').write_text(log)
    assert units.returncode==0 and 'Ran 34 tests' in log and not re.search(r'\bskipped\b|\bFAIL\b|\bERROR\b',log)
    assert len(compilation['documents'])==4 and compilation['class_name']=='econsocart'
    for rec in compilation['documents']:
        assert not any(rec[k] for k in ('undefined','multiply_defined','duplicate_destination','missing_character'))
        assert max(rec['overfull_hbox']+rec['overfull_vbox']+[0])<=1
        assert digest(R/'build'/f"{rec['document']}.pdf")==rec['pdf_sha256']
    inputs={}
    for p in sorted(R.rglob('*')):
        if p.is_file() and p.suffix in {'.py','.tex','.bib','.json'} and 'build' not in p.parts and 'results' not in p.parts:
            inputs[p.relative_to(R).as_posix()]=digest(p)
    result={'freeze_sha256':frozen,'summary_sha256':digest(summary),'outcomes':report,
        'NBO_certified_services':36,'NBO_maximum_mean_regret_upper':max(x['final_certificate_upper'] for x in nbo),
        'certificate_replay':replay,'unit_tests':{'passed':34,'skipped':0,'log_sha256':digest(R/'results/UNIT_TESTS.log')},
        'response_items':18,'preservation':{'source_files_checked':preservation['source_files_checked'],'all_preserved':True},
        'native_compilation':compilation,'revision_source_sha256':inputs,
        'evidence_unit':'Three complete streams. A repeated run is a replay, not additional independent streams.',
        'interpretation':'Finite stored-law scalar-interval accuracy. The complete original vector-menu, diffusion, recursive-utility and game materials remain, with their original distinct scope.'}
    (R/'results/RELEASE_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='revision_source_sha256'},indent=2))
if __name__=='__main__':main()
