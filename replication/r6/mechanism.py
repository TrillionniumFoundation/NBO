#!/usr/bin/env python3
"""Risk-switching locus and preference-option attribution in the original chain.
Holding theta=0 suppresses deliberate adjustment, NOT stochastic preference
shocks. All first-risk-class tails are independently evaluated; no interior
portfolio FOC is used at a box-constrained policy.
"""
from common import *
import contracts as c

class Analysis:
    def __init__(self):
        self.e=c.Economy();accelerate_kernel(self.e);self.center=int(np.linalg.norm(self.e.states-[2,1.25],axis=1).argmin())
        self.cache={}
    def solve(self,d,k=2.,adjust=True):
        key=(float(d),float(k),bool(adjust))
        if key in self.cache:return self.cache[key]
        e=self.e;v=np.empty((e.steps+1,e.ns));v[-1]=c.old.terminal(e.states);p=np.empty((e.steps,e.ns),np.int32)
        for n in range(e.steps-1,-1,-1):
            q=e.common.base+d*e.common.duration-k*e.common.effort+e.common.continuation(v[n+1])
            valid=np.ones_like(q,dtype=bool) if adjust else np.broadcast_to(np.isclose(e.menu[:,1],0,atol=1e-14),q.shape)
            if e.extra:
                z=e.extra[n];other=z.base+d*z.duration-k*z.effort+z.continuation(v[n+1]);q=np.concatenate([q,other],1)
                valid=np.concatenate([valid,np.ones_like(other,dtype=bool) if adjust else np.isclose(z.actions[:,:,1],0,atol=1e-14)],1)
            q=np.where(valid,q,-np.inf);p[n]=q.argmax(1);v[n]=q[np.arange(e.ns),p[n]]
        feat=e.evaluate(p);assert abs(v-(feat[0]+d*feat[1]-k*feat[2])).max()<2e-11
        acts=np.vstack([e.menu,e.extra[0].actions[self.center]]) if e.extra else e.menu
        tails={}
        for name,mask in [('positive',acts[:,2]>0),('nonpositive',acts[:,2]<=0)]:
            action=int(np.argmax(np.where(mask,q[self.center],-np.inf)))
            pol=p.copy();pol[0,self.center]=action
            f=e.evaluate(pol)[:,0,self.center];val=f[0]+d*f[1]-k*f[2]
            assert abs(val-q[self.center,action])<2e-11
            tails[name]=dict(value=val,base=f[0],duration=f[1],effort=f[2],action=acts[action])
        diff=tails['positive']['value']-tails['nonpositive']['value']
        row=dict(d=d,k=k,adjustment_enabled=adjust,value=v[0,self.center],initial_control=e.controls(p)[0,self.center],
            delta=diff,delta_duration=tails['positive']['duration']-tails['nonpositive']['duration'],
            delta_effort=tails['positive']['effort']-tails['nonpositive']['effort'],tails=tails)
        self.cache[key]=row;return row
    def bracket(self,k=2.,adjust=True,width=2e-5):
        lo,hi=0.,1.;a=self.solve(lo,k,adjust);b=self.solve(hi,k,adjust)
        if not (a['delta']<0<b['delta']):
            return dict(k=k,adjustment_enabled=adjust,bracket=None,endpoints=[a,b])
        # This is an opposite-sign bracket, not a proof that no other roots exist.
        while hi-lo>width:
            mid=(lo+hi)/2;m=self.solve(mid,k,adjust)
            if m['delta']>0:hi=mid
            else:lo=mid
        mid=self.solve((lo+hi)/2,k,adjust)
        ratio=mid['delta_effort']/mid['delta_duration'] if abs(mid['delta_duration'])>1e-12 else None
        return dict(k=k,adjustment_enabled=adjust,bracket=[lo,hi],low_delta=self.solve(lo,k,adjust)['delta'],
            high_delta=self.solve(hi,k,adjust)['delta'],midpoint=mid,local_regular_branch_slope=ratio,
            scope='computed opposite-sign bracket; local derivative formula requires differentiable restricted values and nonzero duration gap')

def run():
    a=Analysis();rows=[]
    # Two endpoints and an economically selected band around the published sign change.
    for d in (0.,.25,.35,.365,.375,.4,.5,1.):
        enabled=a.solve(d);disabled=a.solve(d,adjust=False)
        op={s:enabled['tails'][s]['value']-disabled['tails'][s]['value'] for s in ('positive','nonpositive')}
        assert min(op.values())>-2e-11
        assert abs((enabled['delta']-disabled['delta'])-(op['positive']-op['nonpositive']))<2e-11
        rows.append(dict(d=d,adjustable=enabled,no_deliberate_adjustment=disabled,option_values=op,
                         preference_contribution_to_risk_advantage=op['positive']-op['nonpositive']))
        print('MECHANISM',d,enabled['delta'],disabled['delta'],flush=True)
    brackets=[]
    for k in (.5,2.,8.):
        brackets.append(a.bracket(k));print('SWITCH',k,brackets[-1]['bracket'],flush=True)
    brackets.append(a.bracket(2.,False))
    save('mechanism.json',dict(source_sha256=sha(__file__),states=a.e.ns,dates=a.e.steps,rows=rows,brackets=brackets,
        units='d: cardinal flow utility; effort: discounted integral theta^2/2; slope: change in flow utility per unit cost coefficient',
        restriction='theta=0 at all dates/states, same consumption/portfolio mesh, shocks, covariance, stopping, cardinal utility and settlement',
        backend_check=a.e.common.csr_check,initial_state=a.e.states[a.center],kernel_build_seconds=a.e.build_seconds))
    return rows
if __name__=='__main__':run()
