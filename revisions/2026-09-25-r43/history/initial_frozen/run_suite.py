"""Execute every registered R43 case; retain failures and solver stops."""
from pathlib import Path
from fractions import Fraction as F
import gzip, hashlib, json, os, platform, sys, time
import numpy, scipy
from regret import model, solve, write_proof, reference, enc
from verify_regret import verify
ROOT=Path(__file__).resolve().parents[1]

def save(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,default=enc,indent=2)+'\n')

def theoretical(d):
    V,H,star,loss,gain,lo,hi,strict=reference(d)
    if not strict: return dict(strict=False,bound=None)
    b=d['beta']; eps=d['epsilon']; n,T,m=d['n'],d['T'],d['m']
    ed=F(0); es=F(0); maxed=F(0)
    for t in range(T-1,-1,-1):
        if t==T-1: e=F(0)
        else:
            c=max(sum((sum(abs(x-y) for x,y in zip(d['P'][i][a],d['P'][i][star[t][i]]))/loss[t][i][a] for a in range(m) if a!=star[t][i]),F(0)) for i in range(n))
            e=b*eps**2*c/4
        ed=e+b*ed; es=(hi-lo)*e+b*es; maxed=max(maxed,ed)
    dmin=min(loss[t][i][a] for t in range(T) for i in range(n) for a in range(m) if a!=star[t][i])
    dc=max(x for row in d['k'] for x in row)*sum((F(j+1)*b**j for j in range(T)),F(0))
    rho=maxed/((1-b)*eps+maxed)
    return dict(strict=True,d_min=str(dmin),E_D=str(maxed),E_S=str(es),D_C=str(dc),repair_fraction_bound=str(min(F(1),eps/dmin)*rho),exact_LP_width_bound=str(es+dc*min(F(1),eps/dmin)*rho),assumption='exact LP optimizer; rounding and dual residual losses excluded from this theoretical number')

def one(name,d,mode,cap):
    path=ROOT/'proofs'/(name+'_'+mode+'.json.gz')
    try:
        proof,meta=solve(d,mode,cap)
        sha=write_proof(path,proof); check=verify(path)
        row=dict(case=name,seed=d['seed'],n=d['n'],T=d['T'],m=d['m'],beta=str(d['beta']),epsilon=str(d['epsilon']),policy_coordinates=d['n']*d['T']*(d['m']-1),**meta,proof_sha256=sha,check=check,theory=theoretical(d))
        assert check['lower']==meta['lower'] and check['upper']==meta['upper']
    except Exception as exc:
        row=dict(case=name,seed=d['seed'],n=d['n'],T=d['T'],m=d['m'],beta=str(d['beta']),epsilon=str(d['epsilon']),mode=mode,failure=type(exc).__name__+': '+str(exc))
    save(ROOT/'results'/(name+'_'+mode+'.json'),row)
    print(name,mode,('FAIL '+row['failure']) if 'failure' in row else ('gap='+str(row['gap'])+' relative='+str(row['relative_gap'])+' lp_seconds='+str(row['lp_seconds'])),flush=True)
    return row

def mutations(source):
    base=json.loads(gzip.decompress(source.read_bytes())); results=[]
    for name in ('endpoint','negative_probability','negative_dual','transition_mass'):
        o=json.loads(json.dumps(base))
        if name=='endpoint': o['lower']=str(F(o['lower'])+1)
        elif name=='negative_probability': o['policy'][0][0][0]='-1'
        elif name=='negative_dual': o['lambda_nonnegative'][0]='-1'
        else: o['model']['P'][0][0][0]=str(F(o['model']['P'][0][0][0])+F(1,100))
        tmp=ROOT/'results'/'mutation.json.gz'; tmp.write_bytes(gzip.compress(json.dumps(o).encode(),mtime=0))
        try: verify(tmp); rejected=False
        except (AssertionError,ValueError,ZeroDivisionError): rejected=True
        results.append(dict(mutation=name,rejected=rejected)); tmp.unlink()
    assert all(x['rejected'] for x in results)
    return results

def main():
    protocol=json.loads((ROOT/'PROTOCOL.json').read_text())
    # A protocol hash is a prospective identity check, not a correctness proof.
    for name,sha in protocol['source_sha256'].items():
        actual=hashlib.sha256((ROOT/'replication'/name).read_bytes()).hexdigest()
        assert actual==sha,(name,actual,sha)
    save(ROOT/'results'/'environment.json',dict(python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,platform=platform.platform(),threads={k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},protocol_sha256=hashlib.sha256((ROOT/'PROTOCOL.json').read_bytes()).hexdigest(),source_sha256=protocol['source_sha256']))
    rows=[]
    for c in protocol['finite_cases']:
        d=model(**{k:c[k] for k in ('seed','n','T','m','beta','epsilon')})
        for mode in ('unscaled','scaled'): rows.append(one(c['name'],d,mode,protocol['lp_time_cap_seconds']))
    save(ROOT/'results'/'finite_suite.json',rows)
    scales=[]
    for ep in protocol['scaling']['epsilons']:
        c=protocol['scaling']; d=model(c['seed'],c['n'],c['T'],c['m'],c['beta'],ep)
        for mode in ('unscaled','scaled'): scales.append(one('scale_'+ep.replace('.','p'),d,mode,protocol['lp_time_cap_seconds']))
    save(ROOT/'results'/'scaling.json',scales)
    c=protocol['continuum']; M=c['finest_cells']; fibers=[]
    for j in range(M+1):
        eps=F(c['epsilon'])/(1+F(j,M)); d=model(c['seed'],c['n'],c['T'],c['m'],c['beta'],str(eps))
        fibers.append(one('fiber_%02d'%j,d,'scaled',protocol['lp_time_cap_seconds']))
    integral=[]
    for cells in c['reported_cells']:
        if any('failure' in x for x in fibers):
            integral.append(dict(cells=cells,status='missing_fiber_certificate')); continue
        low=F(0); up=F(0); innergap=F(0)
        for i in range(cells):
            left=F(i,cells); right=F(i+1,cells); weight=right-left+(right**2-left**2)/4
            il=i*(M//cells); ir=(i+1)*(M//cells)
            low+=weight*F(fibers[il]['lower']); up+=weight*F(fibers[ir]['upper'])
            innergap+=weight*(F(fibers[ir]['upper'])-F(fibers[ir]['lower']))
        integral.append(dict(cells=cells,status='paired',lower=str(low),upper=str(up),gap=float(up-low),relative_gap=float((up-low)/up),weighted_finite_width=str(innergap),remaining_partition_and_value_change=str(up-low-innergap)))
    save(ROOT/'results'/'continuum.json',dict(model=c,fibers=fibers,integrals=integral,identity='r_z=(1+z)r; g_z=(1+z)g; k_z=(1+z/2)k; z_next=z; initial z uniform and regimes uniform'))
    good=next(ROOT/'proofs'/(x['case']+'_'+x['mode']+'.json.gz') for x in rows if 'failure' not in x)
    save(ROOT/'results'/'mutations.json',mutations(good))
    summary=dict(finite_rows=len(rows),finite_verified=sum('failure' not in r for r in rows),scaling_rows=len(scales),scaling_verified=sum('failure' not in r for r in scales),fiber_rows=len(fibers),fiber_verified=sum('failure' not in r for r in fibers),all_failures=[r for r in rows+scales+fibers if 'failure' in r])
    save(ROOT/'results'/'SUMMARY.json',summary)
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__': main()
