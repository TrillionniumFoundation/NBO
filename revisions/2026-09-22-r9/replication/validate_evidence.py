"""Fail-fast validation of the R9 review package and retained numerical claims.
Does not turn Monte Carlo estimates into deterministic certificates.
"""
from __future__ import annotations
import argparse,hashlib,json,math,pathlib,platform,re,subprocess,sys,time
import numpy as np
import torch
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r9';OUT=REV/'results'
CHECKS=[]
def load(p):return json.loads(pathlib.Path(p).read_text())
def require(name,condition,details=None):
 CHECKS.append({'check':name,'passed':bool(condition),'details':details})
 if not condition:raise AssertionError(name+': '+str(details))
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ordered(rows,key):
 vals=[r[key] for r in rows]
 return all(math.isfinite(float(x)) for x in vals) and all(b<a for a,b in zip(vals,vals[1:]))
def run(require_pdf=True):
 start=time.perf_counter();summary=load(OUT/'scientific_summary.json')
 for tag in ['0.5','2','8']:
  a=load(OUT/f'actor_k{tag}.json');p=load(OUT/f'policy_certificate_k{tag}.json');u=load(OUT/f'upper_certificate_k{tag}.json')
  require('original payoff '+tag,a['original_payoff'] and p['original_payoff'] and u['original_payoff'])
  require('continuous deployed controls '+tag,len(a['c'])==len(a['theta'])==len(a['p'])==16 and all(.05<=c<=.8 for c in a['c']) and all(0<=t<=.2 for t in a['theta']) and all(x==0 for x in a['p']))
  require('original initial state '+tag,a['initial']==p['initial']==u['initial']==[0,2,1.25])
  require('strict wealth feasibility '+tag,p['terminal_wealth_interval'][0]>.5,p['terminal_wealth_interval'])
  require('exact exit correction retained '+tag,0<p['exit_probability_upper']<1.077e-31 and p['exit_payoff_correction_upper']>0)
  require('policy interval refinement '+tag,ordered(p['records'],'width'))
  require('all policy enclosures ordered '+tag,all(r['policy_value_interval'][0]<r['policy_value_interval'][1] for r in p['records']))
  require('verified upper trace '+tag,u['f_over_h_lower_bound']>=-8)
  require('every residual ceiling certified '+tag,all(r['ceiling_met'] and r['residual_upper_bound']<=r['requested_residual_ceiling'] for r in u['reports']))
  require('upper residual refinement '+tag,ordered(u['reports'],'residual_upper_bound'))
  v=p['records'][-1]['policy_value_interval'];upper=u['reports'][-1]['upper_value_initial'];s=next(s for s in summary['economy'] if s['k']==float(tag))
  require('value enclosure consistency '+tag,upper>=v[1] and s['optimal_value_interval']==[v[0],upper])
  require('honest flexible precision flag '+tag,not s['precision_target_met'] and s['regret_upper']>.01)
  require('policy budget primitive range '+tag,0<=p['adjustment_budget_interval'][0]<=p['adjustment_budget_interval'][1]<=.02)
 r=load(OUT/'restricted_dual_certificate.json');rp=load(OUT/'policy_certificate_restricted.json')
 require('restricted dual refinement',ordered(r['records'],'width'))
 require('bounded dual source',-8<r['source_floor_lower']<r['source_ceiling_upper']<0)
 ru=r['records'][-1]['restricted_optimal_value_upper'];rl=rp['records'][-1]['policy_value_interval'][0]
 require('restricted optimal-value enclosure below .01',0<ru-rl<.01,{'lower':rl,'upper':ru,'width':ru-rl})
 require('restricted policy exactly no adjustment',all(x==0 for x in load(OUT/'actor_restricted.json')['theta']))
 for s in summary['economy']:
  k=s['k'];lo=s['policy_value_interval'][0]-ru;hi=s['optimal_value_interval'][1]-rl;w=s['optimal_access_welfare_interval']
  require('positive optimal access welfare '+str(k),0<w[0]<=lo and w[1]>=hi, w)
 actions=load(OUT/'action_certificates.json')
 require('complete action dimension/tolerance grid',{(r['dimension'],r['tolerance']) for r in actions}=={(d,t) for d in [8,16,32,64,128] for t in [.001,.00001]})
 for r in actions:
  name=str((r['dimension'],r['tolerance']))
  require('continuous action certificate '+name,r['meets_tolerance'] and 0<=r['upper_bound']-r['lower_bound']<=r['gap']<=r['tolerance'] and all(-1<=a<=1 for a in r['action']))
  require('action work count '+name,r['scalar_inner_problems']==r['dimension']*r['node_evaluations'])
 for r in load(OUT/'neural_jet_certificates.json'):
  require('neural checkpoint hash '+str(r['dimension']),sha(ROOT/r['critic_checkpoint'])==r['sha256'])
  require('true learned-jet action bounds '+str(r['dimension']),all(0<a['true_neural_action_gap_upper']<=a['tolerance'] for a in r['action_certificates']))
 for d in [8,16,32]:
  r=load(OUT/f'absolute_lower_d{d}.json');require('absolute lower refinement '+str(d),ordered(r['records'],'quadrature_width'))
  require('absolute bound endpoints '+str(d),all(a['lower_bound']==a['relaxed_value_interval'][0]<a['relaxed_value_interval'][1] for a in r['records']))
 # Verify every external record and raw path summary, not only favorable panels.
 ext=OUT/'external';protocol=load(REV/'protocol_external.json')
 require('frozen external source blob',hashlib.sha1(b'blob '+str((REV/'replication/external_suite.py').stat().st_size).encode()+b'\0'+(REV/'replication/external_suite.py').read_bytes()).hexdigest()=='f8d4a42b8ff260e23d65a188cc3d67be6ae6752e')
 seeds=protocol['holdout_seeds'];require('holdout seeds',seeds==list(range(720,732)))
 panels=load(ext/'summary.json')['rows'];require('all six holdout panels',len(panels)==6)
 count=0
 for d in [8,16,32]:
  tuning=load(ext/f'tuning_d{d}.json');require('equal tuning trial counts '+str(d),len(tuning['rows'])==12 and all(sum(r['method']==m for r in tuning['rows'])==6 for m in ['nbo','soc']))
  for b in [10,30]:
   differences=[]
   for seed in seeds:
    prefix=f'd{d}_b{b}_s{seed}';r=load(ext/(prefix+'.json'));count+=1
    require('paired initialization '+prefix,r['methods']['nbo']['initial_hash']==r['methods']['soc']['initial_hash'])
    require('pinned source '+prefix,r['author_commit']=='991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a' and r['source_commit']=='46aef70a24f74cf57503018a7e7f21cb46af08e3')
    paths=np.load(ext/(prefix+'_paths.npz'))
    for m in ['nbo','soc','lq']:
     x=paths[m+'_128'].astype(float)
     require('complete finite paths '+prefix+' '+m,len(x)==4096 and np.isfinite(x).all() and len(paths[m+'_64'])==4096)
     require('raw cost summary '+prefix+' '+m,abs(float(x.mean())-r['methods'][m]['mean_cost'])<1e-13)
     if m!='lq':
      require('honest training clock '+prefix+' '+m,r['methods'][m]['training_seconds']>=b and r['methods'][m]['learning_rate_multiplier']==tuning['selected'][m])
      ck=torch.load(ext/(prefix+'_'+m+'.pt'),map_location='cpu',weights_only=True)
      require('finite complete checkpoint '+prefix+' '+m,all(torch.isfinite(v).all().item() for state in ck.values() for v in state.values()))
    diff=float((paths['nbo_128'].astype(float)-paths['soc_128'].astype(float)).mean());differences.append(diff)
    require('raw paired difference '+prefix,abs(diff-r['paired_difference'])<1e-13)
   panel=next(p for p in panels if p['dimension']==d and p['budget_seconds']==b)
   require('all seed differences summarized '+str((d,b)),np.allclose(differences,panel['raw_differences'],rtol=0,atol=1e-13))
   require('unfavorable baseline retained '+str((d,b)),panel['means']['lq']<panel['means']['nbo']<panel['means']['soc'])
 require('72 holdout pairs retained',count==72)
 # Every inherited file must remain identical; the single stale index is archived.
 old=load(REV/'inherited_manifest.json');changed=[]
 for path,h in old['files'].items():
  target=ROOT/old['archived_replacement'].get(path,path)
  if not target.exists() or sha(target)!=h:changed.append(path)
 require('all inherited files preserved',not changed,{'tracked_files':len(old['files']),'violations':changed})
 require('canonical pointer updated','canonical revision R9' in (ROOT/'REVISION_INDEX.md').read_text())
 require('unvalidated pilot excluded',load(OUT/'wealth_pilot_status.json')['no_success_claim'] is True and 'wealth_upper' not in json.dumps(summary))
 # Tables must be a deterministic function of raw records.
 before={p.name:p.read_bytes() for p in (REV/'paper/tables').glob('*.tex')}
 import make_tables,contextlib,io
 with contextlib.redirect_stdout(io.StringIO()):make_tables.run()
 after={p.name:p.read_bytes() for p in (REV/'paper/tables').glob('*.tex')}
 require('generated numerical tables match raw evidence',before==after and len(after)==8, sorted(after))
 if require_pdf:
  for stem in ['ECTA_R9','SUPP_R9']:
   log_path=ROOT/(stem+'.log')
   if not log_path.exists():log_path=REV/'build_logs'/(stem+'.final.log')
   log=log_path.read_text(errors='replace');info=subprocess.check_output(['pdfinfo',str(ROOT/(stem+'.pdf'))],text=True)
   text=subprocess.check_output(['pdftotext',str(ROOT/(stem+'.pdf')),'-'],text=True)
   require('compiled PDF '+stem,'Pages:' in info and '??' not in text)
   require('no unresolved cross references '+stem,'There were undefined references' not in log and 'multiply-defined labels' not in log and not re.search(r'Citation .* undefined|Reference .* undefined',log))
   require('no overfull boxes or duplicate destinations '+stem,'Overfull ' not in log and 'destination with the same identifier' not in log)
 # Certificate status is evidence, not an assertion of a successful flexible .01 solve.
 result={'status':'PASS','checks':CHECKS,'check_count':len(CHECKS),'seconds':time.perf_counter()-start,'python':platform.python_version(),'numpy':np.__version__,'torch':torch.__version__,
  'scope':'Evidence, preservation, generated-table and build checks. Deterministic mathematical certificates are supplied by their respective verifiers; external sampled means are not deterministic regret bounds.',
  'flexible_precision_target_met':False,'restricted_central_value_width_below_0_01':True,'positive_optimal_access_welfare_all_three_costs':True}
 (REV/'validation_report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2));return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--skip-pdf',action='store_true');a=ap.parse_args();run(not a.skip_pdf)
