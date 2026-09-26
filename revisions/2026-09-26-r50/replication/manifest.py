"""Create a content manifest after successful arithmetic replay and all PDF builds."""
from pathlib import Path
import hashlib,json,subprocess,datetime,sys,platform
ROOT=Path(__file__).resolve().parent.parent;REPO=ROOT.parents[1]
def main():
 verification=json.loads((ROOT/'VERIFICATION.json').read_text());assert verification['valid']
 summaries={}
 for name in ['ECTA_R50','SUPP_R50','RESPONSE_R50','R48_RECONSTRUCTED_R50']:
  p=REPO/f'{name}.pdf';assert p.is_file() and p.stat().st_size>1000
  log=(ROOT/'logs'/f'{name}.log').read_text(errors='replace')
  assert 'Fatal error' not in log and 'undefined references' not in log and 'undefined citations' not in log and 'Overfull \\hbox' not in log,name
  summaries[name]={'pdf_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pdfinfo':subprocess.check_output(['pdfinfo',str(p)]).decode()}
 try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,stderr=subprocess.DEVNULL).decode().strip()
 except subprocess.CalledProcessError:commit='local-source-export; see pinned inherited commits'
 files=[]
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts and 'transport' not in p.parts and p.name!='MANIFEST.json':files.append(p)
 for name in ['ECTA_R50','SUPP_R50','RESPONSE_R50','R48_RECONSTRUCTED_R50']:
  files += [REPO/f'{name}.tex',REPO/f'{name}.pdf']
 files += [REPO/'RESPONSE_R50.md',REPO/'R50_REVIEW.md',REPO/'R50_BUILD.sh',REPO/'R50_REPRODUCE.sh',REPO/'requirements-r50.txt',REPO/'econsocart.cls',REPO/'econsocart.cfg']
 record={'schema':'nbo-r50-publication-manifest-v1','built_from_commit':commit,'review_commit':'73a4f708581834692b817649ba5538b640b9e58d','inherited_r49_commit':'bce0f688dfd0041bc69b858346ef264994d65740','freeze_commit':'62585130b01f1b3479b5fc9f8ee0ee927509633a','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'verification':verification,'pdfs':summaries,'files':{str(p.relative_to(REPO)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}}
 (ROOT/'MANIFEST.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'valid':True,'files':len(files),'pdfs':list(summaries)},indent=2))
if __name__=='__main__':main()
