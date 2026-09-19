"""Extract a sufficient rational certificate from an executed search.

Zero-weight constraints are discarded by weak duality, not by heuristic
rounding. Every bound-generating query is retained. Search files remain local
research outputs; the deposited compact witness records their digests.
"""
from continuous_fees import *
import copy

def main():
    raw=HERE/'output/continuous_fees.json';source=json.loads(raw.read_text());bank=source['bank'];byid={r['id']:r for r in bank};needed=set();results=[]
    for result in source['results']:
        result=copy.deepcopy(result);adj=result['adjustment'];eta=frac(result['eta']);needed.add(result['incumbent']['id'])
        for cell in result['leaves']:
            aa,bb=map(Q,cell['cell']);m=cell['term'];sign=cell['sign'];lp=cell['lp'];dual=cell['dual'];keep=[i for i,x in enumerate(dual['multipliers']) if x!=0.]
            lp['A']=[lp['A'][i] for i in keep];lp['b']=[lp['b'][i] for i in keep];cell['constraints']=[cell['constraints'][i] for i in keep];dual['multipliers']=[dual['multipliers'][i] for i in keep]
            for pr in cell['constraints']:
                if pr['kind'] in ('query','response'):needed.add(pr['data'])
            center=[r for r in bank if r['adjustment']==adj and r['term']==m and r['sign']==sign and r['d']==D0]
            lows=[(max(Q(0),frac(r['H'][0])-(eta/(frac(r['F'])-bb) if eta else Q(0))),r['id']) for r in center if frac(r['F'])>bb or (not eta and frac(r['F'])==bb)]
            highs=[(min(Q(1),frac(r['H'][1])+(eta/(aa-frac(r['F'])) if eta else Q(0))),r['id']) for r in center if frac(r['F'])<aa or (not eta and frac(r['F'])==aa)]
            sources={}
            if lows:val,ii=max(lows);sources['H_lower']=ii;needed.add(ii)
            if highs:val,ii=min(highs);sources['H_upper']=ii;needed.add(ii)
            # Proves that capping the minimally sufficient grant at 20 loses no
            # optimistic purchaser value. It does not restrict actual transfers.
            ff=next(r for r in center if r['F']==1.);sources['grant_cap']=ff['id'];needed.add(ff['id'])
            cell['box_sources']=sources
        results.append(result)
    if any(r['eta']!=0 for r in results):raise ValueError('compact incumbent routine currently supports the exact-response run only')
    used=[r for r in bank if r['id'] in needed];new=[r for r in source['new_queries'] if r['id'] in needed];tags={r['witness'] for r in new}
    with np.load(HERE/'output/continuous_queries.npz') as ar:
        arrays={k:ar[k] for k in ar.files if k.split('.')[0] in tags}
    np.savez_compressed(HERE/'output/continuum_witness.npz',**arrays)
    ans={k:source[k] for k in ('canonical_manifest_sha256','inherited_refinement_sha256','inherited_procurement_sha256','arithmetic','value_allowance','elapsed_seconds','peak_rss_kib')}
    ans.update(schema='nbo-r14-compact-continuum-v1',bank=used,new_queries=new,results=results,archive_sha256=digest(HERE/'output/continuum_witness.npz'),research_search_sha256=digest(raw),research_archive_sha256=digest(HERE/'output/continuous_queries.npz'),search_query_problems=len({(r['adjustment'],r['term'],r['F'],r['d']) for r in source['new_queries']}),scope='All exact best responses, both mandates, eight terms, every fee in [0,1], capacity optimized by the enforcement-frontier theorem. Original zero-multiplier LP inequalities removed exactly; all bound-generating queries retained.')
    dump(HERE/'output/continuum_certificate.json',ans)
    print('RETAINED',len(used),'response queries,',len({(r['adjustment'],r['term'],r['F'],r['d']) for r in used}),'DP problems;',len(tags),'new witness arrays')
if __name__=='__main__':main()
