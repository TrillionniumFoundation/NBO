"""R21: directed continuum transfer of the immutable R20 experiment.

This is a new analysis of R20, not newly randomized training.  No inherited
manuscript or result is overwritten.  The final endpoints are the hull of the
binary64 and MPFR enclosures, not their more favorable intersection.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,math,platform
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-23-r21'; OLD=ROOT/'revisions/2026-09-23-r20'
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
from interval64 import I,exp,log,stack,add_reduce
from validated_gauss import sqrt,pi
Q=I.rational
SEEDS=range(20100,20105); WORK=(0,100,400,1000)
K=[('1.98','1.24'),('1.98','1.26'),('2.02','1.24'),('2.02','1.26')]
def read(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,a):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(a,indent=2,allow_nan=False)+'\n')
def actor(seed,v,step):return OLD/f'results/neural/seed{seed}/vertex{v}/actor_{step:04d}.json'
def cert(seed,v,step):return read(actor(seed,v,step).with_name(f'certificate_{step:04d}.json'))
def hull(seed,v,step):
 a=cert(seed,v,step)['value_interval']
 replay=REV/f'results/replay/binary/neural/seed{seed}/vertex{v}/actor_{step:04d}.json'
 if replay.exists():
  z=read(replay)['value_interval'];a=[min(a[0],z[0]),max(a[1],z[1])]
 if step==1000:
  m=read(OLD/f'results/mpfr/seed{seed}_vertex{v}.json')
  assert m['actor_sha256']==digest(actor(seed,v,step))
  b=m['value_interval'];assert max(a[0],b[0])<=min(a[1],b[1])
  replay=REV/f'results/replay/mpfr/neural/seed{seed}/vertex{v}/actor_{step:04d}.json'
  if replay.exists():
   z=read(replay)['value_interval'];b=[min(b[0],z[0]),max(b[1],z[1])]
  return I(min(a[0],b[0]),max(a[1],b[1]))
 return I(*a)
def tanh(a):
 b=exp(2*a);return (b-1)/(b+1)
MASS=stack([(exp(-Q('.04')*Q(F(j,16)))-exp(-Q('.04')*Q(F(j+1,16))))/Q('.04') for j in range(16)])
PEXIT=2*exp(-Q('.58')**2/(2*Q('.0025')))
PTAIL=exp(-Q(8))/(2*sqrt(2*pi())) # 2 phi(4)/4: all t<=1
LIB=ROOT/'revisions/2026-09-23-r16/results/fresh_library'
NODES=read(LIB/'nodes.json')
def dual_node(node,u,x):
 d=read(LIB/f"dual_k{node['k']:g}.json")
 du=Q(u)-2
 loc=8*exp(-Q(18))*(exp(120*du)+exp(-120*du)-2)
 return I(d['optimal_value_upper'])+du*I(*d['b0_interval'])+(Q(x)-Q('1.25'))*I(d['y0'])+loc

def upper(k,u,x):
 k=F(str(k));left=max((n for n in NODES if F(str(n['k']))<=k),key=lambda n:n['k'])
 right=min((n for n in NODES if F(str(n['k']))>=k),key=lambda n:n['k'])
 if left==right:return dual_node(left,u,x)
 w=Q((k-F(str(left['k'])))/(F(str(right['k']))-F(str(left['k']))))
 return (1-w)*dual_node(left,u,x)+w*dual_node(right,u,x)

def hess_bounds():
 # Outward interval boxes bound the absolute Hessian, not sampled derivatives.
 us=[];cs=[]
 for i in range(64):
  for j in range(64):
   us.append((F(178,100)+F(64,100)*F(i,64),F(178,100)+F(64,100)*F(i+1,64)))
   cs.append((F(1,2)+F(3,10)*F(j,64),F(1,2)+F(3,10)*F(j+1,64)))
 u=I(np.array([Q(a).lo for a,b in us]),np.array([Q(b).hi for a,b in us]))
 c=I(np.array([Q(a).lo for a,b in cs]),np.array([Q(b).hi for a,b in cs]))
 r=u-1;a=-log(c)
 return [float(np.max(z.hi)) for z in [exp(r*a)*((r*a-1).square()+1)/r**3,a*exp(u*a),u*exp((u+1)*a)]]

def jensen_initial(seed,H):
 ds=[read(actor(seed,v,0)) for v in range(4)]
 assert all(d['s']==ds[0]['s'] and d['theta']==ds[0]['theta'] for d in ds)
 b=I(np.array([d['b'] for d in ds]));span=I(np.max(b.hi,axis=0))-I(np.min(b.lo,axis=0))
 dc=Q('.3')*tanh(span/4);du=Q('.04')
 gap=(I(H[0])*du**2+2*I(H[1])*du*dc+I(H[2])*dc.square())/8
 running=add_reduce(MASS*gap)+6*PTAIL*add_reduce(MASS)
 rs=[cert(seed,v,0)['reserve_interval'] for v in range(4)]
 dr=I(max(r[1] for r in rs))-I(min(r[0] for r in rs))
 terminal=exp(-Q('.04'))*(Q('.005')*du**2+Q('.0125')/Q('.5')**2*dr**2)
 return {'bound':float((running+terminal+16*PEXIT).hi),'running':float(running.hi),'terminal':float(terminal.hi),
         'max_consumption_span':float(np.max(dc.hi)),'equal_initial_slopes_and_drifts':True,
         'preference_tail_probability_upper':float(PTAIL.hi),'formula':'weighted Hessian range bound / 8; six-unit marginal preference-tail bound; 16-unit stopping bound'}

def policy_lower_at_price(seed,v,k):
 d=read(actor(seed,v,1000));J=hull(seed,v,1000)
 B=add_reduce(I(d['theta']).square()*MASS)/2
 dk=Q(str(k))-2
 # B_stop in [B_full-.02*C*p_exit, B_full]; pointwise ordering at either sign.
 if F(str(k))>=2:return I(J.lo)-dk*I(B.hi)
 return I(J.lo)-dk*(I(B.lo)-Q('.02')*add_reduce(MASS)*PEXIT)

def main():
 hashes={str(p.relative_to(ROOT)):digest(p) for p in sorted((OLD/'results').rglob('*')) if p.is_file()}
 H=hess_bounds();summary={'scope':'t=0, K=[1.98,2.02]x[1.24,1.26], original stopped economy and unrestricted optimal value',
 'source_training_commit':'b1a2ea39d895b330e5a11b4e55d86b7a4985b101','training_run':35802793602,
 'review_commit':'074849b9aad1812b59e25e1d3833383ed11aa401',
 'hessian_absolute_upper':dict(zip(['uu','uc','cc'],H)),'stopping_probability_upper':float(PEXIT.hi),
 'final_arithmetic':'hull of binary64 and MPFR, not intersection','seeds':[]}
 allrows=[];accepted=0
 for seed in SEEDS:
  original=read(OLD/f'results/neural/seed{seed}/records.json');assert len(original)==16
  for r in original:
   p=ROOT/r['actor_path'];d=read(p);assert digest(p)==r['actor_sha256'];assert digest(ROOT/d['network_file'])==d['network_sha256']
   assert r['check_complete_before_next_update'];assert r['accepted'];accepted+=int(r['step']>0)
  jgap=jensen_initial(seed,H);row={'seed':seed,'jensen_initial':jgap,'checkpoints':[]}
  for step in WORK:
   losses=[];gains=[]
   for v,(u,x) in enumerate(K):
    losses.append(float((upper(2,u,x)-I(hull(seed,v,step).lo)+16*PEXIT).hi))
    gains.append(float((I(hull(seed,v,step).lo)-I(hull(seed,v,0).hi)).lo))
   g=float((I(min(gains))-I(jgap['bound'])-16*PEXIT).lo)
   b=max(losses);out={'step':step,'K_regret_upper':b,'corner_gain_from_initial_lower':min(gains),'K_gain_from_initial_lower':g}
   row['checkpoints'].append(out);allrows.append({'seed':seed,**out})
  B=row['checkpoints'][-1]['K_regret_upper'];gain=row['checkpoints'][-1]['K_gain_from_initial_lower'];assert gain>0 and B<.003
  row['true_regret_ratio_upper']=float((I(B)/(I(B)+I(gain))).hi)
  row['resources']=read(OLD/f'results/neural/seed{seed}/resources.json')
  row['frontier']=[]
  for tol in [.01,.005,.002]:
   candidates=[r for r in row['checkpoints'] if r['K_regret_upper']<=tol]
   if not candidates:row['frontier'].append({'tolerance':tol,'hit':False});continue
   step=candidates[0]['step'];rs=[r for r in original if r['step']==step]
   generation=sum(r['generation_seconds'] for r in rs);verification=sum(r['verification_cumulative_seconds'] for r in rs)
   row['frontier'].append({'tolerance':tol,'hit':True,'step':step,'generation_seconds':generation,'verification_seconds':verification,'generation_plus_verification_seconds':generation+verification})
  summary['seeds'].append(row)
 summary['accepted_expert_transitions']=accepted;assert accepted==60
 # These bounds are a post-training sensitivity calculation; the actors stay fixed.
 kk=sorted(set([F(3,2),F(2),F(5,2)]+[F(str(n['k'])) for n in NODES if 1.5<n['k']<2.5]))
 price=[]
 for k in kk:
  vals=[float((upper(k,u,x)-policy_lower_at_price(seed,v,k)+16*PEXIT).hi) for seed in SEEDS for v,(u,x) in enumerate(K)]
  price.append({'k':str(k),'all_five_K_regret_upper':max(vals)})
 summary['fixed_policy_price_transport']={'price_interval':['1.5','2.5'],'knots':price,'uniform_regret_upper':max(r['all_five_K_regret_upper'] for r in price),'method':'piecewise affine upper minus fixed-policy affine-in-price payoff lower; endpoint checks, not a dense sampled grid'}
 # Named deterministic comparisons: a supporting affine upper is valid on K.
 deterministic=[]
 for d in read(OLD/'results/classical_deterministic/records.json'):
  gaps=[float((I(hull(seed,v,1000).lo)-I(d['K_affine_policy_upper']['corners'][v]['policy_value_upper'])-16*PEXIT).lo) for seed in SEEDS for v in range(4)]
  deterministic.append({'slabs':d['slabs'],'all_five_uniform_neural_payoff_gain_lower':min(gaps),'generation_seconds':d['generation_seconds'],'reference_regret_upper':d['reference_regret_upper']})
 summary['named_deterministic_comparison']=deterministic
 cr=read(OLD/'results/classical_stochastic/records.json');last=[max((r for r in cr if r['vertex']==v),key=lambda r:r['step']) for v in range(4)]
 final_bound=max(float((upper(2,*K[v])-I(r['value_interval'][0])+16*PEXIT).hi) for v,r in enumerate(last))
 cf=[]
 for tol in [.01,.005,.002]:
  chosen=[]
  for v in range(4):
   hits=[r for r in cr if r['vertex']==v and float((upper(2,*K[v])-I(r['value_interval'][0])+16*PEXIT).hi)<=tol]
   if hits:chosen.append(min(hits,key=lambda r:r['step']))
  if len(chosen)!=4:cf.append({'tolerance':tol,'hit':False});continue
  gen=sum(r['generation_seconds'] for r in chosen);ver=sum(r['verification_cumulative_seconds'] for r in chosen)
  cf.append({'tolerance':tol,'hit':True,'steps':[r['step'] for r in chosen],'generation_seconds':gen,'verification_seconds':ver,'generation_plus_verification_seconds':gen+ver})
 summary['classical_stochastic']={'K_regret_upper':final_bound,'frontier':cf,'resources':read(OLD/'results/classical_stochastic/resources.json'),
 'comparison_scope':'same K, same original optimal upper, same 16-slab stochastic family and checker; not a whole-domain MC/SL comparison'}
 wealth=read(OLD/'results/wealth/records.json')
 assert len(wealth)==20
 wg=[]
 for w in wealth:
  assert digest(ROOT/w['actor_path'])==w['compensated_actor_sha256']
  lower=w['value_interval'][0]
  rp=REV/'results/replay/binary'/Path(w['actor_path']).relative_to(OLD.relative_to(ROOT)/'results')
  if rp.exists():lower=min(lower,read(rp)['value_interval'][0])
  wg.append(float((I(lower)-I(w['uncompensated_optimal_upper'])-16*PEXIT).lo))
 summary['neural_wealth_compensation']={'initial_wealth_increment':'0.002','uniform_gain_above_uncompensated_optimum_lower':min(wg),'scope':'all five budget-shifted neural mixtures, all K, k=2,t=0; sufficient not minimum compensation','maximum_fraction_initial_wealth':float((Q('.002')/Q('1.24')).hi)}
 assert min(wg)>0
 summary['cost_ledger']={'shared_fresh_twenty_node_upper_library_seconds':read(LIB/'resources.json')['wall_seconds'],'inherited_final_mpfr_audit_seconds':read(OLD/'results/mpfr/resources.json')['wall_seconds'],'convention':'charge entire shared library to cold-start comparisons or disclose reuse; target frontier excludes separately listed final MPFR and R21 replay audits; no neural speedup claimed','classical_peak_rss':'not recorded in R20; coefficient storage is not process peak memory'}
 # Directed checks for compact, independently readable analytic constants.
 r=Q('1.8');a=Q('.7');D=r*r*a*a-2*r*(r+1)*a+2*(r+1)
 complex_logit_v=Q('6.5')*((2*Q('.065')+Q('2.4'))/16+Q('.065')/256)
 complex_logit_z=Q('6.5')*Q('.3')/2
 kappa=(sqrt(Q('.79'))-sqrt(Q('.49')))/(sqrt(Q('.79'))+sqrt(Q('.49')))
 xmax=Q('.5')+Q('.79')*(1-exp(-Q('.02')))/Q('.02')+Q('.0001')
 pmax=Q('1.5')*Q('6.5')*kappa*(1-Q('.5')/xmax)
 assert D.lo>0 and complex_logit_v.hi<1.05 and complex_logit_z.hi<1.05 and pmax.hi<.8
 summary['analytic_checks']={'concavity_polynomial_lower':float(D.lo),'complex_logit_v_imag_upper':float(complex_logit_v.hi),'complex_logit_z_imag_upper':float(complex_logit_z.hi),'wealth_upper':float(xmax.hi),'portfolio_upper':float(pmax.hi)}
 summary['environment']={'python':platform.python_version(),'numpy':np.__version__}
 summary['scope_not_established']=['all initial states of D and all start times','globally sharp continuation upper witness','matched global MC/SL frontier','neural speed superiority over direct stochastic optimization','broad high-dimensional stochastic neural advantage']
 save(REV/'results/continuum_audit.json',summary);save(REV/'results/r20_result_sha256.json',hashes)
 # Figures in the manuscript are emitted directly from the directed computations.
 def fmt(x,lower=False):return str(Decimal.from_float(float(x)).quantize(Decimal('.00000001'),rounding=ROUND_FLOOR if lower else ROUND_CEILING))
 lines=[r'\begin{table}[htbp]\centering',r'\caption{Four-expert neural policies: bounds uniform on $K$, at $t=0,k=2$. Final bounds use the hull of both arithmetic implementations.}',r'\label{tab:r21-policy}',r'\begin{tabular}{rrrrrr}\toprule',r'Seed & 0 updates & 100 & 400 & 1,000 & Gain over initial \\ \midrule']
 for row in summary['seeds']:
  b=[fmt(r['K_regret_upper']) for r in row['checkpoints']]
  lines.append(str(row['seed'])+' & '+' & '.join(b)+' & '+fmt(row['checkpoints'][-1]['K_gain_from_initial_lower'],True)+r' \\')
 lines+=[r'\bottomrule\end{tabular}',r'\end{table}']
 (REV/'paper/table_policy.tex').write_text('\n'.join(lines)+'\n')
 macros={'RXXIFinalMax':max(r['checkpoints'][-1]['K_regret_upper'] for r in summary['seeds']),
 'RXXIFinalMin':min(r['checkpoints'][-1]['K_regret_upper'] for r in summary['seeds']),
 'RXXIGain':min(r['checkpoints'][-1]['K_gain_from_initial_lower'] for r in summary['seeds']),
 'RXXIRatio':max(r['true_regret_ratio_upper'] for r in summary['seeds']),
 'RXXIPrice':summary['fixed_policy_price_transport']['uniform_regret_upper'],
 'RXXIWealthGain':summary['neural_wealth_compensation']['uniform_gain_above_uncompensated_optimum_lower'],
 'RXXIClassical':final_bound,'RXXIDeterministicGain':min(r['all_five_uniform_neural_payoff_gain_lower'] for r in deterministic)}
 (REV/'paper/result_macros.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+fmt(v,k in ['RXXIGain','RXXIDeterministicGain','RXXIWealthGain','RXXIFinalMin'])+'}' for k,v in macros.items())+'\n')
 print(json.dumps({**macros,'H':H,'accepted':accepted,'price':price,'frontier':summary['seeds'][0]['frontier'],'classical':summary['classical_stochastic']},indent=2))
if __name__=='__main__':main()
