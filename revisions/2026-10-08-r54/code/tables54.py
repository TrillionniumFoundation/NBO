"""Derived publication tables from the fully replayed frozen R53 records."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
import json
R=Path(__file__).resolve().parents[1]
M={'compiled-witness':'W','tensor-fvi':'F','surplus-fvi':'A'}

def put(name,text):
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def number(x,d=4):return f'{x:.{d}f}'
def endpoint(x,lower,d=5):
    unit=Decimal(10)**(-d)
    return format(Decimal.from_float(float(x)).quantize(unit,rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(x,d=5):return '['+endpoint(x[0],True,d)+', '+endpoint(x[1],False,d)+']'
def table(name,caption,label,heads,rows,note,cols=None):
    cols=cols or 'l'+'r'*(len(heads)-1)
    text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n{\\small\n\\begin{tabular}{'+cols+'}\n\\hline\n'
    text+=' & '.join(heads)+r' \\'+'\n\\hline\n'
    text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text+='\n\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    put('tables/'+name+'.tex',text)
def main():
    a=json.loads((R/'audit/RESULT_AUDIT54.json').read_text())
    rows=[]
    for svc in a['primary']:
        T=svc['T'];m=svc['method'];cost=next(x for x in a['primary_costs'] if x['T']==T)
        rows.append([T,M[m],band(cost['absolute_cost'][m+'-pass0']),band(cost['absolute_cost'][m+f'-pass{T}']),band(cost['contrasts'][m+f'-pass{T}-initial-gain'])])
    table('primary-cost54','Actual expected policy costs before and after full sweeps','tab:primary-cost54',
        ['$T$','Method','Initial cost','Final cost','Initial minus final'],rows,
        'W is the compiled witness construction; F is tensor FVI. Every cost is for a complete acquired policy under the original continuous initial and innovation laws. Endpoints are rounded outward for display. Paired gain intervals, not subtraction of the displayed marginal intervals, determine gain signs. The policies and observations were frozen and executed in the R53 primary study.','rrccc')
    rows=[]
    for c in a['primary_costs']:
        T=c['T']
        for k in range(T+1):rows.append([T,k,band(c['contrasts'][f'witness-minus-fvi-pass{k}'])])
    table('cross-method54','Paired witness-minus-FVI cost after every pass','tab:cross-method54',
        ['$T$','Pass','Expected-cost difference'],rows,
        'A positive interval identifies higher witness cost. An interval containing zero is unresolved, not evidence of equality or witness superiority. The same paths couple policies within a horizon; no independence between these estimands is assumed.','rrc')
    rows=[]
    for svc in a['primary']:
        for z in svc['passes']:
            rows.append([svc['T'],M[svc['method']],z['pass_number'],z['changed_cells'],z['nonterminal_changed_cells'],number(z['gap_upper'],5),number(z['prefix_seconds_through_outputs'],3)])
    table('sweeps54','All-date policy changes and certified gap recursion','tab:sweeps54',
        ['$T$','Method','Pass','Changed','Nonterminal','Gap bound','Prefix (s)'],rows,
        'Changed counts refer to distinct deployed cell-date actions in that pass, not to candidate comparisons. The gap is the directed all-state upper bound against the original continuous-action Bellman optimum. It need not decrease monotonically. Prefix work includes primitive construction and previous passes through their recorded array outputs; the final service and inference records are charged separately in the catalogue account.','rrr r r r r')
    rows=[]
    for svc in a['primary']:
        for z in svc['passes']:
            for t,(gap,chi) in enumerate(zip(z['greedy_gap_by_date'],z['contrast_bound_by_date'])):
                rows.append([svc['T'],M[svc['method']],z['pass_number'],t,number(chi,5),number(gap,5)])
    table('date-bounds54','Positive contrast bounds and complete-action gaps','tab:date-bounds54',
        ['$T$','Method','Pass','Date','$\chi$ upper','$\varepsilon$ upper'],rows,
        'The symmetric bound is obtained from anchored signed endpoints and the independent scalar fallback. The deployed gate retains the signed endpoints. The directed gap already includes whole-cell evaluation, continuous-action covering, integration and arithmetic effects; these are not added a second time. Per-bin and per-candidate endpoints remain in the compressed raw records.','rrrrrr')
    rows=[]
    for svc in a['primary']:
        for z in svc['passes']:
            rows.append([svc['T'],M[svc['method']],z['pass_number'],z['strict_candidate_comparisons'],z['symmetric_candidate_acceptances'],z['scalar_candidate_acceptances'],z['blocked_candidate_comparisons']])
    table('gates54','Directed, symmetric and scalar candidate-gate comparison','tab:gates54',
        ['$T$','Method','Pass','Directed','Symmetric','Scalar','Blocked'],rows,
        'Counts concern non-incumbent candidate comparisons. Directed counts use strict negative upper advantages. Symmetric and scalar counts use their recorded weak gates. Blocked counts use the directed rule. All three are evaluated on the same proposed actions; their counts are not independent policies.','rrrrrrr')
    rows=[]
    for svc in a['primary']+a['adaptive']:
        cohort='P' if svc in a['primary'] else 'A'
        work=svc['passes'][-1]['work']
        rows.append([cohort,svc['T'],M[svc['method']],number(svc['construction_seconds'],3),number(svc['total_service_seconds'],3),work['pair_nodes'],work['rectangle_table_bytes'],svc['peak_rss_kib']])
    table('work54','Executed construction, verification work and storage','tab:work54',
        ['Cohort','$T$','Method','Build (s)','Total (s)','Pair nodes','Table bytes','RSS (KiB)'],rows,
        'P denotes the primary cohort and A the separately executed adaptive cohort. Total is the recorded service clock through its final durable record, excluding shared inference. Pair nodes refer to the last pass, not the whole service. Table bytes are logical integer-table storage; RSS is the process peak. Neither quantity is a complete hardware-independent complexity measure. CPU affinity and library versions are in each service record.','rrr r r r r r')
    rows=[]
    for svc in a['adaptive']:
        method=svc['method'];c=a['adaptive_cost']
        for k in range(3):
            gain='--' if k==0 else band(c['contrasts'][f'{method}-pass{k}-initial-gain'])
            rows.append([M[method],k,band(c['absolute_cost'][f'{method}-pass{k}']),gain])
    table('adaptive54','Fresh actual-cost comparison with a nonuniform conventional method','tab:adaptive54',
        ['Method','Pass','Actual expected cost','Gain from initial policy'],rows,
        'A is surplus-driven FVI; W and F denote the same generators as above. All three are reconstructed in the same separately frozen cohort and receive two full improvement passes. W and F policy identities reproduce the primary cohort, while the cost paths are a fresh family. Nonuniformity and pilot work are recorded explicitly.','rrcc')
    rows=[]
    for cat in a['actual_cost_catalogues']:
        cohort={'primary-T2':'P2','primary-T3':'P3','adaptive':'A2'}[cat['cohort']]
        for point in cat['points']:
            rows.append([cohort,M[point['method']],point['selected_policy'].split('-pass')[-1],endpoint(point['actual_cost_upper'],False,5),number(point['construction_and_all_sweeps_seconds'],3),number(point['full_shared_inference_seconds'],3),number(point['measured_catalogue_work_seconds'],3)])
    table('catalogue54','Complete-catalogue work to a verified actual-cost upper bound','tab:catalogue54',
        ['Cohort','Method','Pass','Cost upper','Service (s)','Inference (s)','Sum (s)'],rows,
        'For each method the selected pass minimizes its actual-cost upper endpoint. Work conservatively charges every own executed construction and sweep, plus the entire shared inference service. It is not a first-crossing or minimum-work sequential stopping estimate. Replay and document-production overhead are separately timed in the release audit. The exact finite threshold partition, eligible methods and least-recorded-work choices are deposited in the machine-readable audit.','rrr r r r r')
    mis=a['misspecification']
    rows=[['Controlled cases',mis['cases']],['Closed cells per case',mis['cells_per_case']],['Cell--case combinations',mis['checked_cell_cases']],['Positive-bound cases',mis['nonzero_bound_cases']],['Safe changed cell--cases',mis['safe_changed_cell_cases']],['Harmful false-null cell--cases',mis['false_null_certified_harmful_cell_cases']],['Maximum contrast allowance',number(mis['maximum_contrast_bound'],5)],['New statistical observations',0]]
    table('misspecification54','Controlled deviations from exact action-null structure','tab:misspecification54',
        ['Quantity','Recorded value'],rows,
        'The catalogue changes known ReLU directions, action exposures and action-dependent innovation means. Harm means a strictly positive lower true-cost difference for an action selected by the deliberately false-null rule. Corrected decisions pass the nonpositive true-upper check. Cell--cases are deterministic repeated diagnostics, not independent economic observations.','lr')
    # Compact machine-readable counterpart of all derived tables.
    put('tables/tables54.json',json.dumps(a,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(tables=9,source='audit/RESULT_AUDIT54.json')))
if __name__=='__main__':main()
