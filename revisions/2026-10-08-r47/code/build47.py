"""Offline manuscript rebuild and frozen-evidence audit; never rerun scientific clocks."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1];ROOT=R.parent.parent;BASE=R.parent/'2026-10-07-r46'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run(args,log,env=None,cwd=R):
    with log.open('w') as f:p=subprocess.run(args,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError(f'{args}: inspect {log}')
    return log.read_text(errors='replace')

def main(preview=False):
    (R/'audit').mkdir(exist_ok=True);(R/'build').mkdir(exist_ok=True)
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):env[k]='1'
    run([sys.executable,str(R/'code/assemble47.py')],R/'audit/assemble47.log',env)
    run([sys.executable,str(R/'code/audit47.py')],R/'audit/reconstruct47.log',env)
    env['PYTHONPATH']=os.pathsep.join([str(R.parent/'2026-10-07-r45/preserved/R41/code'),str(R.parent/'2026-10-07-r45/preserved/R41/vendor/r38/code'),env.get('PYTHONPATH','')])
    tests=[]
    for version,root,pattern,count in [('R47',R,'tests.py',15),('R46',BASE,'tests.py',14),('feasible46',BASE,'test_feasible.py',8),('R45',R.parent/'2026-10-07-r45','tests.py',13),('R44',R.parent/'2026-10-07-r44','tests.py',14)]:
        log=R/'audit'/f'regression-{version}.log'
        s=run([sys.executable,'-m','unittest','discover','-s',str(root/'code'),'-p',pattern,'-v'],log,env)
        match=re.search(r'Ran (\d+) tests?',s);assert match and int(match[1])==count,(version,s[-1000:])
        assert re.search(r'\nOK\s*$',s),version
        tests.append({'name':version,'tests':count,'successful':True,'log':str(log.relative_to(R))})
    for k in ('TEXINPUTS','BIBINPUTS','BSTINPUTS'):env[k]=str(R)+':'+env.get(k,'')
    if preview:
        extra=r'''
\bibitem[\protect\citeauthoryear{Brumm and Scheidegger}{Brumm and Scheidegger}{2017}]{brumm2017}
\textsc{Brumm, Johannes and Simon Scheidegger} (2017): ``Using Adaptive Sparse Grids to Solve High-Dimensional Dynamic Models,'' \emph{Econometrica}, 85 (5), 1575--1612.

\bibitem[\protect\citeauthoryear{Felzenszwalb and Huttenlocher}{Felzenszwalb and Huttenlocher}{2012}]{felzenszwalb2012}
\textsc{Felzenszwalb, Pedro F. and Daniel P. Huttenlocher} (2012): ``Distance Transforms of Sampled Functions,'' \emph{Theory of Computing}, 8 (19), 415--428.
'''
        for name in ('ECTA','supp'):
            s=(BASE/'build'/f'{name}.bbl').read_text().replace(r'\end{thebibliography}',extra+'\n'+r'\end{thebibliography}')
            (R/'build'/f'{name}.bbl').write_text(s)
    for iteration in range(3):
        for name in ('ECTA','supp','response'):
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(name+'.tex'))],R/'audit'/f'latex47-{name}-{iteration}.log',env)
            if iteration==0 and not preview and r'\bibdata' in (R/'build'/(name+'.aux')).read_text():
                run([shutil.which('bibtex.original') or 'bibtex','build/'+name],R/'audit'/f'bib47-{name}.log',env)
    documents=[]
    for name in ('ECTA','supp','response'):
        s=(R/'build'/(name+'.log')).read_text(errors='replace')
        bad=[line for line in s.splitlines() if ('undefined' in line.lower() and ('reference' in line.lower() or 'citation' in line.lower())) or any(w in line for w in ('multiply-defined labels','Missing character:','Overfull \\hbox','Overfull \\vbox'))]
        assert not bad,(name,bad)
        info=subprocess.check_output(['pdfinfo',str(R/'build'/(name+'.pdf'))],text=True)
        pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
        documents.append({'document':name,'pages':pages,'sha256':H(R/'build'/(name+'.pdf')),'undefined_references':0,'duplicate_labels':0,'missing_characters':0,'overfull_boxes':0})
    result={'revision':'R47 executed comparisons','preview_only':preview,'review_commit':'0bf1ff6060bb9211762f191b6ead306ae4725beb',
        'manuscript_baseline':'c3930399e3b8267451096d0e70ea67f49510065e','study_source_commit':'0cbc5138373923eb282114532fc5624daeb863ba',
        'study_run':37701989313,'study_artifact':11517677897,'study_artifact_sha256':'9ef9bb39be0cb7291cf467e47e5af5f2e8adf27e4f09ac2b74879d5e6a6759e2',
        'publication_source_commit':os.environ.get('GITHUB_SHA','local-preview'),'publication_run':os.environ.get('GITHUB_RUN_ID'),
        'tests':tests,'total_tests':sum(t['tests'] for t in tests),'compilation':documents,
        'reconstruction':json.loads((R/'audit/PUBLICATION_SUMMARY.json').read_text()),'peer_or_editorial_approval':False}
    (R/'audit/RELEASE_AUDIT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    manifest={str(p.relative_to(R)):H(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='FILES_SHA256.json' and p.suffix!='.pyc'}
    (R/'audit/FILES_SHA256.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'tests':result['total_tests'],'documents':documents,'preview_only':preview},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');main(p.parse_args().preview)
