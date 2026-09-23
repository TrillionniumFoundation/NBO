"""Numerical regressions for the budget-coordinate derivation, not model proofs."""
from pathlib import Path
import json,sys,math,time,hashlib
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r23'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r22/replication'))
from crossed import Actor,Slab,NODES
from budget_coordinates import setup,implicit_offset,QuotientSlab,RootAccounting

def main():
 torch.set_default_dtype(torch.float64);torch.set_num_threads(1)
 records=[];gen=torch.Generator().manual_seed(23999)
 for scale in [.01,1.,20.,100.]:
  base=scale*torch.randn(17,generator=gen);weights=torch.linspace(.3,1.7,17);target=.41*float(weights.sum())
  z=base.clone().requires_grad_(True);ac=RootAccounting();a=implicit_offset(z,weights,target,ac)
  gradient=torch.autograd.grad(a,z)[0];sig=torch.sigmoid(z.detach()+float(a.detach()));expected=-weights*sig*(1-sig)/(weights*sig*(1-sig)).sum()
  fd=[];step=2e-5
  for j in range(17):
   plus=base.clone();minus=base.clone();plus[j]+=step;minus[j]-=step
   fd.append((float(implicit_offset(plus,weights,target))-float(implicit_offset(minus,weights,target)))/(2*step))
  err=float((gradient-expected).abs().max());fderr=float(np.max(np.abs(gradient.numpy()-np.asarray(fd))))
  assert err<2e-14 and fderr<2e-8
  shifts=[]
  for shift in [-1e6,-1000.,0.,1000.,1e6]:
   transformed=base+shift;transformed=transformed-transformed.mean();aa=implicit_offset(transformed,weights,target)
   error=float((torch.sigmoid(transformed+aa)-sig).abs().max())
   assert error<2e-9
   shifts.append({'shift':shift,'delivered_sigmoid_difference':error})
  records.append({'scale':scale,'analytic_gradient_max_error':err,'finite_difference_max_error':fderr,'common_shift_derivative':float(gradient.sum()),'translations':shifts,'root_budget_residual':ac.max_absolute_discrete_budget_residual})
 invalid=[]
 for label,z,w,t in [('nan_logits',torch.tensor([float('nan')]),torch.ones(1),.5),('negative_weight',torch.zeros(2),torch.tensor([1.,-1.]),.5),('endpoint_budget',torch.zeros(2),torch.ones(2),2.)]:
  try:implicit_offset(z,w,t)
  except (FloatingPointError,ValueError,ArithmeticError):invalid.append(label)
  else:raise AssertionError(label+' was not rejected')
 torch.manual_seed(23000);neural=Actor();direct=Slab(neural(NODES));quotient=QuotientSlab(neural(NODES));obj=setup(1.98,1.24)
 a,b,c=[obj(m,details=True) for m in [neural,direct,quotient]]
 assert all(a[k]==b[k] for k in ('b','s','theta','approx_budget','approx_value'))
 qerr=max(abs(x-y) for k in ('b','s','theta') for x,y in zip(a[k],c[k]));assert qerr<2e-12
 result={'status':'PASS','protocol_commit':'f0ab87bec39e4ba96a49bd01ba5608a7de739bed','cases':records,'invalid_inputs_rejected':invalid,'exact_neural_direct_initial_match':True,'quotient_delivered_coefficient_max_error':qerr,'dimension_neural':sum(p.numel() for p in neural.parameters()),'dimension_direct':sum(p.numel() for p in direct.parameters()),'dimension_quotient':sum(p.numel() for p in quotient.parameters()),'scope':'floating-point numerical/code regressions; continuous-model validity requires the separate directed certifier and analytic proofs'}
 (REV/'results').mkdir(exist_ok=True);(REV/'results/root_tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
