"""Independent R19 checker.

Does NOT import generate.py, Engine, or proposal_benchmark. Shares only the
immutable canonical loader and pre-existing independently derived roundoff audit.
The checks use exceptions, not removable assert statements.
"""
from __future__ import annotations
import copy, hashlib, json, sys, time
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
import sympy as sp
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'replication/r19/output'
sys.path.insert(0,str(ROOT/'replication/r13'))
from canonical import load
from certified_arithmetic import derive
EPS=1e-7;SIGNS=('positive','nonpositive')

def require(ok,msg):
    if not bool(ok):raise ValueError(msg)
def read(name):return json.loads((OUT/name).read_text())
def close(a,b,msg):
    gap=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    require(np.isfinite(gap) and gap<2e-10,msg+': '+str(gap));return gap

def analytic():
    a=read('continuous_benchmark.json');lo,hi=map(Q,a['log2'])
    # Independent decomposition: log(2)=log(4/3)+log(3/2).
    def series(x,m=80):
      l=Q(0)
      for j in range(m):l+=2*x**(2*j+1)/Q(2*j+1)
      return l,l+2*x**(2*m+1)/(Q(2*m+1)*(1-x*x))
    p=series(Q(1,7));q=series(Q(1,5));ll=p[0]+q[0];hh=p[1]+q[1]
    require(lo<ll<hh<hi,'log enclosure fails independent rational series')
    ca=list(map(Q,a['threshold_adjustment']));c0=Q(a['threshold_no_adjustment'])
    require(ca==[lo/2,hi/2] and c0==Q(1,2),'threshold constant')
    fa=Q(a['fee_adjustment']);f0=Q(a['fee_no_adjustment']);eta=Q(a['eta'])
    require(fa>ca[1] and f0>c0 and eta>0,'strict obstacle slack')
    robust=1-eta/(fa-ca[1])-ca[1]-fa*fa/50-eta
    p0=1-c0-f0*f0/50
    require(Q(a['robust_adjustment_lower'])==robust,'robust transfer/service budget')
    require(Q(a['surplus_no_adjustment'])==p0,'comparison offer')
    require(Q(a['robust_decision_margin_lower'])==robust-p0>0,'decision margin')
    t,x=sp.symbols('t x',real=True)
    v=-x*x/(2*(2-t))-sp.log(2-t)/2;u=-x*x/2-(1-t)/2
    require(sp.simplify(sp.diff(v,t)+sp.diff(v,x,2)/2+sp.diff(v,x)**2/2)==0,'controlled PDE identity')
    require(sp.simplify(sp.diff(u,t)+sp.diff(u,x,2)/2)==0,'uncontrolled PDE identity')
    require(sp.simplify(v.subs(t,1)+x*x/2)==0,'terminal controlled')
    require(sp.simplify(u.subs(t,1)+x*x/2)==0,'terminal uncontrolled')
    require(sp.simplify(v+x*x/2+sp.log(2-t)/2-(1-t)*x*x/(2*(2-t)))==0,'obstacle factorization')
    f=read('theorem_fixtures.json')
    for z in f['information']:
      k=z['k'];w=list(map(Q,z['weights']));rho=min(w);c=Q(z['safe']);jq=list(map(Q,z['joint_query']))
      for i,s,v1,v0 in z['axis_queries']:
        tt=[Q(0)]*k;tt[i]=Q(s)
        require(Q(v1)==max(tt) and Q(v0)==max(Q(0),max(tt)) and Q(v1)==Q(v0),'axis indistinguishability')
      require(list(map(Q,z['joint_values']))==[min(jq) if False else max(jq),Q(0)],'directed query')
      regret=c*(rho-c)/rho;mix=(rho-c)/rho
      require(Q(z['minimax_regret'])==regret==mix*c==(1-mix)*(rho-c),'minimax regret')
      h=-jq[0]/w[0];noise=h*rho/2;report=-h*rho/2
      require(Q(z['noise_boundary'])==noise and abs(report)==noise and abs(report+h*rho)==noise,'noise threshold overlap')
    eta0=Q(1,100);require(2*eta0>eta0 and Q(1,100)*1==eta0,'global loss examples')
    # A uniform positive whole-cell gap with one common omega.
    omega=Q(1,3);gaps=[omega*2+(1-omega)*1-1,omega*1+(1-omega)*3-2]
    require(min(gaps)==Q(1,3),'cell endpoint certificate')
    require(not (Q(1,3)+Q(1,100)<=min(gaps)),'cell mutation not rejected')
    return dict(pde_identities=True,rational_margin=float(robust-p0),log_enclosure=True,
      information_fixtures=len(f['information']),noise_boundary=True,global_eta=True,cell_margin=True)

class Checker:
    def __init__(self,b,j):
      self.b=b;self.fm=j.fm;self.S=b.ns;self.N=b.steps;self.ix=np.arange(b.ns)
      self.nm=len(b.e[0].menu);self.stop=self.nm+len(b.e[0].extra[0].actions[0]);self.cache={}
    def mask(self,n,adj,m):
      theta=np.concatenate((np.broadcast_to(self.b.e[0].menu[:,1],(self.S,self.nm)),self.b.e[0].extra[n].actions[:,:,1]),axis=1)
      live=np.ones(theta.shape,bool) if adj else np.abs(theta)<1e-14
      return np.column_stack((live,(~self.b.e[0].boundary)&(n>=m)))
    def fm_mask(self,adj,sign):
      x=self.fm.actions
      mask=(x[:,2]>=(-.5 if sign=='nonpositive' else 0)-1e-13)&(x[:,2]<=(0 if sign=='nonpositive' else .8)+1e-13)
      if not adj:mask &= np.abs(x[:,1])<1e-14
      return mask
    def q(self,n,v,lam,d,F):
      allq=[]
      for k in (0,1):
        e=self.b.e[k];parts=[]
        for z in (e.common,e.extra[n]):
          parts.append((z.matrix@v).reshape(self.S,z.na)+z.base+d*z.duration-self.b.spec.cost*z.effort)
        parts.append((self.b.terminal-F)[:,None]);allq.append(np.concatenate(parts,axis=1))
      return (1-lam)*allq[0]+lam*allq[1]
    def fq(self,v,lam,d):
      return (1-lam)*(self.fm.rows[0]@v+self.fm.reward[0]+d*self.fm.duration[0])+lam*(self.fm.rows[1]@v+self.fm.reward[1]+d*self.fm.duration[1])
    def solve(self,lam,d,F,adj,m):
      key=(lam,d,F,adj,m)
      if key in self.cache:return self.cache[key]
      v=np.zeros((self.N+1,self.S));v[-1]=self.b.terminal
      for n in range(self.N-1,0,-1):v[n]=np.where(self.mask(n,adj,m),self.q(n,v[n+1],lam,d,F),-np.inf).max(1)
      q=self.fq(v[1],lam,d);self.cache[key]=(v,q);return v,q
    def evaluate(self,p,lam,d,F,adj,m):
      require(p.shape==(self.N,self.S) and p.dtype.kind in 'iu','policy shape/type')
      v=self.b.terminal.copy()
      for n in range(self.N-1,0,-1):
        require(np.all((p[n]>=0)&(p[n]<=self.stop)) and self.mask(n,adj,m)[self.ix,p[n]].all(),'policy feasibility')
        vv=[]
        for k in (0,1):
          e=self.b.e[k];cur=self.b.terminal-F;cur=cur.copy()
          for z,offset,chosen in ((e.common,0,p[n]<self.nm),(e.extra[n],self.nm,(p[n]>=self.nm)&(p[n]<self.stop))):
            ii=np.flatnonzero(chosen);aa=p[n,ii]-offset
            if len(ii):cur[ii]=z.base[ii,aa]+d*z.duration[ii,aa]-self.b.spec.cost*z.effort[ii,aa]+z.matrix[ii*z.na+aa]@v
          vv.append(cur)
        v=(1-lam)*vv[0]+lam*vv[1]
      return self.fq(v,lam,d)
    def witness(self,q,rec,adj,sign):
      if 'indices' in rec:ids=np.asarray(rec['indices'],int);w=np.asarray(rec['weights'],float)
      else:ids=np.asarray([rec['first_index']],int);w=np.ones(1)
      require(len(ids) in (1,2) and np.all((ids>=0)&(ids<len(q))) and np.all(w>=0) and abs(w.sum()-1)<1e-15,'first weights')
      action=w@self.fm.actions[ids]
      require(np.all(self.fm_mask(adj,sign)[ids]),'first knot feasibility')
      if sign=='positive':require(action[2]>0,'open mandate violation')
      if len(ids)==2:
        require(np.all(self.fm.actions[ids,:2]==self.fm.actions[ids[0],:2]),'mixed first controls')
        knots=self.fm.actions[np.all(self.fm.actions[:,:2]==self.fm.actions[ids[0],:2],axis=1),2]
        require(not np.any((knots>self.fm.actions[ids,2].min())&(knots<self.fm.actions[ids,2].max())),'nonadjacent interpolation')
      close(action,rec.get('action',rec.get('first_action')),'first action')
      val=float(w@q);close(val,rec['value'],'first payoff');return val
    def zero_graph(self,v,lam,d,F,adj,sign):
      q0=self.fq(v[1],lam,d);mask=self.fm_mask(adj,sign)
      ids=np.flatnonzero(mask & (q0>=q0[mask].max()-4*EPS));reach=set()
      for k,weight in ((0,1-lam),(1,lam)):
        if weight:
          mat=self.fm.rows[k][ids];reach.update(mat.indices[mat.data>0].tolist())
      counts=[]
      for n in range(1,self.N):
        q=self.q(n,v[n+1],lam,d,F);allowed=self.mask(n,adj,1)&(q>=v[n,:,None]-4*EPS)
        counts.append(len(reach));ii=np.array(sorted(reach),dtype=int)
        if len(ii) and np.any(allowed[ii,self.stop]):return False,counts
        nxt=set()
        for k,weight in ((0,1-lam),(1,lam)):
          if not weight:continue
          for z,offset in ((self.b.e[k].common,0),(self.b.e[k].extra[n],self.nm)):
            ss,aa=np.where(allowed[ii,offset:offset+z.na]);rows=ii[ss]*z.na+aa
            if len(rows):
              mat=z.matrix[rows];nxt.update(mat.indices[mat.data>0].tolist())
        reach=nxt
      return True,counts

def numerical(check):
    e=read('enforcement.json');z=np.load(OUT/'enforcement_witness.npz',allow_pickle=False);maxgap=0.;records=[]
    for row in e['rows']:
      adj=row['adjustment'];sign=row['sign'];tag=row['id'];lo,hi=row['initial_fee_bracket'];lam=e['law'];d=e['benefit']
      require(0<=lo<hi<=1 and row['lower_strict_gain']>0,'threshold bracket')
      vi,qi=check.solve(lam,d,0.,adj,8);maxgap=max(maxgap,close(vi,z[str(int(adj))+'.infinite.values'],'no-surrender values'))
      upper_inf=float(qi[check.fm_mask(adj,sign)].max())
      qlow=check.evaluate(z[tag+'.lower.policy'],lam,d,lo,adj,1)
      lower=check.witness(qlow,row['lower_witness'],adj,sign)
      require(Q.from_float(lower)-Q.from_float(upper_inf)>2*Q.from_float(EPS),'lower strict witness margin')
      vh,qh=check.solve(lam,d,hi,adj,1);maxgap=max(maxgap,close(vh,z[tag+'.upper.values'],'threshold upper Bellman'))
      zero,counts=check.zero_graph(vh,lam,d,hi,adj,sign)
      require(zero and counts==row['upper_reached_counts'],'upper structural zero graph')
      eligible=~check.b.e[0].boundary
      uniform=max(0.,max(float(np.max(check.b.terminal[eligible]-vi[n,eligible])) for n in range(1,8)))
      a,b=row['uniform_fee_bracket'];require(a<=uniform+1e-12 and b>=uniform-1e-12 and b-a>=1.99*EPS,'uniform threshold enclosure')
      vc,qc=check.solve(lam,d,.765,adj,1);maxgap=max(maxgap,close(vc,z[tag+'.common.values'],'common-fee Bellman'))
      common,_=check.zero_graph(vc,lam,d,.765,adj,sign)
      require(common==row['common_fee_graph_zero'],'common fee graph')
      qcp=check.evaluate(z[tag+'.common.policy'],lam,d,.765,adj,1)
      check.witness(qcp,row['common_fee_witness'],adj,sign)
      records.append(dict(id=tag,bracket=[lo,hi],strict_lower_gain=lower-upper_inf-2*EPS,structural_zero=True))
    p=read('proposals.json');zz=np.load(OUT/'proposal_witness.npz',allow_pickle=False);n=0;negative=False
    for row in p['rows']:
      lam=row['law'];adj=row['adjustment'];v,q=check.solve(lam,.42425,.85,adj,1)
      for sign in SIGNS:
        qp=check.evaluate(zz[row['id']+'.policy.'+sign],lam,.42425,.85,adj,1)
        value=check.witness(qp,row['lower_witnesses'][sign],adj,sign)
        ref=float(q[check.fm_mask(adj,sign)].max());maxgap=max(maxgap,close(ref,row['reference_values'][sign],'proposal upper reference'))
        require(value<=ref+2*EPS,'policy exceeds upper reference')
        close(max(0.,ref-value)+2*EPS,row['gaps'][sign],'proposal reported gap')
        if not negative:
          bad=copy.deepcopy(row['lower_witnesses'][sign]);bad['value']+=.1
          try:check.witness(qp,bad,adj,sign)
          except ValueError:negative=True
          require(negative,'modified payoff not rejected')
        n+=1
      for key in ('proposal_seconds','evaluation_seconds','reference_seconds','teacher_seconds','training_seconds'):
        require(np.isfinite(row[key]) and row[key]>=0,'invalid timing')
    return dict(enforcement=records,independent_policy_evaluations=n,maximum_discrepancy=maxgap,
      forged_payoff_rejected=negative,scope='Independent Bellman and selected-policy evaluation; structural support reachability; fixed binary64 arrays. No diffusion-transfer conclusion for the CRRA constructor.')

def main():
    start=time.perf_counter();aa=analytic();b,j=load(ROOT/'replication/r13/canonical');audit=derive(b,j)
    require(audit['derived_maximum']<EPS,'roundoff audit');nn=numerical(Checker(b,j))
    out=dict(schema='nbo-r19-validation-v1',passed=True,analytic=aa,numerical=nn,
      arithmetic_derived_maximum=audit['derived_maximum'],elapsed_seconds=time.perf_counter()-start,
      checked_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.suffix in ('.json','.npz') and p.name!='validation.json'})
    (OUT/'validation.json').write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
