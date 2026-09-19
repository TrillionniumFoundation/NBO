"""Reproduce the sufficient R14 query/cell witness without rerunning discovery.

The blueprint contains parameters, rational fee cells, and nonnegative dual
proposals, not values or bound conclusions. Values, supports, LP coefficients
and residual-charged bounds are recomputed. Reusing a dual proposal avoids a
new optimizer call on numerically ill-conditioned cells; its validity is never
assumed. verify.py checks the result through independent recursions.
"""
from continuous_fees import *
import compact_certificate

def main():
    blueprint=json.loads((HERE/'blueprint.json').read_text());work=Research()
    if digest(ROOT/'replication/r13/canonical/manifest.json')!=blueprint['canonical_manifest_sha256']:
        raise ValueError('blueprint belongs to another numerical target')
    for record in blueprint['queries']:
        tag,adj,m,F,d=record;work.seq=int(tag[1:]);work.query(adj,m,F,d)
    results=[]
    for design in blueprint['regimes']:
        adj=design['adjustment'];leaves=[]
        for recipe,proposal in zip(design['cells'],design['dual_proposals']):
            m,sg,a,b=recipe
            a,b=Q(a),Q(b);lp,c,const,pr=cell_lp(work.bank,adj,m,sg,a,b,eta=0.)
            indices={(item['kind'],item['data']):i for i,item in enumerate(pr)}
            mu=[0.]*len(pr)
            for kind,identifier,weight in proposal:
                if not np.isfinite(weight) or weight<0:raise ValueError('invalid proposed multiplier')
                key=(kind,identifier)
                if key not in indices:raise ValueError('dual proposal names an unavailable semantic row')
                mu[indices[key]]+=weight
            bound,residual=lp.dual_bound(c,mu)
            cert=dict(certified_upper=upward(bound),exact_upper=encode(bound),multipliers=mu,residual=[encode(x) for x in residual],status='Recomputed exact weak-duality bound from a nonnegative proposal; no primal optimizer flag is used.')
            leaves.append(dict(upper=upward(Q(cert['exact_upper'])+const),dual=cert,constant=encode(const),lp=lp.json(),constraints=pr,cell=[encode(a),encode(b)],term=m,sign=sg))
        inc=work.incumbent(adj,0.);upper=max(v['upper'] for v in leaves)
        if (inc['F'],inc['term'],inc['sign'])!=tuple(design['executable_contract']):
            raise ValueError('reproduced executable contract differs from discovery')
        regret=upward(frac(upper)-frac(inc['lower']))
        if regret>3e-6:raise ValueError('replayed certificate fails required global regret')
        rival=max(v['upper'] for v in leaves if v['term']!=inc['term'])
        if not rival<inc['lower']:raise ValueError('compulsory term not identified')
        results.append(dict(adjustment=adj,fee_domain=[0.,1.],eta=0.,incumbent=inc,global_upper=upper,regret_upper=regret,tolerance=3e-6,tolerance_met=True,splits=len(leaves)-320,leaves=leaves,not_excluded=[{k:v[k] for k in ('term','sign','cell','upper')} for v in leaves if v['upper']>=inc['lower']],trace=[],execution='sufficient-query replay; adaptive discovery recorded separately'))
        print('REPLAY REGIME',adj,'REGRET',regret,'TERM',inc['term'],flush=True)
    work.save(results);compact_certificate.main()

if __name__=='__main__':main()
