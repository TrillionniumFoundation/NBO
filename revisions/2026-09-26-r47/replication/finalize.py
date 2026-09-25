"""Create publication identity after all build logs and PDFs have been closed."""
from pathlib import Path
import hashlib,json,subprocess,os
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
BASE='fb88b1122ce5709d36104993937083b57470d1de'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
checks=load(R/'results/r46_recheck.json');w=load(R/'results/independent_witness.json');a=load(R/'results/witness_adversarial.json')
assert checks['passed'] and checks['completed']==checks['expected']==64
assert w['passed'] and w['objects']==64 and a['passed'] and a['mutations']==51
pres=load(R/'history/R45_SOURCE_IDENTITY.json')
for path,h in pres.items():assert sha(ROOT/path)==h,('R45 source altered',path)
gitroot=(ROOT/'.git').exists(); inherited_count=None; source_commit=os.environ.get('GITHUB_SHA','local source snapshot')
if gitroot:
 source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 baseline=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
 changed=subprocess.check_output(['git','diff',BASE,'--name-only','--'],cwd=ROOT,text=True).splitlines()
 bad=sorted(set(baseline)&set(changed));assert not bad,('Inherited files changed',bad)
 inherited_count=len(baseline)
(R/'results/publication_checks.json').write_text(json.dumps(dict(passed=True,r46_objects=64,new_witness_objects=64,rejected_mutations=51,valid_mutation_controls=3,preserved_R45_sources=len(pres),unchanged_baseline_files=inherited_count,base_commit=BASE,source_commit=source_commit),indent=2)+'\n')
files={}
for d in [ROOT/'revisions/2026-09-25-r45',R]:
 for p in d.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.name!='PUBLICATION_MANIFEST.json' and 'input' not in p.relative_to(R if d==R else d).parts:
   files[str(p.relative_to(ROOT))]=sha(p)
for n in ['ECTA','SUPP','RESPONSE','COMPUTATION','HISTORY']:
 for ext in ['tex','pdf']:
  p=ROOT/f'{n}_R47.{ext}';assert p.exists();files[str(p.relative_to(ROOT))]=sha(p)
for n in ['ECTA','SUPP','RESPONSE','HISTORY']:
 for ext in ['tex','pdf']:
  p=ROOT/f'{n}_R45.{ext}';assert p.exists();files[str(p.relative_to(ROOT))]=sha(p)
for n in ['R47_BUILD.sh','R47_REVIEW.md']:
 files[n]=sha(ROOT/n)
manifest=dict(schema='nbo-r47-publication-v1',base_commit=BASE,source_commit=source_commit,review_report_commit='bdfd4e94b74a41ef904158d0061d10a6fcf39c8c',note='Final Git commit identifies the complete review tree. Self-hash and future commit hash are intentionally not embedded.',files=dict(sorted(files.items())))
(R/'PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Publication identity recorded for',len(files),'files.')
