"""Gate the reading edition on immutable history, labels, reports and build.

The gate certifies publication integrity, not acceptance or closure of every
empirical referee concern. All four registered families are complete, while
method rankings and optimality claims retain their proved scope.
"""
import hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'revisions/2026-10-04-r16/publication'
R16='revisions/2026-10-04-r16/'
BASE='1cb3cc9efe135966ec228dfaf51c6841a6dfc97c'
SIGNED='d74c20877b27b5c4a94d41bac3ec16e9fa5da497'
REPLICATION='2f17d8163a1d1d6b72a32b6ea6d6b683dc62031e'
MENU_SOURCE='503a724817899105a78f8c2fd516f417efb6b483'
MENU_EVIDENCE='103b6717dac939cb9cd18876f56d889c9e2a751d'
ROBUSTNESS_EVIDENCE='0b0b113b8c249d916daf0da22808180ce15caa2f'

def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def tree(ref):
 out={}
 for line in git('ls-tree','-rz','--full-tree',ref).split(b'\0'):
  if line:
   meta,name=line.split(b'\t',1);mode,kind,sha=meta.split()
   if kind==b'blob':out[name.decode()]=(mode.decode(),sha.decode())
 return out

def labels(text):return set(re.findall(r'\\label\{([^}]+)\}',text))
def reachable(path,seen=None):
 seen=set() if seen is None else seen
 if path in seen:return seen
 seen.add(path);text=(ROOT/path).read_text()
 for name in re.findall(r'\\input\{([^}]+)\}',text):
  if not name.endswith('.tex'):name+='.tex'
  reachable(name,seen)
 return seen

def main():
 stage=git('write-tree').decode().strip();before=tree(BASE);now=tree(stage)
 changed={p for p,b in before.items() if now.get(p)!=b}
 assert changed=={'ECTA.tex','supp.tex','README.md'},changed
 for p in changed:assert now['revisions/2026-10-04-r16/publication/archive/'+p]==before[p],p
 immutable={}
 for source,paths in [
  (SIGNED,[R16+'results/signed_mechanism',R16+'results/signed_mechanism_summary']),
  (REPLICATION,[R16+'results/replication',R16+'results/replication_summary']),
  (MENU_SOURCE,[R16+'code',R16+'protocols',R16+'manuscript']),
  (MENU_EVIDENCE,[R16+'results/continuation_menu',R16+'results/continuation_menu_summary']),
  (ROBUSTNESS_EVIDENCE,[R16+'results/robustness',R16+'results/robustness_summary'])]:
  for p in paths:
   subprocess.run(['git','diff','--exit-code',source,stage,'--',p],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
   immutable[p]={'source_commit':source,'tree':git('rev-parse',source+':'+p).decode().strip()}
 roots=['ECTA.tex','supp.tex'];original_roots=[]
 for name in roots:
  original_roots.append(git('show',BASE+':'+name).decode())
 all_original_labels=set()
 for p in (ROOT/'revisions/2026-10-04-r15/manuscript').glob('*.tex'):
  if p.name!='response_body.tex':all_original_labels|=labels(p.read_text())
 current_sources=reachable('ECTA.tex')|reachable('supp.tex')
 assert R16+'publication/manuscript/abstract.tex' in current_sources
 assert (P/'manuscript/abstract.tex').read_bytes()==(P/'editorial/abstract.tex').read_bytes()
 current_labels=set()
 for p in current_sources:current_labels|=labels((ROOT/p).read_text())
 missing=sorted(all_original_labels-current_labels)
 # Some editorial helper files may not have been included even in R15. Require
 # every label of the actually compiled R15 article/supplement, not orphan files.
 old_reachable=set()
 def old_visit(path):
  if path in old_reachable:return
  old_reachable.add(path);s=git('show',BASE+':'+path).decode()
  for n in re.findall(r'\\input\{([^}]+)\}',s):old_visit(n if n.endswith('.tex') else n+'.tex')
 for name in roots:old_visit(name)
 required=set()
 for p in old_reachable:required|=labels(git('show',BASE+':'+p).decode())
 assert not required-current_labels,sorted(required-current_labels)
 comp=json.loads((P/'results/COMPILATION.json').read_text())
 for name,v in comp.items():
  assert v['pages']>0 and not any(v[k] for k in ['undefined','multiply_defined','duplicate_destinations','overfull_hbox_pt']), (name,v)
  assert hashlib.sha256((P/'build'/f'{name}.pdf').read_bytes()).hexdigest()==v['pdf_sha256']
 completed={}
 for family,path in [('signed',R16+'results/signed_mechanism/FINAL_AUDIT.json'),('replication',R16+'results/replication_summary/FINAL_AUDIT.json'),('continuation_menu',R16+'results/continuation_menu_summary/FINAL_AUDIT.json'),('strengthened_hjb',R16+'results/robustness_summary/FINAL_AUDIT.json')]:
  a=json.loads((ROOT/path).read_text());assert a['complete'] is True
  completed[family]=a
 reading=json.loads((P/'results/COMPLETED_EVIDENCE_READING_AUDIT.json').read_text())
 assert reading['complete'] is True
 checks=P/'checks/remote'
 expected={'signed_tests.py':12,'menu_tests.py':17,'menu_verification_tests.py':12,'menu_pipeline_tests.py':10,'menu_transport_tests.py':8,'robustness_tests.py':11,'test_decision_value.py':8}
 for name,count in expected.items():
  t=(checks/(name+'.stdout')).read_text(errors='replace')
  assert f'Ran {count} tests' in t and re.search(r'\nOK\s*$',t),name
 strong=json.loads((checks/'STRONG_HJB.json').read_text());assert strong['status']=='passed'
 source=os.environ['NBO_R16_PUBLICATION_SOURCE']
 scientific=json.loads((P/'COMMENT_STATUS.json').read_text())
 audit={'schema':'nbo-r16-publication-integrity-v2','publication_integrity_passed':True,
   'publication_source_commit':source,'reviewed_commit':BASE,
   'review_commit':'cb4595bbcc7147e47e44ba40cb2f5034510ae19f',
   'preceding_blobs_checked':len(before),'preceding_blobs_unchanged_at_original_path':len(before)-3,
   'root_replacements_preserved_exactly':sorted(changed),'original_compiled_labels_preserved':len(required),
   'current_compiled_labels':len(current_labels),'current_tex_source_files':len(current_sources),
   'immutable_scientific_subtrees':immutable,'completed_family_audits':completed,
   'all_four_registered_evidence_families_complete':True,
   'completed_evidence_reading_audit':reading,
   'unit_tests_passed':sum(expected.values()),'unit_test_counts':expected,
   'strong_hjb_manufactured_checks':strong,'compilation':comp,
   'scientific_comment_status':scientific,
   'all_empirical_referee_concerns_closed':False,
   'scope':'Integrity, mathematical checks and completed evidence; not editorial acceptance or a claim of universal NBO dominance.'}
 (P/'FINAL_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
 manifest={}
 for p in sorted(P.rglob('*')):
  if p.is_file() and p.name!='PUBLICATION_MANIFEST.json' and p.suffix not in ['.aux','.out','.bbl','.blg']:
   manifest[str(p.relative_to(ROOT))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 (P/'PUBLICATION_MANIFEST.json').write_text(json.dumps({'publication_source_commit':source,'files':manifest},indent=2)+'\n')
 print(json.dumps({k:audit[k] for k in ['publication_integrity_passed','preceding_blobs_checked','original_compiled_labels_preserved','unit_tests_passed','all_empirical_referee_concerns_closed']},indent=2))
if __name__=='__main__':main()
