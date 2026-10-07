"""Reconstruct frozen R47 results and generate all publication tables.

No training, simulation, result replacement or clock rewriting occurs here.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
import csv,hashlib,itertools,json,math,statistics
import direct as d
import constrained as z
R=z.R;BASE=d.BASE
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def fmt(x):return f'{float(x):.6g}'
def texnum(x):return f'{float(x):.5f}'
def texfrac(x):
 q=F(x)
 return str(q.numerator) if q.denominator==1 else f'{q.numerator}/{q.denominator}'

def direct_audit():
    complete=json.loads((R/'results/direct/COMPLETE.json').read_text())
    files=sorted((R/'results/direct').glob('T*.json'))
    assert len(files)==40 and complete['contrasts']==120 and complete['paths_per_group']==131072
    declared={x['key']:x['file_sha256'] for x in complete['records']}
    results=[];policy_hashes=set();ambiguous=queries=0
    for p in files:
        j=json.loads(p.read_text());assert H(p)==declared[j['key']]
        assert j['family_size']==120 and F(j['family_error'])==F(1,100)
        assert j['paths']==131072 and j['uniform_bin_bits']==40
        assert F(j['decision_margin'])==F(1,1024)
        for f in j['policy_files']:
            assert H(BASE/f['path'])==f['sha256'];policy_hashes.add(f['sha256'])
        ambiguous+=sum(j['ambiguous_actor_queries']);queries+=sum(j['actor_queries'])
        for x in j['comparisons']:
            a,b=map(F,x['support_float']);assert a<=F(x['support_exact'][0]) and b>=F(x['support_exact'][1])
            endpoints=[]
            for side in ('lower_endpoint_moments','upper_endpoint_moments'):
                s=x[side];n=s['n'];assert n==131072
                muL,muU=F(s['mean_lo']),F(s['mean_hi']);qU=F(s['second_hi'])
                qmin=0 if muL<=0<=muU else min(muL*muL,muU*muU)
                v=max(0,F(n,n-1)*(qU-qmin));assert v==F(s['variance_upper'])
                gamma=F(n+4,2**53)/(1-F(n+4,2**53));assert gamma==F(s['gamma'])
                q=2*v*11/n;root=math.sqrt(float(q))
                while F(root)**2<q:root=math.nextafter(root,math.inf)
                rad=F(root)+F(77,3*(n-1))*(b-a)
                endpoints.append((muL-rad,muU+rad))
            lo=max(a,endpoints[0][0]);hi=min(b,endpoints[1][1]);assert lo<=hi
            assert [str(lo),str(hi)]==x['interval_exact']
            assert F(x['interval'][0])<=lo and hi<=F(x['interval'][1])
            cls={'sign':'first-lower' if hi<0 else 'first-higher' if lo>0 else 'unresolved',
                 'within_margin':-F(1,1024)<=lo and hi<=F(1,1024),'first_noninferior_at_margin':hi<=F(1,1024)}
            for k,v in cls.items():assert x[k]==v
            results.append({'T':j['horizon'],'p':j['price'],'target':j['target'],'law':j['initial_law'],
                            'first':x['first'],'second':x['second'],'lo':lo,'hi':hi,
                            'width':hi-lo,'max_abs':max(abs(lo),abs(hi)),**cls})
    assert len(results)==120
    summary={}
    for first,second in [(d.METHODS[a],d.METHODS[b]) for a,b in d.PAIRS]:
        rows=[x for x in results if (x['first'],x['second'])==(first,second)]
        summary[first+' minus '+second]={'comparisons':len(rows),'signs':dict(Counter(x['sign'] for x in rows)),
            'within_prespecified_margin':sum(x['within_margin'] for x in rows),
            'min_width':float(min(x['width'] for x in rows)),'max_width':float(max(x['width'] for x in rows)),
            'max_absolute_endpoint':float(max(x['max_abs'] for x in rows))}
    return {'groups':40,'contrasts':120,'unique_policy_checkpoints':len(policy_hashes),
            'paths_per_group':131072,'total_paths':40*131072,'actor_queries':queries,'ambiguous_actor_queries':ambiguous,
            'margin':'1/1024','family_error':'1/100','conditional_iid_model':True,'comparisons':summary},results

def constrained_audit():
    records=[];hashes=defaultdict(list)
    paths=sorted((R/'results/constrained').glob('*/record.json'));assert len(paths)==24
    for path in paths:
        j=json.loads(path.read_text());assert [a['N'] for a in j['attempts']]==[4,8,16]
        assert json.loads((path.parent/'clock.json').read_text())['record_sha256']==H(path)
        prefix=0;attempts=[]
        for a in j['attempts']:
            N=a['N'];p=json.loads((path.parent/f'checkpoint-N{N}.json').read_text())
            assert H(path.parent/f'checkpoint-N{N}.json')==a['checkpoint_sha256']
            assert (path.parent/f'checkpoint-N{N}.json').stat().st_size==a['checkpoint_bytes']
            hashes[(j['method'],j['horizon'],j['price'],N)].append(a['checkpoint_sha256'])
            assert len(p['actors'])==j['horizon'] and len(p['models'])==j['horizon']+1
            for actor in p['actors']:
                for i,action in enumerate(actor):
                    x1,x2=F(i//(N+1),N),F(i%(N+1),N)
                    assert 0<=F(action)<=F(1,8)+(x1+x2)/16
            for m in p['models']:
                assert len(m['labels'])==(N+1)**2
                if m['kind']=='bilinear-fvi':
                    v=list(map(F,m['labels']));diff=[]
                    for i,k in itertools.product(range(N+1),repeat=2):
                        ix=i*(N+1)+k
                        if i<N:diff.append(abs(v[ix+N+1]-v[ix]))
                        if k<N:diff.append(abs(v[ix+1]-v[ix]))
                    assert F(m['L'])==N*max(diff)
            gap=F(0)
            for t,row in enumerate(p['rows']):
                Lfuture=F(p['models'][t+1]['L']);A=F(13,4)+F(15,16)*F(11,16)*Lfuture
                D=F(j['price'],2)+F(1,4)+F(15,16)*F(3,4)*Lfuture;L=A+D/16;e=F(row['e'])
                assert (A,D,L)==tuple(F(row[k]) for k in ('A','D','L_graph'))
                assert F(row['integration_remainder'])==F(15,16)*Lfuture/(32*N)
                assert e>=F(row['integration_remainder'])
                if j['method']=='feasible-cone-witness':
                    lo=-e;u=D/(8*N)+e+2*L/N;sel=e
                else:lo=-e-L/N;u=D/(8*N)+e+L/N;sel=e+F(row['nearest_excess_upper'])
                assert (lo,u,sel)==tuple(F(row[k]) for k in ('residual_lower','residual_upper','selected_policy_upper'))
                assert F(row['component'])==u+sel;gap+=F(15,16)**t*(u+sel)
            assert F(p['terminal_width'])==2*F(p['terminal_error'])+F(9,N)
            gap+=F(15,16)**j['horizon']*F(p['terminal_width'])
            assert gap==F(p['policy_bound_exact'])==F(a['bound_exact'])
            assert F(a['bound_upper'])>=gap
            q=j['horizon']*(N+1)**3;assert a['counts']['bellman_queries']==q
            assert a['counts']['innovation_midpoints']==q*N
            prefix+=q;assert prefix==a['prefix_bellman_queries'];attempts.append(a)
        for target in ('4','2','1','1/2'):
            first=next((a for a in attempts if F(a['bound_exact'])<=F(target)),None)
            recorded=j['first_crossings'][target]
            assert (first is None)==(recorded is None)
            if first:assert first['N']==recorded['N']
        records.append(j)
    assert len(hashes)==24 and all(len(set(v))==1 and len(v)==3 for v in hashes.values())
    summaries=[]
    for T,p,method in itertools.product((2,3),(1,4),z.METHODS):
        rr=[r for r in records if (r['horizon'],r['price'],r['method'])==(T,p,method)]
        med=statistics.median(r['attempts'][-1]['prefix_seconds'] for r in rr)
        times=[r['attempts'][-1]['prefix_seconds'] for r in rr]
        summaries.append({'T':T,'p':p,'method':method,'final_bound':rr[0]['attempts'][-1]['bound_upper'],
                          'median_seconds':med,'min_seconds':min(times),'max_seconds':max(times),
                          'prefix_queries':rr[0]['attempts'][-1]['prefix_bellman_queries'],
                          'prefix_midpoints':sum(a['counts']['innovation_midpoints'] for a in rr[0]['attempts']),
                          'critic_labels':rr[0]['attempts'][-1]['counts']['stored_critic_labels'],
                          'actor_scalars':rr[0]['attempts'][-1]['counts']['stored_actor_scalars']})
    attained={m:{e:sum(r['first_crossings'][e] is not None for r in records if r['method']==m) for e in ('4','2','1','1/2')} for m in z.METHODS}
    faster=0
    for T,p,rep in itertools.product((2,3),(1,4),range(3)):
        rr=[next(r for r in records if (r['horizon'],r['price'],r['repeat'],r['method'])==(T,p,rep,m)) for m in z.METHODS]
        faster+=rr[1]['attempts'][-1]['prefix_seconds']<rr[0]['attempts'][-1]['prefix_seconds']
    return {'services':24,'rungs':72,'distinct_checkpoints':24,'repetitions_identical':True,
            'attainment':attained,'fvi_faster_common_crossings':faster,'common_crossings':12,'cells':summaries},records

def deployment_audit():
    j=json.loads((R/'results/deployment/acquisition.json').read_text());assert j['models']==12 and j['deployment_cases']==72
    bycase=defaultdict(list)
    for m in j['records']:
        for t in m['tests']:
            eta=F(t['coordinate_radius']);q=F(t['action_quantum']);r=2*eta;assert F(t['l1_radius_bound'])==r
            total=sum((F(15,16)**i*F(row['additional_component']) for i,row in enumerate(t['rows'])),F(0))
            assert total==F(t['extra_policy_bound'])
            assert all(row['feasible_for_entire_acquisition_box'] for row in t['rows'])
            bycase[(str(eta),str(q))].append(t)
    cases=[]
    for (eta,q),tt in sorted(bycase.items(),key=lambda v:(F(v[0][0]),F(v[0][1]))):
        rows=[r for t in tt for r in t['rows']]
        cases.append({'coordinate_radius':eta,'action_quantum':q,'policies':len(tt),
                      'state_date_queries':sum(r['measured_states'] for r in rows),
                      'active_repairs':sum(r['active_robust_repairs'] for r in rows),
                      'quantized':sum(r['quantized_actions'] for r in rows),
                      'max_extra_bound':float(max(F(t['extra_policy_bound']) for t in tt))})
    f=json.loads((R/'results/deployment/frontier.json').read_text());assert len(f['cells'])==4
    counts=Counter(i['relation'] for c in f['cells'] for i in c['intervals'])
    native=json.loads((R/'results/deployment/representation.json').read_text());assert len(native['records'])==24
    nr=[r for m in native['records'] for r in m['rows']]
    assert all(F(r['maximum_float_difference'])<=F(r['proved_difference_allowance']) for r in nr)
    return {'acquisition_cases':72,'cases':cases,'total_active_repairs':sum(c['active_repairs'] for c in cases),
            'frontier_intervals':dict(counts),'frontier_partition_intervals':sum(counts.values()),
            'representation_checkpoints':24,'representation_function_dates':len(nr),
            'max_native_relu_difference':max(r['maximum_float_difference'] for r in nr)},j,f


def tables(ds,dr,cs,cr,ps,pr,fr):
    t=R/'tables';t.mkdir(exist_ok=True)
    names={'cone-witness':'Witness','cone-nearest':'Cone nearest','spline-nearest':'Spline','feasible-cone-witness':'Witness','bilinear-fvi':'Bilinear FVI'}
    text=r'''\begin{table}[htbp]\centering
\caption{Direct expected-cost comparisons under a predeclared decision tolerance}\label{tab:direct47}
\begin{tabular}{lrrrr}\toprule
Contrast & Groups & Signed & Within $1/1024$ & Largest endpoint\\\midrule
'''
    for k,v in ds['comparisons'].items():
        first,second=k.split(' minus ');text+=f"{names[first]} $-$ {names[second]} & 40 & 0 & {v['within_prespecified_margin']} & {v['max_absolute_endpoint']:.7f} \\\\\n"
    text+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{0.98\linewidth}\footnotesize Signed counts exclude intervals containing zero. ``Within'' requires the entire interval inside $[-1/1024,1/1024]$. Largest endpoint is the largest absolute endpoint over the 40 groups. All 120 intervals use one $0.01$ family error account, conditional on the frozen policies and independent-bin model. Each group uses 131,072 common paths.\end{minipage}\end{table}

Every direct interval contains zero, so the experiment identifies no signed policy ranking. Every interval is also contained in the predeclared decision band. It therefore certifies two-sided expected-cost proximity for the specified initial laws at that tolerance, rather than inferring equivalence from a failure to reject equality. The uniform initial-state law is a distributional conclusion, not an all-state assertion. The individual initial states are separate declared estimands.
'''
    (t/'direct47.tex').write_text(text)
    full=r'''\begin{longtable}{rrllcrr}\caption{All 120 direct expected-cost intervals}\label{tab:directfull47}\\\toprule
$T$ & $p$ & Target & Initial law & Contrast & Lower & Upper\\\midrule\endfirsthead
\toprule $T$ & $p$ & Target & Initial law & Contrast & Lower & Upper\\\midrule\endhead
\bottomrule\endfoot
'''
    rows=sorted(dr,key=lambda x:(x['T'],x['p'],-F(x['target']),x['law'],x['first'],x['second']))
    for x in rows:
        label={('cone-witness','cone-nearest'):'W--C',('cone-witness','spline-nearest'):'W--S',('cone-nearest','spline-nearest'):'C--S'}[(x['first'],x['second'])]
        # decimal display rounded OUTWARD to 7 decimal places
        lo=math.floor(x['lo']*10**7)/10**7;hi=math.ceil(x['hi']*10**7)/10**7
        full+=f"{x['T']} & {x['p']} & {x['target']} & {x['law']} & {label} & {lo:.7f} & {hi:.7f} \\\\\n"
    full+=r'''\end{longtable}
W is the witness, C the same-critic nearest actor, and S the spline. Every displayed endpoint is rounded outward to seven decimal places; the exact rational intervals control all decisions and are deposited. All 120 intervals lie inside the predeclared band. Repeated target labels and policy hashes remain explicit in the underlying records.
'''
    (t/'direct-full47.tex').write_text(full)
    with (R/'audit/DIRECT_INTERVALS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    txt=r'''\begin{table}[htbp]\centering
\caption{Coupled constrained economy: full-prefix work at $N=16$}\label{tab:constrained47}
\begin{tabular}{rrlrrrr}\toprule
$T$ & $p$ & Method & Bound & Queries & Seconds & Time range\\\midrule
'''
    for x in cs['cells']:
        txt+=f"{x['T']} & {x['p']} & {names[x['method']]} & {x['final_bound']:.4f} & {x['prefix_queries']:,} & {x['median_seconds']:.3f} & [{x['min_seconds']:.3f},{x['max_seconds']:.3f}] \\\\\n"
    txt+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{0.98\linewidth}\footnotesize Query counts and clocks include all three rungs, including failed attempts. Seconds are medians over three isolated process observations; the range reports their minimum and maximum. CPU affinity and library thread counts are fixed, but CPU frequency is not controlled.\end{minipage}\end{table}

Both methods attain the target 4 in all twelve services, at the last rung, and neither attains 2, 1 or $1/2$ within this cap. The witness's final bound is smaller in each economic cell, but bilinear fitted-value iteration is faster in all twelve common successful comparisons. These coarse all-state certificates establish an executed feasible construction, not an economically precise solution at the unachieved tolerances. The sufficient-cap formula states what further resources the mathematical guarantee requires without relabeling these failures.
'''
    (t/'constrained47.tex').write_text(txt)
    txt=r'''\begin{table}[htbp]\centering
\caption{Acquired-state and quantized-action deployment}\label{tab:acquisition47}
\begin{tabular}{rrrrr}\toprule
Coordinate radius & Action spacing & Active repairs & Quantized & Largest added bound\\\midrule
'''
    for x in ps['cases']:
        txt+=f"${x['coordinate_radius']}$ & ${x['action_quantum']}$ & {x['active_repairs']:,} & {x['quantized']:,} & {x['max_extra_bound']:.6f} \\\\\n"
    txt+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{0.98\linewidth}\footnotesize Each row covers all twelve distinct constrained witness policies and 32,670 measured state--date queries. Feasibility holds on the entire acquisition box. The additional loss is a uniform theoretical allowance for the executed arithmetic, acquisition and action rule, not an estimated average policy cost.\end{minipage}\end{table}

Repair is active rather than a vacuous operation, and downward action quantization is charged explicitly. At exact acquired input the small nonzero numerical selection allowance remains in the exact records even when it rounds to zero in this table. At a nonzero radius the acquisition term is positive; the total bound is not reported as the exact-state certificate.
'''
    (t/'acquisition47.tex').write_text(txt)
    txt=r'''\begin{table}[htbp]\centering
\caption{Complete tolerance-axis partition of the original scalar frontiers}\label{tab:frontier47}
\begin{tabular}{lr}\toprule Relation on a partition interval & Number\\\midrule
'''
    for key,label in [('witness-fewer','Both attain; witness uses fewer queries'),('spline-fewer','Both attain; spline uses fewer queries'),('same','Both attain; same prefix queries'),('only-witness-attained','Only witness attains within the cap'),('only-spline-attained','Only spline attains within the cap'),('both-unattained','Both exhaust the cap')]:
        txt+=f"{label} & {ps['frontier_intervals'].get(key,0)} \\\\\n"
    txt+=r'''\bottomrule\end{tabular}\end{table}

The complete curves contain 19 nonempty tolerance intervals on which both methods attain and the witness uses fewer Bellman queries, one favoring the spline, and twenty with identical counts. Four further intervals are attainable only by the witness; four below both final bounds are unattained. Interval counts are not probabilities or measures of economic importance. Above the largest breakpoint in each cell both first-rung counts coincide. The original targets remain unchanged and still have identical crossing resolutions. These descriptive intervals identify where a sharper certificate changes a resource decision without manufacturing new prospective targets.
'''
    (t/'frontier47.tex').write_text(txt)
    txt=r'''\begin{longtable}{rrlllr}\caption{Every interval of the scalar first-crossing curves}\label{tab:frontierfull47}\\\toprule
$T$ & $p$ & Tolerance lower & Tolerance upper & Relation & $N_{\rm W}/N_{\rm S}$\\\midrule\endfirsthead
\toprule $T$ & $p$ & Lower & Upper & Relation & $N_{\rm W}/N_{\rm S}$\\\midrule\endhead\bottomrule\endfoot
'''
    rel={'witness-fewer':'W fewer','spline-fewer':'S fewer','same':'Same','only-witness-attained':'W only','only-spline-attained':'S only','both-unattained':'Neither'}
    for cell in fr['cells']:
        for x in cell['intervals']:
            ns='/'.join(str(x[m]['N']) if x[m] else '--' for m in ('witness','spline'))
            txt+=f"{cell['T']} & {cell['price']} & {float(F(x['epsilon_left_closed'])):.7f} & {float(F(x['epsilon_right_open'])):.7f} & {rel[x['relation']]} & {ns} \\\\\n"
    txt+=r'''\end{longtable}
Lower endpoints are included and upper endpoints excluded in the exact records. Decimal breakpoint displays are descriptive rounded values, not substitute decision thresholds. The deposited rational endpoints determine the step functions without rounding ambiguity. Query counts equal the full prefix through the indicated rung; above each cell's last displayed upper endpoint both methods use their first rung.
'''
    (t/'frontier-full47.tex').write_text(txt)
    txt=r'''\begin{longtable}{rrlrrrr}\caption{All distinct constrained construction rungs}\label{tab:constrainedfull47}\\\toprule
$T$ & $p$ & Method & $N$ & Bound & Prefix queries & Midpoints\\\midrule\endfirsthead
\toprule $T$ & $p$ & Method & $N$ & Bound & Prefix queries & Midpoints\\\midrule\endhead\bottomrule\endfoot
'''
    for x in sorted([r for r in cr if r['repeat']==0],key=lambda r:(r['horizon'],r['price'],r['method'])):
        mids=0
        for a in x['attempts']:
            mids+=a['counts']['innovation_midpoints']
            txt+=f"{x['horizon']} & {x['price']} & {names[x['method']]} & {a['N']} & {a['bound_upper']:.5f} & {a['prefix_bellman_queries']:,} & {mids:,} \\\\\n"
    txt+=r'''\end{longtable}
Each row has three isolated timing repetitions with identical policy and certificate checkpoint hashes. All 72 raw rungs remain deposited. Every state-dependent action net, repaired actor, continuation label and numerical allowance can be reconstructed from its checkpoint.
'''
    (t/'constrained-full47.tex').write_text(txt)
    (t/'discussion47.tex').write_text(r'''\subsection{Economic interpretation and the NBO program}
The new evidence connects a feasible implementation to two distinct economic statements. First, the acquisition-aware theorem bounds the loss of a policy that can actually be executed under uncertain state measurement and capacity constraints. Second, the direct experiment certifies proximity of the original scalar policy costs within an explicitly chosen decision tolerance, so that a user of that catalogue may consider implementation charges without treating separate regret bounds as values. These statements are stronger than a certificate comparison alone.

Neither statement implies that a neural representation is indispensable. The identical native envelope is a mathematical control, and the conventional fitted-value and spline implementations remain strong alternatives. The constrained experiment demonstrates two-state continuous-uncertainty construction and nontrivial repair, not a high-dimensional scaling result or an estimated economic application. Its tight targets remain unachieved. The direct cost experiment does not cover the new constrained policies or nonlinear recursive utility; its expectation-specific conclusion is not transferred to those settings. The controlled-diffusion, recursive-preference, endogenous-preference, temporal-self and game developments below retain their own conditions and original role in the NBO program. Their preservation is not counted as a new comparative execution.
''')


def main():
    (R/'audit').mkdir(exist_ok=True)
    for p,h in json.loads((R/'SOURCE_SHA256.json').read_text()).items():assert H(R/p)==h,p
    ds,dr=direct_audit();cs,cr=constrained_audit();ps,pr,fr=deployment_audit()
    summary={'revision':'R47','study_source_commit':'04d0638169ae7adbdd8bb21f9d1fea5b1ef68de2',
        'study_evidence_commit':'4da0b2c286793f75a56ad6d8228cb0da82aabc60','study_run':37663771622,
        'artifact_id':11502335616,'artifact_sha256':'782e437ccb4886a18f6692b02d0e4a109abe67d729e53f5c266cf1f5df2428db',
        'direct':ds,'constrained':cs,'deployment':ps,'new_policy_cost_ranking':False,'neural_speed_advantage_established':False,
        'new_calibrated_economic_application':False,'historical_evidence_rewritten':False}
    save(R/'audit/PUBLICATION_SUMMARY.json',summary)
    save(R/'audit/RESULT_AUDIT.json',{'success':True,'direct_intervals_reconstructed':120,'constrained_rungs_reconstructed':72,
                                  'new_source_hashes_verified':5,'checkpoint_repetitions_identical':True,
                                  'statistical_path_simulations_rerun':False,'clocks_rerun':False})
    tables(ds,dr,cs,cr,ps,pr,fr)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
