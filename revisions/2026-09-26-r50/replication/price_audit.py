"""Retrospective uncapped-price audit. Exact occupation witnesses bound the uncapped LP optimum.
This diagnostic uses exact finite Bellman values, not a costly operating oracle.
"""
from fractions import Fraction as F
from pathlib import Path
import sys,json,time,gzip,hashlib,itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'2026-09-26-r48'/'replication'))
import core
Z=F(0)

def matrices(d,adv,mu):
 n,T,m=d['n'],d['T'],d['m'];keys=[];idx={};rows=[];rhs=[];labels=[]
 def var(key):idx[key]=len(keys);keys.append(key)
 for t in range(T):
  for i in range(n):var(('v',t,i));var(('l',t,i))
 for t in range(T-1):
  for i in range(n):
   for j in range(n):
    if any(d['P'][t][i][a][j] for a in range(m)):var(('h',t,i,j))
 for key in keys:
  if key[0]=='h':
   _,t,i,j=key
   rows.append({idx[key]:F(1),idx['l',t,i]:F(-1)});rhs.append(Z);labels.append(('alpha',t,i,j))
   rows.append({idx[key]:F(1),idx['l',t+1,j]:F(-1)});rhs.append(Z);labels.append(('gamma',t,i,j))
 for t in range(T):
  for i in range(n):
   for a in range(m):
    row={idx['v',t,i]:F(1),idx['l',t,i]:d['epsilon']-adv[t][i][a]}
    if t<T-1:
     for j,p in enumerate(d['P'][t][i][a]):
      if p:row[idx['v',t+1,j]]=-d['beta']*p;row[idx['h',t,i,j]]=-d['beta']*d['epsilon']*p
    rows.append(row);rhs.append(d['k'][t][i][a]);labels.append(('y',t,i,a))
 c=[Z]*len(keys)
 for i,v in enumerate(mu):c[idx['v',0,i]]=v
 return keys,idx,rows,rhs,c,labels

def solve(d,adv,mu,cap=None):
 keys,idx,rows,rhs,c,labels=matrices(d,adv,mu);ii=[];jj=[];vv=[]
 for i,r in enumerate(rows):
  for j,v in r.items():ii.append(i);jj.append(j);vv.append(float(v))
 A=coo_matrix((vv,(ii,jj)),shape=(len(rows),len(keys))).tocsr()
 bounds=[(None,None) if key[0]=='v' else (0,float(cap) if cap is not None else None) for key in keys]
 r=linprog(-np.array(c,float),A_ub=A,b_ub=np.array(rhs,float),bounds=bounds,method='highs-ds',options={'time_limit':8})
 if r.x is None:return {'status':int(r.status),'certified':False}
 field=[[max(Z,min(F(cap),core.dyad(r.x[idx['l',t,i]]))) if cap is not None else max(Z,core.dyad(r.x[idx['l',t,i]])) for i in range(d['n'])] for t in range(d['T'])]+[[Z]*d['n']]
 u,clipped=core.price_replay(d,{'dl':adv},field);L=core.dot(mu,u[0]);cert=dict(status=int(r.status),field=field,masked_lower=L,clipped_lower=clipped,certified=False)
 if cap is not None:return cert
 # Reconstruct exact flow from numerical conditional occupations, then repair
 # capacity inequalities by mixing with an explicit strictly feasible occupation.
 dual={lab:max(Z,F(str(float(-r.ineqlin.marginals[i])))) for i,lab in enumerate(labels)}
 n,T,m=d['n'],d['T'],d['m'];beta=d['beta'];eps=d['epsilon']
 peak=max(z for date in adv for row in date for z in row)
 theta=min(F(1,2),eps*(1-beta)/(4*peak)) if peak else F(1,2)
 def make(strict):
  occ={};mass=[list(mu)]+[[Z]*n for _ in range(T)]
  for t in range(T):
   for i in range(n):
    best=min(range(m),key=lambda a:adv[t][i][a])
    if strict:row=[theta/m+(1-theta if a==best else Z) for a in range(m)]
    else:
     row=[dual.get(('y',t,i,a),Z) for a in range(m)];z=sum(row)
     row=[v/z for v in row] if z else [F(a==best) for a in range(m)]
    for a in range(m):occ['y',t,i,a]=mass[t][i]*row[a]
    if t<T-1:
     for j in range(n):
      f=beta*sum(occ['y',t,i,a]*d['P'][t][i][a][j] for a in range(m));mass[t+1][j]+=f
      aa=dual.get(('alpha',t,i,j),Z);gg=dual.get(('gamma',t,i,j),Z)
      z=F(1,2) if strict or aa+gg==0 else aa/(aa+gg)
      occ['alpha',t,i,j]=eps*f*z;occ['gamma',t,i,j]=eps*f*(1-z)
  return occ
 a=make(False);ref=make(True);mix=Z
 def slack(occ,t,i):
  return sum(occ.get(('y',t,i,b),Z)*(eps-adv[t][i][b]) for b in range(m))-sum(occ.get(('alpha',t,i,j),Z) for j in range(n))-(sum(occ.get(('gamma',t-1,h,i),Z) for h in range(n)) if t else Z)
 for t in range(T):
  for i in range(n):
   v=slack(a,t,i);h=slack(ref,t,i)
   assert h>=0
   if v<0:
    assert h>0
    mix=max(mix,(-v)/(h-v))
 occ={key:(1-mix)*a.get(key,Z)+mix*ref.get(key,Z) for key in set(a)|set(ref)}
 U=sum(occ.get(('y',t,i,a),Z)*d['k'][t][i][a] for t in range(T) for i in range(n) for a in range(m))
 assert U>=L
 cert.update(certified=True,upper=U,occupation=[dict(label=list(lab),value=z) for lab,z in sorted(occ.items()) if z],repair_mix=mix,variables=len(keys),constraints=len(rows))
 return cert

def advantages(d):
 n,T,m=d['n'],d['T'],d['m'];V=[[] for _ in range(T+1)];V[T]=d['g']
 for t in reversed(range(T)):V[t]=[max(d['r'][t][i][a]+d['beta']*core.dot(d['P'][t][i][a],V[t+1]) for a in range(m)) for i in range(n)]
 return [[[V[t][i]-d['r'][t][i][a]-d['beta']*core.dot(d['P'][t][i][a],V[t+1]) for a in range(m)] for i in range(n)] for t in range(T)]

def audit(path):
 from check_price import verify
 start=time.perf_counter();raw=json.loads(Path(path).read_text());d=core.load(raw);adv=advantages(d);w=core.witness(d,F(1,1000));p,U,meta=core.repair(d,w,greedy=True);J,C=core.policy_value(d,p)
 support=[i for i,v in enumerate(d['nu']) if v];masks=[list(s) for k in range(1,len(support)+1) for s in itertools.combinations(support,k)]
 certificates=[];best=Z;remaining=[]
 for mask in masks:
  mu=[d['nu'][i] if i in mask else Z for i in range(d['n'])];fallback=core.dot(mu,C[0])
  if fallback<=best:
   certificates.append(dict(mask=mask,skipped=True,upper=fallback));continue
  cert=solve(d,adv,mu);cert.update(mask=mask,skipped=False)
  if cert.get('certified'):
   cert['occupation_upper']=cert['upper'];cert['upper']=min(cert['upper'],fallback)
  else:cert['upper']=fallback
  best=max(best,cert.get('clipped_lower',Z));certificates.append(cert)
 ideal_upper=max([Z]+[v['upper'] for v in certificates]);cap_rows=[]
 for cap in [256,1024,4096,16384]:
  selected=[[Z]*d['n'] for _ in range(d['T']+1)];_,portfolio=core.price_replay(d,{'dl':adv},selected);attempts=[]
  # All masks rather than state-count-based truncation; exact ideal upper above is cap free.
  for mask in masks:
   mu=[d['nu'][i] if i in mask else Z for i in range(d['n'])];c=solve(d,adv,mu,F(cap))
   if c.get('clipped_lower',Z)>portfolio:portfolio=c['clipped_lower'];selected=c['field']
   attempts.append({'mask':mask,'status':c['status']})
  cap_rows.append(dict(cap=cap,field=selected,lower=portfolio,loss_upper=ideal_upper-portfolio,attempts=attempts))
 e=core.enc(dict(schema='nbo-r50-price-audit-v1',model=raw,policy=p,certificates=certificates,ideal_lower=best,ideal_upper=ideal_upper,cap_rows=cap_rows,construction_seconds=time.perf_counter()-start))
 ts=time.perf_counter();v=verify(e,raw);e['verification_seconds']=time.perf_counter()-ts;e['verification']=v
 root=Path(__file__).resolve().parent.parent;out=root/'proofs'/f'price-audit-{Path(path).stem}.json.gz';blob=gzip.compress(json.dumps(e,separators=(',',':')).encode(),mtime=0);out.write_bytes(blob)
 summ={k:e[k] for k in ['ideal_lower','ideal_upper','cap_rows','construction_seconds','verification_seconds','verification']};summ.update(case=Path(path).stem,masks=len(masks),exact_occupation_certificates=sum(c.get('certified',False) for c in certificates),pruned_masks=sum(c.get('skipped',False) for c in certificates),proof_bytes=len(blob),proof_sha256=hashlib.sha256(blob).hexdigest())
 (root/'results'/f'price-audit-{Path(path).stem}.json').write_text(json.dumps(summ,indent=2)+'\n');print(Path(path).stem,'masks',len(masks),'exact',summ['exact_occupation_certificates'],'gap',float(F(e['ideal_upper'])-F(e['ideal_lower'])),'sec',e['construction_seconds'],flush=True)
if __name__=='__main__':audit(sys.argv[1])
