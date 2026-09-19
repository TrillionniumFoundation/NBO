"""Exact first-row arithmetic, secant-scale sensitivity and standard lifted DP.

Independent rational first-row recomputation is a cross-check of first-stage
arithmetic, not a claim of arbitrary-precision solution of the whole MDP.
"""
from __future__ import annotations
import json,time,resource
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
from canonical import load,dump,digest
from engine import Engine,SIGNS,EPS
from certified_arithmetic import derive,rat,upward,downward
HERE=Path(__file__).parent

def exact_first(eng,v,d):
    result=[]
    for i in range(len(eng.fm.actions)):
        ans=Q(0)
        for k,prob in ((0,Q(7,8)),(1,Q(1,8))):
            r=eng.fm.rows[k];ss=slice(r.indptr[i],r.indptr[i+1])
            val=sum((rat(w)*rat(v[j]) for w,j in zip(r.data[ss],r.indices[ss])),Q(0))
            val+=rat(eng.fm.reward[k][i])+rat(d)*rat(eng.fm.duration[k][i]);ans+=prob*val
        result.append(ans)
    return result

def lifted(eng,a,b,d,F,adj,m):
    """Optimistic interval/rectangular Bellman DP: nature can reselect lambda."""
    v=eng.b.terminal.copy()
    for n in range(eng.N-1,0,-1):
        q0=eng.q(0,n,v,d,F);q1=eng.q(1,n,v,d,F)
        q=np.maximum((1-a)*q0+a*q1,(1-b)*q0+b*q1)
        v=np.where(eng.mask(n,adj,m),q,-np.inf).max(1)
    q0=eng.fq(0,v,d);q1=eng.fq(1,v,d)
    q=np.maximum((1-a)*q0+a*q1,(1-b)*q0+b*q1)
    return {s:float(q[eng.first_mask(adj,s,.8,.5)].max()) for s in SIGNS}

def run():
    start=time.perf_counter();b,j=load(HERE/'canonical');eng=Engine(b,j);audit=derive(b,j);ar=upward(rat(audit['bounds']['bellman_value'])*rat(audit['maximum_discounted_mass']));exact=[]
    data=np.load(HERE/'output/procurement_witness.npz',allow_pickle=False)
    for adj,F,m,sign in [(True,.6,3,'positive'),(True,.8,1,'positive'),(False,.6,4,'positive'),(False,.8,1,'nonpositive')]:
        for shift in (-1,0,1):
            d=.42425+shift*.01;tag=f'{int(adj)}.{F:.1f}.{m}.{shift}';v=data[tag+'.values'][0]
            vals=exact_first(eng,v,d);ids=np.flatnonzero(eng.first_mask(adj,sign,.8,.5));mx=max(vals[i] for i in ids)
            stored=float(data[tag+'.first_values'][SIGNS.index(sign)])
            error=abs(mx-rat(stored));assert error<rat(audit['bounds']['bellman_value'])
            exact.append(dict(contract=tag,sign=sign,exact_first_row_value=str(mx),binary64_value=stored,first_row_discrepancy=upward(error),remaining_continuation_allowance=ar,initial_lower=downward(mx-rat(ar)),initial_upper=upward(mx+rat(ar))))
        print('EXACT FIRST ROWS',adj,F,m,flush=True)
    data.close()
    # A value function is convex in d. Interpolate the *certified* upper endpoint
    # values and use a feasible central policy's affine value as a lower bound.
    # These are derived probes, not fictitious additional Bellman optimizations.
    src=json.loads((HERE/'output/procurement.json').read_text());sensitivity=[]
    def evaluate(rows,b,kap,adj):
        rr=[r for r in rows if r['adjustment']==adj]
        lo=[b*r['service_lower']-r['grant_executable']-kap*(r['term']-1)/8 for r in rr]
        hi=[b*r['service_upper']-r['grant_lower']-kap*(r['term']-1)/8 for r in rr]
        best=max(range(len(rr)),key=lambda i:lo[i]);rival=max([0.]+[x for i,x in enumerate(hi) if i!=best])
        return dict(adjustment=adj,choice=rr[best]['id'] if lo[best]>0 else 'outside',margin=lo[best]-rival if lo[best]>0 else -max(hi))
    for h in (.0025,.005,.01):
        rr=[]
        for row in src['rows']:
            z=dict(row);w=row['value'];A=row['service'];h0=.01
            # Original service secants already enclose *all* eta-responses. The
            # enclosure under shorter derived probes follows by convexity and
            # the same center feasible-policy affine lower witness.
            sm=row['service_lower'];sp=row['service_upper'];
            # Recover upper endpoint secants before the 2 EPS + eta charge.
            # Use the original enclosure directly plus the extra error/h cost:
            # this is conservative and avoids assuming an observed policy is
            # the unique optimizer between queries.
            extra=(2*EPS+1e-8)*(1/h-1/h0)
            z['service_lower']=max(0.,sm-extra);z['service_upper']=min(1.,sp+extra);rr.append(z)
        sensitivity += [dict(h=h,mode='nested conservative secant allowance',**evaluate(rr,1.,.02,adj)) for adj in (True,False)]
    # Applied operator perturbation bridge. For every policy, a reward error r and
    # discounted-kernel l1 error k yield delta <= sum(r+k M_remaining).
    # Input probes and grant outside value must obey the stated common budget.
    base_margin=min(r['margin'] for r in src['box_corners']);r=Q(1,10**10);k=Q(1,10**12)
    M=list(map(rat,audit['value_norm_by_horizon']));delta=sum((r+k*M[h] for h in range(8)),Q(0))
    surcharge=2*(Q(2)*rat(1.02)/rat(.01)+1)*delta
    bridge=dict(per_date_reward_error=str(r),per_date_discounted_kernel_l1_error=str(k),terminal_and_outside_error='0',per_policy_value_error=upward(delta),two_contract_margin_charge=upward(surcharge),original_minimum_margin=base_margin,remaining_margin=downward(rat(base_margin)-surcharge),passed=rat(base_margin)>surcharge,scope='An applied perturbation neighborhood of the stored economy, uniformly over benefit probes and policies. This does not assert that the original diffusion discretization lies in this neighborhood.')
    baselines=[]
    for adj in (True,False):
        for count in (1,2,4,8):
            total=0.;gap=0.;rectgap=0.;policies=0
            for cell in range(count):
                a=cell/count;c=(cell+1)/count;t=time.perf_counter()
                va,pa,fa=eng.solve(a,.42425,.85,adj,1);vb,pb,fb=eng.solve(c,.42425,.85,adj,1)
                upper=lifted(eng,a,c,.42425,.85,adj,1)
                for s in SIGNS:
                    lowers=[]
                    for p,f in ((pa,fa),(pb,fb)):
                        action=eng.fm.actions[f[s][1]]
                        if s=='positive' and action[2]<=0:continue
                        co=eng.coefficients(p,action,adj,1,s,.42425,.85,.8,.5)
                        from engine import restrict
                        lowers.append(float(restrict(co,a,c).min()))
                    lb=max(lowers);gap=max(gap,upper[s]-lb+2*EPS);policies+=len(lowers)
                total+=time.perf_counter()-t;eng.cache.clear()
            baselines.append(dict(adjustment=adj,cells=count,law=[0.,1.],uniform_value_gap=gap,wall_seconds=total,feasible_policy_coefficients=policies,target='same canonical rows and financial permissions',upper_method='standard rectangular/parameter-lifted optimistic dynamic programming'))
            print('LIFTED BASELINE',adj,count,gap,total,flush=True)
    return dict(schema='nbo-r13-stress-v1',canonical_manifest_sha256=digest(HERE/'canonical/manifest.json'),exact_first_stage=exact,secant_sensitivity=sensitivity,applied_operator_neighborhood=bridge,standard_baseline=baselines,elapsed_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
if __name__=='__main__':dump(HERE/'extensions/stress.json',run())
