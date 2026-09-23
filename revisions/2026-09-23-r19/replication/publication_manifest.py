"""Pin provenance and fail on modification of any inherited tracked file."""
from pathlib import Path
import subprocess,json,hashlib,os,datetime
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19'
REVIEW='074849b9aad1812b59e25e1d3833383ed11aa401';INPUT='b937ba65111cd2687401cb5d61d3fda3c5567bb5';PROTOCOL='2e19256c5d40f7f0d090cccd6d86892958ae2147'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    git=(ROOT/'.git').exists()
    if git:
        raw=subprocess.check_output(['git','ls-tree','-rz',REVIEW],cwd=ROOT)
        entries=[]
        for item in raw.split(b'\0'):
            if not item:continue
            header,path=item.split(b'\t',1);mode,typ,blob=header.decode().split();path=path.decode()
            if typ!='blob':continue
            p=ROOT/path
            actual=subprocess.check_output(['git','hash-object',str(p)],cwd=ROOT,text=True).strip()
            if actual!=blob:raise RuntimeError('Inherited file modified: '+path)
            entries.append({'path':path,'git_blob_sha1':blob,'sha256':h(p)})
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    else:
        # Local checkout is an immutable GitHub git-archive snapshot, not a git clone.
        baseline=json.loads(Path('/mnt/data/r19_original_hashes.json').read_text());entries=[]
        for path,expected in baseline.items():
            p=ROOT/path
            if h(p)!=expected:raise RuntimeError('Archived input modified: '+path)
            entries.append({'path':path,'sha256':expected})
        source=os.environ.get('SOURCE_COMMIT','local-materialization-of-'+INPUT)
    (R/'PRESERVATION.json').write_text(json.dumps({'review_commit':REVIEW,'count':len(entries),'status':'ALL_INPUT_FILES_UNCHANGED','files':entries},indent=2)+'\n')
    artifacts=[]
    for p in sorted(R.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name=='PUBLICATION_MANIFEST.json' or 'publication' in p.parts:continue
        artifacts.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':h(p)})
    for n in ['ECTA_R19.tex','ECTA_R19.pdf','SUPP_R19.tex','SUPP_R19.pdf','RESPONSE_R19.tex','RESPONSE_R19.pdf','R19_REVIEW.md']:
        p=ROOT/n;artifacts.append({'path':n,'bytes':p.stat().st_size,'sha256':h(p)})
    result={'review_commit':REVIEW,'reviewed_manuscript_commit':'49d286a174a7d3f71293adc920284584673f390b','input_snapshot_commit':INPUT,
      'pre_execution_protocol_commit':PROTOCOL,'publication_source_commit':source,'publication_commit':'the commit containing this manifest; deliberately not self-referential',
      'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preserved_file_count':len(entries),'artifacts':artifacts,
      'scientific_scope':{'policy_progress':'verified on K at t=0,k=2','reference_neural_target':'all five new seeds below 0.01',
      'full_domain_feedback_0.01':'not established; original objective retained','global_sharp_MC_SL_frontier':'not established',
      'nonlinear_work':'finite predeclared query sets and tolerances; not universal speedup'},'formal_mathematical_verification':False}
    (R/'PUBLICATION_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n');print('PRESERVED',len(entries),'ARTIFACTS',len(artifacts))
if __name__=='__main__':main()
