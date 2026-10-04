"""Proof-derived range and planning calculations; no new confirmation."""
import sys,pathlib,json,math
import numpy as np
P=pathlib.Path('/workspace/scratch/f7129d88c27c/NBO/revisions/2026-10-04-r15')
sys.path.insert(0,str(P/'code'))
import costate_bridge as b
I,pc=b.I,b.pc
protocol=json.loads((P/'MECHANISM_PROTOCOL.json').read_text())
p,_=b.verifier.bind_primitives(protocol['primitives'])
wt=pc.weights(2048)
T=I(p['T']); h=T/2048
v=8.; nold=4096
pi=pc.midpoint(wt['M'])/(p['T']/2048)
guard_lo=pc.up(wt['center'].hi-.1);guard_hi=pc.down(wt['center'].lo+.1)
lower=np.minimum(guard_lo,pi);upper=np.maximum(guard_hi,pi)
delta=max(float(np.max((I(lower)-I(pi)).absmax())),float(np.max((I(upper)-I(pi)).absmax())))
gradlo=wt['A']/h*(1/I(lower)-p['adjustment']*I(lower))-wt['B']/h
gradhi=wt['A']/h*(1/I(upper)-p['adjustment']*I(upper))-wt['B']/h
Lell=max(float(gradlo.absmax().max()),float(gradhi.absmax().max()))
gradpi=wt['A']/h*(1/I(pi)-p['adjustment']*I(pi))-wt['B']/h
L0=float(gradpi.absmax().max())
L2=b.iu(pc.I(float((wt['A']/h).hi.max()))*(1/I(float(lower.min())).square()+p['adjustment']))
stage_first=b.iu(T*I(delta)*Lell)
stage_second=b.iu(T*(I(delta)*L0+I(delta).square()*L2/2))
stage_bound=min(stage_first,stage_second)
oldsummary=json.loads((P/'results/mechanism/report/MECHANISM_SUMMARY.json').read_text())
diag=json.loads(pathlib.Path('/workspace/scratch/f7129d88c27c/r16-mechanism-proposal/R15_DIAGNOSTIC.json').read_text())
out={'purpose':'prospective precision planning based on established parameter-derived bounds and disclosed retrospective variances; no coverage assertion for new G on R15 data','margin_economic':.0005,'tail_v':v,'r_pairs_assumed':2,'possible_n_per_dimension':[4096,8192,16384],'fixed_statistics':['finite_bridge_gain_G','signed_critic_correction_C','approximate_gain_M'],'prospective_family_example':{'alpha':.01,'event_count':6,'event_alpha':.01/6},'stage_range':{'delta':delta,'Lell':Lell,'reference_stationarity_residual':L0,'curvature_absolute_upper':L2,'first_order_bound':stage_first,'second_order_bound':stage_second,'chosen_stage_bound':stage_bound},'dimensions':{}}
for d in [10,50]:
 records=[json.loads(f.read_text()) for f in sorted((P/'results/mechanism').glob(f'trials/d{d}_*/BRIDGE.json'))]
 gamma=I(max(r['constants']['critic']['terminal_costate_coefficient'][1] for r in records))
 Hbase=I(.5)+I(p['coupling']+.1)*T+I(max(r['constants']['arithmetic']['bridge_state_error'] for r in records))
 CZ=I(max(r['constants']['C_Z'] for r in records));AZ=I(max(r['constants']['A_E'] for r in records))
 sigma=I(p['idiosyncratic_sigma'])/b.isqrt(I(d));sd=b.isqrt(I(d-1))
 CQ=gamma*(Hbase+sigma*b.isqrt(T)*sd)+CZ
 AQ=gamma*sigma*b.isqrt(T)+AZ
 CG=I(stage_bound)+T*I(delta)*CQ
 AG=T*I(delta)*AQ
 bound=b.iu(CG+AG*v)
 tau=b.iu(2*AG*pc.exp_i(-I(v).square()/2)/v)
 e=oldsummary['dimensions'][str(d)]
 oldmean=diag['dimensions'][str(d)]['directional_gain']['mean'];oldvar=diag['dimensions'][str(d)]['directional_gain']['sample_variance']
 # Endpoint variance may differ, so show both empirical historical scenario and conservative variance cap.
 log=math.log(4/(.01/6))
 rows=[]
 for N in [4096,8192,16384]:
  root=math.sqrt(2*oldvar*log/N);linear=14*bound*log/(3*(N-1))
  deterministic=e['holding_deficit_upper']+e['paired_payoff_transfer_upper']
  total=root+linear+tau+deterministic
  # Max variance still permitting economic target from planning mean, ignoring tiny arithmetic.
  remaining=oldmean-.0005-linear-tau-deterministic
  maxvar=(max(0,remaining))**2*N/(2*log)
  rows.append({'N':N,'historical_variance_scenario_root_term':root,'range_term':linear,'legacy_CT_plus_hold_allowance':deterministic,'planned_halfwidth_including_CT':total,'planning_lower_if_historical_mean_variance_recur':oldmean-total,'largest_variance_allowing_lower_0.0005_at_historical_mean':maxvar})
 out['dimensions'][str(d)]={'residual_CZ':float(CZ.hi),'residual_AZ':float(AZ.hi),'G_affine_intercept':b.iu(CG),'G_affine_slope':b.iu(AG),'G_clipping_bound':bound,'G_tail_expectation_allowance':tau,'historical_directional_mean':oldmean,'historical_directional_variance':oldvar,'planning_rows':rows}
p=pathlib.Path('/workspace/scratch/f7129d88c27c/r16-mechanism-proposal/SIGNED_BRIDGE_POWER.json');p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
