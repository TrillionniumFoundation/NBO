"""Executed diagnostics: conditioning, immutable R16 loss mismatch, controls,
and a rigorous witness-specific refinement floor. No floor is actual regret.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,hashlib
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];R16=ROOT/'revisions/2026-09-23-r16';OUT=HERE.parent/'results'
sys.path.insert(0,str(R16/'replication'));import accessibility_certificate as C
I,Q,exp,log=C.I,C.Q,C.exp,C.log

def main():
    out=OUT/'diagnostics';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for n in [64,128,256]:
        q=exp(-Q('.04')/n);amp=2*q/(1-q).square();res=1/(1-q)
        rows.append({'time_steps':n,'q':q.pair(),'evaluation_amplifier':amp.pair(),'greedy_amplifier':res.pair(),'one_step_evaluation_defect_for_0.01':float((Q('.01')/amp).lo)})
    (out/'finite_mdp_conditioning.json').write_text(json.dumps(rows,indent=2)+'\n')
    hist=[]
    for seed in range(16100,16110):
        p=R16/'results/neural'/f'seed{seed}';h=json.loads((p/'history.json').read_text());c0=json.loads((p/'certificate800.json').read_text());c1=json.loads((p/'certificate2400.json').read_text())
        a=next(x for x in h if x['step']==800);b=next(x for x in h if x['step']==2400)
        hist.append({'seed':seed,'bound800':c0['t0_regret_upper'],'bound2400':c1['t0_regret_upper'],'bound_ratio':c1['t0_regret_upper']/c0['t0_regret_upper'],'history800':a,'history2400':b})
    (out/'r16_loss_mismatch.json').write_text(json.dumps(hist,indent=2)+'\n')
    floors=[];jump=Q('6.45')-Q('.1')*log(Q(2))-Q('25.1')*exp(-Q(8));s=I([[0.,2.,2.]])
    for arch in ['accessible','allface']:
        for seed in range(17100,17110):
            p=OUT/arch/f'seed{seed}'/'network_step0400.json';d=json.loads(p.read_text());j=C.critic_jet(s,d);g=-Q('.02')*Q(0)+Q('.1')*log(Q(2))-8
            trace=j[0]-g;lower=jump-I(float(trace.hi[0]));floors.append({'architecture':arch,'seed':seed,'continuation_jump_lower':float(jump.lo),'upper_trace_excess_interval':[float(trace.lo[0]),float(trace.hi[0])],'positive_residual_certificate_floor_lower':max(0.,float(lower.lo)),'scope':'Lower bound on the integrated supremum positive Bellman residual for this fixed critic, independent of cover resolution. NOT a lower bound on policy regret.'})
    (out/'witness_floor.json').write_text(json.dumps(floors,indent=2)+'\n')
    # Full-box bounds for each actual change in controls, plus center diagnostics.
    cells,idx=C.cell_grid(4,16,16);control=[]
    for seed in range(17100,17110):
        p=OUT/'accessible'/f'seed{seed}';a=json.loads((p/'network_step0000.json').read_text());b=json.loads((p/'network_step0400.json').read_text())
        av=C.actions(cells,a,0.);bv=C.actions(cells,b,0.)
        control.append({'seed':seed,'complete_cells':len(idx),'final_action_hulls':[[float(z.lo.min()),float(z.hi.max())] for z in bv],'uniform_action_change_upper':[float((x-y).maxabs().max()) for x,y in zip(av,bv)],'scope':'Exact-real controls over the entire original state-time domain; conservative interval hulls, not statistical confidence intervals'})
    (out/'control_changes.json').write_text(json.dumps(control,indent=2)+'\n')
    # A predesignated factorial recombination quantifies the witness/actor roles.
    p=OUT/'accessible/seed17100';a=json.loads((p/'network_step0000.json').read_text());b=json.loads((p/'network_step0400.json').read_text());causal=[]
    for actorstep,criticstep in [(0,400),(400,0)]:
        d=dict(b);d['actor']=(a if actorstep==0 else b)['actor'];d['critic']=(a if criticstep==0 else b)['critic'];d['factorial_components']={'actor_step':actorstep,'critic_step':criticstep};npth=out/f'factorial_a{actorstep}_v{criticstep}.json';npth.write_text(json.dumps(d,indent=2)+'\n');r=C.audit(npth,out/f'factorial_a{actorstep}_v{criticstep}_certificate.json',chunk=1024);causal.append({'actor_step':actorstep,'critic_step':criticstep,'bound':r['t0_regret_upper']})
    (out/'factorial_summary.json').write_text(json.dumps(causal,indent=2)+'\n')
    print('diagnostics complete',flush=True)
if __name__=='__main__':main()
