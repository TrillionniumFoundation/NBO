"""One fixed protocol; clean execution records every task, including failures."""
from __future__ import annotations
import argparse,traceback,time
from common import *
import training,evaluation,observation,reference

def main(shard,smoke=False):
    out=R/('development' if smoke else 'results')/str(shard);out.mkdir(parents=True,exist_ok=True);ledger=[]
    # Pay the shared optimizer/runtime initialization before comparative clocks.
    torch.manual_seed(0);q=torch.nn.Parameter(torch.zeros(1));opt=torch.optim.Adam([q]);(q*q).sum().backward();opt.step()
    def call(name,fn,*args,**kwargs):
        t=time.perf_counter()
        try:r=fn(*args,**kwargs);ledger.append(dict(task=name,success=True,seconds=time.perf_counter()-t));return r
        except Exception as exc:
            text=traceback.format_exc();(out/(name+'.error.txt')).write_text(text)
            ledger.append(dict(task=name,success=False,seconds=time.perf_counter()-t,error=str(exc)));print(text,flush=True);return None
    if shard=='reference':call('reference',reference.run,out,smoke)
    elif shard=='aux':
        call('observation',observation.audit,out)
        seed=PROTOCOL['auxiliary_seed'];variants=[('value_only',dict(costate_weight=0.)),('costate_only',dict(value_weight=0.)),('updates1',dict(updates=1)),('updates10',dict(updates=10)),('width16',dict(width=16)),('width64',dict(width=64))]
        dims=[10] if smoke else PROTOCOL['auxiliary_dimensions']
        for d in dims:
            specs=[('nbo',name,kw) for name,kw in variants]+[(method,f'r{eps:g}',dict(epsilon=eps)) for eps in PROTOCOL['fresh_radius_fits'] for method in ['nbo','dpo']]
            if smoke:specs=specs[:1]
            for method,tag,kw in specs:
                tr=call(f'fit_{d}_{method}_{tag}',training.train,d,seed,method,out,tag='_'+tag,seconds=.3 if smoke else None,**kw)
                if tr and tr.get('weights_sha256'):
                    call(f'eval_{d}_{method}_{tag}',evaluation.evaluate,out/(tr['id']+'.pt'),out,design='population',steps=32 if smoke else None,paths=64 if smoke else None,test_seed=PROTOCOL['development_noise_seed'] if smoke else None)
        # Full state stresses are separately run for both main nonlinear methods.
        if not smoke:
            for d in PROTOCOL['dimensions']:
                for method in ['nbo','dpo']:
                    tr=call(f'stressfit_{d}_{method}',training.train,d,seed,method,out,tag='_stress')
                    if tr and tr.get('weights_sha256'):
                        for shift,spread in PROTOCOL['initial_state_stresses']:
                            call(f'stress_{d}_{method}_{shift}_{spread}',evaluation.evaluate,out/(tr['id']+'.pt'),out,design='stress',shift=shift,spread=spread)
    else:
        seed=int(shard);dims=[1] if smoke else PROTOCOL['dimensions']
        for d in dims:
            fits={};methods=PROTOCOL['methods'];rotate=seed%len(methods);order=methods[rotate:]+methods[:rotate]
            for method in order:
                tr=call(f'fit_{d}_{method}',training.train,d,seed,method,out,seconds=.3 if smoke else None)
                if tr and tr.get('weights_sha256'):fits[method]=tr
            for design in PROTOCOL['designs']:
                rows={}
                for method,tr in fits.items():
                    row=call(f'eval_{d}_{method}_{design}',evaluation.evaluate,out/(tr['id']+'.pt'),out,design=design,steps=32 if smoke else None,paths=64 if smoke else None,test_seed=PROTOCOL['development_noise_seed'] if smoke else None)
                    if row:rows[method]=row
                for left,right in PROTOCOL['method_contrasts']:
                    if left in rows and right in rows:
                        call(f'pair_{d}_{left}_{right}_{design}',evaluation.paired,out/(rows[left]['id']+'.json'),out/(rows[right]['id']+'.json'),out)
    result=dict(shard=str(shard),source_commit=source(),protocol_sha256=digest(R/'PROTOCOL.json'),smoke=smoke,tasks=ledger,all_tasks_completed=all(x['success'] for x in ledger))
    write(out/'EXECUTION.json',result)
    if not result['all_tasks_completed']:raise SystemExit(1)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--shard',required=True);p.add_argument('--smoke',action='store_true');a=p.parse_args();main(a.shard,a.smoke)
