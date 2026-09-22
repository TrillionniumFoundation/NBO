"""Validate preserved source identity, complete raw evidence, and publication files."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,subprocess
import numpy as np
from scipy.stats import binomtest
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r11'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def run(skip_pdf=False):
 baseline=json.loads((REV/'inherited_manifest.json').read_text());repl=baseline['archived_replacement']
 for p,h in baseline['files'].items():assert sha(ROOT/repl.get(p,p))==h,('historical_file_changed',p)
 old=(REV/'archive/REVISION_INDEX_before_R11.md').read_bytes();assert (ROOT/'REVISION_INDEX.md').read_bytes().startswith(old)
 raw=(REV/'review_input/referee_report.md').read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='42cee0954515e5578dc579a4ca0428bb4e399b2e'
 summary=json.loads((REV/'results/robustness/summary.json').read_text());assert summary['status']=='PASS' and len(summary['rows'])==3
 for row in summary['rows']:
  d=row['dimension'];folder=REV/f'results/robustness/d{d}'
  assert (folder/'author_commit.txt').read_text().strip()=='991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a'
  assert (folder/'author_source_diff.txt').read_text()==''
  tuning=json.loads((folder/'tuning/tuning.json').read_text());assert len(tuning['rows'])==56
  assert not tuning['failures'] and all(r['status']=='success' for r in tuning['rows'])
  for m in ['nbo','soc']:assert len([r for r in tuning['rows'] if r['method']==m])==28
  vals=[]
  for seed in range(1820,1832):
   r=json.loads((folder/f'holdout/seed_{seed}.json').read_text());assert r['status']=='success' and r['source_commit']==summary['source_commit']
   assert r['methods']['nbo']['initial_hash']==r['methods']['soc']['initial_hash']
   with np.load(folder/f'holdout/seed_{seed}_paths.npz') as z:
    assert set(z.files)=={'nbo','soc','lq'}
    for m in z.files:
     assert len(z[m])==4096 and np.isfinite(z[m]).all()
     assert abs(z[m].mean()-r['methods'][m]['mean_cost'])<1e-12
    v=float((z['nbo']-z['soc']).mean());assert abs(v-r['paired_difference'])<1e-12;vals.append(v)
  assert np.max(np.abs(np.array(vals)-row['raw_differences']))<1e-12
  p=binomtest(sum(x<0 for x in vals),12,.5,alternative='greater').pvalue
  assert abs(min(1.,3*p)-row['bonferroni_three_p'])<1e-15
 accuracy=json.loads((REV/'results/accuracy/summary.json').read_text());assert accuracy['status']=='PASS' and len(accuracy['rows'])==30
 assert len(accuracy['matched_accuracy_frontier'])==30
 for r in accuracy['matched_accuracy_frontier']:
  if r['attained']:assert r['first']['absolute_regret'][1]<=r['target']
 tests=json.loads((REV/'validation_tests.json').read_text());assert tests['status']=='PASS'
 report={'status':'PASS','historical_files_preserved':len(baseline['files']),'review_blob':'42cee0954515e5578dc579a4ca0428bb4e399b2e','holdout_pairs_recomputed':36,'tuning_trials_retained':168,'accuracy_policies':30,'accuracy_target_records':30,'tests':len(tests['checks']),'pdf_checked':not skip_pdf}
 if not skip_pdf:
  for stem in ['ECTA_R11','SUPP_R11']:
   p=ROOT/f'{stem}.pdf';assert p.is_file()
   info=subprocess.check_output(['pdfinfo',str(p)],text=True);pages=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert pages>0
   text=subprocess.check_output(['pdftotext',str(p),'-'],text=True)
   assert 'Neural Bellman Operators' in text or 'NEURAL BELLMAN OPERATORS' in text
   report[stem]={'pages':pages,'sha256':sha(p)}
   log=(REV/f'build_logs/{stem}.log').read_text(errors='replace')
   for bad in ['Overfull \\hbox','undefined references','undefined citations','multiply defined','! LaTeX Error','! Undefined control sequence']:assert bad not in log,(stem,bad)
  assert report['ECTA_R11']['pages']>=40 and report['SUPP_R11']['pages']>=105
  main=subprocess.check_output(['pdftotext',str(ROOT/'ECTA_R11.pdf'),'-'],text=True)
  assert '0.00952' in main or '.00952' in main
 report['residual_typesetting_notice']='The inherited class emits an empty frontmatter anchor notice; no overfull boxes or unresolved cross-references are accepted.'
 dump(REV/'validation_report.json',report);print(json.dumps(report,indent=2));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--skip-pdf',action='store_true');a=p.parse_args();run(a.skip_pdf)
