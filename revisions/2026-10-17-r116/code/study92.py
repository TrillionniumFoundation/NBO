"""Frozen deterministic catalogue; records never count as economic observations."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,os,platform,resource,time
import centered92 as c
R=Path(__file__).resolve().parents[1]
HORIZONS=(2,3,4,8,16,32,64)
ALPHAS=(F(0),F(1,2),F(3,4))
THETAS=(-1,0,1,2)
RADII=(F(0),F(1,64),F(1,8))

def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(c.strings(x),sort_keys=True,separators=(',',':'))+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def maxbits(x):
    if isinstance(x,F):return max(abs(x.numerator).bit_length(),x.denominator.bit_length())
    if isinstance(x,dict):return max((maxbits(v) for v in x.values()),default=0)
    if isinstance(x,(tuple,list)):return max((maxbits(v) for v in x),default=0)
    return 0

def main():
    start=time.perf_counter();start_cpu=time.process_time();out=R/'results92';out.mkdir(exist_ok=True)
    if list(out.glob('case-*.json')):raise RuntimeError('Existing catalogue: preserve or use an explicit clean replay directory')
    cases=[]
    for T in HORIZONS:
        for ai,alpha in enumerate(ALPHAS):
            for theta in THETAS:
                begin=time.perf_counter();m=c.fixture(T,alpha,theta);k,r,pi=c.prepare(m)
                bs=[c.bounds(m,k,r,pi,e) for e in RADII];fl=c.flow(m,k,r,pi,bs[0])
                record={'model':m,'kernels':k,'residuals':r,'policy':pi,'bounds':bs,'flow':fl}
                bits=maxbits(record);name=f'case-T{T}-a{ai}-p{theta}.json';write(out/name,record)
                cases.append({'file':name,'sha256':sha(out/name),'T':T,'alpha':alpha,'theta':theta,
                    'rational_bits_max_retained':bits,'computation_and_serialization_seconds':time.perf_counter()-begin,
                    'risk_affine_support_terms_one_pass':sum(len(x['q'])*3 for layer in k for row in layer for x in row),
                    'bounds':[{'radius':b['radius'],'scalar_bound':b['scalar_bound'],
                               'max_state_bound':max(b['initial_loss_bounds']),
                               'pieces_before':b['pieces_before'],'pieces_after':b['pieces_after']} for b in bs]})
    examples=[]
    for T in HORIZONS:
        m=c.absorbing(T);k,r,pi=c.prepare(m);b=c.bounds(m,k,r,pi,0)
        if b['scalar_bound']!=T or any(b['initial_loss_bounds']):raise AssertionError('Absorbing strict example')
        examples.append({'T':T,'scalar':b['scalar_bound'],'state_dependent':b['initial_loss_bounds']})
    report={'status':'executed','cases':cases,'case_count':len(cases),'interval_configurations':len(cases)*len(RADII),
       'absorbing':examples,'new_fit_attempts':0,'new_independent_economic_rows':0,
       'scope':'Deterministic finite-state original nested-AVaR fixtures, not an independent largest-vector or investment experiment',
       'ledger_scope':'Risk-affine support terms per backward pass; not a complete machine-independent operation or energy ledger',
       'process_seconds_to_summary':time.perf_counter()-start,'process_cpu_seconds_to_summary':time.process_time()-start_cpu,
       'peak_resident_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'machine':platform.machine(),
       'python':platform.python_version(),'source_files':{p.name:sha(p) for p in sorted((R/'code').glob('*92.py'))}}
    write(out/'SUMMARY92.json',report)
    print(json.dumps({k:v for k,v in c.strings(report).items() if k!='cases'},indent=2),flush=True)
if __name__=='__main__':main()
