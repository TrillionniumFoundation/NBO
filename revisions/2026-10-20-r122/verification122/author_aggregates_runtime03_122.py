"""New read-only author aggregate reconstruction after runtime loss.

This is a new administrative source, not recovery of a lost helper identity.
It authenticates the actual completed report, checks full fixed catalogues,
compares every paired ReLU/hinge primary row, and retains exact rationals.
It does not import scientific code or generate observations, prices, policies,
confidence intervals, or new clocks for a decision service.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time

FIELDS = ('index', 'budget', 'arm', 'loss', 'service')
ARMS = ('quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid')
F_COMMIT = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D_COMMIT = 'a3323b6f557315ea91b536637419ef6fd7984b61'
M_COMMIT = '796c5f2badf68b051ac6c144884c0e61b87faf5e'
PRIMARY_SHA = '94fc7537e5020e464118c64076c8f6ace5ff3dd6d77b1e15d35dc3f2712e5044'

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def require(ok, message):
    if not ok: raise ValueError(message)

def key(r): return tuple(r[f] for f in FIELDS)
def total(rs, name): return sum((F(r[name]) for r in rs), F(0))
def exact_range(rs, name):
    vals = [F(r[name]) for r in rs]
    return {'minimum': str(min(vals)), 'maximum': str(max(vals))}
def outward(x, places=9, upper=False):
    x, scale = F(x), 10 ** places
    n = -((-x.numerator * scale) // x.denominator) if upper else x.numerator * scale // x.denominator
    return f'{n // scale}.{n % scale:0{places}d}'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--primary', type=Path, required=True)
    ap.add_argument('--resume-verification', type=Path, required=True)
    ap.add_argument('--report-verification', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--tex-output', type=Path, required=True)
    a = ap.parse_args(); started = datetime.now(timezone.utc).isoformat(); tick = time.perf_counter()
    rev = Path(__file__).resolve().parents[1]; repo = rev.parents[1]
    report = a.report.resolve(); bound = {}
    def bind(p):
        p = Path(p).resolve(); b = {'bytes': p.stat().st_size, 'sha256': sha(p)}
        if str(p) in bound: require(bound[str(p)] == b, 'Input changed during read: ' + str(p))
        bound[str(p)] = b
        return p
    def load(p): return json.loads(bind(p).read_text())
    def rows(p): return [json.loads(s) for s in bind(p).read_text().splitlines() if s.strip()]
    freeze = load(rev/'SOURCE_FREEZE122.json')
    require(len(freeze['scientific_files']) == 243, 'Wrong frozen closure count')
    for name, digest in freeze['scientific_files'].items():
        p = bind(repo/name); require(bound[str(p)]['sha256'] == digest, 'Frozen source changed: ' + name)
    manifest = load(report/'OUTPUT_MANIFEST122.json')
    for row in manifest['files']:
        p = bind(report/row['path'])
        require(bound[str(p)] == {'bytes': row['bytes'], 'sha256': row['sha256']}, 'Report manifest mismatch: ' + row['path'])
    for name in ('EXECUTION122.json', 'OUTER_EXECUTION122.json'):
        r = load(report/name); require(r.get('status') == 'executed' and r.get('exit_code') == 0, 'Report did not execute successfully')
    s = load(report/'SUMMARY_REPORT122.json')
    require((s['source_commit'], s['state_commit'], s['actor_commit']) == (F_COMMIT, D_COMMIT, M_COMMIT), 'Wrong scientific identity')
    require(s['independent_state_units'] == 32 and s['primary_decisions'] == 5568 and s['timed_decisions'] == 8352, 'Wrong fixed sample')
    resume = load(a.resume_verification); core = load(a.report_verification)
    require(resume['status'] == core['status'] == 'verified' and core['verified_through'] == 'report', 'Incomplete verification scope')
    require(resume['primary_sha256'] == PRIMARY_SHA and resume['source_commit_F'] == F_COMMIT, 'Composite belongs to different source')
    policies = rows(report/'POLICY_CELLS122.jsonl')
    contrasts = rows(report/'SERVICE_CONTRASTS122.jsonl')
    signed = rows(report/'SIGNED_POPULATION_COMPARISONS122.jsonl')
    clocks = rows(report/'CLOCKS122.jsonl')
    intersections = rows(report/'ALL_THREE_CLOCK_INTERSECTIONS122.jsonl')
    menus = rows(report/'PRICE_MENUS122.jsonl')
    catalog = [(i, b, arm, loss) for i in range(2) for b,arm,loss in
        [(0,'online','online')] + [(b,arm,loss) for b in (5,9) for arm in ARMS for loss in ('value','marginal')]]
    cells = {k+(service,) for k in catalog for service in ('control','recycled','adaptive')}
    pm = {key(r):r for r in policies}; cm = {key(r):r for r in contrasts}
    require(len(policies) == len(pm) == 174 and set(pm) == cells, 'Incomplete policy catalogue')
    require(len(contrasts) == len(cm) == 116 and set(cm) == {k for k in cells if k[-1] != 'control'}, 'Incomplete contrast catalogue')
    require(all(r['n'] == 32 for r in policies+contrasts+signed), 'Independent state count changed')
    clockmap = {(r['scenario'],key(r)):r for r in clocks}
    require(len(clocks) == len(clockmap) == 696 and set(clockmap) == {(sc,k) for sc in ('primary32','timing00','timing01','timing02') for k in cells}, 'Incomplete clocks')
    require(all(r['n'] == (32 if r['scenario']=='primary32' else 16) for r in clocks), 'Timing and economics cohort mismatch')
    require(len(signed)==348 and len(intersections)==96 and len(menus)==384, 'Incomplete adoption catalogue')
    groups=[]
    for i in range(2):
        for service in ('recycled','adaptive'):
            pr=[r for r in policies if r['index']==i and r['service']==service]
            cr=[r for r in contrasts if r['index']==i and r['service']==service]
            require(len(pr)==len(cr)==29,'Unequal risk/service grouping')
            groups.append({'index':i,'alpha':('1/2','3/4')[i],'service':service,'actor_cells':29,
                'accepted_actions':sum(r['changed_actions'] for r in pr),
                'independent_gain_confirmations':sum(r['accepted_action_independent_gain_confirmations'] for r in pr),
                'independent_candidate_containments':sum(r['accepted_action_independent_candidate_containment'] for r in pr),
                'positive_population_lower_cells':sum(F(r['population_gain_lower'])>0 for r in cr),
                'paid_refinement_attempts':sum(r['paid_anchor_refinement_attempts'] for r in pr),
                'paid_refinements':sum(r['paid_anchor_refinements'] for r in pr),
                'qualification_refusals':sum(r['candidate_qualification_refusals'] for r in pr),
                'extra_candidate_economic_queries':sum(r['extra_candidate_economic_queries'] for r in pr),
                'sample_gain_lower_range':exact_range(cr,'sample_gain_lower'),
                'sample_gain_upper_range':exact_range(cr,'sample_gain_upper'),
                'population_gain_lower_range':exact_range(cr,'population_gain_lower'),
                'population_gain_upper_range':exact_range(cr,'population_gain_upper')})
    reference=[]; neural_comparisons=[]
    for i in range(2):
        online=pm[(i,0,'online','online','control')]
        item={f:online[f] for f in FIELDS}
        for f in ('original_policy_mean_lower','original_policy_mean_upper','independent_mean_regret_upper','independent_rms_action_error_upper'):
            item[f]=online[f]
        item['outward_display']={'policy_lower':outward(item['original_policy_mean_lower']),
            'policy_upper':outward(item['original_policy_mean_upper'],upper=True),
            'regret_upper':outward(item['independent_mean_regret_upper'],upper=True),
            'rms_action_upper':outward(item['independent_rms_action_error_upper'],upper=True)}
        item['clocks']=[{k:r[k] for k in ('scenario','n','fully_allocated_matching_cohort_seconds')} for r in clocks if key(r)==key(online)]
        reference.append(item)
        for r in policies:
            if r['index']==i and r['arm']=='relu':
                neural_comparisons.append({**{f:r[f] for f in FIELDS},
                    'neural_mean_lower':r['original_policy_mean_lower'],
                    'neural_mean_upper':r['original_policy_mean_upper'],
                    'online_control_mean_upper':online['original_policy_mean_upper'],
                    'strict_sample_online_dominance':F(r['original_policy_mean_lower'])>F(online['original_policy_mean_upper']),
                    'strict_sample_cost_gap_lower':str(F(r['original_policy_mean_lower'])-F(online['original_policy_mean_upper']))})
    neural_ranges=[]
    for i in range(2):
        rs=[r for r in policies if r['index']==i and r['arm']=='relu']
        observed={}
        for scenario in ('primary32','timing00','timing01','timing02'):
            cs=[r for r in clocks if r['index']==i and r['arm']=='relu' and r['scenario']==scenario]
            observed[scenario]=exact_range(cs,'fully_allocated_matching_cohort_seconds')
        neural_ranges.append({'index':i,'policy_lower_range':exact_range(rs,'original_policy_mean_lower'),
            'policy_upper_range':exact_range(rs,'original_policy_mean_upper'),
            'full_allocated_cohort_seconds':observed})
    primary_path=bind(a.primary/'records122.jsonl')
    require(bound[str(primary_path)]['sha256']==PRIMARY_SHA,'Primary records changed')
    # Stream and retain only the paired comparison fields, not every large trace.
    matched_fields=('action_hex','baseline_action_hex','complete_policy_lower','complete_policy_upper',
        'certified_regret_upper','certified_policy_gain_lower','accepted_improvement',
        'paid_refinement_attempt_count','refinement_count','extra_candidate_economic_queries','counts')
    paired={}; nprimary=0
    with primary_path.open() as f:
        for line in f:
            if not line.strip(): continue
            r=json.loads(line); nprimary+=1
            if r['arm'] in ('relu','hinge'):
                pk=(r['index'],r['budget'],r['loss'],r['service'],r['row'],r['arm'])
                require(pk not in paired,'Duplicate primary pair key')
                paired[pk]={name:r[name] for name in matched_fields}
    require(nprimary==5568 and len(paired)==1536,'Incomplete primary paired catalogue')
    mismatches=[]; pair_count=0
    for k, v in paired.items():
        if k[-1]!='relu': continue
        other=paired[k[:-1]+('hinge',)]; pair_count+=1
        different=[name for name in matched_fields if v[name]!=other[name]]
        if different: mismatches.append({'index':k[0],'budget':k[1],'loss':k[2],'service':k[3],'row':k[4],'different_fields':different})
    counts={'policy_cells':len(policies),'treatment_cells':len(contrasts),'primary_rows':nprimary,
        'accepted_actions':sum(r['changed_actions'] for r in policies),
        'accepted_gain_confirmations':sum(r['accepted_action_independent_gain_confirmations'] for r in policies),
        'accepted_candidate_containments':sum(r['accepted_action_independent_candidate_containment'] for r in policies),
        'positive_safe_population_lower_cells':sum(F(r['population_gain_lower'])>0 for r in contrasts),
        'signed_population_cells':len(signed),'positive_signed_population_lower_cells':sum(F(r['population_gain_lower'])>0 for r in signed),
        'negative_signed_population_upper_cells':sum(F(r['population_gain_upper'])<0 for r in signed),
        'paid_refinement_attempts':sum(r['paid_anchor_refinement_attempts'] for r in policies),
        'qualification_refusals':sum(r['candidate_qualification_refusals'] for r in policies),
        'extra_candidate_economic_queries':sum(r['extra_candidate_economic_queries'] for r in policies),
        'three_clock_menus':len(intersections),
        'nonempty_three_clock_sufficient':sum(not r['sufficient_price_domain']['empty'] for r in intersections),
        'nonempty_three_clock_upper_not_ruled_out':sum(not r['upper_not_ruled_out_domain']['empty'] for r in intersections),
        'relu_cells':len(neural_comparisons),'relu_cells_strictly_dominated_in_sample_by_online':sum(r['strict_sample_online_dominance'] for r in neural_comparisons)}
    require(counts['accepted_actions']==resume['accepted_claims']==s['changed_treatment_actions'],'Accepted count mismatch')
    require(counts['positive_safe_population_lower_cells']==s['positive_population_gain_cells'],'Population summary mismatch')
    for p,b in bound.items(): require(Path(p).stat().st_size==b['bytes'] and sha(p)==b['sha256'],'Input changed before output: '+p)
    require(not a.tex_output.exists(), 'Refuse to overwrite an earlier author table')
    table = [r'% All 174 cells; objective/error endpoints rounded outward from exact saved rational values.',
        r'\section{Complete current policy and work cells}\label{dev:allcells122}',
        r'\begingroup\setlength{\tabcolsep}{2pt}\scriptsize',
        r'\begin{longtable}{llrrrrrr}',
        r'\caption{The complete fixed 174-cell catalogue. Risk indices 0 and 1 denote $\alpha=1/2$ and $3/4$; v and m denote value and marginal fitting. Original-policy objective and error endpoints are rounded outward to nine decimal places. Work is the fully allocated 32-decision primary cohort, in seconds, rounded for display. Exact rational endpoints and clocks remain in the authenticated report.}\label{tab:allcells122}\\',
        r'\hline Cell & Service & $J_L$ & $J_U$ & Regret$_U$ & Action$_U$ & Changed & Work \\ \hline\endfirsthead',
        r'\hline Cell & Service & $J_L$ & $J_U$ & Regret$_U$ & Action$_U$ & Changed & Work \\ \hline\endhead']
    for r in policies:
        short = f"{r['index']}/{r['budget']}/{r['arm']}/{r['loss'][0]}"
        work = clockmap['primary32',key(r)]['fully_allocated_matching_cohort_seconds']
        values=[short,r['service'],outward(r['original_policy_mean_lower']),
            outward(r['original_policy_mean_upper'],upper=True),
            outward(r['independent_mean_regret_upper'],upper=True),
            outward(r['independent_rms_action_error_upper'],upper=True),
            str(r['changed_actions']),f'{float(F(work)):.5f}']
        table.append(' & '.join(values)+r' \\')
    table.extend([r'\hline\end{longtable}',r'\endgroup'])
    a.tex_output.parent.mkdir(parents=True,exist_ok=True)
    a.tex_output.write_text('\n'.join(table)+'\n')
    output={'kind':'New runtime03 exact read-only author aggregate reconstruction',
        'status':'executed','exit_code':0,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
        'seconds':time.perf_counter()-tick,'source_file_sha256':sha(__file__),
        'source_F':F_COMMIT,'states_D':D_COMMIT,'actors_M':M_COMMIT,
        'scope':'Descriptive arithmetic and paired equality checks on the complete authenticated current evidence. No new statistical inference or experiment.',
        'unpublished_lost_helper_byte_identity_claimed':False,
        'new_economic_queries':0,'new_states':0,'new_training':0,'new_service_clock_executions':0,
        'input_files':bound,'counts':counts,'risk_service_groups':groups,'online_control_reference':reference,
        'relu_vs_online_complete_catalogue':neural_comparisons,'relu_complete_risk_ranges':neural_ranges,
        'relu_hinge_primary_equality':{'pairs':pair_count,'fields':list(matched_fields),'mismatched_pairs':len(mismatches),'mismatches':mismatches},
        'author_table':{'path':str(a.tex_output),'sha256':sha(a.tex_output),'cells':174,'objective_and_error_endpoint_rounding':'outward to nine decimal places','clock_rounding':'nearest five decimal places, display only'},
        'actual_composite_assertions':resume['assertions'],'actual_core_through_report_assertions':core['assertions'],
        'actual_independent_evaluations':resume['total_distinct_original_evaluations_represented'],
        'actual_independent_witnesses':resume['canonical_witness_records'],
        'cost_clock_components':[{'category':'reporting','clock_fields':[['seconds']],
          'scope':'This new author reader only; no inherited experimental work is recharged.',
          'partial_lower_bound_only':False,'overlaps_counted_parent':False}]}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    require(not a.output.exists(),'Refuse to overwrite an earlier aggregate receipt')
    a.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'output':str(a.output),'sha256':sha(a.output),'counts':counts,'matched_pairs':pair_count,'mismatched_pairs':len(mismatches),'seconds':output['seconds']}))

if __name__=='__main__': main()
