"""Publication manifest, source-preservation and exact-head checks."""
from pathlib import Path
import argparse,subprocess,json,hashlib,re
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
BASE='3175974aed89dac1595af174a201dcae7bcfae31'
NAMES=('ECTA_R30','SUPP_R30','RESPONSE_R30','COMPUTATION_R30','HISTORY_R30')
MAN=R/'PUBLICATION_MANIFEST.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def source_checks():
 data=json.loads((R/'disposition.json').read_text());ids={x['id'] for x in data}
 required={f'R29-SP-{kind}{i}' for kind,n in [('F',17),('T',12)] for i in range(1,n+1)}
 required|={f'R29-{kind}{i}' for kind,n in [('F',16),('T',18),('P',4),('N',12)] for i in range(1,n+1)}
 assert ids==required and len(data)==79
 for name in NAMES:
  log=(ROOT/(name+'.log')).read_text(errors='replace')
  assert all(term not in log for term in ('undefined','Overfull','multiply defined','Fatal error')),name
  assert (ROOT/(name+'.pdf')).stat().st_size>10000
 try:
  baseline=subprocess.check_output(['git','show',BASE+':REVISION_INDEX.md'],cwd=ROOT)
  assert (R/'source_audit/REVISION_INDEX_before_R30.md').read_bytes()==baseline
  changed=git('diff','--name-only',BASE).splitlines()
  for path in changed:
   assert path.startswith(('revisions/2026-09-24-r30/','.github/workflows/r30-','.r30-transfer/')) or path in {'REVISION_INDEX.md','R30_REVIEW.md'} or any(path==n+e for n in NAMES for e in ('.tex','.pdf')),path
 except subprocess.CalledProcessError:
  # A source-export checkout can be checked locally without git metadata.
  assert not (ROOT/'.git').exists()
 return {'review_items':len(data),'documents':list(NAMES)}
def manifest():
 facts=source_checks()
 files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p!=MAN]
 files += [ROOT/(name+ext) for name in NAMES for ext in ('.tex','.pdf')]+[ROOT/'R30_REVIEW.md',ROOT/'REVISION_INDEX.md']
 record={'baseline_review_commit':BASE,'reviewed_manuscript_commit':'788246778893695471015ce4db76e6a61a2c9ca0',
  'original_target':'.01','original_global_bound':'7.181834580823298','original_target_certified':False,
  'facts':facts,'sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}}
 MAN.write_text(json.dumps(record,indent=2)+'\n');print('Manifest files',len(record['sha256']))
def verify():
 m=json.loads(MAN.read_text())
 for p,h in m['sha256'].items():assert sha(ROOT/p)==h,p
 print('Committed publication hash manifest verified:',len(m['sha256']))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['manifest','verify','sources']);args=ap.parse_args()
 if args.mode=='manifest':manifest()
 elif args.mode=='verify':verify()
 else:print(source_checks())
