"""Deterministic extensions of the R19 policy-value experiment.
(1) Uniform policy improvement on K by a paired-payoff modulus.
(2) Four-vertex optimality bounds using inherited dual witnesses.
(3) Independently evaluated one-sided continuation traces of the new policies.
These are analytic extensions, not additional randomized training experiments.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import sys,json,math,time,numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19';OUT=R/'results/policy_sensitive'
sys.path.insert(0,str(Path(__file__).resolve().parent))
import policy_sensitive as P
from validated_gauss import pi,sqrt
from state_cost_certificate import corner_upper
import independent_primal as IP
I,Q,M=P.I,P.Q,P.M

def write(p,d):P.write(p,d)
def control_distance(a,b):
    n=math.lcm(len(a['c']),len(b['c']))
    ca=np.repeat(a['c'],n//len(a['c']));cb=np.repeat(b['c'],n//len(b['c']))
    ta=np.repeat(a['theta'],n//len(a['theta']));tb=np.repeat(b['theta'],n//len(b['theta']))
    dc=float((I(ca)-I(cb)).maxabs().max());dt=I(ta)-I(tb);cum=I(0);mu=0.
    for i in range(n):cum=cum+dt[i]/n;mu=max(mu,float(cum.maxabs()))
    return I(dc),I(mu),I(float(cum.maxabs()))

def variation(a,b):
    dc,dm,dT=control_distance(a,b)
    qr=(1-M.exp(-Q('.02')))/Q('.02');disc=(1-M.exp(-Q('.04')))/Q('.04')
    shift=I(float(((-Q('.01'))/qr).lo),float((Q('.01')/qr).hi))
    for plan in [a,b]:
        c=I(plan['c'])+shift;th=I(plan['theta'])
        if c.lo.min()<Q('.7').hi or c.hi.max()>Q('.8').lo:raise ArithmeticError('Consumption range not certified on K')
        if th.lo.min()<0 or th.hi.max()>Q('.2').lo:raise ArithmeticError('Preference range not certified')
    c=I(float(Q('.7').lo),float(Q('.8').hi));u=I(float(Q('1.78').lo),float(Q('2.42').hi));r=u-1;lc=M.log(c)
    eu=M.exp(-r*lc)
    huu=eu/r**3*((r*lc+1).square()+1)
    huc=(-lc)*M.exp(-u*lc);hcc=u*M.exp(-(u+1)*lc)
    muu,muc,mcc=[I(float(z.hi)) for z in [huu,huc,hcc]]
    ug=I(float(Q('1.2').lo),float(Q('2.8').hi));rg=ug-1
    lu=I(float((M.exp(-rg*lc)*(1+rg*lc)/rg.square()).hi));lcg=I(float(M.exp(-ug*lc).hi))
    tail=M.exp(-Q(8))/(2*sqrt(2*pi())) # two-sided Mills bound at |Z|=4
    tailosc=I(min(12.,float((2*(lu*dm+lcg*dc)).hi)))
    central=Q('.02')*(muu*dm+muc*dc)+Q('.01')/qr*(muc*dm+mcc*dc)
    pe=2*M.exp(-Q('.58').square()/(2*Q('.05').square()))
    fourth=Q('.22')**4+6*Q('.22').square()*Q('.0025')+3*Q('.0025').square()
    stop=15*pe+Q('.02')*sqrt(fourth*pe)
    bound=disc*(central+tailosc*tail)+Q('.04')*M.exp(-Q('.04'))*Q('.02')*dT+4*stop
    return {'variation_upper':float(bound.hi),'control_sup_difference':float(dc.hi),'mean_path_sup_difference':float(dm.hi),
        'terminal_mean_difference':float(dT.hi),'central_hessian_bounds':{'uu':float(muu.hi),'uc':float(muc.hi),'cc':float(mcc.hi)},
        'two_sided_normal_tail_upper':float(tail.hi),'tail_oscillation_upper':float(tailosc.hi),'stopping_error_per_policy_upper':float(stop.hi),
        'proof':'paired-payoff state derivatives on |Z|<=4, global clipped-utility Lipschitz tail, exact terminal difference, four stopping allowances'}

def no_transfer_inputs(actor,u0='2',x0='2'):
    d=json.loads(Path(actor).read_text());c=I(d['c']);th=I(d['theta']);n=len(d['c'])
    if any(v!=0 for v in d.get('p',[0]*n)):raise ValueError('p must vanish')
    if not F('1.98')<=F(u0)<=F('2.02') or not F('1.25')<=F(x0)<=2:raise ValueError('Outside continuation strip')
    if c.lo.min()<Q('.7').hi or c.hi.max()>Q('.8').lo or th.lo.min()<0 or th.hi.max()>Q('.2').lo:raise ValueError('Control range')
    w=M.stack([(M.exp(-Q('.02')*Q(F(j,n)))-M.exp(-Q('.02')*Q(F(j+1,n))))/Q('.02') for j in range(n)])
    terminal=M.exp(Q('.02'))*(Q(x0)-M.add_reduce(c*w))
    if terminal.lo<=Q('.5').hi or (Q('.02')*2-I(float(c.lo.min()))).hi>=0:raise ArithmeticError('Wealth accessibility check failed')
    return d,c,th,terminal

def main():
    rows=json.loads((OUT/'results.json').read_text());upper=P.upper_comparator();lam=Q(upper['lambda_rational']);duals=[]
    for r in upper['endpoints']:
        duals.append(json.loads((ROOT/f"revisions/2026-09-23-r16/results/fresh_library/dual_k{r['k']:g}.json").read_text()))
    gains=[];state=[];traces=[]
    classic=json.loads((OUT/'classical_slsqp_n16.json').read_text());cv=json.loads((OUT/'classical_value_n16.json').read_text())['value_interval']
    for seed in P.SEEDS:
        arow=next(r for r in rows if r['seed']==seed and r['step']==0);brow=next(r for r in rows if r['seed']==seed and r['step']==800)
        a=json.loads((ROOT/arow['actor_path']).read_text());b=json.loads((ROOT/brow['actor_path']).read_text())
        mod=variation(b,a);d0=I(*brow['value_interval'])-I(*arow['value_interval']);total=d0+I(-mod['variation_upper'],mod['variation_upper'])
        cm=variation(classic,b);cd0=I(*cv)-I(*brow['value_interval']);ctotal=cd0+I(-cm['variation_upper'],cm['variation_upper'])
        gains.append({'seed':seed,'state_rectangle':{'u':['1.98','2.02'],'x':['1.24','1.26'],'t':0,'k':2},
            'central_payoff_gain_interval':d0.pair(),'uniform_payoff_gain_interval':total.pair(),'uniform_strict_improvement':bool(total.lo>0),
            'paired_modulus':mod,'uniform_classical_minus_neural_interval':ctotal.pair(),'classical_comparison_modulus':cm,
            'scope':'true original stopped payoff, uniformly on K; neither a critic-bound decrease nor a full-domain claim'})
        corners=json.loads((OUT/f'seed{seed}/final_corner_values.json').read_text());cc=[]
        for v in corners:
            u,x=v['u0'],v['x0'];ub=lam*corner_upper(duals[0],u,x)+(1-lam)*corner_upper(duals[1],u,x)
            gap=I(float(ub.hi))-I(v['value_interval'][0]);cc.append({'u':u,'x':x,'upper':float(ub.hi),'lower':v['value_interval'][0],'gap_upper':float(gap.hi)})
        state.append({'seed':seed,'corners':cc,'uniform_K_regret_upper':max(c['gap_upper'] for c in cc),
            'proof':'joint concavity of the covered original utility and the common tail/stopping correction; convex dual upper interpolation',
            'scope':'all initial (u,x) in K at t=0,k=2; not all original states or all initial times'})
        old=IP.policy_inputs
        try:
            IP.policy_inputs=no_transfer_inputs;vs=[]
            for u in ['1.98','2','2.02']:
                v=IP.evaluate(ROOT/brow['actor_path'],'2',u0=u,x0='2');g=-Q('.02')*(Q(u)-2).square()+Q('.1')*M.log(Q(2))-8
                excess=I(*v['value_interval'])-g
                v.update({'scope':'one-sided interior limit x up to 2 under this fixed no-transfer time policy; NOT its value when initialized on the absorbing boundary',
                          'trace_excess_interval':excess.pair()});vs.append(v)
        finally:IP.policy_inputs=old
        traces.append({'seed':seed,'face_values':vs,'uniform_u_segment_trace_excess_lower':min(v['trace_excess_interval'][0] for v in vs if v['u0']!='2'),
                       'proof':'concavity of the covered payoff minus settlement in u, with common error allowances; inward deterministic wealth gives the interior limit',
                       'scope':'constructive fixed-policy continuation-value witness, not an optimal Bellman upper witness'})
        write(OUT/'uniform_policy_gain.json',gains);write(OUT/'uniform_state_regret.json',state);write(OUT/'continuation_value_traces.json',traces)
        print('STATE_GAIN',seed,total.pair(),state[-1]['uniform_K_regret_upper'],traces[-1]['uniform_u_segment_trace_excess_lower'],flush=True)
if __name__=='__main__':main()
