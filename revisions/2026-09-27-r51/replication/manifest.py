from pathlib import Path
import hashlib,json,subprocess,os
R=Path(__file__).resolve().parent.parent;REPO=R.parents[1]
files=[]
for p in sorted(REPO.rglob('*')):
    if not p.is_file():continue
    name=str(p.relative_to(REPO))
    new=name.startswith('revisions/2026-09-27-r51/') and p.name!='MANIFEST.json' and '__pycache__' not in name
    roots=name in ['ECTA_R51.tex','ECTA_R51.pdf','SUPP_R51.tex','SUPP_R51.pdf','RESPONSE_R51.tex','RESPONSE_R51.pdf','RESPONSE_R51.md','R51_REVIEW.md','R51_BUILD.sh','R51_REPRODUCE.sh','econsocart.cls','econsocart.cfg','SUPP_R50.pdf','RESPONSE_R50.pdf','R48_RECONSTRUCTED_R50.pdf']
    inherited=(name.startswith('revisions/2026-09-26-r50/paper/') and p.suffix=='.tex')
    if new or roots or inherited:files.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'role':'inherited-input' if inherited or p.name in ['SUPP_R50.pdf','RESPONSE_R50.pdf','R48_RECONSTRUCTED_R50.pdf'] else 'revision'})
try:head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
except (subprocess.CalledProcessError,FileNotFoundError):head='local validation; remote commit recorded by publication workflow'
d={'base_commit':'8fb2b5e09610bf596758892cd5ffd5ad83ddb707','source_freeze_commit':'5b9ad94a866f25d4552dce088b677763f4d9ce06','build_input_commit':head,'workflow_run':os.getenv('GITHUB_RUN_ID'),'files':files,'self_hash':'Excluded to avoid a circular content hash; the containing git commit binds this manifest.'}
(R/'MANIFEST.json').write_text(json.dumps(d,indent=2)+'\n')
print('Manifest entries:',len(files))
