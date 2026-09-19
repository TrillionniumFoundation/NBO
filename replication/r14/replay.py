"""Reproduce the sufficient R14 query/cell witness without rerunning discovery.

The blueprint contains parameter requests and rational cell boundaries, not
values or proof conclusions. Producer solves, supports and LP proposals are all
recomputed; verify.py subsequently checks them through independent recursions.
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
        for m,sg,a,b in design['cells']:
            a,b=Q(a),Q(b);lp,c,const,pr=cell_lp(work.bank,adj,m,sg,a,b,eta=0.)
            cert=maximize(lp,c)
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
