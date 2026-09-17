"""Independent dense recursions audit the new paired, streaming implementation."""
from model import *
from certificate import upper_pair, focal_coefficients
from types import SimpleNamespace

class Toy:
    def __init__(self,K,R,g):
        self.K,self.R,self.terminal=K,R,g;self.steps=len(R);self.ns=len(g);self.center=0
        menu=np.array([[.2,0.,-.5],[.4,0.,.5],[.2,.1,-.5],[.4,.1,.5]])
        self.e=[SimpleNamespace(menu=menu,ns=self.ns,extra=[],common=SimpleNamespace(continuation=lambda v,k=k:np.einsum('sat,t->sa',self.K[k],v))) for k in (0,1)]
    def q(self,k,n,v,d):return self.R[n,k]+self.e[k].common.continuation(v)
    def selected(self,k,n,p,v,d):return self.q(k,n,v,d)[np.arange(self.ns),p]
    def class_pair(self,t,d,adjust):return r7.classes(self,t,d,adjust)

def independent_count(m,a,b,adj,sign):
    prev=m.terminal[None,:]
    for n in range(m.steps-1,-1,-1):
        h=m.steps-n;z=[]
        for j in range(h+1):
            q=np.zeros((m.ns,4))
            if j<h:q+=(1-j/h)*((1-a)*(m.R[n,0]+np.einsum('sat,t->sa',m.K[0],prev[j]))+a*(m.R[n,1]+np.einsum('sat,t->sa',m.K[1],prev[j])))
            if j>0:q+=j/h*((1-b)*(m.R[n,0]+np.einsum('sat,t->sa',m.K[0],prev[j-1]))+b*(m.R[n,1]+np.einsum('sat,t->sa',m.K[1],prev[j-1])))
            # Explicit mask does not call the production mask.
            if not adj:q[:,2:]=-np.inf
            if n==0:q[:,[0,2] if sign=='positive' else [1,3]]=-np.inf
            z.append(q.max(1))
        prev=np.stack(z)
    return prev[:,0]

def run():
    rng=np.random.default_rng(1709202608);records=[]
    for H in (1,2,3,4,6,8):
        for rep in range(10):
            K=rng.uniform(size=(2,3,4,3));K*=rng.uniform(.6,.995,size=(2,3,4,1))/K.sum(-1,keepdims=True)
            m=Toy(K,rng.uniform(-1,1,(H,2,3,4)),rng.uniform(-1,1,3));a,b=sorted(rng.uniform(0,1,2))
            for adj in (True,False):
                za=m.class_pair(a,0,adj);zb=m.class_pair(b,0,adj)
                count=upper_pair(m,a,b,0.,za,zb,adj,'count');chord=upper_pair(m,a,b,0.,za,zb,adj,'chord')
                for sign in ('positive','nonpositive'):
                    reference=independent_count(m,a,b,adj,sign)
                    err=float(abs(reference-count[sign]).max());order=float((chord[sign]-count[sign]).min())
                    assert err<3e-12 and order>-3e-12
                    co=focal_coefficients(m,za[sign]['policy'],0.)
                    for t in (a,(a+b)/2,b):
                        v=m.terminal.copy()
                        for n in range(H-1,-1,-1):v=(1-t)*m.selected(0,n,za[sign]['policy'][n],v,0)+t*m.selected(1,n,za[sign]['policy'][n],v,0)
                        replay=abs(float(r7.bernstein_value(co,t))-v[0]);assert replay<3e-12
                        exact=r7.solve(m,t,0.,adj,sign)['value'][0,0]
                        uu=float(r7.bernstein_value(count[sign],(t-a)/(b-a)))
                        assert uu>=exact-3e-12
                    records.append(dict(horizon=H,replicate=rep,adjustment=adj,sign=sign,count_error=err,chord_minus_count_min=order,policy_replay_error=float(replay)))
    out=dict(seed=1709202608,models=60,class_recursions=len(records),parameter_value_checks=3*len(records),max_count_error=max(r['count_error'] for r in records),minimum_order=min(r['chord_minus_count_min'] for r in records),max_policy_replay_error=max(r['policy_replay_error'] for r in records),records=records)
    save('streaming_validation.json',out);print({k:v for k,v in out.items() if k!='records'})
    return out
if __name__=='__main__':run()
