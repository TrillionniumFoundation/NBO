"""Directed payoff secants for original stopped economy, not gradient certificates."""
from __future__ import annotations
import importlib.util,json,sys,time
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r25'
spec=importlib.util.spec_from_file_location('study25',REV/'replication/study.py')
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M);S=M.S
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
from interval64 import I

def main():
    paths=[REV/f'results/heldout/seed25101/q8_16/{m}/checkpoint_400.json' for m in ('neural_adam','direct_lbfgsb')]
    raw=[torch.tensor(json.loads(p.read_text())['raw_outputs']) for p in paths]
    direction=S.CHART.T@(raw[1]-raw[0]).flatten();rows=[];start=time.perf_counter()
    for alpha in (0.,.25,.5,.75,1.):
        net=S.Coordinates((1-alpha)*raw[0]+alpha*raw[1],S.CHART);obj=S.setup();net.zero_grad(set_to_none=True)
        val=obj(net);val.backward();derivative=float((net.z.grad*direction).sum());actor=obj(net,True);cert,sec=S.cert(actor)
        if cert['status']!='CERTIFIED':raise RuntimeError((alpha,cert))
        rows.append({'alpha':alpha,'raw_outputs':net(S.NODES).detach().tolist(),'actor':actor,'certificate':cert,
                     'proposal_value':float(val.detach()),'proposal_directional_derivative':derivative,'checker_seconds':sec})
    secants=[]
    for a,b in zip(rows,rows[1:]):
        ia=I(*a['certificate']['value_interval']);ib=I(*b['certificate']['value_interval']);enclosure=((ib-ia)/I(.25)).pair()
        secants.append({'alpha_left':a['alpha'],'alpha_right':b['alpha'],'stopped_payoff_secant_interval':enclosure,
                        'pointwise_gradient_certificate':False})
    out={'protocol_commit':'b0e932c49b02759a7bcda3b30c534fdc390999b7','source_paths':[str(p.relative_to(ROOT)) for p in paths],
         'rows':rows,'secants':secants,'elapsed_seconds':time.perf_counter()-start,
         'rigorous_stopped_gradient_error_established':False,'post_selection_diagnostic_not_used_for_tuning':True}
    S.write(REV/'results/secants.json',out);print(json.dumps(secants),flush=True)
if __name__=='__main__':main()
