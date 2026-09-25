"""Publication audit. Independent primitive registration and continuum sums.
Theorem statements remain analytic, not machine-checked. This program uses the
independent endpoint reader but not the constructor when verifying the audit.
"""
from fractions import Fraction as Q
from pathlib import Path
import gzip,hashlib,json,random,sys,time
from verify_regret import verify
R=Path(__file__).resolve().parents[1]

def primitive_check(raw):
    n,T,m,seed=raw['n'],raw['T'],raw['m'],raw['seed']; rng=random.Random(seed)
    prices=[Q(0),Q(9,100),Q(8,25),Q(11,20),Q(4,5)]
    assert list(map(Q,raw['terminal']))==[Q(j,2*(n-1)) for j in range(n)]
    assert list(map(Q,raw['nu']))==[Q(1,n)]*n
    for i in range(n):
        incumbent=0 if i>=n//2 else seed%2
        for a in range(m):
            integers=[max(1,38-10*a)+rng.randrange(4),36+rng.randrange(4),12+7*a+rng.randrange(4),2+11*a+rng.randrange(4)]
            expected=[Q(0)]*n
            for j,w in zip([max(0,i-1),i,min(n-1,i+1),n-1],integers): expected[j]+=Q(w,sum(integers))
            assert list(map(Q,raw['P'][i][a]))==expected
            assert Q(raw['r'][i][a])==Q(i,n-1)-prices[a]-Q(rng.randrange(1,20)*a,100000)
            assert Q(raw['k'][i][a])==(1+Q(i,n-1))*int(a!=incumbent)

def main():
    begin=time.perf_counter(); p=json.loads((R/'PROTOCOL_AMENDED.json').read_text())
    files={name:hashlib.sha256((R/'replication'/name).read_bytes()).hexdigest() for name in p['source_sha256']}
    assert files==p['source_sha256']
    original=json.loads((R/'PROTOCOL.json').read_text())
    assert original['finite_cases']==p['finite_cases'] and original['scaling']==p['scaling'] and original['continuum']==p['continuum']
    rows=json.loads((R/'results/finite_suite.json').read_text())+json.loads((R/'results/scaling.json').read_text())
    continuum=json.loads((R/'results/continuum.json').read_text());rows+=continuum['fibers']
    expected=[]
    for c in p['finite_cases']:
        expected.extend((c['name'],mode,c['seed'],c['n'],c['T'],c['m'],Q(c['beta']),Q(c['epsilon'])) for mode in ('unscaled','scaled'))
    c=p['scaling']
    for ep in c['epsilons']:
        expected.extend(('scale_'+ep.replace('.','p'),mode,c['seed'],c['n'],c['T'],c['m'],Q(c['beta']),Q(ep)) for mode in ('unscaled','scaled'))
    c=p['continuum'];M=c['finest_cells']
    expected.extend(('fiber_%02d'%j,'scaled',c['seed'],c['n'],c['T'],c['m'],Q(c['beta']),Q(c['epsilon'])/(1+Q(j,M))) for j in range(M+1))
    assert len(rows)==len(expected)==41
    checks=[]
    for row,exp in zip(rows,expected):
        name,mode,seed,n,T,m,b,eps=exp
        assert (row['case'],row['mode'])==(name,mode)
        assert 'failure' not in row
        file=R/'proofs'/(name+'_'+mode+'.json.gz'); payload=json.loads(gzip.decompress(file.read_bytes()));d=payload['model']
        assert (d['seed'],d['n'],d['T'],d['m'],Q(d['beta']),Q(d['epsilon']))==(seed,n,T,m,b,eps)
        primitive_check(d)
        check=verify(file);assert check['lower']==row['lower'] and check['upper']==row['upper'] and check['sha256']==row['proof_sha256']
        checks.append(dict(case=name,mode=mode,**check))
    # Rebuild the continuous-state endpoints from exact positive cell weights.
    sums=[]
    for result in continuum['integrals']:
        cells=result['cells'];L=Q(0);U=Q(0)
        for j in range(cells):
            a=Q(j,cells);b=Q(j+1,cells);weight=b-a+(b*b-a*a)/4
            il=j*(M//cells);ir=(j+1)*(M//cells)
            L+=weight*Q(continuum['fibers'][il]['lower']);U+=weight*Q(continuum['fibers'][ir]['upper'])
        assert str(L)==result['lower'] and str(U)==result['upper'] and L<=U
        sums.append(dict(cells=cells,lower=str(L),upper=str(U),passed=True))
    out=dict(passed=True,source_hash_equality=files,original_cases_unchanged=True,objects=len(checks),all_restart_checks=sum(x['all_restart_checks'] for x in checks),checks=checks,continuum=sums,seconds=time.perf_counter()-begin,trust_boundary='Analytic regret/fiber theorems are not machine-checked. Arithmetic and registered primitive contracts are independently reconstructed. No empirical calibration is asserted.')
    (R/'results/publication_rechecks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('checks','continuum')},indent=2))
if __name__=='__main__': main()
