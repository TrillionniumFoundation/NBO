"""Complete frozen-run attribution and trace intervention; not new actor training."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,time
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19';OLD=ROOT/'revisions/2026-09-23-r17/results'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import accessibility_certificate as C
I,Q,exp,log=C.I,C.Q,C.exp,C.log

def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def components(c):
    p,n=I(0),I(0);nt=len(c['slabs'])
    for r in c['slabs']:
        t=r['slab'];mass=(exp(-Q('.04')*Q(F(t,nt)))-exp(-Q('.04')*Q(F(t+1,nt))))/Q('.04')
        p=p+mass*I(r.get('positive_upper',r.get('ep')));n=n+mass*I(r.get('negative_policy',r.get('em')))
    return {'positive_component_interval':p.pair(),'negative_component_interval':n.pair(),'total':c['t0_regret_upper']}

def trace(d):
    j=C.critic_jet(I([[0.,2.,2.]]),d);g=Q('.1')*log(Q(2))-8;z=j[0]-g
    return I(float(z.lo[0]),float(z.hi[0]))

def main():
    out=R/'results/attribution';out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    jump=Q('6.45')-Q('.1')*log(Q(2))-Q('25.1')*exp(-Q(8));traces=[];factorial=[];interventions=[]
    for seed in range(17100,17110):
        src=OLD/'accessible'/f'seed{seed}';d0=json.loads((src/'network_step0000.json').read_text());df=json.loads((src/'network_step0400.json').read_text())
        for step in [0,100,400]:
            p=src/f'network_step{step:04d}.json';d=json.loads(p.read_text());c=json.loads((src/f'certificate{step}.json').read_text());tr=trace(d)
            traces.append({'seed':seed,'step':step,'source_path':str(p.relative_to(ROOT)),'source_sha256':digest(p),'trace_excess':tr.pair(),
                'fixed_witness_floor_lower':max(0.,float((jump-I(float(tr.hi))).lo)),'continuation_jump_lower':float(jump.lo),**components(c)})
        for ai,vi in [(0,0),(400,0),(0,400),(400,400)]:
            if ai==vi:
                cp=src/f'certificate{ai}.json';c=json.loads(cp.read_text());new=False
            else:
                d=dict(df);d['actor']=(d0 if ai==0 else df)['actor'];d['critic']=(d0 if vi==0 else df)['critic'];d['factorial_components']={'actor_step':ai,'critic_step':vi}
                p=out/f'seed{seed}/a{ai}_v{vi}.json';cp=p.with_name(p.stem+'_certificate.json');write(p,d)
                c=json.loads(cp.read_text()) if cp.exists() else C.audit(p,cp,chunk=1024);new=True
            factorial.append({'seed':seed,'actor_step':ai,'critic_step':vi,**components(c),'certificate_path':str(cp.relative_to(ROOT)),
                'certificate_sha256':digest(cp),'new_arithmetic_execution':new,'scope':'frozen R17 actor/critic interchange; not a policy-value ordering'})
        write(out/'trace_trajectories.json',traces);write(out/'factorial.json',factorial)
        if seed<17105:
            d=json.loads(json.dumps(df));bias0=float(d['critic'][-1]['bias'][0]);lo=0.;hi=1.
            while True:
                d['critic'][-1]['bias'][0]=bias0+hi
                if trace(d).lo>=jump.hi:break
                hi*=2
                if hi>64:raise RuntimeError('Trace search did not certify a lift')
            for _ in range(40):
                mid=(lo+hi)/2;d['critic'][-1]['bias'][0]=bias0+mid
                if trace(d).lo>=jump.hi:hi=mid
                else:lo=mid
            d['critic'][-1]['bias'][0]=bias0+hi;tr=trace(d);assert tr.lo>=jump.hi
            p=out/f'seed{seed}/trace_lift.json';cp=p.with_name('trace_lift_certificate.json');write(p,d)
            c=json.loads(cp.read_text()) if cp.exists() else C.audit(p,cp,chunk=1024)
            interventions.append({'seed':seed,'bias_lift':hi,'trace_excess':tr.pair(),'delta':jump.pair(),'necessary_floor_zero':True,**components(c),
                'source_actor_unchanged':d['actor']==df['actor'],'certificate_path':str(cp.relative_to(ROOT)),
                'scope':'removal of one pointwise necessary obstruction, not a sufficient whole-domain witness construction'})
            write(out/'trace_interventions.json',interventions)
    baseline=[]
    for p in sorted((OLD/'unrestricted').rglob('certificate.json')):
        try:c=json.loads(p.read_text())
        except Exception:continue
        if 'slabs' in c and c['slabs'] and ('positive_upper' in c['slabs'][0] or 'ep' in c['slabs'][0]):baseline.append({'path':str(p.relative_to(ROOT)),**components(c)})
    write(out/'classical_signed.json',baseline)
    write(out/'resources.json',{'seconds':time.perf_counter()-start,'new_full_cover_audits':25,'reused_full_cover_audits':20,'historical_trace_checkpoints':30,
      'protocol_commit':'2e19256c5d40f7f0d090cccd6d86892958ae2147','arithmetic':'MPFR 128-bit with directed binary64 endpoints','scope':'arithmetic independent; shared mathematics'})
if __name__=='__main__':main()
