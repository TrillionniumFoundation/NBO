"""Generate R28 article/supplement tables from executed records, never placeholders."""
from __future__ import annotations
import json, math, statistics
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-24-r29';R=ROOT/'revisions/2026-09-24-r28/results';G=REV/'paper/generated'

def load(p):return json.loads(Path(p).read_text())
def number(x,sig=4,bound=None):
    if x is None:return '--'
    x=float(x)
    if not math.isfinite(x):raise ValueError('Non-finite table entry')
    if x==0:return '0'
    v=Decimal.from_float(x);e=v.copy_abs().adjusted();q=Decimal(1).scaleb(e-sig+1)
    mode=ROUND_CEILING if bound=='upper' else ROUND_FLOOR if bound=='lower' else ROUND_HALF_EVEN
    v=v.quantize(q,rounding=mode);e=v.copy_abs().adjusted()
    if e<-3 or e>=5:
        m=format(v.scaleb(-e),'f').rstrip('0').rstrip('.')
        return '$'+m+'\\times10^{'+str(e)+'}$'
    s=format(v,'f')
    return s.rstrip('0').rstrip('.') if '.' in s else s

def rows(name,data):
    G.mkdir(parents=True,exist_ok=True)
    (G/(name+'.tex')).write_text(''.join(' & '.join(str(z) for z in row)+r' \\'+'\n' for row in data))

def quantile(a,p):
    a=sorted(a);h=(len(a)-1)*p;i=int(h);return a[i]+(h-i)*(a[min(i+1,len(a)-1)]-a[i])
def med(a):return statistics.median(a)
def tag(x):
    s=x['spec']
    return ('N%d/%d/%d'%(s['width'],s['depth'],s['seed']-27000)) if s['kind']=='neural' else 'P%d'%s['degree']
def upper(x):return number(x,bound='upper')
def method(m):return {'neural_adam':'Neural Adam','direct_adam':'Direct Adam','direct_lbfgsb':'Direct L-BFGS-B'}[m]

def main():
    inv=load(R/'inventory/summary.json');mec=load(R/'central/mechanism_summary.json');pro=load(R/'central/production_summary.json');sli=load(R/'slice_summary.json')
    assert len(inv)==34 and len(mec)==6 and len(pro)==12 and len(sli)==2
    raw_pass=sum(Fraction(load(R/'inventory'/f"d{x['d']}_L{x['L']}"/x['tag']/'raw_certificate.json')['bound_rational'])<=Fraction(1,100) for x in inv)
    cp=sum(x['completed_target_established_exact'] for x in inv)
    rejections=sum(x['rejected_blocks'] for x in pro if x['gated'])
    macros={'InventoryCases':str(len(inv)),'InventoryRawPass':str(raw_pass),'InventoryCompletedPass':str(cp),
      'InventoryWorstCompleted':upper(max(x['completed_residual_bound'] for x in inv)),
      'MechanismMaxError':upper(max(x['max_parameter_discrepancy'] for x in mec)),
      'ProductionRejections':str(rejections)}
    G.mkdir(parents=True,exist_ok=True)
    (G/'macros.tex').write_text(''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macros.items()))
    groups=[];costs=[];tols=[];storage=[];full=[];invwork=[];byrestart=[]
    for d,L in [(2,4),(3,4),(4,4),(4,5)]:
        a=[x for x in inv if (x['d'],x['L'])==(d,L)]
        groups.append([d,L,a[0]['states'],len(a),sum(x['raw_residual_bound']<=.01 for x in a),sum(x['completed_target_established_exact'] for x in a),upper(max(x['completed_residual_bound'] for x in a))])
        costs.append([f'{d},{L}',number(med([x['generation_seconds'] for x in a if x['spec']['kind']=='neural'])),number(med([x['generation_seconds'] for x in a if x['spec']['kind']=='polynomial'])),number(med([x['raw_certification_seconds'] for x in a])),number(med([x['completion_seconds'] for x in a])),number(med([x['completed_certification_seconds'] for x in a])),number(a[0]['reference_solve_seconds'])])
        storage.append([f'{d},{L}',a[0]['states'],a[0]['actions'],a[0]['demand_outcomes'],a[0]['model_array_bytes'],a[0]['compiled_policy_bytes'],max(x['process_high_water_kib'] for x in a)])
        for tol in [.01,.05,.1,.5]:
            t=Fraction(str(tol));rawcert=0;compcert=0
            for x in a:
                base=R/'inventory'/f'd{d}_L{L}'/x['tag']
                rawcert+=Fraction(load(base/'raw_certificate.json')['bound_rational'])<=t
                compcert+=Fraction(load(base/'completed_certificate.json')['bound_rational'])<=t
            tols.append([f'{d},{L}',str(tol),rawcert,sum(Fraction(x['raw']['worst_regret_rational'])<=t for x in a),compcert,len(a)])
        for t in range(8):
            byrestart.append([f'{d},{L}',t,upper(max(x['raw']['worst_regret_by_restart'][t] for x in a)),upper(max(x['completed']['worst_regret_by_restart'][t] for x in a))])
    for x in inv:
        full.append([f"{x['d']},{x['L']}",tag(x),upper(x['raw_residual_bound']),upper(x['raw']['worst_regret']),upper(x['completed_residual_bound']),upper(x['completed']['worst_regret']),x['changed_actions']])
        invwork.append([f"{x['d']},{x['L']}",tag(x),number(x['construction_seconds']+x['completion_construction_seconds']),number(x['compilation_seconds']),number(x['candidate_and_reference_free_certification_elapsed']),number(x['standalone_completed_seconds']),number(100*x['changed_fraction_nonstopped']),number(x['raw']['regret_quantiles']['q99'])])
    rows('inventory_group_rows',groups);rows('inventory_cost_rows',costs);rows('inventory_full_rows',full);rows('inventory_work_rows',invwork);rows('inventory_tolerance_rows',tols);rows('inventory_storage_rows',storage);rows('inventory_restart_rows',byrestart)
    rows('slice_rows',[[x['k'],x['final_poll_theta'],upper(x['smoothness']['lipschitz_gradient_bound']),number(x['smoothness']['strong_concavity_lower'],bound='lower'),upper(x['restricted_class_global_regret_upper']),number(x['standalone_seconds'])] for x in sli])
    sr=[];budgets=[]
    for x in sli:
        for p in x['polls']:
            initial_lower=p['trajectory'][0]['incumbent_interval'][0]
            h=Fraction(p['mesh']);sigma=Fraction(p['forcing_sigma'])
            # M=0 is established analytically for this slice; outward lower payoff is conservative.
            accepted_bound=math.floor((-Fraction.from_float(initial_lower))/(sigma*h*h))
            sr.append([x['k'],p['mesh'],p['theta'],p['oracle_calls'],upper(p['projected_gradient_tau1_bound']),number(p['elapsed_seconds']),3*(1+accepted_bound)])
        for j in range(3):
            b=x['error_budget'];budgets.append([x['k'],j,upper(b['flow_remainders'][j]),upper(b['terminal_remainders'][j]),upper(b['stopped_bridge_remainders'][j]),upper(b['total_remainders'][j])])
    rows('slice_poll_rows',sr);rows('slice_error_rows',budgets)
    rows('mechanism_rows',[[x['seed'],'(%d,%d)'%tuple(x['orders']),upper(x['max_parameter_discrepancy']),upper(max(h['output_discrepancy_linf'] for h in load(R/'central'/f"mechanism_s{x['seed']}_q{x['orders'][0]}_{x['orders'][1]}"/'history.json'))),upper(x['max_retained_nonlinear_remainder'])] for x in mec])
    mr=[];mc=[]
    for x in mec:
        h=load(R/'central'/f"mechanism_s{x['seed']}_q{x['orders'][0]}_{x['orders'][1]}"/'history.json')
        norms=[a['quotient_output_step_norm'] for a in h]
        mr.append([x['seed'],'%d/%d'%tuple(x['orders']),number(min(norms)),number(med(norms)),number(quantile(norms,.95)),upper(x['max_first_moment_discrepancy']),upper(x['max_second_moment_discrepancy'])])
        mc.append([x['seed'],'%d/%d'%tuple(x['orders']),number(x['setup_seconds']),number(x['neural_generation_seconds']),number(x['transport_generation_seconds']),number(x['diagnostic_seconds']),number(x['standalone_seconds'])])
    rows('mechanism_distribution_rows',mr);rows('mechanism_cost_rows',mc)
    rows('production_rows',[[x['seed'],method(x['method'])+(' / G' if x['gated'] else ' / U'),x['gradient_calls'],x['rejected_blocks'],upper(x['final_certificate']['regret_upper']),number(x['standalone_elapsed_seconds'])] for x in pro])
    decisions=[];pw=[];pairs=[]
    for x in pro:
        key=method(x['method'])+(' G' if x['gated'] else ' U')
        pw.append([x['seed'],key,number(x['setup_seconds']),number(x['generation_seconds']),number(x['initial_checker_seconds']+x['checker_seconds']),number(x['bookkeeping_seconds']),number(x['standalone_elapsed_seconds'])])
        for z in x['decisions']:
            a=z['candidate_certificate']['value_interval'];b=z['incumbent_before']['value_interval']
            decisions.append([x['seed'],key,z['block'],number(a[0],7,'lower'),number(a[1],7,'upper'),number(z['strict_margin'],4,'lower'),upper(z['candidate_interval_width']),('R' if z['deployment']=='REJECT_AND_RESTORE' else 'A' if x['gated'] else 'D')])
    for seed in [27201,27202]:
        for methodname in ['neural_adam','direct_adam','direct_lbfgsb']:
            g=next(x for x in pro if x['seed']==seed and x['method']==methodname and x['gated'])
            u=next(x for x in pro if x['seed']==seed and x['method']==methodname and not x['gated'])
            a=g['final_certificate']['value_interval'];b=u['final_certificate']['value_interval']
            lo=math.nextafter(a[0]-b[1],-math.inf);hi=math.nextafter(a[1]-b[0],math.inf)
            pairs.append([seed,method(methodname),number(lo,5,'lower'),number(hi,5,'upper'),'yes' if lo>0 else 'no',g['rejected_blocks']])
    rows('production_decision_rows',decisions);rows('production_cost_rows',pw);rows('production_pair_rows',pairs)
    digest_summary={'inventory_cases':len(inv),'raw_target_passes':raw_pass,'completed_target_passes':cp,
        'worst_completed_reference_free_bound':max(x['completed_residual_bound'] for x in inv),
        'mechanism_paths':len(mec),'maximum_parameter_discrepancy':max(x['max_parameter_discrepancy'] for x in mec),
        'production_trajectories':len(pro),'production_gated_rejections':rejections,
        'all_rejections_restored_exact':all(x['all_rejections_restored_exact'] for x in pro),
        'original_full_domain_bound':7.181834580823298,'original_full_domain_target':.01,'original_full_domain_target_closed':False,
        'decimal_bound_display':'directed outward rounding; exact rational records remain authoritative'}
    (REV/'results/R28_HEADLINE_RESULTS.json').write_text(json.dumps(digest_summary,indent=2)+'\n')
    print(json.dumps(digest_summary,indent=2))
if __name__=='__main__':main()
