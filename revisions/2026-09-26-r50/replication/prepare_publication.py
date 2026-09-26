"""Reconstruct the historical article without altering the reviewed source paths."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent.parent;REPO=ROOT.parents[1]
def main():
 old=REPO/'revisions/2026-09-26-r48/paper';dest=ROOT/'paper/archive_r48';dest.mkdir(parents=True,exist_ok=True)
 for name in ['appendix.tex','duality.tex','finite.tex']:
  (ROOT/'paper'/name).write_text((old/name).read_text().replace('revisions/2026-09-26-r48/paper','revisions/2026-09-26-r50/paper'))
 report=[]
 for p in sorted(old.glob('*.tex')):
  s=p.read_text();new=s.replace('revisions/2026-09-26-r48/paper','revisions/2026-09-26-r50/paper/archive_r48')
  (dest/p.name).write_text(new);report.append({'original':str(p.relative_to(REPO)),'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archived':str((dest/p.name).relative_to(REPO)),'only_change':'TeX input-path relocation'})
 (ROOT/'PRESERVATION.json').write_text(json.dumps({'review_commit':'73a4f708581834692b817649ba5538b640b9e58d','reviewed_manuscript_commit':'77b90a92250694271265e91f9624b7d6aacb0dea','files':report,'tables':'reconstructed from unchanged original result fractions'},indent=2)+'\n')
if __name__=='__main__':main()
