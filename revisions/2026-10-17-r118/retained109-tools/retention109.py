"""Source-preservation and review/theorem indexes, without invented closure claims."""
from pathlib import Path
import json,hashlib,re,shutil
R=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
base=json.loads((R/'evidence109/BASELINE99_FILES.json').read_text());rows=[]
for rec in base['files']:
 p=R/rec['path'];arc=R/'retained99'/rec['path']
 if p.exists() and h(p)==rec['sha256']:status='unchanged in this revision';dest=rec['path']
 elif arc.exists() and h(arc)==rec['sha256']:status='byte-preserved original entry point';dest=str(arc.relative_to(R))
 elif rec['path'].startswith(('build/','publication/')):status='original publication retained at immutable R99 commit; not relabeled current';dest='git:f78d7fcec9f657dfec56a0af7899fe967948652d:revisions/2026-10-14-r99/'+rec['path']
 else:raise AssertionError('Unaccounted inherited change: '+rec['path'])
 rows.append(dict(rec,status=status,current_location=dest))
# Literal theorem environment inventory is an index, not a proof-validity verdict.
entries=[]
for folder in ('sections','new','new109'):
 for p in sorted((R/folder).glob('*.tex')):
  text=p.read_text()
  for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary)\}(?:\[([^]]*)\])?(.*?)\\end\{\1\}',text,re.S):
   labels=re.findall(r'\\label\{([^}]+)\}',m.group(3))
   entries.append({'path':str(p.relative_to(R)),'file_sha256':h(p),'type':m.group(1),'title':m.group(2),'labels':labels,'line':text[:m.start()].count('\n')+1,'statement_sha256':hashlib.sha256(m.group(0).encode()).hexdigest(),'not_an_independent_proof_verdict':True})
save(R/'evidence109/CONTENT_RETENTION109.json',{'baseline_commit':base['commit'],'files':rows,'split_records':json.loads((R/'evidence109/SECTION_SPLITS109.json').read_text()),'theorem_environment_index':entries,'coverage':'all files in the retrieved complete R99 referee package, every current inherited scientific source, and literal theorem environments; not every historical branch file or experiment independently reverified'})
print('retained baseline files',len(rows),'indexed theorem environments',len(entries))
