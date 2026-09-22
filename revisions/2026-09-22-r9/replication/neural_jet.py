"""Outward interval derivatives of the actual retained neural critics.
Exact stored weights and state coordinates are interpreted as real constants.
The resulting jet error links the non-enumerative action certificate to a
learned neural function, rather than only to a floating-point gradient vector.
"""
from __future__ import annotations
import json,pathlib,time,hashlib
import numpy as np
import torch
from mpmath import iv
iv.dps=60
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'
def I(x):return iv.mpf(x)
def bounds(x):return [float(np.nextafter(float(x.a),-np.inf)),float(np.nextafter(float(x.b),np.inf))]
def neural_gradient(state,x,t):
 d=len(x);h=[I(float(t))]+[I(float(z)) for z in x]
 J=[[I(int(i==j+1)) for j in range(d)] for i in range(d+1)]
 for layer in [0,2,4]:
  W=state[f'net.{layer}.weight'].cpu().numpy();b=state[f'net.{layer}.bias'].cpu().numpy()
  H=[];K=[]
  for i in range(len(b)):
   weights=[I(float(z)) for z in W[i]]
   q=I(float(b[i]))+sum(w*z for w,z in zip(weights,h))
   jac=[sum(w*J[k][j] for k,w in enumerate(weights)) for j in range(d)]
   if layer!=4:
    e=iv.exp(2*q);y=(e-1)/(e+1);s=1-y*y
    H.append(y);K.append([s*z for z in jac])
   else:H.append(q);K.append(jac)
  h,J=H,K
 X=[I(float(z)) for z in x];shared=I('.2')/iv.sqrt(I(d))*iv.sin(sum(X)/iv.sqrt(I(d)))
 return [2*(X[j]-I('.5'))/d-shared+(1-I(float(t)))*J[0][j] for j in range(d)]
def run():
 actions=json.loads((OUT/'action_certificates.json').read_text());rows=[]
 for d in [8,16]:
  entries=[r for r in actions if r['dimension']==d];r=entries[0];path=ROOT/r['provenance']['checkpoint'];start=time.perf_counter()
  assert hashlib.sha256(path.read_bytes()).hexdigest()==r['provenance']['sha256']
  data=torch.load(path,map_location='cpu',weights_only=True)
  jets=neural_gradient(data['critic'],r['provenance']['state'],r['provenance']['time']);p=r['gradient'];errors=[]
  for q,z in zip(jets,p):
   a=q-I(float(z));bb=bounds(a);errors.append(max(abs(bb[0]),abs(bb[1])))
  err=sum(I(e) for e in errors);enclosure=[bounds(q) for q in jets]
  updates=[]
  for a in entries:
   lower=bounds(I(a['lower_bound'])-2*err)[0];upper=bounds(I(a['upper_bound'])+2*err)[1]
   gap=bounds(I(a['gap'])+4*err)[1]
   updates.append({'tolerance':a['tolerance'],'true_neural_hamiltonian_lower':lower,'true_neural_candidate_upper':upper,'true_neural_action_gap_upper':gap})
  row={'dimension':d,'critic_checkpoint':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
   'gradient_intervals':enclosure,'component_error_bounds':errors,'l1_gradient_error_upper':bounds(err)[1],
   'action_certificates':updates,'seconds':time.perf_counter()-start,
   'scope':'True mathematical neural critic at this single stored state; no whole-state residual or policy-regret conclusion'}
  rows.append(row);print(d,row['l1_gradient_error_upper'],row['seconds'],flush=True)
 (OUT/'neural_jet_certificates.json').write_text(json.dumps(rows,indent=2)+'\n');return rows
if __name__=='__main__':run()
