"""Compile a materialized review object and fail closed on evidence mismatches."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, gzip, hashlib, json, math, os, re, subprocess, sys
P=Path(__file__).resolve().parent.parent;ROOT=P.parents[1];R=P/'results';LOG=P/'build_logs'
BASE='bb09ac177fc766aea8aba26cb6a40b8aff68528c'
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main(local=False):
    LOG.mkdir(exist_ok=True)
    subprocess.run([sys.executable,str(P/'replication/generate_tables.py')],cwd=ROOT,check=True)
    summary=read('paper_summary.json');assert summary['original_neural_checkpoints']==20 and summary['inventory_checkpoints']==20
    assert summary['classical_candidates']==6 and summary['mpfr_nodes']==18
    # Current prose states these distinctions; changed outcomes require a reviewed text revision.
    assert not summary['original_neural_target_met'] and not summary['classical_target_met']
    assert summary['fresh_gap']<.01 and summary['mpfr_gap']<.01 and summary['inventory_final_max_per_coordinate']<.001
    for seed in range(16100,16110):
        for step in (800,2400):
            f=R/f'neural/seed{seed}/certificate{step}.json';r=json.loads(f.read_text())
            model=f.parent/f'network_step{step:04d}.json'
            assert r['network_sha256']==sha(model)
            assert r['failed_cells']==r['skipped_cells']==0 and r['boundary_budget']==0
            assert math.isfinite(r['t0_regret_upper']) and r['t0_regret_upper']>=0
            assert r['interior_cells']==math.prod(r['grid'])
            assert f.with_suffix('.cells.json.gz').is_file()
    for r in read('inventory/summary.json'):
        f=R/f"inventory/network_s{r['seed']}_n{r['step']}.json"
        assert r['network_sha256']==sha(f) and r['failed_cells']==r['skipped_cells']==0
        assert r['per_coordinate_regret_upper']>=0 and math.isfinite(r['per_coordinate_regret_upper'])
        assert [x['d'] for x in r['dimensions']]==[4,8,16,32,64,128]
    for r in read('baselines/summary.json'):
        assert (ROOT/r['policy_file']).is_file() and r['failed_cells']==r['skipped_cells']==0
    assert len(read('fresh_library/attempts.json'))==summary['fresh_nodes']
    assert all(x['status']=='completed' for x in read('fresh_library/attempts.json'))
    assert all(x['status']=='completed' for x in read('mpfr_library/attempts.json'))
    assert read('foundation_checks.json')['kernel_tests']['exact_rational_checks']==450
    if not local:
        assert read('pipeline_resources.json')['status']=='completed'
        assert all(x['returncode']==0 for x in read('pipeline_attempts.json'))
        assert len(read('pipeline_attempts.json'))==4
        env=read('execution_environment.json');assert env['source_commit']
        for path,digest in env['source_sha256'].items():assert sha(ROOT/path)==digest,('scientific source changed',path)
        changes=git('diff','--name-status',BASE,'--').splitlines()
        historical=[line for line in changes if line.split('\t')[0] in ['M','D','T','R'] and not line.endswith('\tREVISION_INDEX.md')]
        assert not historical,('historical tracked file changed',historical)
        old_index=subprocess.check_output(['git','show',BASE+':REVISION_INDEX.md'],cwd=ROOT)
        assert old_index==(P/'archive/REVISION_INDEX_R14.md').read_bytes()
        oldpaths=git('ls-tree','-r','--name-only',BASE).splitlines()
        preservation={'review_base_commit':BASE,'historical_tracked_paths':len(oldpaths),'historical_scientific_files_changed':[],
          'only_replaced_historical_path':'REVISION_INDEX.md','old_index_archived_byte_for_byte':True,
          'all_historical_review_and_scientific_paths_retained':True,'validation':'git diff against immutable review input; no historical modification except current index'}
        (P/'PRESERVATION_MANIFEST.json').write_text(json.dumps(preservation,indent=2)+'\n')
    pdfs=[]
    for name in ['ECTA_R16','SUPP_R16']:
        for i in range(1,4):
            with (LOG/f'{name}_pass{i}.log').open('w') as f:
                subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
        log=(ROOT/(name+'.log')).read_text(errors='replace')
        bad=[s for s in ['undefined references','undefined citations','multiply defined','Overfull','! LaTeX Error'] if s in log]
        assert not bad,(name,bad)
        info=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
        pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
        pdfs.append({'path':name+'.pdf','sha256':sha(ROOT/(name+'.pdf')),'bytes':(ROOT/(name+'.pdf')).stat().st_size,
          'pages':pages,'undefined_references':0,'overfull_boxes':0,'underfull_warnings':log.count('Underfull'),'compile_passes':3})
    manifest={'revision':'R16','revision_date':'2026-09-23','validated_at_utc':datetime.now(timezone.utc).isoformat(),
      'status':'LOCAL_LAYOUT_ONLY' if local else 'VALIDATED_MATERIALIZED_PUBLICATION','review_base_commit':BASE,
      'publication_input_commit':None if local else git('rev-parse','HEAD'),
      'scientific_source_commit':None if local else read('execution_environment.json')['source_commit'],
      'scientific_result_commit':os.environ.get('R16_RESULT_COMMIT'),
      'pdfs':pdfs,'scientific_summary':summary,
      'claims_not_made':['original nonlinear neural regret below .01','matched-.01 nonlinear neural/classical superiority','generic dimension-free nonlinear HJB certification','machine-library tanh or simulator correctness'],
      'files':{str(f.relative_to(ROOT)):sha(f) for f in sorted(P.rglob('*')) if f.is_file() and f.suffix in ['.py','.c','.tex','.json','.md','.gz','.npz'] and f.name!='PUBLICATION_MANIFEST.json' and '__pycache__' not in f.parts}}
    (P/'PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':manifest['status'],'pdfs':pdfs,'summary':summary},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--local',action='store_true');a=p.parse_args();main(a.local)
