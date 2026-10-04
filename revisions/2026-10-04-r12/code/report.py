"""Replay saved evidence and generate every R12 numerical table.
The final gate rejects missing records, not negative economic findings.
"""
from __future__ import annotations
import argparse,math,re
from collections import defaultdict
from common import *
import evaluation
M=R/'manuscript'

def fixed(x,side=None,digits=6):
    if side=='lo':x=math.floor(float(x)*10**digits)/10**digits
    elif side=='hi':x=math.ceil(float(x)*10**digits)/10**digits
    return f'{x:.{digits}f}'
def esc(x):return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def table(name,title,label,columns,head,rows,note):
    text=r'\begingroup\small\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{longtable}{'+columns+'}\n'+r'\caption{'+title+'}'+r'\label{'+label+'}'+r'\\'+'\n'+r'\toprule'+'\n'+' & '.join(head)+r'\\\midrule'+'\n'+r'\endfirsthead'+'\n'+r'\toprule'+'\n'+' & '.join(head)+r'\\\midrule'+'\n'+r'\endhead'+'\n'
    if rows:text+='\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'
    else:text+=r'\multicolumn{'+str(len(head))+r'}{l}{Development smoke: no observations in this table.}\\'+'\n'
    text+=r'\bottomrule\end{longtable}'+'\n'+r'\noindent '+note+'\n'+r'\endgroup'+'\n'
    (M/name).write_text(text)

def run(development=False):
    base=R/('development' if development else 'results');M.mkdir(exist_ok=True)
    records=[];inputs={};fit=[];ev=[];pairs=[];ledgers=[];refs=[]
    for path in sorted(base.rglob('*.json')):
        if path.name in ['AUDIT.json','RECORDS.json','COMPILATION.json','REMOTE_EXECUTION.json']:continue
        r=json.loads(path.read_text());inputs[str(path.relative_to(ROOT))]=digest(path);r['_path']=str(path.relative_to(ROOT))
        if path.name=='EXECUTION.json':ledgers.append(r)
        elif path.name=='REFERENCE.json':refs=r['records']
        elif 'history' in r and 'method' in r:fit.append(r)
        elif 'bound' in r and 'constants' in r and 'weights' in r:ev.append(r)
        elif 'bound' in r and 'left' in r:pairs.append(r)
    if not development:
        expected={str(x) for x in PROTOCOL['seeds']}|{'aux','reference'}
        if {x['shard'] for x in ledgers}!=expected:raise AssertionError('missing or extra worker ledgers')
        for r in ledgers:
            if not r['all_tasks_completed'] or r['smoke'] or r['source_commit']!=source() or r['protocol_sha256']!=digest(R/'PROTOCOL.json'):raise AssertionError('unclean or different-source worker')
    def close(a,b):
        if not math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=2e-14):raise AssertionError(f'replay mismatch {a} != {b}')
    for r in fit:
        if r.get('failure') or not r.get('weights_sha256'):raise AssertionError('fit failure retained: '+r['id'])
        path=ROOT/r['_path'];w=path.with_suffix('.pt')
        if digest(w)!=r['weights_sha256']:raise AssertionError('fitted weight identity')
        inputs[str(w.relative_to(ROOT))]=digest(w)
        for h in r['history']:
            cp=path.with_name(path.stem+f"_k{h['iteration']}.pt")
            if digest(cp)!=h['weights_sha256']:raise AssertionError('checkpoint identity')
            inputs[str(cp.relative_to(ROOT))]=digest(cp)
        if r['source_commit']!=source():raise AssertionError('fit source identity')
    for r in ev:
        p=ROOT/r['_path'];rawp=p.with_suffix('.npz')
        if digest(rawp)!=r['raw_sha256'] or digest(ROOT/r['weights'])!=r['weights_sha256']:raise AssertionError('evaluation identity')
        inputs[str(rawp.relative_to(ROOT))]=digest(rawp);inputs[r['weights']]=r['weights_sha256']
        with np.load(rawp) as z:
            np.testing.assert_array_equal(z['production']-z['consumption_deficit']+z['terminal_gain'],z['paired_gain'])
            _,con=evaluation.account(r['dimension'],r['steps'],r['epsilon'],r['design'],r['shift'],r['spread'])
            for key in ['bias_upper','clipping_threshold','clipping_bias','anchor_upper']:close(con[key],r['constants'][key])
            again=pc.empirical_lower(z['paired_gain'],con['clipping_threshold'],con['bias_upper'],con['clipping_bias'],PROTOCOL['one_sided_family_size'],PROTOCOL['alpha'])
            for key in ['mean','sample_sd','lower','upper','empirical_bernstein_margin']:close(again[key],r['bound'][key])
            if len(z['paired_gain'])!=r['paths']:raise AssertionError('path count')
        fees,ceil=evaluation.fee_account(r['bound']);close(ceil,r['fee_lower_break_even'])
        for new,oldfee in zip(fees,r['consumption_fee']):close(new['lower'],oldfee['lower']);close(new['upper'],oldfee['upper'])
        if r['source_commit']!=source():raise AssertionError('evaluation source identity')
    ev_by_path={r['_path']:r for r in ev}
    for r in pairs:
        a=ev_by_path[r['left']];b=ev_by_path[r['right']]
        for key in ['dimension','design','steps','paths','initial_state_hash','initial_index_hash','noise_seed','noise_sha256']:
            if a[key]!=b[key]:raise AssertionError('nonpaired method records')
        p=ROOT/r['_path'];rp=p.with_suffix('.npz')
        if digest(rp)!=r['raw_sha256']:raise AssertionError('paired raw identity')
        with np.load((ROOT/a['_path']).with_suffix('.npz')) as xa,np.load((ROOT/b['_path']).with_suffix('.npz')) as xb,np.load(rp) as zz:
            np.testing.assert_array_equal(xa['terminal_anchor'],xb['terminal_anchor']);np.testing.assert_array_equal(zz['paired_difference'],xa['paired_gain']-xb['paired_gain'])
            ca,cb=a['constants'],b['constants'];I=pc.I
            bias=float((I(ca['actor_bias_upper'])+I(cb['actor_bias_upper'])+I(ca['statistic_error_upper'])+I(cb['statistic_error_upper'])+I(1e-12)).hi)
            clip=float((I(ca['clipping_threshold'])+I(cb['clipping_threshold'])).hi);tail=float((I(ca['clipping_bias'])+I(cb['clipping_bias'])).hi)
            for x,y in [(bias,r['bias_upper']),(clip,r['clipping_threshold']),(tail,r['clipping_bias'])]:close(x,y)
            again=pc.empirical_lower(zz['paired_difference'],clip,bias,tail,PROTOCOL['one_sided_family_size'],PROTOCOL['alpha'])
            for key in ['mean','sample_sd','lower','upper']:close(again[key],r['bound'][key])
        inputs[str(rp.relative_to(ROOT))]=digest(rp)
    primary_fits=[r for r in fit if Path(r['_path']).parent.name in set(map(str,PROTOCOL['seeds'])) and not r.get('tag') and r['dimension'] in PROTOCOL['dimensions']]
    ids={r['id'] for r in primary_fits}
    primary=[r for r in ev if Path(r['weights']).stem in ids and r['design'] in PROTOCOL['designs']]
    if not development:
        if len(primary_fits)!=90 or len(primary)!=180 or len(pairs)!=120:raise AssertionError('incomplete primary study')
        if len(refs)!=4 or any(not r['converged'] for r in refs):raise AssertionError('independent reference incomplete')
        for d in PROTOCOL['dimensions']:
            for method in PROTOCOL['methods']:
                for design in PROTOCOL['designs']:
                    if len([r for r in primary if r['dimension']==d and r['method']==method and r['design']==design])!=10:raise AssertionError('primary cell missing seeds')
    if 2*(len(ev)+len(pairs))>PROTOCOL['one_sided_family_size']:raise AssertionError('finite-family allocation exceeded')
    groups=[];trows=[]
    for design in PROTOCOL['designs']:
        for d in PROTOCOL['dimensions']:
            for method in PROTOCOL['methods']:
                rows=[r for r in primary if r['design']==design and r['dimension']==d and r['method']==method]
                if not rows:continue
                g=dict(dimension=d,method=method,design=design,n=len(rows),mean_paired_statistic=float(np.mean([r['bound']['mean'] for r in rows])),seed_sd=float(np.std([r['bound']['mean'] for r in rows],ddof=1)) if len(rows)>1 else None,min_lower=min(r['bound']['lower'] for r in rows),max_upper=max(r['bound']['upper'] for r in rows),max_regret=max(r['policy_regret_upper'] for r in rows),positive=sum(r['bound']['lower']>0 for r in rows),negative=sum(r['bound']['upper']<0 for r in rows));groups.append(g)
                trows.append([d,method.upper()+' / '+('P' if design=='population' else '0'),fixed(g['mean_paired_statistic']),fixed(g['min_lower'],'lo'),fixed(g['max_regret'],'hi'),f"{g['positive']}/{len(rows)}"])
    table('table_primary.tex','Budgeted primary policy verification','tab:r12primary','rlrrrr',['$d$','Method / state','Mean statistic','Min. lower','Max. regret','Positive'],trows,'P denotes the fixed nine-profile population; 0 denotes the origin. Lower endpoints are rounded downward and regret bounds upward. Counts refer to fixed fitted policies, not unseen training seeds. All quantities except counts are in discounted utility units.')
    pairgroups=[];trows=[]
    for design in PROTOCOL['designs']:
        for d in PROTOCOL['dimensions']:
            for other in ['dpo','linear']:
                rows=[r for r in pairs if r['dimension']==d and r['design']==design and ev_by_path[r['right']]['method']==other]
                if not rows:continue
                g=dict(dimension=d,comparison='nbo-'+other,design=design,n=len(rows),mean_paired_statistic=float(np.mean([r['bound']['mean'] for r in rows])),min_lower=min(r['bound']['lower'] for r in rows),max_upper=max(r['bound']['upper'] for r in rows),positive=sum(r['bound']['lower']>0 for r in rows),negative=sum(r['bound']['upper']<0 for r in rows));pairgroups.append(g)
                trows.append([d,'P' if design=='population' else '0',other.upper(),fixed(g['mean_paired_statistic']),fixed(g['min_lower'],'lo'),fixed(g['max_upper'],'hi'),f"{g['positive']}/{g['negative']}"])
    table('table_paired.tex','Direct NBO-minus-comparator endpoints','tab:r12paired','rllrrrr',['$d$','State','Comparator','Mean statistic','Min. lower','Max. upper','$+/-$'],trows,'Each row summarizes the recorded seed-matched pairs. The last column counts strictly positive lower endpoints and strictly negative upper endpoints. The other pairs are inconclusive. Bounds are computed from pathwise differences; the common schedule transfer cancels.')
    trows=[]
    for d in PROTOCOL['dimensions']:
        for method in PROTOCOL['methods']:
            fits=[r for r in primary_fits if r['dimension']==d and r['method']==method];rows=[r for r in primary if r['dimension']==d and r['method']==method and r['design']=='population']
            if fits and rows:trows.append([d,method.upper(),fixed(np.median([r['seconds'] for r in fits]),digits=2),fixed(np.median([r['seconds'] for r in rows]),digits=2),fixed(1000*np.median([r['decision_batch256_seconds'] for r in rows]),digits=3),fixed(np.median([r['training_state_visits']+r['validation_state_visits'] for r in fits])/1e6,digits=3)])
    table('table_cost.tex','Actual work at the announced fitting budget','tab:r12cost','rlrrrr',['$d$','Method','Fit sec.','Verify sec.','Actor ms.','Visits, mln.'],trows,'Medians across the recorded primary fits. Verification refers to the population row. Actor timing is a batch of 256 proposals and excludes sensing and drift-integral acquisition. All fitting methods use the same announced 20-second budget; actual times include iteration completion.')
    stress=[r for r in ev if r['design']=='stress'];trows=[]
    for d in PROTOCOL['dimensions']:
        for mu,sd in PROTOCOL['initial_state_stresses']:
            a=[r for r in stress if r['dimension']==d and r['method']=='nbo' and r['shift']==mu and r['spread']==sd];b=[r for r in stress if r['dimension']==d and r['method']=='dpo' and r['shift']==mu and r['spread']==sd]
            if a and b:trows.append([d,f'{mu:g}',f'{sd:g}',fixed(a[0]['bound']['mean']),fixed(a[0]['bound']['lower'],'lo'),fixed(b[0]['bound']['lower'],'lo')])
    table('table_stress.tex','Severe initial-state stresses','tab:r12stress','rrrrrr',['$d$','Mean','Spread','NBO statistic','NBO lower','DPO lower'],trows,'Both methods are freshly fitted with the stated auxiliary seed under the population training design. These fixed-state stresses are outside the primary population in general. Negative lower endpoints are inconclusive, not proof of a negative true gain; full upper endpoints are saved.')
    trows=[]
    for d in PROTOCOL['dimensions']:
        for method in PROTOCOL['methods']:
            rows=[r for r in primary if r['dimension']==d and r['method']==method and r['design']=='population']
            if rows:
                counts=[sum(r['consumption_fee'][j]['lower']>0 for r in rows) for j in [1,2,3]]
                trows.append([d,method.upper(),*counts,fixed(min(r['fee_lower_break_even'] for r in rows)*10000,'lo',2)])
    table('table_fee.tex','Self-financed management-fee support in the population','tab:r12fee','rlrrrr',['$d$','Method','5 bp','10 bp','20 bp','Min. ceiling, bp'],trows,'The three central columns count fitted policies with a positive simultaneous lower improvement endpoint after the stated fee. One basis point is 0.01 percent of gross withdrawals. The ceiling is the smallest certified fee ceiling across the recorded seeds; zero does not prove that every positive fee is unprofitable.')
    trows=[]
    for r in refs:
        p=base/'reference'/(r['id']+'.npz')
        if digest(p)!=r['raw_sha256']:raise AssertionError('reference arrays altered')
        inputs[str(p.relative_to(ROOT))]=digest(p);loss=r['center_policy_losses']
        trows.append([r['nx'],r['nt'],f"{r['L']:g}",fixed(loss.get('nbo',0)),fixed(loss.get('dpo',0)),fixed(loss.get('anchor',0))])
    table('table_reference.tex','Independent nonlinear scalar HJB policy-loss diagnostics','tab:r12reference','rrrrrr',['Space nodes','Time cells','$L$','NBO loss','DPO loss','Schedule loss'],trows,'Losses are measured at initial log capital zero within the declared finite HJB approximation. The wider-domain row changes both boundary placement and mesh spacing. These are not certified multidimensional continuous-time optimality gaps.')
    nbo=[r for r in primary if r['method']=='nbo' and r['design']=='population'];direct=[r for r in pairs if r['design']=='population' and ev_by_path[r['right']]['method']=='dpo']
    statement=(f'The executed study contains {len(primary_fits)} primary fitted policies, {len(ev)} policy-evaluation rows and {len(pairs)} direct paired comparisons. '
      f'For the prespecified population, {sum(r["bound"]["lower"]>0 for r in nbo)} of {len(nbo)} NBO policies have a positive simultaneous lower improvement endpoint. '
      f'Of {len(direct)} population NBO-minus-direct-policy pairs, {sum(r["bound"]["lower"]>0 for r in direct)} have a positive lower endpoint and {sum(r["bound"]["upper"]<0 for r in direct)} have a negative upper endpoint; the remainder are inconclusive. '
      'These counts distinguish verified policy improvement from comparative method evidence. They do not turn a completed optimization run, a positive sample mean or a loose global regret bound into proof of near optimality.\n')
    if development:statement='Development smoke only; these are not final empirical results. '+statement
    (M/'results_summary.tex').write_text(statement)
    full=r'\section{Complete R12 Seed and Auxiliary Results}\label{app:r12results}'+'\n'+r'All rows below use the same stated conditional inference and are retained irrespective of sign. The raw arrays and hashes provide the full precision.\n'.replace('\\n','\n')
    table('table_seed_all.tex','Primary seed-level endpoints','tab:r12seeds','rrllrrr',['$d$','Seed','Method','State','Statistic','Lower','Upper'],[[r['dimension'],re.search(r'_s(\d+)',r['id']).group(1),r['method'].upper(),'P' if r['design']=='population' else '0',fixed(r['bound']['mean']),fixed(r['bound']['lower'],'lo'),fixed(r['bound']['upper'],'hi')] for r in primary],'Individual fitted-policy endpoints, with outward decimal presentation; no seed is replaced.')
    aux=[r for r in ev if Path(r['_path']).parent.name=='aux' and r['design']=='population']
    table('table_aux_all.tex','Fresh-radius and critic ablations','tab:r12aux','rlp{0.25\linewidth}rrr',['$d$','Method','Variant','Statistic','Lower','Upper'],[[r['dimension'],r['method'].upper(),esc(Path(r['weights']).stem.split('_s'+str(PROTOCOL['auxiliary_seed']))[-1].strip('_').replace('_',' ')),fixed(r['bound']['mean']),fixed(r['bound']['lower'],'lo'),fixed(r['bound']['upper'],'hi')] for r in aux],'Every radius variant is freshly trained. The raw-costate variant has no fitted critic; the stored method identifier retains loader compatibility and is not a claim of Bellman evaluation.')
    frontier=[r for r in ev if re.search(r'_k\d+$',Path(r['weights']).stem)]
    table('table_frontier_all.tex','Full-path work-selected checkpoint frontier','tab:r12frontier','rlrrrr',['$d$','Method','Iteration','Statistic','Lower','Upper'],[[r['dimension'],r['method'].upper(),r['iteration'],fixed(r['bound']['mean']),fixed(r['bound']['lower'],'lo'),fixed(r['bound']['upper'],'hi')] for r in frontier],'Checkpoints are chosen by elapsed fitting work, not by final economic results. All frontier rows receive the full final path count; corresponding clocks, simulator visits and verification costs are saved.')
    for name in ['table_seed_all.tex','table_aux_all.tex','table_frontier_all.tex']:full+='\\input{revisions/2026-10-04-r12/manuscript/'+name+'}\n'
    (M/'full_results.tex').write_text(full)
    audit=dict(source_commit=source(),protocol_sha256=digest(R/'PROTOCOL.json'),development=development,primary_fits=len(primary_fits),all_fits=len(fit),policy_evaluations=len(ev),method_comparisons=len(pairs),raw_arrays_replayed=len(ev)+len(pairs),one_sided_used=2*(len(ev)+len(pairs)),one_sided_allocated=PROTOCOL['one_sided_family_size'],training_failures=[r['id'] for r in fit if r.get('failure')],primary_groups=groups,method_groups=pairgroups,state_stress_rows=len(stress),auxiliary_rows=len(aux),frontier_rows=len(frontier),reference=refs,worker_ledgers=[r['_path'] for r in ledgers],scope='conditional finite-family verification; population integration is not state-uniform; exact observed-history assumptions; no universal method ranking')
    write(base/'AUDIT.json',audit)
    outputs={str(p.relative_to(ROOT)):digest(p) for p in M.glob('table_*.tex')};outputs[str((M/'results_summary.tex').relative_to(ROOT))]=digest(M/'results_summary.tex');outputs[str((M/'full_results.tex').relative_to(ROOT))]=digest(M/'full_results.tex')
    write(R/'TABLE_MANIFEST.json',dict(source_commit=source(),development=development,inputs=inputs,outputs=outputs))
    print(json.dumps(audit,indent=2),flush=True);return audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--development',action='store_true');a=p.parse_args();run(a.development)
