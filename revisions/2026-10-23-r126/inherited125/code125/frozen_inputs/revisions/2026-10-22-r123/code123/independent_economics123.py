"""Independent original continuous-risk economics for every distinct action.

The retained exact rational primitive imports no production solver/model/code.
New R123 evaluations have their own states, witnesses, clocks and receipts.
"""
import argparse,json,sys,time
from fractions import Fraction as F
from common123 import *

def key(x,a,alpha):return (tuple(float(v).hex() for v in x),float(a).hex(),float(alpha).hex())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primary',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    out,tick,initial=start(args.output,'independent-original-economics')
    trace=None
    try:
        freeze=verify_source();bounds=boundaries()
        sys.path.insert(0,str(ROOT/'vendor/2026-10-20-r121/code121'))
        import exact121 as ex
        ir,primitive=ex.load_primitives()
        primary_path=Path(args.primary)/'records123.jsonl.gz'
        primary_sha256=digest(primary_path)
        state_file=json.loads((ROOT/'results123/states/states123.json').read_text())
        if state_file['source_commit']!=bounds['source_commit']:raise ValueError('Frozen states have wrong source')
        state_census={r['row']:r for r in state_file['states']}
        if set(state_census)!=set(range(N)) or len(state_file['states'])!=N:raise ValueError('Invalid frozen state census')
        expected={k+(j,) for k in groups() for j in range(N)};seen=set()
        wanted={};claims=[];row_count=0
        for row in rows(primary_path):
            row_count+=1
            if row['source_commit']!=bounds['source_commit'] or row['state_commit']!=bounds['state_commit']:raise ValueError('Mixed primary identity')
            identity=tuple(row[k] for k in FIELDS)+(row['row'],)
            if identity not in expected or identity in seen:raise ValueError('Duplicated or undeclared primary identity')
            seen.add(identity)
            state=state_census[row['row']]
            if row['population_observation'] is not True or row['repeat'] is not None:raise ValueError('Non-primary population observation')
            if row['state']!=state['state'] or row['state_hex']!=state['state_hex']:raise ValueError('Primary state is not frozen state')
            if row['alpha']!=(.5,.75)[row['index']]:raise ValueError('Primary risk identity mismatch')
            x=row['state'];alpha=row['alpha']
            actions=[row['action'],row['baseline_action'],row.get('raw_proposal_kept')]
            actions.extend(r['original_action'] for r in row.get('initial_support_certificates',[]))
            for a in actions:
                if a is None:continue
                k=key(x,a,alpha);wanted[k]=dict(x=list(map(F,x)),a=F(a),alpha=F(alpha))
            if row['accepted_improvement']:
                keep=(*FIELDS,'row','state','alpha','baseline_action','action','complete_policy_lower','complete_policy_upper','certified_policy_gain_lower')
                claims.append({k:row[k] for k in keep})
        if row_count!=7424 or seen!=expected:raise ValueError('Entire R123 primary required')
        if digest(primary_path)!=primary_sha256:raise ValueError('Primary input changed during read')
        trace=ex.ExactTrace(out/'original_terminal_witnesses123.jsonl.gz')
        cache={};best={}
        def evaluate(k,bins):
            if (k,bins) in cache:return
            ex.BINS=bins
            result=ex.evaluate_action(ir,k,wanted[k],trace)
            result['state_hex']=list(k[0]);result['action_hex']=k[1]
            result.update(source_commit=bounds['source_commit'],state_commit=bounds['state_commit'],primitive_sha256=ex.PRIMITIVE_SHA256,
                          original_Q_and_same_implemented_future=True)
            append(out/'values123.jsonl',result);cache[k,bins]=result
            if k not in best:best[k]=dict(result)
            else:
                for f in ('q_lower','j_lower','optimum_lower'):best[k][f]=max(best[k][f],result[f])
                for f in ('q_upper','j_upper'):best[k][f]=min(best[k][f],result[f])
                if best[k]['q_lower']>best[k]['q_upper']:raise ArithmeticError('Independent levels contradict')
        for j,k in enumerate(sorted(wanted)):
            evaluate(k,32)
            if (j+1)%10==0:print(json.dumps(dict(phase='all-actions',completed=j+1,total=len(wanted),seconds=time.perf_counter()-tick)),flush=True)
        for j,row in enumerate(claims):
            a=key(row['state'],row['baseline_action'],row['alpha']);b=key(row['state'],row['action'],row['alpha'])
            stages=[]
            for level in (32,128,256):
                evaluate(a,level);evaluate(b,level)
                gain=best[a]['j_lower']-best[b]['j_upper']
                upper=best[a]['j_upper']-best[b]['j_lower']
                if max(best[b]['j_lower'],F(row['complete_policy_lower']))>min(best[b]['j_upper'],F(row['complete_policy_upper'])):
                    raise ArithmeticError('Independent economic enclosure disjoint from produced enclosure')
                contained=F(row['complete_policy_lower'])<=best[b]['j_lower']<=best[b]['j_upper']<=F(row['complete_policy_upper'])
                confirmed=gain>=F(row['certified_policy_gain_lower'])
                stages.append(dict(bins=level,gain_lower=gain,gain_upper=upper,production_gain_confirmed=confirmed,
                                   candidate_interval_contained=contained))
                if confirmed and contained:break
            append(out/'claims123.jsonl',dict(identity={k:row[k] for k in (*FIELDS,'row')},baseline_action_hex=a[1],action_hex=b[1],stages=stages,
                   independently_confirmed=confirmed and contained,unresolved_not_failed=not(confirmed and contained)))
            if (j+1)%10==0:print(json.dumps(dict(phase='accepted-claims',completed=j+1,total=len(claims),seconds=time.perf_counter()-tick)),flush=True)
        trace.close();trace=None
        if digest(primary_path)!=primary_sha256:raise ValueError('Primary input changed during independent evaluation')
        finish(out,tick,initial,primary_records_sha256=primary_sha256,complete_primary_census=len(seen),source=freeze,boundaries=bounds,primitive=primitive,distinct_actions=len(wanted),
               evaluations=len(cache),accepted_claims=len(claims),counts=ex.COUNTS,
               original_witness_sha256=digest(out/'original_terminal_witnesses123.jsonl.gz'),
               production_arithmetic_or_models_imported=False,new_population_states=False)
    except BaseException:
        if trace is not None:trace.close()
        failed(out,tick);raise

if __name__=='__main__':main()
