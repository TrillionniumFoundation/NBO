"""Complete fixed procedures; no fitting routine can inspect audit outputs."""
from __future__ import annotations
import numpy as np
import torch
from economy import tasks

METHODS=['myopic','quadratic','rbf','NBO','shared_actor','SAA','enumerated']
STAGES=[dict(rows=64,paths=4,epochs=64),dict(rows=192,paths=16,epochs=192)]

class ScalarNet(torch.nn.Module):
    def __init__(self,e):
        super().__init__();self.e=e
        self.net=torch.nn.Sequential(torch.nn.Linear(e.d,32),torch.nn.Tanh(),torch.nn.Linear(32,32),torch.nn.Tanh(),torch.nn.Linear(32,1))
        torch.nn.init.zeros_(self.net[-1].weight);torch.nn.init.zeros_(self.net[-1].bias)
    def forward(self,x):return self.e.base(x)+self.net(x).squeeze(-1)

class Ridge:
    def __init__(self,e,kind,x):
        self.e=e;self.kind=kind;self.centers=x[:32].detach().numpy().copy();self.width2=.75**2*e.d
        self.beta=None
    def features(self,x):
        n,d=x.shape
        if self.kind=='quadratic':
            return torch.cat([torch.ones(n,1),x,x*x,x.mean(1,keepdim=True)**2],1)
        c=torch.from_numpy(self.centers)
        return torch.cat([torch.ones(n,1),x,torch.exp(-((x[:,None,:]-c[None,:,:])**2).sum(-1)/(2*self.width2))],1)
    def matrices(self,x):
        z=x.numpy();n,d=z.shape;p=2*d+2 if self.kind=='quadratic' else 1+d+len(self.centers)
        f=self.features(x).numpy();df=np.zeros((n,d,p))
        df[:,:,1:1+d]=np.eye(d)[None,:,:]
        if self.kind=='quadratic':
            df[:,:,1+d:1+2*d]=2*z[:,:,None]*np.eye(d)[None,:,:]
            df[:,:,-1]=2*z.mean(1)[:,None]/d
        else:
            rb=f[:,1+d:]
            df[:,:,1+d:]=-(z[:,:,None]-self.centers.T[None,:,:])*rb[:,None,:]/self.width2
        return f,df
    def fit(self,x,v,g):
        f,df=self.matrices(x);base=self.e.base(x)
        xx=x.detach().clone().requires_grad_(True)
        gb=torch.autograd.grad(self.e.base(xx).sum(),xx)[0]
        n,d=x.shape
        A=np.vstack([f,np.sqrt(d)*df.reshape(n*d,-1)])
        b=np.concatenate([(v-base).numpy(),np.sqrt(d)*(g-gb).numpy().ravel()])
        ridge=1e-6*np.eye(A.shape[1]);ridge[0,0]=0.
        self.beta=torch.from_numpy(np.linalg.solve(A.T@A/n+ridge,A.T@b/n))
        return self
    def __call__(self,x):return self.e.base(x)+self.features(x)@self.beta

class Cached:
    def __init__(self,e,ids):self.e=e;self.ids=ids
    def __call__(self,x):return self.e.future(x,self.ids).mean(0)

class Actor(torch.nn.Module):
    def __init__(self,e):
        super().__init__()
        self.net=torch.nn.Sequential(torch.nn.Linear(e.d+4,32),torch.nn.Tanh(),torch.nn.Linear(32,32),torch.nn.Tanh(),torch.nn.Linear(32,1))
    def forward(self,y,t):return .05+(t[:,3]-.05)*torch.sigmoid(self.net(torch.cat([y,t],1)).squeeze(-1))


def myopic(e,t):
    b=e.W[0]/e.A[0]+t[:,2]
    return torch.minimum(t[:,3],torch.clamp(2*t[:,0]/(b+torch.sqrt(b*b+4*t[:,1]*t[:,0])),min=.05))


def construct(e,method,seed,stage):
    """Return fitted scalar predictor or shared actor, plus exact cache IDs.

    Stages are fresh fits at predetermined budgets. Previous work is retained
    by the caller and charged; no stage is selected by hidden pilot outcomes.
    """
    s=STAGES[stage]
    g=np.random.default_rng(seed+e.d*100+stage)
    ids=torch.tensor(g.integers(0,16,s['paths']),dtype=torch.long)
    torch.manual_seed(seed+195530+stage)
    if method=='myopic':return None,[]
    if method=='enumerated':return Cached(e,None),list(range(16))
    if method=='SAA':return Cached(e,ids),ids.tolist()
    y,t=tasks(s['rows'],e.d,seed+195600)
    a=torch.from_numpy(g.uniform(.05,.95,s['rows']))
    x=e.post(y,a).detach()
    if method=='shared_actor':
        model=Actor(e);opt=torch.optim.Adam(model.parameters(),lr=.003)
        for _ in range(s['epochs']):
            opt.zero_grad();loss=-e.value(y,model(y,t),t,ids).mean();loss.backward();opt.step()
        return model,ids.tolist()
    v,grad=e.value_gradient(x,ids)
    if method in ('quadratic','rbf'):return Ridge(e,method,x).fit(x,v,grad),ids.tolist()
    if method!='NBO':raise ValueError('unknown method')
    model=ScalarNet(e)
    with torch.no_grad():model.net[-1].bias.fill_(float((v-e.base(x)).mean()))
    opt=torch.optim.Adam(model.parameters(),lr=.003)
    xx=x.detach().clone().requires_grad_(True)
    for _ in range(s['epochs']):
        opt.zero_grad();xx.grad=None
        pred=model(xx);gg=torch.autograd.grad(pred.sum(),xx,create_graph=True)[0]
        loss=((pred-v)**2).mean()+e.d**2*((gg-grad)**2).mean()
        loss.backward();opt.step()
    return model,ids.tolist()


def select(e,method,model,y,t):
    if method=='myopic':return myopic(e,t).detach()
    if method=='shared_actor':return model(y,t).detach()
    # Deterministic bracket updates form a candidate generator. Global
    # concavity is proved only for the true finite objective, not for a fitted
    # surrogate. The independent true-objective certificate applies either way.
    low=torch.full((len(y),),.05);high=t[:,3].clone()
    def q(a):return e.current(a,t)+model(e.post(y,a))
    for _ in range(28):
        mid=((low+high)/2).detach().requires_grad_(True)
        derivative=torch.autograd.grad(q(mid).sum(),mid)[0].detach()
        low=torch.where(derivative>0,mid.detach(),low)
        high=torch.where(derivative>0,high,mid.detach())
    candidates=torch.stack([torch.full_like(low,.05),t[:,3],(low+high)/2],1)
    with torch.no_grad():values=torch.stack([q(candidates[:,i]) for i in range(3)],1)
    return candidates[torch.arange(len(y)),values.argmax(1)].detach()
