import numpy as np, json, math, pathlib, hashlib
root=pathlib.Path('/workspace/scratch/f7129d88c27c/NBO/revisions/2026-10-04-r15/results/mechanism')
summary=json.loads((root/'report/MECHANISM_SUMMARY.json').read_text())
output={'purpose':'retrospective R15 diagnostic and prospective R16 power planning only; no new coverage or scientific claim','dimensions':{}}
for d in [10,50]:
 fs=sorted(root.glob(f'trials/d{d}_*/BRIDGE.npz'))
 a={k:np.concatenate([np.load(f)[k] for f in fs]) for k in ['M','A','E','D','E_raw','E_minus_raw','qhat','bank1','bank2','action','reference_action','nodes','bridge','state']}
 delta=a['action']-a['reference_action'][:,None]
 correction=np.mean(delta*(a['qhat']-(a['bank1']+a['bank2'])/2),axis=1)
 g=a['M']+correction
 ans={'N':len(g),'signed_correction':{'mean':float(np.mean(correction)),'sample_variance':float(np.var(correction,ddof=1)),'max_observed_absolute':float(np.max(np.abs(correction)))},'directional_gain':{'mean':float(np.mean(g)),'sample_variance':float(np.var(g,ddof=1)),'max_observed_absolute':float(np.max(np.abs(g)))},'range_diagnostics':{}}
 for k in ['M','A','E','D','E_raw','E_minus_raw']:
  old=summary['dimensions'][str(d)]['intervals'][k]
  n=old['paths']; alpha=old['event_alpha']; L=math.log(4/alpha)
  stochastic=math.sqrt(2*old['variance']*L/n)
  linear=14*old['range_upper']*L/(3*(n-1))
  # Formula in method_statistics source uses log(4/alpha) (verify independently).
  ans['range_diagnostics'][k]={'mean':old['raw_descriptive_mean'],'standard_deviation':math.sqrt(old['variance']),'population_absolute_range':old['range_upper'],'empirical_bernstein_margin':old['empirical_bernstein_margin'],'sqrt_term_formula':stochastic,'linear_term_formula':linear,'old_variance_only_required_n_for_halfwidth_1e-5':math.ceil(2*old['variance']*L/(1e-5)**2),'old_range_only_required_n_for_halfwidth_1e-5':math.ceil(14*old['range_upper']*L/(3*1e-5)+1)}
 output['dimensions'][str(d)]=ans
out=pathlib.Path('/workspace/scratch/f7129d88c27c/r16-mechanism-proposal/R15_DIAGNOSTIC.json');out.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
