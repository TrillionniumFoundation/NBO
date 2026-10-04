"""Audit the scientific reading set, complete populations and exact report replay."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
BASE='3a5bae12938077002d1619a0dd32be6071e9adab'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reading_set(roots):
 files={}
 def visit(p):
  rel=str(p.relative_to(ROOT))
  if rel in files:return
  text=p.read_text();files[rel]=text
  for name in re.findall(r'\\(?:input|include)\{([^}]+)\}',text):
   q=ROOT/name
   if not q.suffix:q=q.with_suffix('.tex')
   if not q.is_file():raise FileNotFoundError(q)
   visit(q)
 for p in roots:visit(p)
 return files

def audit():
 import decision_closure,tables
 cat=decision_closure.make_report();tables.generate()
 old=reading_set([R/'archive/ECTA.tex',R/'archive/supp.tex',R/'archive/applications.tex'])
 new=reading_set([ROOT/'ECTA.tex',ROOT/'supp.tex',R/'applications.tex'])
 def labels(files):return set(re.findall(r'\\label\{([^}]+)\}','\n'.join(files.values())))
 lo,ln=labels(old),labels(new)
 if not lo<=ln:raise ValueError('Lost labels '+str(sorted(lo-ln)))
 pattern=r'\\begin\{(theorem|proposition|lemma|corollary|assumption|definition|proof|algorithm)\}(.*?)\\end\{\1\}'
 def blocks(files):return Counter(hashlib.sha256((kind+'\0'+body).encode()).hexdigest() for text in files.values() for kind,body in re.findall(pattern,text,re.S))
 bo,bn=blocks(old),blocks(new)
 if bo-bn:raise ValueError('Mathematical or proof block removed/changed without preservation')
 out=R/'results/RISK_REPORT_REPLAY.json'
 with (R/'results/RISK_REPLAY.log').open('w') as log:
  subprocess.run([sys.executable,str(ROOT/'revisions/2026-10-05-r17/code/contrast_risk.py'),'report','--root',str(ROOT/'revisions/2026-10-05-r17/results/contrast_risk'),'--out',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 original=ROOT/'revisions/2026-10-05-r17/results/RISK_REPORT.json'
 if original.read_bytes()!=out.read_bytes():raise ValueError('Independent risk replay differs')
 risk=json.loads(out.read_text());rows=risk['rows']
 counts={'nbo_lower_risk':sum(x['upper']<0 for x in rows),'raw_lower_risk':sum(x['lower']>0 for x in rows),'unresolved':sum(x['lower']<=0<=x['upper'] for x in rows)}
 if not risk['complete'] or len(rows)!=24 or sum(counts.values())!=24:raise ValueError('Risk attrition')
 if len(cat['rows'])!=8 or sum(x['candidate_count'] for x in cat['rows'])!=128:raise ValueError('Catalogue attrition')
 for tag,folder in [('R17','revisions/2026-10-05-r17/code'),('CLOSURE','revisions/2026-10-05-r18/code')]:
  with (R/f'results/{tag}_TESTS.log').open('w') as log:
   subprocess.run([sys.executable,'-m','unittest','discover','-s',folder,'-p','test_*.py','-v'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 response=(R/'manuscript/response_body.tex').read_text()
 ids=[f'B{i}' for i in range(1,9)]+[f'M{i}' for i in range(1,11)]
 if any(response.count('\\label{resp:'+i+'}')!=1 for i in ids):raise ValueError('Incomplete response map')
 abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',(ROOT/'ECTA.tex').read_text(),re.S)[1]
 words=len(abstract.split())
 if words>150:raise ValueError('Abstract exceeds 150 whitespace-delimited words')
 report=dict(complete=True,base=BASE,inherited_label_count=len(lo),current_label_count=len(ln),inherited_mathematical_proof_block_count=sum(bo.values()),current_mathematical_proof_block_count=sum(bn.values()),all_inherited_labels_and_blocks_preserved=True,old_reading_files=len(old),current_reading_files=len(new),risk_replay_byte_identical=True,risk_sha256=digest(original),risk_comparisons=counts,all_risk_comparisons_retained=len(rows),catalogue_records=128,new_simulation_observations=0,catalogue_analysis='post-freeze deterministic closure',abstract_whitespace_words=words,referee_response_ids=ids,confidence=dict(menu_payoff_failure=.018,risk_failure=.01,joint_menu_payoff_risk_failure_upper=.028,all_prior_families_plus_risk_failure_upper=.06),original_roots={str(p.relative_to(ROOT)):digest(p) for p in (R/'archive').iterdir() if p.is_file()},source_sha256={p:digest(ROOT/p) for p in new})
 (R/'results/SCIENTIFIC_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))
 return report
if __name__=='__main__':audit()
