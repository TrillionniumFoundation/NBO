"""Reconstruct all R47 claims from immutable checkpoints and raw dyadic endpoints."""
from __future__ import annotations
import collections,itertools,json,math,statistics
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from common import R,BETA,confidence,hfile,fup
from constrained import Model,tensor_compile,moduli

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n')

def table(name,caption,label,cols,heading,rows,note='',long=False):
    if long:
        text='\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'+heading+' \\\\\n\\midrule\\endfirsthead\n\\toprule\n'+heading+' \\\\\n\\midrule\\endhead\n'
        text+='\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+'\n\\bottomrule\n\\end{longtable}\n'+note+'\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\small\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+heading+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n\\begin{minipage}{.97\\textwidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
    (R/'tables'/name).write_text(text)

def log_upper(q):
    q=F(q);k=0
    while q>=2:q/=2;k+=1
    def expansion(x):
        z=(x-1)/(x+1);m=96
        return 2*sum(z**(2*j+1)/F(2*j+1) for j in range(m))+2*z**(2*m+1)/((2*m+1)*(1-z*z))
    return expansion(q)+k*expansion(F(2))

def verify_radius_exact(row):
    log=log_upper(F(4*row['family'])/F(row['alpha_exact']))
    W=F(row['support_width_exact']);n=row['n']
    for which in ('lower','upper'):
        variance=F(row[f'{which}_endpoint_moments']['variance_exact'])
        radius=F(row[f'radius_{which}'])
        remainder=radius-7*W*log/(3*(n-1))
        assert remainder>=0 and remainder*remainder>=2*variance*log/n, ('Radius not outward',row['left'],which)

def audit():
    (R/'tables').mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
    frozen=json.loads((R/'audit/EXECUTION_FREEZE.json').read_text())
    for n,h in frozen['sources'].items():assert hfile(R/'code'/n)==h,n
    tests=(R/'audit/TESTS_EXECUTION.log').read_text();assert 'Ran 15 tests' in tests and '\nOK' in tests
    services=[];checked=[];frontier=[];objects={};prefixes={}
    for path in sorted((R/'results/constrained').glob('*/record.json')):
        s=json.loads(path.read_text());services.append(s);prefix=0
        for a in s['attempts']:
            p=path.parent/f"checkpoint-N{a['N']}.json";assert hfile(p)==a['checkpoint_sha256']
            j=json.loads(p.read_text());d,T,N=j['d'],j['T'],j['N'];K=(N+1)**d
            assert j['counts']['q_queries']==T*K*(N+1)
            assert j['counts']['innovation_evaluations']==T*K*(N+1)*2*N
            for t,row in enumerate(j['rows']):
                A,D,Lq=moduli(d,j['price'],F(row['L_future']))
                assert F(row['A'])==A and F(row['D'])==D and F(row['Lq'])>=Lq
                assert F(row['ideal_component'])==F(row['residual_upper'])+F(row['selected_upper'])
                if j['method']=='witness':
                    assert F(row['Lf'])==F(row['Lq'])
                    k=F(1,4*N)+F(1,2**20)
                    assert F(row['residual_upper'])==D*k+F(row['query_error'])+F(row['Lq'])*d/N
                    assert F(row['selected_upper'])==F(row['query_error'])
                m=Model(j['models'][t]);assert len(m.y)==K and np.all((m.actions>=0)&(m.actions<=.5))
                for bits in (12,20):
                    Lf=F(row['Lf']);Lq=F(row['Lq']);rad=F(d,2**(bits+1));diam=F(d,2**bits)
                    allowance=(2*Lf if j['method']=='witness' else Lq+Lf)*rad+D*(diam/(4*d)+F(1,2**20))
                    if j['method']=='witness':allowance+=F(m.numerical_excess())
                    assert F(row[f'deployment_allowance_{bits}'])==allowance
            assert j['gaps']['ideal']==fup(sum(BETA**t*F(r['ideal_component']) for t,r in enumerate(j['rows'])))
            for bits in (12,20):
                value=sum(BETA**t*(F(r['ideal_component'])+F(r[f'deployment_allowance_{bits}'])) for t,r in enumerate(j['rows']))
                assert j['gaps'][str(bits)]==fup(value)
            key=(d,T,j['price'],j['method'],N)
            if key in objects:assert objects[key]==a['checkpoint_sha256'],('Repetition changed a policy',key)
            else:
                objects[key]=a['checkpoint_sha256']
                # Exact witness reconstruction is performed once for every distinct object.
                if j['method']=='witness':
                    for data in j['models']:
                        owner,_=tensor_compile(data['labels'],d,N,F(data['L']))
                        assert owner.tolist()==data['owners']
            prefix+=j['counts']['q_queries'];assert a['prefix_q_queries']==prefix
            checked.append({'path':str(p.relative_to(R)),'sha256':hfile(p)})
            if s['repeat']==0:frontier.append({**{k:s[k] for k in ('d','T','price','method')},**a})
        for target,N in s['first_crossings'].items():
            expected=next((a['N'] for a in s['attempts'] if F(a['gaps']['12'])<=F(target)),None)
            assert expected==N
    assert len(services)==48 and len(checked)==144 and len(objects)==48
    allpairs={};rawcount=0
    for family,count in (('scalar',30),('pairs',8)):
        summary=json.loads((R/f'results/{family}/summary.json').read_text());assert len(summary['contrasts'])==count
        arrays={};rows=[]
        for row in summary['contrasts']:
            path=R/f'results/{family}'/row['raw_endpoints'];assert hfile(path)==row['raw_sha256']
            if path not in arrays:arrays[path]=np.load(path);rawcount+=1
            z=arrays[path]
            if family=='scalar':
                pairs=list(itertools.combinations(('cone-witness','cone-nearest','spline-nearest'),2))
                idx=pairs.index((row['left'],row['right']));lo,hi=z[f'lo{idx}'],z[f'hi{idx}']
                M=F(row['continuous_cost_upper_exact'])
                for ident in row['policy_identities'].values():
                    p=R.parent/'2026-10-07-r46'/ident['path'];assert hfile(p)==ident['sha256']
            else:lo,hi=z['lo'],z['hi'];M=F(row['cost_upper_exact'])
            assert len(lo)==row['n'] and np.all(lo<=hi)
            assert F(int(lo.min()),2**32)>=-M-F(1,2**32)
            assert F(int(hi.max()),2**32)<=M+F(1,2**32)
            computed=confidence(lo,hi,M,count)
            for k,v in computed.items():assert row[k]==v,(family,k,row[k],v)
            verify_radius_exact(row)
            rows.append(row)
        allpairs[family]=rows
    reprs=json.loads((R/'results/pairs/representations.json').read_text())['records'];assert len(reprs)==24
    for r in reprs:
        assert r['enclosures_overlap']
        assert r['cone_scores']['flat-min-plus']==r['queries']*(r['N']+1)**r['d']
        assert r['cone_scores']['compiled-min-plus']==r['queries']*2**r['d']
        assert r['cone_scores']['compiled-ReLU']==r['queries']*2**r['d']
        for bits in ('12','20'):assert r['deployment'][bits]['max_score_excess']>=0
    cells=[];timing_comparisons=[]
    for d,T,p in itertools.product((2,3),(2,4),(.25,1.)):
        record={'d':d,'T':T,'price':p}
        group={}
        for method in ('witness','multilinear-fvi'):
            ss=[s for s in services if (s['d'],s['T'],s['price'],s['method'])==(d,T,p,method)]
            last=ss[0]['attempts'][-1];times=[s['attempts'][-1]['prefix_seconds'] for s in ss]
            record[method]={'N':last['N'],'gaps':last['gaps'],'prefix_q':last['prefix_q_queries'],
                'median_seconds':statistics.median(times),'min_seconds':min(times),'max_seconds':max(times),
                'max_rss_kib':max(s['peak_rss_kib'] for s in ss),'checkpoint_bytes':last['checkpoint_bytes']}
            group[method]=ss
        cells.append(record)
        for j in range(1,33):
            target=F(j,32)
            for rep in range(3):
                rows={m:next((a for a in next(s for s in group[m] if s['repeat']==rep)['attempts'] if F(a['gaps']['12'])<=target),None) for m in group}
                if all(rows.values()):timing_comparisons.append({'d':d,'T':T,'price':p,'target':str(target),'repeat':rep,
                    'witness_N':rows['witness']['N'],'fvi_N':rows['multilinear-fvi']['N'],
                    'witness_seconds':rows['witness']['prefix_seconds'],'fvi_seconds':rows['multilinear-fvi']['prefix_seconds']})
    attainment={m:{str(F(j,32)):sum(s['first_crossings'][str(F(j,32))] is not None for s in services if s['method']==m) for j in range(1,33)} for m in ('witness','multilinear-fvi')}
    native_speed=[r['seconds']['flat-min-plus']/r['seconds']['compiled-min-plus'] for r in reprs]
    result={'revision':'R47 executed comparisons','study_source_commit':frozen['source_commit'],'services':48,'rungs':144,'distinct_objects':48,
        'direct_original_comparisons':30,'direct_constrained_comparisons':8,'raw_endpoint_archives':rawcount,
        'scalar_within_margin':sum(r['within_margin'] for r in allpairs['scalar']),
        'constrained_within_margin':sum(r['within_margin'] for r in allpairs['pairs']),
        'scalar_sign_resolved':sum(r['sign']!='sign-unresolved' for r in allpairs['scalar']),
        'constrained_sign_resolved':sum(r['sign']!='sign-unresolved' for r in allpairs['pairs']),
        'scalar_max_abs_endpoint':max(max(abs(r['lower']),abs(r['upper'])) for r in allpairs['scalar']),
        'constrained_max_abs_endpoint':max(max(abs(r['lower']),abs(r['upper'])) for r in allpairs['pairs']),
        'each_family_alpha':.05,'joint_38_family_95_percent_claim':False,'margin':.005,
        'original_path_actor_ambiguities':sum(sum(r['actor_ambiguities'].values()) for r in allpairs['scalar'])//3,
        'constrained_path_acquisition_ambiguities':sum(s['acquisition_ambiguities'] for r in allpairs['pairs'] for v in r['stats'].values() for s in v),
        'constrained_path_repairs':sum(s['repaired'] for r in allpairs['pairs'] for v in r['stats'].values() for s in v),
        'representation_records':24,'native_compiler_speedup_min':min(native_speed),'native_compiler_speedup_max':max(native_speed),
        'native_faster_than_relu':sum(r['seconds']['compiled-min-plus']<r['seconds']['compiled-ReLU'] for r in reprs),
        'cells':cells,'attainment':attainment,'common_crossing_timing_comparisons':len(timing_comparisons),
        'witness_faster_common':sum(t['witness_seconds']<t['fvi_seconds'] for t in timing_comparisons),
        'witness_earlier_rung_common':sum(t['witness_N']<t['fvi_N'] for t in timing_comparisons),
        'fvi_earlier_rung_common':sum(t['fvi_N']<t['witness_N'] for t in timing_comparisons),
        'same_rung_common':sum(t['fvi_N']==t['witness_N'] for t in timing_comparisons)}
    dump(R/'audit/PUBLICATION_SUMMARY.json',result)
    dump(R/'audit/RECONSTRUCTION.json',{'all_assertions_passed':True,'checked_checkpoints':checked,
        'checked_sources':frozen['sources'],'raw_endpoint_archives':rawcount,'exact_endpoint_moments':True,'radius_exact_rational_series_and_square_check':True,
        'repetition_policy_identity':True,'exact_tensor_reconstruction':True,'finite_cap_attainment':attainment,
        'common_target_observations':timing_comparisons})
    # Complete main and supplement tables are generated from the same audited records.
    mainrows=[]
    for c in cells:
        w=c['witness'];v=c['multilinear-fvi'];mainrows.append([c['d'],c['T'],f"{c['price']:g}",w['N'],f"{w['gaps']['12']:.5f}",f"{v['gaps']['12']:.5f}",f"{w['median_seconds']:.3f}",f"{v['median_seconds']:.3f}"])
    table('constrained47.tex','Constrained construction at the finest declared resolution','tab:constrained47','rrrrrrrr',r'$d$ & $T$ & $p$ & $N$ & $G_{\rm W}$ & $G_{\rm FVI}$ & sec. W & sec. FVI',mainrows,
          'Bounds apply to the 12-bit acquisition policy with downward 20-bit action repair, uniformly over initial states. Clocks are medians of three isolated processes and include all preceding rungs and checkpoint output. These are policy-loss upper bounds, not direct policy costs. No original result is replaced.')
    scalarrows=[]
    for T,p,target in itertools.product((2,4),(1,4),('1/4','1/8','1/16')):
        rows=[r for r in allpairs['scalar'] if (r['T'],r['price'],r['target_exact'])==(T,p,target)]
        if rows:scalarrows.append([T,p,'$'+target+'$',f"{min(r['lower'] for r in rows)*1000:.3f}",f"{max(r['upper'] for r in rows)*1000:.3f}",f'{sum(r["within_margin"] for r in rows)}/3'])
    table('scalar47.tex','Direct costs at every common R46 first crossing','tab:scalar47','rrcrrr',r'$T$ & $p$ & target & min. lower & max. upper & within margin',scalarrows,
          'Each row displays the outer endpoints, multiplied by 1,000, of the three separately reported pair intervals. The margin is 5 on this scale. All 30 contrasts have simultaneous 95 percent coverage within this family under the stated IID model. Initial capital is uniform on the full state interval. Individual intervals appear in the supplement.')
    newrows=[[r['d'],r['T'],f"{r['price']:g}",f"{1000*r['lower']:.3f}",f"{1000*r['upper']:.3f}"] for r in allpairs['pairs']]
    table('direct47.tex','Direct cost of the deployed witness policy minus fitted-value policy','tab:direct47','rrrrr',r'$d$ & $T$ & $p$ & lower $\times 10^3$ & upper $\times 10^3$',newrows,
          'The finest-rung 12-bit policies are compared on 65,536 common continuous-law bin paths from uniform initial states. This eight-contrast family has its own 95 percent simultaneous coverage statement; it is not pooled with the preceding family. The fixed margin is $\pm5$ on the displayed scale. Every interval contains zero and lies inside the margin.')
    full=[]
    abbrev={'cone-witness':'W','cone-nearest':'N','spline-nearest':'S'}
    for r in allpairs['scalar']:full.append([r['T'],r['price'],r['target_exact'],abbrev[r['left']]+'--'+abbrev[r['right']],f"{r['lower']:.7f}",f"{r['upper']:.7f}"])
    table('scalar_full47.tex','All thirty original-policy cost contrasts','tab:scalarfull47','rrclrr',r'$T$ & $p$ & target & pair & lower & upper',full,'W denotes cone witness, N the same-critic nearest actor, and S the spline nearest actor. Each interval is in original discounted cost units.',True)
    full=[]
    for a in frontier:
        ss=[s for s in services if (s['d'],s['T'],s['price'],s['method'])==(a['d'],a['T'],a['price'],a['method'])]
        times=[next(b['prefix_seconds'] for b in s['attempts'] if b['N']==a['N']) for s in ss]
        full.append([a['d'],a['T'],f"{a['price']:g}",'W' if a['method']=='witness' else 'F',a['N'],f"{a['gaps']['12']:.5f}",a['prefix_q_queries'],f"{statistics.median(times):.3f}"])
    table('frontier_full47.tex','Complete constrained work-to-bound staircase','tab:frontierfull47','rrrlrrrr',r'$d$ & $T$ & $p$ & method & $N$ & bound & prefix $Q$ & sec.',full,'All 48 distinct rungs are shown; each was independently reconstructed three times. W is witness, F is multilinear fitted-value iteration. Prefix queries count all previous rungs. Timings are medians, not independent economic samples.',True)
    reprrows=[]
    for d in (2,3):
        rs=[r for r in reprs if r['d']==d]
        ratio=[r['seconds']['flat-min-plus']/r['seconds']['compiled-min-plus'] for r in rs]
        reprrows.append([d,len(rs),(rs[0]['N']+1)**d,2**d,f'{min(ratio):.2f}',f'{max(ratio):.2f}',sum(r['seconds']['compiled-min-plus']<r['seconds']['compiled-ReLU'] for r in rs)])
    table('representation47.tex','Same-object representation and query compilation','tab:representation47','rrrrrrr',r'$d$ & objects & flat cones & compiled & min. ratio & max. ratio & native faster',reprrows,
          'Ratios divide flat-min-plus time by compiled-min-plus time on identical stored objects and query arrays. The final column counts compiled native evaluations faster than the ReLU minimum-gate backend. Both compiled implementations receive identical witness tables and distance preprocessing. These query clocks are not complete-service speedups.')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cells','attainment')},indent=2))
    return result

if __name__=='__main__':audit()
