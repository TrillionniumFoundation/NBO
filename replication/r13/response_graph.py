"""All-exact-best-response supports on a certified Bellman equality graph.

A floating comparison is used ONLY to enlarge the action set: the threshold
exceeds the independently derived error in the Q-minus-V comparison. Thus no
exactly optimal action can be discarded. Maximizing service over this enlarged
graph gives an upper bound, and maximizing its negative gives a lower bound.
"""
from __future__ import annotations
import numpy as np
from certified_arithmetic import rat,upward,gamma,SUB

def support_allowance(audit,b,weights):
    s=max(r['max_terms'] for r in audit['all_kernel_rows'])
    m=rat(audit['maximum_discounted_mass']);duration=max(float(z.duration.max()) for e in b.e for z in [e.common]+e.extra)
    magnitude=max(sum(abs(rat(x)) for x in row) for row in weights)
    R=magnitude*rat(duration);stop=magnitude;norm=rat(0);err=rat(0);n=2*s+40
    for _ in range(b.steps):
        norm=max(stop,R+m*norm);err=m*err+gamma(n)*norm+n*SUB
    bound=upward(err)
    if bound>=1e-9:raise ValueError('support arithmetic exceeds charge')
    return bound

def supports(eng,v,first,adj,m,F,audit,d=.42425,lam=.125,L=.8,S=.5):
    b=eng.b;ns=eng.S;nm=len(b.e[0].menu);quality=(b.e[0].states[:,1]>=1.25).astype(float)
    # Duration, surrender, quality-adjusted duration, and economically joint
    # directions. H is discounted elective-surrender incidence, not physical exit.
    dirs=np.array([[1,0,0],[0,1,0],[0,0,1],[1,F,0],[1,.5*F,0],[1,0,.05],[1,0,-.05],[1,F,.05]],float)
    weights=np.vstack((dirs,-dirs));nfeatures=len(weights);prev=np.zeros((ns,nfeatures));widths=[]
    mask_slack=8*audit['bounds']['bellman_value'];support_round=support_allowance(audit,b,weights);allowance=1e-9
    for n in range(eng.N-1,0,-1):
        q=(1-lam)*eng.q(0,n,v[n+1],d,F)+lam*eng.q(1,n,v[n+1],d,F)
        good=eng.mask(n,adj,m)&(q>=v[n,:,None]-mask_slack)
        if not good.any(axis=1).all():raise ValueError('empty approximate equality graph')
        st,ac=np.nonzero(good);ans=np.zeros((len(st),nfeatures));stop=ac==eng.stop
        ans[stop]=weights[:,1]
        for k,prob in enumerate((1-lam,lam)):
            for z,offset,use in ((b.e[k].common,0,ac<nm),(b.e[k].extra[n],nm,(ac>=nm)&(ac<eng.stop))):
                ii=np.flatnonzero(use)
                if not len(ii):continue
                ss=st[ii];aa=ac[ii]-offset;rr=ss*z.na+aa
                reward=z.duration[ss,aa,None]*(weights[:,0][None,:]+quality[ss,None]*weights[:,2][None,:])
                ans[ii]+=prob*(reward+z.matrix[rr]@prev)
        cur=np.full_like(prev,-np.inf);np.maximum.at(cur,st,ans)
        if not np.isfinite(cur).all():raise ValueError('nonfinite graph support')
        widths.append(dict(date=n,actions=int(good.sum()),maximum_per_state=int(good.sum(1).max())))
        prev=cur
    q=(1-lam)*eng.fq(0,v[1],d)+lam*eng.fq(1,v[1],d)
    features=np.zeros((len(q),nfeatures))
    for k,prob in enumerate((1-lam,lam)):
        features+=prob*(eng.fm.rows[k]@prev+eng.fm.duration[k][:,None]*(weights[:,0]+quality[b.center]*weights[:,2]))
    out={}
    for sign in ('positive','nonpositive'):
        ids=np.flatnonzero(eng.first_mask(adj,sign,L,S)&(q>=first[sign][0]-mask_slack))
        if not len(ids):raise ValueError('empty first-date equality graph')
        mx=features[ids].max(0);lo=-mx[len(dirs):]-allowance;hi=mx[:len(dirs)]+allowance
        lo[:3]=np.maximum(0,lo[:3]);hi[:3]=np.minimum(1,hi[:3])
        if np.any(lo>hi):raise ValueError('reversed graph support')
        out[sign]=dict(lower=lo.tolist(),upper=hi.tolist(),first_admissible=len(ids),first_action=eng.fm.actions[first[sign][1]].tolist(),attained_positive=(sign!='positive' or eng.fm.actions[first[sign][1],2]>0))
    return dict(responses=out,directions=dirs.tolist(),graph_inventory=widths,comparison_slack=mask_slack,derived_support_roundoff=support_round,charged_support_allowance=allowance,scope='All exact best responses; a superset graph is bounded, not a selected optimizer. Near-optimal responses use the separate perturbed-value theorem.')
