"""Additional independent release checks and exact display bounds."""
from __future__ import annotations
import json,sys,time
from fractions import Fraction as Q
import numpy as np
from verify import Checker,ROOT,OUT,require,close,read,EPS
sys.path.insert(0,str(ROOT/'replication/r13'))
from canonical import load

def rs(q):return f'{q.numerator}/{q.denominator}'
def main():
    start=time.perf_counter();b,j=load(ROOT/'replication/r13/canonical');c=Checker(b,j)
    en=read('enforcement.json');att=[];bounds=[]
    for adj in (True,False):
      for F,m,label in ((0.,8,'no_surrender'),(.765,1,'common_fee')):
        v,q=c.solve(.125,.42425,F,adj,m);pos=c.fm_mask(adj,'positive');zero=pos&(c.fm.actions[:,2]==0)
        strict=pos&(c.fm.actions[:,2]>0);margin=float(q[strict].max()-q[zero].max())
        require(margin>4*EPS,'positive-mandate attainment is not separated from zero')
        att.append(dict(adjustment=adj,problem=label,zero_exclusion_margin=margin-4*EPS))
    for r in en['rows']:
      adj=r['adjustment'];sign=r['sign'];v,q=c.solve(.125,.42425,0.,adj,8)
      val=Q.from_float(float(q[c.fm_mask(adj,sign)].max()));eps=Q.from_float(EPS)
      if sign=='positive':require(r['no_surrender_witness']['attained'],'reported positive witness')
      eligible=~b.e[0].boundary
      u=max(Q(0),max(Q.from_float(float(x))-Q.from_float(float(y)) for n in range(1,8) for x,y in zip(b.terminal[eligible],v[n,eligible])))
      bounds.append(dict(id=r['id'],no_surrender_value=[rs(val-eps),rs(val+eps)],
        uniform_fee=[rs(max(Q(0),u-eps)),rs(u+eps)],
        initial_fee=[rs(Q.from_float(x)) for x in r['initial_fee_bracket']]))
    pp=read('proposals.json');z=np.load(OUT/'proposal_witness.npz',allow_pickle=False);inference=0
    state=b.e[0].states.astype(float);u=state[:,0];x=np.log(state[:,1]);u=(u-u.mean())/(u.std()+1e-12);x=(x-x.mean())/(x.std()+1e-12)
    for row in pp['rows']:
      adj=row['adjustment'];lam=row['law'];prefix=str(int(adj));method=row['method']
      features=np.concatenate([np.column_stack((u,x,np.full(c.S,n/8),np.full(c.S,lam))) for n in range(1,8)])
      if method in ('neural','polynomial'):
        classes=z[prefix+'.classes']
        if method=='neural':
          ww=[z[f'{prefix}.seed{row["seed"]}.weight{i}'] for i in range(6)]
          score=np.maximum(np.maximum(features@ww[0]+ww[1],0)@ww[2]+ww[3],0)@ww[4]+ww[5]
        else:
          phi=np.column_stack((np.ones(len(features)),features,*[features[:,i]*features[:,j] for i in range(features.shape[1]) for j in range(i,features.shape[1])]))
          score=phi@z[prefix+'.polynomial']
        policy=np.zeros((8,c.S),np.int32)
        for n in range(1,8):
          allowed=c.mask(n,adj,1)[:,classes];sc=score[(n-1)*c.S:n*c.S]
          policy[n]=classes[np.where(allowed,sc,-np.inf).argmax(1)]
        for sign in ('positive','nonpositive'):require(np.array_equal(policy,z[row['id']+'.policy.'+sign]),'inference policy differs from deposited model')
      elif method=='nearest':
        policy=z[f'{prefix}.anchor{int(lam>.125)}']
        for sign in ('positive','nonpositive'):require(np.array_equal(policy,z[row['id']+'.policy.'+sign]),'nearest policy provenance')
      elif method=='bank':
        qs=[c.evaluate(z[f'{prefix}.anchor{i}'],lam,.42425,.85,adj,1) for i in (0,1)]
        for sign in ('positive','nonpositive'):
          mask=c.fm_mask(adj,sign)
          if sign=='positive':mask &= c.fm.actions[:,2]>0
          best=max(float(qq[mask].max()) for qq in qs);close(best,row['lower_witnesses'][sign]['value'],'evaluated bank envelope')
      elif method=='exact':
        v,q=c.solve(lam,.42425,.85,adj,1)
        for sign in ('positive','nonpositive'):
          p=z[row['id']+'.policy.'+sign]
          for n in range(1,8):
            qq=c.q(n,v[n+1],lam,.42425,.85);mx=np.where(c.mask(n,adj,1),qq,-np.inf).max(1)
            require(np.all(mx-qq[c.ix,p[n]]<4*EPS),'exact control is not Bellman-greedy')
          actual=c.evaluate(p,lam,.42425,.85,adj,1)
          c.witness(actual,row['lower_witnesses'][sign],adj,sign)
      else:raise ValueError('unknown method')
      inference+=1
    out=dict(schema='nbo-r19-final-checks-v1',passed=True,positive_attainment=att,
      rational_bounds=bounds,proposal_inference_rows=inference,
      elapsed_seconds=time.perf_counter()-start,
      scope='Attainment from strict zero-knot exclusion; exact rational display bounds; inference recomputed from stored weights and identical features; exact-control Bellman greediness. Training is reproducible from the producer but no independent optimizer implementation is claimed.')
    (OUT/'final_checks.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
