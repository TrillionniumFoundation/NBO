"""Reconstruct the full catalogue and generate manuscript tables; never retime."""
import hashlib,itertools,json,statistics
from fractions import Fraction as F
from pathlib import Path
import witness as w
R=w.R
J=lambda p:json.loads(p.read_text())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def write(name,obj):
    (R/'audit'/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def main():
    records={};hashes={};checkpoint_count=0;by_definition={}
    expected=set(itertools.product(w.METHODS,(2,4),(1,4),range(3)))
    for path in sorted((R/'results/services').glob('*/record.json')):
        record=J(path);key=(record['method'],record['horizon'],record['price'],record['repeat'])
        assert key in expected and key not in records,key
        assert H(path)==J(path.with_name('clock.json'))['record_sha256']
        assert [a['N'] for a in record['attempts']]==list(w.old.LADDER)
        for name,digest in record['source_sha256'].items():assert H(R.parent/name)==digest,name
        first={str(e):None for e in w.TARGETS};cum=0;prev=0
        for att in record['attempts']:
            cp=path.with_name(f"checkpoint-N{att['N']}.json");payload=J(cp)
            assert H(cp)==att['checkpoint_sha256']
            assert payload==w.enhance(payload['definition'],record['method']),str(cp)
            base=payload['definition'];T=base['T'];N=base['N']
            assert (N,T,base['price'])==(att['N'],record['horizon'],record['price'])
            for model in base['models']:
                d=model['definition'];grid=list(map(F,d['grid']));labels=list(map(F,d['labels']))
                rebuilt=w.old.PWL.from_labels(grid,labels,F(d.get('L',0)),d['method'])
                assert rebuilt.k==list(map(F,model['knots'])) and rebuilt.v==list(map(F,model['values']))
                assert rebuilt.L==F(model['L'])
            # Independent summation of the one-sided policy account.
            total=w.old.BETA**T*F(base['terminal_width'])
            for row in payload['joint_rows']:
                total+=w.old.BETA**row['date']*(F(row['optimal_residual_upper'])+F(row['selected_policy_upper']))
            assert total==F(payload['joint_bound_exact'])
            assert F(payload['policy_bound_exact'])==min(total,F(base['policy_bound_exact']))
            assert F(att['bound_upper'])>=F(att['bound_exact'])
            assert att['counts']['q_evaluations']==T*(N+1)**2
            cum+=T*(N+1)**2;assert cum==att['prefix_q_evaluations']
            assert att['prefix_seconds']>=prev;prev=att['prefix_seconds']
            assert att['checkpoint_bytes']==cp.stat().st_size
            for e in w.TARGETS:
                if first[str(e)] is None and F(att['bound_exact'])<=e:
                    first[str(e)]={k:att[k] for k in ('N','bound_exact','bound_upper','prefix_seconds','prefix_q_evaluations')}
            checkpoint_count+=1;hashes[str(cp.relative_to(R))]=H(cp)
            by_definition[key+(N,)]=hashlib.sha256(w.old.canonical(base)).hexdigest()
        assert first==record['first_crossings']
        records[key]=record
    assert set(records)==expected and checkpoint_count==216
    for m,T,p in itertools.product(w.METHODS,(2,4),(1,4)):
        for j,N in enumerate(w.old.LADDER):
            assert len({records[m,T,p,r]['attempts'][j]['checkpoint_sha256'] for r in range(3)})==1
    for T,p,r,N in itertools.product((2,4),(1,4),range(3),w.old.LADDER):
        assert by_definition['cone-witness',T,p,r,N]==by_definition['cone-nearest',T,p,r,N]
    attained={m:{str(e):sum(records[m,T,p,r]['first_crossings'][str(e)] is not None for T,p,r in itertools.product((2,4),(1,4),range(3))) for e in w.TARGETS} for m in w.METHODS}
    comparisons={}
    for comparator in w.METHODS[1:]:
        wins=0;exceptions=[];timepairs=[]
        for T,p in itertools.product((2,4),(1,4)):
            a=records['cone-witness',T,p,0];b=records[comparator,T,p,0]
            for av,bv in zip(a['attempts'],b['attempts']):
                if F(av['bound_exact'])<F(bv['bound_exact']):wins+=1
                else:exceptions.append({'T':T,'price':p,'N':av['N'],'witness':av['bound_upper'],'comparator':bv['bound_upper']})
            for r,e in itertools.product(range(3),w.TARGETS):
                av=records['cone-witness',T,p,r]['first_crossings'][str(e)];bv=records[comparator,T,p,r]['first_crossings'][str(e)]
                if av and bv:timepairs.append((av['prefix_seconds'],bv['prefix_seconds']))
        comparisons[comparator]={'strictly_tighter_witness':wins,'unique_comparisons':24,'exceptions':exceptions,
            'witness_faster':sum(a<b for a,b in timepairs),'common_target_clocks':len(timepairs),
            'pooled_prefix_clock_ratio':sum(a for a,b in timepairs)/sum(b for a,b in timepairs),
            'ratio_scope':'descriptive pooled target-prefix clocks; prefixes overlap and are not independent or a total-study runtime'}
    final=[]
    for T,p in itertools.product((2,4),(1,4)):
        item={'T':T,'price':p}
        for m in w.METHODS:item[m]=records[m,T,p,0]['attempts'][-1]['bound_upper']
        final.append(item)
    summary={'services':36,'rungs':216,'distinct_method_economy_resolution_rows':72,'attainment':attained,
             'comparisons':comparisons,'final_bounds':final,'identical_repetition_checkpoints':True,
             'identical_cone_critics_and_node_actions':True,'expected_policy_cost_ranking':'not inferred from regret bounds'}
    write('RESULT_AUDIT.json',{'verified_checkpoints':checkpoint_count,'all_sources_and_record_hashes_verified':True,
          'all_first_crossings_reconstructed':True,'all_rational_critics_reconstructed':True,'summary':summary})
    write('PUBLICATION_SUMMARY.json',summary);write('CHECKPOINT_SHA256.json',hashes)
    (R/'tables').mkdir(exist_ok=True)
    rows=[r'\begin{table}[htbp]\centering',r'\caption{Final all-state policy-loss bounds at $N=512$}\label{tab:witness46}',
          r'\begin{tabular}{rrrrr}\toprule',r'$T$ & $p$ & Witness neural & Nearest neural & Spline \\ \midrule']
    for a in final:rows.append(f"{a['T']} & {a['price']} & {a['cone-witness']:.6f} & {a['cone-nearest']:.6f} & {a['spline-nearest']:.6f} \\")
    # A row terminator is two literal backslashes.
    rows=[s+'\\' if s.endswith(' \\') and not s.endswith(' \\\\') else s for s in rows]
    rows += [r'\bottomrule\end{tabular}',r'\par\smallskip\footnotesize Bounds are rounded upward in the records; displayed decimals are summaries, not the target test. All three repetitions have identical checkpoints. Both nearest-node comparators use the strengthened one-sided certificate.',r'\end{table}']
    (R/'tables/witness-summary.tex').write_text('\n'.join(rows)+'\n')
    c=comparisons['spline-nearest'];ex=c['exceptions'][0]
    paragraph=(r'All three methods certify $12/12$ services at $1/4$ and at $1/8$, and $6/12$ at $1/16$. The latter failures are all horizon-four services and are retained. The witness bound is strictly tighter than the nearest-node neural ablation in all 24 distinct economy/resolution comparisons, and tighter than the strengthened spline in 23 of 24. '
      +f"The exception is $T={ex['T']}$, $p={ex['price']}$, $N={ex['N']}$, where the witness and spline bounds are approximately {ex['witness']:.5f} and {ex['comparator']:.5f}. "
      +r'The declared dyadic targets have the same first-crossing resolution for all three methods in every economic cell. Thus the certificate improvement does not yield an earlier first crossing on this particular ladder. The spline is faster in all 30 common successful target/repetition clock comparisons; the witness construction is faster than the nearest-node neural ablation in all 30. These local clocks and tighter regret bounds establish neither policy-cost superiority nor a general neural speed advantage.'+'\n')
    # Check the equal-crossing statement independently before emitting it.
    for T,p,r,e in itertools.product((2,4),(1,4),range(3),w.TARGETS):
        crossing=[records[m,T,p,r]['first_crossings'][str(e)] for m in w.METHODS]
        assert len({a['N'] if a else None for a in crossing})==1
    assert comparisons['cone-nearest']['strictly_tighter_witness']==24 and c['strictly_tighter_witness']==23
    assert c['witness_faster']==0 and c['common_target_clocks']==30
    assert comparisons['cone-nearest']['witness_faster']==30
    (R/'tables/witness-outcomes.tex').write_text(paragraph)
    rows=[r'\begin{longtable}{rrrrrr}',r'\caption{Complete matched witness frontiers}\label{tab:witnessfront46}\\',
          r'\toprule $T$ & $p$ & $N$ & Witness & Nearest neural & Spline \\ \midrule\endfirsthead',
          r'\toprule $T$ & $p$ & $N$ & Witness & Nearest neural & Spline \\ \midrule\endhead']
    for T,p in itertools.product((2,4),(1,4)):
        for j,N in enumerate(w.old.LADDER):
            vals=[records[m,T,p,0]['attempts'][j]['bound_upper'] for m in w.METHODS]
            rows.append(f'{T} & {p} & {N} & '+ ' & '.join(f'{v:.6f}' for v in vals)+r' \\')
    rows += [r'\bottomrule\end{longtable}'];(R/'tables/witness-frontier.tex').write_text('\n'.join(rows)+'\n')
    rows=[r'\begin{longtable}{llrrrr}',r'\caption{Full-frontier isolated construction clocks in seconds}\label{tab:witnesstime46}\\',
          r'\toprule Method & $(T,p)$ & Median & Minimum & Maximum & Peak MiB \\ \midrule\endfirsthead',
          r'\toprule Method & $(T,p)$ & Median & Minimum & Maximum & Peak MiB \\ \midrule\endhead']
    for m in w.METHODS:
        for T,p in itertools.product((2,4),(1,4)):
            rr=[records[m,T,p,r] for r in range(3)];tt=[a['attempts'][-1]['prefix_seconds'] for a in rr]
            rows.append(f'{m} & $({T},{p})$ & {statistics.median(tt):.4f} & {min(tt):.4f} & {max(tt):.4f} & {max(a["peak_process_rss_kib"] for a in rr)/1024:.1f}'+r' \\')
    rows += [r'\bottomrule\end{longtable}',r'Clocks include all six rungs through checkpoint fsync. Peak resident memory includes the interpreter and warm-up. These are three local repetitions, not independent economic draws.']
    (R/'tables/witness-timing.tex').write_text('\n'.join(rows)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
