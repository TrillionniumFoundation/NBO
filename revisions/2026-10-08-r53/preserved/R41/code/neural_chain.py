"""Direct all-state Bellman certificates for stored trained continuations.

The verifier evaluates f[t] and f[t+1], never a reference spline. Stored
coefficients are exact dyadics; interval arithmetic covers their evaluation.
The inherited policy is separately retained. A newly tabulated actor is a
second, explicitly different policy, not a revision of historical evidence.
"""
from __future__ import annotations
import sys, json, math, hashlib, time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
R=Path(__file__).resolve().parents[1]
OLD=(R/'vendor/r38') if (R/'vendor/r38/code').exists() else R.parent/'2026-10-07-r38'
sys.path.insert(0,str(OLD/'code'))
from nonlinear import I, transition, cost, risk, own_value, encode
BETA=F(15,16)


def upper(x):
    return math.nextafter(float(x),math.inf)

def lower(x):
    return math.nextafter(float(x),-math.inf)

def pieces(net):
    """Exact rational breakpoints and slopes, including zero and negative w."""
    w,b,c=([F(float(z)) for z in net[k]] for k in ('w','b','c'))
    if len(w)!=len(b) or len(w)!=len(c):raise ValueError('Network shape')
    cuts=sorted({F(0),F(1)}|{-bb/ww for ww,bb in zip(w,b) if ww and 0<-bb/ww<1})
    def val(x):
        return F(float(net['intercept']))+F(float(net['linear']))*x+sum(cc*max(F(0),ww*x+bb) for ww,bb,cc in zip(w,b,c))
    slopes=[]
    for a,z in zip(cuts[:-1],cuts[1:]):
        x=(a+z)/2
        slopes.append(F(float(net['linear']))+sum(ww*cc for ww,bb,cc in zip(w,b,c) if ww*x+bb>0))
    return cuts,slopes,val


def network_lipschitz(net):
    return upper(max(abs(s) for s in pieces(net)[1]))


def network_direct(net,x):
    out=I.point(net['intercept'])+I.point(net['linear'])*x
    for w,b,c in zip(net['w'],net['b'],net['c']):
        z=I.point(w)*x+b
        out=out+c*I(np.maximum(z.lo,0),np.maximum(z.hi,0))
    return out


_COMPILED={}
def compiled(net):
    key=id(net)
    if key not in _COMPILED:
        cuts,slopes,val=pieces(net)
        roots=np.array([float(x) for x in cuts[1:-1]])
        root_error=max([abs(F(float(x))-x) for x in cuts[1:-1]]+[F(0)])
        intercepts=[val((a+b)/2)-s*(a+b)/2 for a,b,s in zip(cuts[:-1],cuts[1:],slopes)]
        data=dict(roots=roots,sl=np.array([lower(z) for z in slopes]),
            su=np.array([upper(z) for z in slopes]),
            bl=np.array([lower(z) for z in intercepts]),bu=np.array([upper(z) for z in intercepts]),
            L=upper(max(abs(z) for z in slopes)),root_error=upper(root_error))
        _COMPILED[key]=(net,data)
    return _COMPILED[key][1]

def network(net,x):
    """Evaluate the trained network's exact affine-region compilation.

    Rounding a breakpoint can choose an adjacent affine extension. Projection
    to the chosen true region moves the midpoint by at most root_error;
    continuity and two Lipschitz inequalities charge 2*L*root_error. Slope and
    intercept enclosures are obtained from exact rational network weights.
    No reference spline data enter this evaluation.
    """
    c=compiled(net)
    mid=np.clip(x.midpoint(),0.,1.)
    j=np.searchsorted(c['roots'],mid,side='right')
    v=I(c['sl'][j],c['su'][j])*I.point(mid)+I(c['bl'][j],c['bu'][j])
    rad=np.maximum(np.nextafter(mid-x.lo,np.inf),np.nextafter(x.hi-mid,np.inf))
    e=I.point(c['L'])*(I.point(rad)+2*I.point(c['root_error']))
    return v+I(-e.hi,e.hi)


def terminal_residual(net):
    cuts,slopes,val=pieces(net)
    cuts=sorted(set(cuts)|{F(3,8)})
    points=set(cuts)
    for a,b in zip(cuts[:-1],cuts[1:]):
        m=(a+b)/2
        slope=(val(b)-val(a))/(b-a)
        # g'=8x-17/4 below 3/8, and 4x-11/4 above it.
        x=(slope+(F(17,4) if m<F(3,8) else F(11,4)))/(8 if m<F(3,8) else 4)
        if a<=x<=b:points.add(x)
    ds=[val(x)-2*(x-F(11,16))**2-2*max(F(0),F(3,8)-x)**2 for x in points]
    return dict(lower=lower(min(ds)),upper=upper(max(ds)),exact_candidates=len(points),
                proof='Piecewise quadratic stationary points and all exact rational breakpoints')


def small_risk(v,theta):
    """Cash-centered entropic interval; rigorous Taylor tails, no libm oracle."""
    if theta==0:return risk(v,0)
    center=v.lo[...,1]+(v.hi[...,1]-v.lo[...,1])*.5
    d=theta*(v-I.point(center[...,None]))
    if np.max(np.maximum(abs(d.lo),abs(d.hi)))>.5:return risk(v,theta)
    p=I.point(1)/math.factorial(12)
    for k in range(11,-1,-1):p=p*d+I.point(1)/math.factorial(k)
    tail=I.point(2)/(2**13*math.factorial(13))
    z=p+I(-tail.hi,tail.hi)
    q=.25*I(z.lo[...,0],z.hi[...,0])+.5*I(z.lo[...,1],z.hi[...,1])+.25*I(z.lo[...,2],z.hi[...,2])
    y=(q-1)/(q+1);y2=y.square();a=np.maximum(abs(y.lo),abs(y.hi))
    if np.max(a)>=.334:return risk(v,theta)
    m=16;p=I.point(1)/(2*m-1)
    for k in range(m-2,-1,-1):p=p*y2+I.point(1)/(2*k+1)
    exponent=2*m+1;power=I.point(1);base=I.point(a)
    while exponent:
        if exponent&1:power=power*base
        exponent//=2
        if exponent:base=base.square()
    tail=2*power/((2*m+1)*(I.point(1)-I.point(a).square()))
    return I.point(center)+(2*y*p+I(-tail.hi,tail.hi))/theta


def qvalues(net,x,actions,theta,price):
    xi=I.point(np.asarray(x)[:,None]);ai=I.point(np.asarray(actions)[None,:])
    return cost(xi,ai,price)+.9375*small_risk(network(net,transition(xi,ai)),theta)


def certify_chain(nets,price,theta,N,A,old_policy=None,batch=32):
    if N<=0 or A<=0 or N&(N-1) or A&(A-1):raise ValueError('Dyadic meshes required')
    start=time.perf_counter();T=len(nets)-1
    knots=np.linspace(0.,1.,N+1);actions=np.linspace(0.,.25,A+1)
    lips=[network_lipschitz(n) for n in nets]
    terminal=terminal_residual(nets[-1]);records=[];actors=[];old_allowances=[]
    for t in range(T):
        lx=(I.point(2.875)+.9375*.875*lips[t+1]).hi.item()
        la=(I.point(price)/2+.25+.9375*lips[t+1]).hi.item()
        da=(I.point(la)/8/A).hi.item()
        rem=((I.point(lips[t])+lx)/2/N).hi.item()
        lo=[];hi=[];actor_nodal=[];chosen=[];retained_nodal=[]
        if old_policy is not None:
            old_N=len(old_policy['knots'])-1
            if N%old_N or A%old_policy['A']:raise ValueError('Nested verification meshes required')
        for i in range(0,N+1,batch):
            xs=knots[i:i+batch]
            q=qvalues(nets[t+1],xs,actions,theta,price)
            mnlo=np.min(q.lo,axis=1);mnhi=np.min(q.hi,axis=1)
            fv=network(nets[t],I.point(xs))
            # mnlo-da must itself be outward-rounded before constructing I.
            rr=fv-I(np.nextafter(mnlo-da,-np.inf),mnhi)
            lo.append(np.min(rr.lo));hi.append(np.max(rr.hi))
            idx=np.argmin(q.hi,axis=1)
            actor_nodal.extend((I(q.lo[np.arange(len(xs)),idx],q.hi[np.arange(len(xs)),idx])-I.point(mnlo)).hi)
            chosen.extend(actions[idx])
            if old_policy is not None:
                for j in range(len(xs)):
                    k=i+j
                    if k%(N//old_N)==0:
                        a=old_policy['actors'][t][k//(N//old_N)]
                        aj=int(round(float(a)*4*A))
                        if actions[aj]!=a:raise ValueError('Retained action not in grid')
                        retained_nodal.append((I.point(q.hi[j,aj])-mnlo[j]).hi.item())
        ell=(I.point(min(lo))-rem).lo.item();uu=(I.point(max(hi))+rem).hi.item()
        eta=(I.point(max(actor_nodal))+da+I.point(lx)/N).hi.item()
        records.append(dict(date=t,residual_lower=ell,residual_upper=uu,
            residual_oscillation=(I.point(uu)-ell).hi.item(),actor_allowance=eta,
            neural_lipschitz=lips[t],future_neural_lipschitz=lips[t+1],
            bellman_state_lipschitz=lx,action_lipschitz=la,action_cover_allowance=da,
            state_cover_allowance=rem))
        actors.append(np.array(chosen))
        if old_policy is not None:
            old_allowances.append((I.point(max(retained_nodal))+da+I.point(lx)/old_N).hi.item())
    def loss(allowances):
        total=I.point(0.);disc=I.point(1.);lower_shift=I.point(0.)
        for rec,eta in zip(records,allowances):
            total=total+disc*(I.point(rec['residual_upper'])-rec['residual_lower']+eta)
            lower_shift=lower_shift+disc*rec['residual_upper'];disc=disc*.9375
        total=total+disc*(I.point(terminal['upper'])-terminal['lower'])
        lower_shift=lower_shift+disc*terminal['upper']
        return total.hi.item(),lower_shift.hi.item()
    bound,shift=loss([r['actor_allowance'] for r in records])
    policy=dict(knots=knots,actors=actors,T=T,A=A,theta=theta,price=price)
    states=[.125,.25,.5,.75];values=own_value(policy,states)
    f0=network(nets[0],I.point(states));vl=f0-I.point(shift)
    state_gaps=(values-I.point(vl.lo)).hi
    result=dict(N=N,A=A,T=T,theta=theta,price=price,records=records,terminal=terminal,
        policy_gap_upper=bound,optimal_value_lower=vl.lo,
        statewise_policy_gap_upper=state_gaps,
        own_policy_values=dict(states=states,lower=values.lo,upper=values.hi),
        policy=policy,network_digest=hashlib.sha256(json.dumps(nets,sort_keys=True).encode()).hexdigest(),
        certificate='f_t minus T_t f_(t+1); no spline values or spline Bellman brackets read',
        terminal_kind='exact rational extrema of trained network minus primitive terminal cost',
        bellman_transition_evaluations=T*(N+1)*(A+1)*3,
        verification_and_new_policy_seconds=time.perf_counter()-start)
    if old_policy is not None:
        result['retained_policy_direct_gap_upper']=loss(old_allowances)[0]
        result['retained_actor_allowances']=old_allowances
    return result


def load_record(price,theta):
    if (R/'inputs/INDEX.json').exists():
        row=json.loads((R/'inputs/INDEX.json').read_text())[f'neural-neural-{price}-{theta}']
        data=(R/'inputs'/(row['id']+'.json')).read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['clock']['record_sha256']:raise ValueError('Frozen input hash')
        return row,json.loads(data)
    run=OLD/'results/run-1'
    rows=json.loads((run/'EXECUTIONS.json').read_text())
    row=next(r for r in rows if r['specification']['kind']=='neural' and r['specification']['name']==f'neural-{price}-{theta}')
    p=run/'raw'/(row['id']+'.json');data=p.read_bytes()
    if hashlib.sha256(data).hexdigest()!=row['clock']['record_sha256']:raise ValueError('Frozen source record hash')
    return row,json.loads(data)


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--price',type=float,required=True);p.add_argument('--theta',type=float,required=True);p.add_argument('--N',type=int,default=1024);p.add_argument('--A',type=int,default=512)
    args=p.parse_args();row,record=load_record(args.price,args.theta)
    result=certify_chain(record['networks'],args.price,args.theta,args.N,args.A,record['candidate'])
    result['frozen_source_record']=row['id'];result['source_record_sha256']=row['clock']['record_sha256']
    out=R/'results'/f'neural-{args.price}-{args.theta}-{args.N}.json'
    if out.exists():raise FileExistsError(out)
    out.write_text(json.dumps(result,default=encode,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('price','theta','N','policy_gap_upper','retained_policy_direct_gap_upper','statewise_policy_gap_upper','verification_and_new_policy_seconds')},default=encode))
if __name__=='__main__':main()
