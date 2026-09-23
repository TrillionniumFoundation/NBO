"""Rebuild R24 tables and wrappers from every frozen record, without retraining."""
from pathlib import Path
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import csv, hashlib, json, math, re, statistics
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-23-r24'; P=REV/'paper'
COUNTS={'tuning':30,'heldout':28,'multicell':36,'reference':12,'failure':4}
LABEL={'neural_adam':'Neural--Adam','direct_adam':'Direct--Adam','diagonal_adam':'Diagonal--Adam','tangent_adam':'Tangent--Adam','white_adam':'Whitened--Adam','neural_lbfgsb':'Neural--L-BFGS-B','direct_lbfgsb':'Direct--L-BFGS-B'}
ARMS=list(LABEL); CPS=(25,50,100,200,400)
def read(p): return json.loads(Path(p).read_text())
def write(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def text(n,s): (P/n).write_text(s+'\n')
def arm(r): return r.get('method','')+'_'+r['optimizer']
def mean(xs): return statistics.mean(xs)
def fmt(x): return '--' if x is None else f'{x:.3f}'
def bound(x,lower=False):
    if x is None: return '--'
    if x==0: return '0'
    d=Decimal.from_float(float(x)); unit=Decimal(1).scaleb(d.copy_abs().adjusted()-6)
    q=d.quantize(unit,rounding=ROUND_FLOOR if lower else ROUND_CEILING)
    if abs(q)<Decimal('0.00001'):
        a,b=f'{q:.6E}'.split('E'); return '$'+a+r'\times10^{'+str(int(b))+'}$'
    return format(q,'f')
def table(name,title,label,cols,head,rows,note=''):
    s='\\begin{table}[htbp]\\centering\\small\n\\caption{'+title+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\\toprule\n'
    s+=' & '.join(head)+r'\\\midrule'+'\n'
    s+='\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)
    s+='\n\\bottomrule\\end{tabular}\n'
    if note: s+='\\par\\smallskip\\begin{minipage}{.97\\textwidth}\\footnotesize '+note+'\\end{minipage}\n'
    text(name,s+'\\end{table}')
def main():
    P.mkdir(parents=True,exist_ok=True); records={}; ledger=[]; checkpoint_ledger=[]
    for ds,n in COUNTS.items():
        pp=sorted((REV/'results'/ds).rglob('record.json')); assert len(pp)==n,(ds,len(pp),n)
        records[ds]=[{**read(p),'record_path':str(p.relative_to(ROOT))} for p in pp]
        for r in records[ds]:
            a=arm(r) if ds!='failure' else Path(r['record_path']).parent.name
            c=r['final_candidate_certificate']; d=r['final_deployed_certificate']
            row={'dataset':ds,'path':r['record_path'],'arm':a,'seed':r.get('seed',23203 if ds=='failure' else None),'rate':r['learning_rate'],'orders':str(r.get('orders','--')),'calls':r['gradient_calls'],'generation_seconds':r['generation_seconds'],'checker_seconds':r['checker_seconds'],'candidate_status':c['status'],'candidate_bound':c.get('regret_upper'),'deployed_bound':d.get('regret_upper'),'termination':r['termination']}
            ledger.append(row)
            for q in r['checkpoints']:
                checkpoint_ledger.append({'dataset':ds,'path':r['record_path'],'arm':a,'seed':row['seed'],'orders':row['orders'],'cap':q['checkpoint'],'calls':q['actual_calls'],'accepted':q['accepted_for_deployment'],'candidate_status':q['certificate']['status'],'candidate_bound':q['certificate'].get('regret_upper'),'deployed_bound':q['deployed_certificate'].get('regret_upper'),'generation_seconds':q['generation_seconds'],'cumulative_check_seconds':q['cumulative_checker_seconds']})
    assert len(ledger)==110 and len(checkpoint_ledger)==286
    for name,rr in [('COMPLETE_LEDGER',ledger),('CHECKPOINT_LEDGER',checkpoint_ledger)]:
        write(REV/f'results/{name}.json',rr)
        with (REV/f'results/{name}.csv').open('w',newline='') as h:
            w=csv.DictWriter(h,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    tune=read(REV/'results/tuning_selection.json'); multi=read(REV/'results/multicell_summary.json'); failure=read(REV/'results/failure_summary.json')
    rows=[]; tuning_costs={}
    for m,rate in tune['selected'].items():
        rr=[r for r in records['tuning'] if r['method']==m]
        score=next(v['score'] for v in tune['scores'][m] if v['lr']==rate)
        gen=sum(r['generation_seconds'] for r in rr); prep=sum(r.get('preprocessing_seconds',0) for r in rr); check=sum(r['checker_seconds'] for r in rr)
        tuning_costs[m]=gen+prep+check
        rows.append([LABEL[m+'_adam'],str(rate),sum(r['gradient_calls'] for r in rr),fmt(gen),fmt(prep),fmt(check),bound(score,True)])
    table('tuning_table.tex','Disjoint tuning, with all trials charged','tab:r24tuning','lrrrrrr',['Arm','Rate','Calls','Gen. s','Prep. s','Check s','Mean lower payoff'],rows,'Two seeds, three rates, 200 calls per trial. Costs include every trial, not only the selected rate. Every arm selected the upper grid endpoint .08; optimal calibration beyond this declared finite grid is not established. Shared preprocessing is charged conservatively as a standalone cost.')
    summary=[]; rows=[]; costs=[]; curves={}; pair=[]
    for order in ([8,16],[12,24]):
        for a in ARMS:
            rr=[r for r in records['heldout'] if arm(r)==a and r['orders']==order]; assert len(rr)==2
            initial=[read(ROOT/Path(r['record_path']).parent.parent/'initial.json')['checker_seconds'] for r in rr]
            x={'orders':order,'arm':a,'max_regret_upper':max(r['final_deployed_certificate']['regret_upper'] for r in rr),'mean_calls':mean(r['gradient_calls'] for r in rr),'mean_generation_seconds':mean(r['generation_seconds'] for r in rr),'mean_checkpoint_check_seconds':mean(r['checker_seconds'] for r in rr),'mean_preprocessing_seconds':mean(r.get('preprocessing_seconds',0) for r in rr),'mean_initial_check_seconds':mean(initial),'mean_diagnostic_seconds':mean(r.get('diagnostic_seconds',0)+r.get('gradient_diagnostic_seconds',0) for r in rr)}
            x['mean_certified_cost']=sum(x[k] for k in ('mean_generation_seconds','mean_checkpoint_check_seconds','mean_preprocessing_seconds','mean_initial_check_seconds'))
            x['unamortized_accounting_cost']=x['mean_certified_cost']+415.789
            x['standalone_tuning_charge']=tuning_costs.get(a.split('_')[0],0) if a.endswith('_adam') else 0
            summary.append(x); rule=f'{order[0]}/{order[1]}'
            rows.append([rule,LABEL[a],bound(x['max_regret_upper']),f"{x['mean_calls']:.1f}",fmt(x['mean_generation_seconds']),fmt(x['mean_checkpoint_check_seconds']),fmt(x['mean_certified_cost'])])
            costs.append([rule,LABEL[a],fmt(x['mean_preprocessing_seconds']),fmt(x['mean_initial_check_seconds']),fmt(x['mean_diagnostic_seconds']),fmt(x['mean_certified_cost']),fmt(x['unamortized_accounting_cost']),fmt(x['standalone_tuning_charge'])])
            points=[]
            for cp in CPS:
                qq=[next(q for q in r['checkpoints'] if q['checkpoint']==cp) for r in rr]
                points.append({'cap':cp,'calls':mean(q['actual_calls'] for q in qq),'generation':mean(q['generation_seconds'] for q in qq),'certified':mean(q['generation_seconds']+q['cumulative_checker_seconds']+initial[i]+rr[i].get('preprocessing_seconds',0) for i,q in enumerate(qq)),'regret':max(q['deployed_certificate']['regret_upper'] for q in qq)})
            curves[f'{order[0]}_{a}']=points
        for a in ARMS[1:]:
            lo=[]; hi=[]
            for seed in (24101,24102):
                n=next(r for r in records['heldout'] if arm(r)=='neural_adam' and r['orders']==order and r['seed']==seed)['final_deployed_certificate']['value_interval']
                d=next(r for r in records['heldout'] if arm(r)==a and r['orders']==order and r['seed']==seed)['final_deployed_certificate']['value_interval']
                lo.append(math.nextafter(n[0]-d[1],-math.inf)); hi.append(math.nextafter(n[1]-d[0],math.inf))
            pair.append({'orders':order,'baseline':a,'lower':min(lo),'upper':max(hi)})
    table('heldout_table.tex','Held-out central state: accuracy and computation','tab:r24heldout','llrrrrr',['Rule','Arm','Regret upper','Calls','Gen. s','Check s','Cert. cost s'],rows,'Regret is the worse of two seeds at (t,u,x)=(0,2,1.25); calls and times are means. Policies are final deployed checkpoints. Checking includes all five scheduled checks, including converged repeats. Certified cost adds preprocessing and initial checking. Diagnostic-only calls and tuning are separate.')
    table('cost_table.tex','Standalone costs, instrumentation and upper-library allocation','tab:r24cost','llrrrrrr',['Rule','Arm','Prep.','Initial','Diag.','Cert.','+ dual','Tune'],costs,'Seconds. Diag. is additional optional scientific instrumentation. Cert. includes generation, preprocessing, initial and checkpoint checking. + dual adds the unamortized historical 415.789-second construction; divide that charge by M for M valid reuses. Tune charges all tuning trials and is additional. The historical dual charge is not a same-machine timing comparison.')
    table('pairwise_table.tex','Neural Adam minus comparator: dual-free payoff intervals','tab:r24pairwise','llrr',['Rule','Comparator','Lower','Upper'],[[f"{x['orders'][0]}/{x['orders'][1]}",LABEL[x['baseline']],bound(x['lower'],True),bound(x['upper'])] for x in pair],'Each row encloses both evaluation-seed payoff differences using independent delivered-policy intervals. Positive lower endpoints prove a payoff advantage in both matched problems; negative upper endpoints prove the reverse. This is not a confidence interval or an unrestricted optimality comparison.')
    table('multicell_table.tex','Four cells and nine distinct experts per method','tab:r24multi','lrrrr',['Arm','Region regret upper','Calls','Gen. s','Check s'],[[LABEL[x['method']],bound(x['region_regret_upper']),x['gradient_calls'],fmt(x['generation_seconds']),fmt(x['checker_seconds'])] for x in multi['rows']],'Region [1.98,2.02] x [1.24,1.27] at time zero. Every cell is certified using its deployed expert records and the retained concavity/exit theorem. The controller has the explicit augmented state. Generation/checking are totals across nine genuinely distinct experts; initial checks and preprocessing remain in the ledger.')
    refs=[]; rows=[]
    for a in ARMS:
        if a=='neural_lbfgsb':continue
        rr=[r for r in records['reference'] if arm(r)==a]; assert len(rr)==2
        x={'arm':a,'worst_gap':max(r['final_deployed_certificate']['regret_upper'] for r in rr),'worst_width':max(r['final_deployed_certificate']['policy_lower_width'] for r in rr)};refs.append(x)
        rows.append([LABEL[a],bound(x['worst_gap']),bound(x['worst_width']),f"{mean(r['gradient_calls'] for r in rr):.1f}",fmt(mean(r['generation_seconds'] for r in rr)),fmt(mean(r['checker_seconds'] for r in rr))])
    table('reference_table.tex','Analytic reference: solver gap and arithmetic width','tab:r24reference','lrrrrr',['Arm','Gap upper','Payoff width','Calls','Gen. s','Check s'],rows,'Worst gap and width across two seeds, mean calls and times. This separate deterministic economy has zero class and temporal quadrature errors. Rates transfer from original-economy tuning without reference-specific calibration. The common consumption intercept is retained; the other two output channels are inactive.')
    table('failure_table.tex','Post-hoc seed-23203 failure diagnosis','tab:r24failure','lrrrr',['Case','Regret upper','Calls','Raw distance','Financed distance'],[[k.replace('_',' '),bound(v['regret_upper']),v['gradient_calls'],fmt(v['raw_outputs_l2_to_frozen_direct']),fmt(v['financed_coefficients_l2_to_frozen_direct'])] for k,v in failure['diagnostic_results'].items()],'Distances are to the unchanged frozen R23 direct solution. Tighter and direct restarts use additional budgets. Regenerated and chart-scaled trajectories start at identical outputs; these diagnostics are excluded from tuning and held-out selection.')
    gate={'accepted':0,'rejected':0,'unchanged_candidate_rejections':0,'new_candidate_rejections':0}; grad=[]; rel=[]; offsets=[]; widths=[]; clipped=0
    for r in records['heldout']:
        prev=None
        for cp in CPS:
            q=read(ROOT/Path(r['record_path']).parent/f'checkpoint_{cp:03d}.json')
            if q['accepted_for_deployment']:gate['accepted']+=1
            else:
                gate['rejected']+=1; gate['unchanged_candidate_rejections' if prev==q['candidate_actor'] else 'new_candidate_rejections']+=1
            prev=q['candidate_actor']; dg=q['quadrature_gradient_diagnostic']; grad.append(dg['raw_gradient_difference_l2']);rel.append(dg['relative_gradient_difference_l2']);offsets.append(dg['offset_difference']);clipped+=q['candidate_actor']['clipped_nodes']
            c=q['certificate']
            if c['status']=='CERTIFIED':widths.append(c['value_interval'][1]-c['value_interval'][0])
    metrics={'protocol_commit':'b54afa8c9107d70094a1d84be4a3c0279916530c','datasets':COUNTS,'trial_count':110,'checkpoint_count':286,'heldout':summary,'pairwise':pair,'reference':refs,'gate':gate,'max_policy_enclosure_width':max(widths),'max_raw_gradient_rule_difference':max(grad),'max_relative_raw_gradient_rule_difference':max(rel),'max_financing_offset_rule_difference':max(offsets),'clipped_checkpoint_nodes_total':clipped,'selected_rates':tune['selected'],'multicell':multi,'current_state_global_bound':7.241462443133396,'full_state_target':.01,'new_full_state_accuracy_established':False}
    write(REV/'results/PUBLICATION_SUMMARY.json',metrics)
    macros={'RXXIVWidth':bound(max(widths)),'RXXIVGradientDiff':bound(max(grad)),'RXXIVRelativeGradientDiff':bound(max(rel)),'RXXIVOffsetDiff':bound(max(offsets))}
    text('result_macros.tex','\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in macros.items()))
    s=r'\section{Complete configuration ledger}\small'+'\n'+r'\begin{longtable}{llrrrrr}\toprule Dataset & Arm/rate & Seed & Calls & Gen. s & Check s & Candidate bound\\\midrule\endhead'+'\n'
    for x in ledger:
        label=LABEL.get(x['arm'],x['arm'].replace('_',' '))+(f"/{x['rate']:g}" if x['dataset']=='tuning' else '')
        s+=' & '.join([x['dataset'],label,str(x['seed'] or '--'),str(x['calls']),fmt(x['generation_seconds']),fmt(x['checker_seconds']),bound(x['candidate_bound'])])+r'\\'+'\n'
    s+=r'\bottomrule\end{longtable}\normalsize'+'\n'+r'\section{All 140 held-out checkpoints}\small'+'\n'+r'\begin{longtable}{llrrrrr}\toprule Seed/rule & Arm & Cap & Calls & Deployed bound & Gen. s & Cum. check s\\\midrule\endhead'+'\n'
    for r in records['heldout']:
        for q in r['checkpoints']:
            s+=' & '.join([f"{r['seed']}/{r['orders'][0]}",LABEL[arm(r)],str(q['checkpoint']),str(q['actual_calls']),bound(q['deployed_certificate']['regret_upper']),fmt(q['generation_seconds']),fmt(q['cumulative_checker_seconds'])])+r'\\'+'\n'
    text('full_ledger.tex',s+r'\bottomrule\end{longtable}\normalsize')
    s=''
    for rule in (8,12):
        for axis,label in [('calls','Objective/gradient calls'),('generation','Generation seconds'),('certified','Generation plus cumulative certification seconds')]:
            s+='\\begin{figure}[p]\\centering\n\\begin{tikzpicture}\\begin{axis}[width=.95\\textwidth,height=.53\\textwidth,ymode=log,xlabel={'+label+'},ylabel={Worst central-state regret upper},legend style={font=\\scriptsize,at={(0.5,-0.23)},anchor=north,legend columns=2},cycle list name=black white,grid=major]\n'
            for a in ARMS:
                pts=' '.join(f"({x[axis]:.12g},{x['regret']:.12g})" for x in curves[f'{rule}_{a}'])
                s+='\\addplot+ coordinates {'+pts+'};\\addlegendentry{'+LABEL[a]+'}\n'
            s+='\\end{axis}\\end{tikzpicture}\n\\caption{All five prospective checkpoints, rule '+str(rule)+'/'+str(2*rule)+'. Ordinate: worse regret bound across two seeds; abscissa: mean actual calls or cost. Lines connect recorded checkpoints, not extra observations. Certification is serial replay, so cumulative cost is reconstructed rather than directly timed online wall time.}\\end{figure}\n'
    text('curves.tex',s)
    text('results.tex',RESULTS)
    text('conclusion.tex',CONCLUSION)
    make_wrappers()
    print('Assembled 110 trajectories, 286 checkpoints and every prescribed comparison.')

RESULTS=r'''\section{Numerical results}\label{sec:r24results}
The study contains 110 trajectories and 286 prescribed checkpoint records, separated into tuning, evaluation, multicell construction, an analytic reference and post-hoc diagnostics. These are not pooled as independent replications of a single claim. The supplement and machine-readable ledgers retain every configuration, candidate, termination and gate decision.

\subsection{Calibrated performance and the direct frontier}
Table~\ref{tab:r24tuning} charges every tuning trial. Every arm selects $.08$, the upper edge of the finite grid. Table~\ref{tab:r24heldout} reports final deployed policies, not favorable endpoints selected after evaluation. Equal calls do not imply equal work.
\input{revisions/2026-09-23-r24/paper/tuning_table}
\input{revisions/2026-09-23-r24/paper/heldout_table}
At the coarse rule, neural Adam's worst bound is $.001925713$, versus $.002039228$ for direct Adam and $.002008735$ for diagonal Adam. The frozen tangent chart does not reproduce the neural endpoint, and inverse-metric whitening is worse. These findings are consistent with roles for adaptive geometry, transported momentum and nonlinear steps, but do not separately identify those causal contributions.

Direct L-BFGS-B remains the strongest tested solver: its deployed bound is below $.001923443$ with mean $111.5$ calls and $.321$ generation seconds, versus $400$ calls and $1.303$ seconds for neural Adam. Neural L-BFGS-B retains an adverse held-out endpoint near $.009609$. The dual-free intervals in Table~\ref{tab:r24pairwise} identify payoff ordering without confounding it with a common unrestricted upper. The old shared-rate comparison remains historical; the present finite tuning envelope governs the new interpretation.
\input{revisions/2026-09-23-r24/paper/pairwise_table}

\subsection{Quadrature, geometry and the acceptance rule}
The largest ordinary raw-gradient difference between the two rules is \RXXIVGradientDiff{}, and the largest financing-offset difference is \RXXIVOffsetDiff{}. The largest relative difference is \RXXIVRelativeGradientDiff{}, at a nearly stationary fine-rule direct L-BFGS-B checkpoint. Small absolute differences therefore do not justify interpreting a surrogate stopping tolerance as a continuous-gradient tolerance. The principal endpoint ordering survives this finite refinement comparison, but no uniform stopped-gradient error bound follows. No held-out checkpoint node was clipped. Actual Jacobian and adaptive-metric spectra and transport remainders are retained as ordinary diagnostics, not rigorous rank certificates.

The 140 held-out replayed decisions contain 121 accepted replacements and 19 rejections: seven repeat the preceding candidate exactly and twelve concern changed candidates. The optimizer was not rolled back after rejection. These observations establish the recorded deployment effect, not a contribution to proposal convergence. Curves retain every scheduled checkpoint, including carried-forward converged endpoints, against actual calls, generation time and reconstructed generation-plus-checking cost.

\subsection{Expanded state coverage and known-solution calibration}
Table~\ref{tab:r24multi} reports all four cells through their union bound. Nine distinct policies per method are trained and checked. The neural union bound $.004280526$ and direct L-BFGS-B bound $.004274863$ both meet $.01$ throughout the expanded initialization region under the augmented-state realization. They are not sampled-point, high-dimensional or all-start-time results.
\input{revisions/2026-09-23-r24/paper/multicell_table}
In the analytic reference, class and temporal quadrature errors are zero, so the remaining gap is optimization error plus directed evaluation uncertainty. Direct L-BFGS-B reaches a worst gap below $3.393\times10^{-13}$ with a payoff enclosure width around $10^{-14}$. Neural Adam has one gap below $3.621\times10^{-8}$ and another near $.002772$, worse in the latter case than the direct first-order baselines. That adverse transferred-rate outcome is retained; it precludes universal neural superiority.
\input{revisions/2026-09-23-r24/paper/reference_table}

\subsection{Failure mechanism, verification slack and the unchanged objective}
The regenerated seed-23203 bound $.010503068$ reproduces the old failure. An equivalent layer-scaled chart reduces it to $.002554827$ within its 400-call diagnostic budget. Tighter tolerance and a direct restart from the already saturated raw outputs leave the bound near $.010503067$. Removing network redundancy only after reaching the adverse output is not sufficient; decoder saturation and the preceding trajectory also matter. Raw distances are not economic payoff distances. Restart budgets are explicitly additional, not equal-total-work comparisons.
\input{revisions/2026-09-23-r24/paper/failure_table}
The largest held-out policy enclosure width is \RXXIVWidth{}. For exact policy payoff $J$ and unrestricted upper $\overline V$,
\[
 \overline V-L=(\overline V-V)+(V-J)+(J-L),\qquad 0\leq J-L\leq U-L.
\]
The first two terms are not separately identified in the original economy. Tight policy intervals alone do not identify dual slack. The reference separates these components in its own economy, while the original-economy pairwise intervals eliminate the dual. Preprocessing, generation, initial and checkpoint checking, scientific instrumentation, tuning and upper-library allocations are separately reported. The historical $415.789$-second dual cost is an accounting scenario, not a same-machine comparison; the reference/failure recovery stages also used a separately provisioned host.

The original-state all-start-time bound remains $7.241462443133396$ against the unchanged $.01$ objective. A new versioned record corrects the stale name of the older undiscounted field without changing historical bytes. This revision does not establish a new original-state full-domain accuracy certificate, a separate payoff increase for that actor, a successful nonreplicable stochastic execution, or rigorous numerical stopped-gradient errors. The new analytical and empirical results specify their actual domains while retaining the stronger objectives and their historical derivations.
'''
CONCLUSION=r'''\section{Conclusion}\label{sec:r24conclusion}
Neural Bellman Operators require explicit policy information, optimization geometry and economic verification. The financed library has a Markov realization with controller memory and the original unrestricted value under the original information structure. Its local accuracy remains separate from the full-state current-state target. Neural parameterization acts through geometry and historical gradient transport, not a larger finite-node policy family.

Disjoint tuning, explicit direct charts, quadrature refinement, all certified checkpoints, a genuine multicell cover and an analytic reference strengthen the method's empirical identification. Direct-method advantages and neural failures are scientific findings, not configurations to omit. The original $.01$ full-domain objective still requires stronger policy-sensitive verification and a separately established actor payoff improvement. The state realization, derivative theorem and executed diagnostics supply constructive ingredients without substituting an easier economic problem.
'''

def make_wrappers():
    old=(ROOT/'ECTA_R23.tex').read_text()
    pre=old.split('\\begin{document}')[0].replace('Revision R23','Revision R24').replace('R23 Manuscript','R24 Manuscript')+'\\input{revisions/2026-09-23-r24/paper/result_macros}\n'
    front=old.split('\\begin{document}',1)[1].split('\\end{frontmatter}',1)[0]
    abstract=r'''\begin{abstract}We develop Neural Bellman Operators for a stopped consumption--portfolio economy with costly preference adjustment. A financed expert controller admits an explicit augmented-state Bellman formulation with the original unrestricted value. We derive momentum-correct neural output transport and a conditional financing-gradient perturbation theorem. A prospectively fixed 110-trajectory study uses disjoint tuning, direct preconditioners, two quadrature rules, certified checkpoints, a four-cell cover and an analytic reference. Tuned neural Adam attains a central-state regret bound below $.001926$; direct L-BFGS-B remains more accurate and cheaper. Nine neural experts certify an expanded initial-state region below $.004281$. The regional controller stores initial weights and a common factor, rather than using the original state alone. All earlier derivations and adverse outcomes remain. The original full-domain $.01$ target is unchanged and is not established by the regional evidence.\end{abstract}'''
    front=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:abstract,front,flags=re.S)+'\\end{frontmatter}\n'
    body=''
    for n in ['introduction','FOUNDATIONS','state','geometry','design','results','conclusion']:
        path='revisions/2026-09-23-r18/paper/retained_foundations' if n=='FOUNDATIONS' else 'revisions/2026-09-23-r24/paper/'+n
        body+='\\input{'+path+'}\n'
    hist=old.split('\\end{frontmatter}',1)[1].split('\\begin{appendix}',1)[0]
    hist=hist.replace('\\input{revisions/2026-09-23-r18/paper/retained_foundations}','')
    text('historical_body.tex','\\section{Preserved R23 main-text development}\nThe following unchanged source components retain all preceding arguments and outcomes. Their revision-specific claims are historical; the R24 main text defines the current objects and evidence. The original foundations are already reproduced in the main text.\n'+hist)
    tail=old.split('\\begin{appendix}',1)[1]
    main=pre+'\\begin{document}'+front+body+'\\begin{appendix}\n\\input{revisions/2026-09-23-r24/paper/proofs}\n\\input{revisions/2026-09-23-r24/paper/historical_body}\n'+tail
    (ROOT/'ECTA_R24.tex').write_text(main)
    sup=(ROOT/'SUPP_R23.tex').read_text().replace('ECTA_R23','ECTA_R24').replace('Revision R23','Revision R24').replace('R23 Technical Supplement','R24 Technical Supplement')
    sup=sup.replace('\\usepackage{xr}','\\usepackage{xr}\n\\usepackage{pgfplots}\n\\pgfplotsset{compat=1.18}')
    sup=sup.replace('\\begin{document}','\\input{revisions/2026-09-23-r24/paper/result_macros}\n\\begin{document}')
    sup=sup.replace('\\end{frontmatter}','\\end{frontmatter}\n\\input{revisions/2026-09-23-r24/paper/supplement}\n\\clearpage\\section{Preserved R23 and earlier supplements}\nThe following historical components are unchanged; R24 text governs the new study.\n',1)
    (ROOT/'SUPP_R24.tex').write_text(sup)
    response=pre+'\\begin{document}'+front
    response=response.replace('\\title{Neural Bellman Operators}','\\title{Response to the Referees: Neural Bellman Operators}')
    response=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'\begin{abstract}Revision R24 responds to both reports on the sealed R23 manuscript, with new proofs and a prospective 110-trajectory study. Forty scientific and technical findings are mapped to the delivered changes. The original full-state objective and all historical material remain. Numerical requirements not established by the delivered evidence are explicitly distinguished from resolved definitional and analytical questions.\end{abstract}',response,flags=re.S)
    response+='\\input{revisions/2026-09-23-r24/paper/response}\n\\end{document}\n'
    (ROOT/'RESPONSE_R24.tex').write_text(response)
if __name__=='__main__': main()
