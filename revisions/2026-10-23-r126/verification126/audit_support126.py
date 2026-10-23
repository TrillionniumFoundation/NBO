"""Post-execution orchestration of the frozen independent rational checker.

No model call, scientific-selection change or numerical optimization occurs.
All predeclared pools and contrasts, including failed entries, are retained.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,datetime as dt,gzip,hashlib,json,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code126'))
from independent_support126 import verify_certificate,cell_regret,encode

def rows(p):
    with gzip.open(p,'rt') as f:return [json.loads(s) for s in f if s.strip()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primary',required=True);ap.add_argument('--support',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    primary=Path(a.primary);support=Path(a.support);out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();receipt={'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'started','economic_queries':0,'solver_imports':False,'source_checker_sha256':sha(ROOT/'code126/independent_support126.py'),'orchestration_sha256':sha(__file__)}
    try:
        original=rows(primary/'records126.jsonl.gz');selected=[r for r in original if r['mode']=='fused_control' and (r['row']==0 or r['arm']=='online')]
        pools=rows(support/'pools126.jsonl.gz');contrasts=rows(support/'contrasts126.jsonl.gz');totals=json.loads((support/'SUMMARY126.json').read_text())
        assert len(original)==1584 and len(selected)==len(pools)==74 and len(contrasts)==totals['contrasts']
        checks=0;bycontrast=[];cuts=0;weights=0;improved=[];improvedregret=[];seen=[]
        for i,c in enumerate(contrasts):
            result=verify_certificate(c);bycontrast.append(result);cuts+=result['cut_count'];weights+=result['nonzero_dual_count'];checks+=1
            pi=c['pool_index'];r=selected[pi];case=c['problem']['case']
            assert c['identity']=={k:r[k] for k in ('index','budget','arm','training_loss','row','state126','alpha')}
            assert F(case['A'])==F(1,8)+sum(F(x) for x in r['state126'])/16 and F(case['incumbent'])==F(r['action'])
            assert F(case['delta'])==F(15,2**24) and F(case['mu'])==2 and F(case['gradient_cap'])==7
            assert len(case['payloads'])==len(r['initial_support_certificates'])
            for pp,raw in zip(case['payloads'],r['initial_support_certificates']):
                for x,y in [('a','original_action'),('W','support_anchor_lower'),('U','original_q_upper'),('p_lower','support_slope_lower'),('p_upper','support_slope_upper')]:assert F(pp[x])==F(raw[y])
            checks+=1
            if result['certified_upper']<result['cheap_upper']:
                improved.append({'contrast_id':i,'pool':pi,'origin':c['problem']['origin'],'target':c['problem']['target'],'gain_in_upper_bound':result['cheap_upper']-result['certified_upper']})
        strict=0
        for i,p in enumerate(pools):
            assert p['pool_index']==i and p['failure'] is None and p['status']=='bounded-certificate-calculation-completed'
            for candidate in p['candidates']:
                ids=candidate['contrast_record_ids'];seen.extend(ids);xs=list(map(F,candidate['grid']));act=F(candidate['action']);case=contrasts[ids[0]]['problem']['case'];L=F(case['L'])
                assert len(ids)==len(xs)
                for cid,x in zip(ids,xs):
                    cc=contrasts[cid];assert cc['pool_index']==i and F(cc['problem']['origin'])==x and F(cc['problem']['target'])==act
                bound,cells=cell_regret(xs,[bycontrast[cid]['certified_upper'] for cid in ids],L)
                assert bound==F(candidate['grid_regret'])
                retained=min(F(candidate['cheap_original_regret']),bound+F(case['delta']))
                assert retained==F(candidate['retained_original_regret'])
                incumbent=F(case['incumbent']);contrast=bycontrast[ids[xs.index(incumbent)]]['certified_upper']
                gain=F(0) if act==incumbent else -contrast-F(case['delta'])
                assert gain==F(candidate['certified_gain_lower'])
                accept=(act!=incumbent and gain>0 and retained<=F(1,256) and F(candidate['width'])<=F(1,8192))
                assert accept==candidate['strict_qualified_gain'] and not candidate['changed_primary_policy']
                assert candidate['target_qualified']==(retained<=F(1,65536) and F(candidate['width'])<=F(1,8192))
                strict+=accept;checks+=1
                if retained<F(candidate['cheap_original_regret']):improvedregret.append({'pool':i,'identity':p['identity'],'action':act,'old_regret':F(candidate['cheap_original_regret']),'new_regret':retained,'reduction':F(candidate['cheap_original_regret'])-retained})
        assert sorted(seen)==list(range(len(contrasts)))
        assert len(improved)==totals['strictly_sharper_contrasts'] and len(improvedregret)==totals['strictly_sharper_regrets'] and strict==totals['strict_qualified_gains']
        receipt.update(status='passed',exact_record_checks=checks,contrasts=len(contrasts),pools=len(pools),candidate_actions=sum(len(p['candidates']) for p in pools),reconstructed_cuts=cuts,nonzero_weights=weights,strictly_sharper_contrasts=len(improved),strictly_sharper_regrets=len(improvedregret),strict_qualified_gains=strict,full_primary_selection_verified=True,all_support_payload_levels_and_slopes_bound_to_primary=True,finite_solver_optimality_certified=False,raw_duals_and_final_intersections_distinguished=True,source_hashes={str(p):sha(p) for p in [primary/'records126.jsonl.gz',support/'contrasts126.jsonl.gz',support/'pools126.jsonl.gz',support/'SUMMARY126.json']})
        (out/'IMPROVEMENTS126.json').write_text(json.dumps(encode({'contrasts':improved,'regrets':improvedregret}),indent=2)+'\n')
    except BaseException:
        receipt.update(status='failed',traceback=traceback.format_exc());raise
    finally:
        receipt.update(seconds=time.perf_counter()-start,ended_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        (out/'SUPPORT_VERIFICATION126.json').write_text(json.dumps(encode(receipt),indent=2)+'\n')
    print(json.dumps(encode(receipt)))
if __name__=='__main__':main()
