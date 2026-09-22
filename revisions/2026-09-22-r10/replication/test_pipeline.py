"""Synthetic fault injection: these are pipeline tests, NOT scientific executions."""
import hashlib,json,pathlib,shutil,tempfile
from collect_evidence import collect,REV

def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def fixture(root,source):
    for k in (.5,2.,8.):
        tag=f'k{k:g}';c=root/f'r10-cell-{tag}';c.mkdir(parents=True)
        for stem in ('actor','dual_pilot','policy_certificate','flexible_dual'):
            p=REV/'results'/f'{stem}_{tag}.json';shutil.copy2(p,c/p.name)
        s={'cell':tag,'source_commit':source,'status':'success','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in c.iterdir()}}
        write(c/'status.json',s)
def run():
    outcomes=[]
    for case in ('complete','missing','failed','nonfinite','wrong_source','changed_input'):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);inputs=root/'in';source='synthetic-source-not-an-execution';fixture(inputs,source)
            c=inputs/'r10-cell-k2';s=json.loads((c/'status.json').read_text())
            if case=='missing':shutil.rmtree(c)
            elif case=='failed':s['status']='failed';write(c/'status.json',s)
            elif case=='wrong_source':s['source_commit']='wrong';write(c/'status.json',s)
            elif case in ('nonfinite','changed_input'):
                name='flexible_dual_k2.json' if case=='nonfinite' else 'actor_k2.json'
                p=c/name;x=json.loads(p.read_text())
                if case=='nonfinite':x['total_seconds']=float('nan')
                else:x['c'][0]=.1
                write(p,x);s['files'][name]=hashlib.sha256(p.read_bytes()).hexdigest();write(c/'status.json',s)
            r=collect(inputs,root/'out',source)
            assert r['status']==('PASS' if case=='complete' else 'FAIL')
            assert len(r['cells'])==3 and (root/'out/ci_recheck.json').is_file()
            assert (root/'out/k0.5/policy_certificate_k0.5.json').is_file()
            if case=='nonfinite':assert 'NaN' in (root/'out/k2/flexible_dual_k2.json').read_text()
            if case=='failed':assert json.loads((root/'out/k2/status.json').read_text())['status']=='failed'
            outcomes.append({'case':case,'passed':True,'scientific_execution':False})
    result={'status':'PASS','cases':outcomes,'scope':'synthetic fault injection only'}
    (REV/'pipeline_tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run()
