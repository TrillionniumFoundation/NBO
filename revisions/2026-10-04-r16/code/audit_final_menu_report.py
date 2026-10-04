#!/usr/bin/env python3
"""Independent post-execution audit of the frozen R16 continuation-menu report.

Uses only the Python standard library. No inference implementation is imported,
no raw observation bank is downloaded, and no random draw or fit is performed.
The exact rational endpoint-to-secant-to-gradient-to-whole-segment calculation
and a separate 100-digit empirical-Bernstein formula calculation are checked.
The collector's raw-bank replay remains a distinct, source-bound operation.

From any checkout, for example::

    python revisions/2026-10-04-r16/code/audit_final_menu_report.py \
        --root . --out /tmp/final-menu-independent-audit.json

Explicit --report, --protocol and --power paths can audit an extracted evidence
bundle while preserving exactly the same checks. Defaults resolve from --root.
This audit was added after execution and is not part of the frozen estimator.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import argparse
import collections
import datetime
import hashlib
import json
import math

REVISION = Path("revisions/2026-10-04-r16")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def display_path(path, root):
    path = Path(path).resolve()
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3],
        help="Repository root; defaults to this script's checkout.")
    parser.add_argument("--report", type=Path,
        help="Final protected REPORT.json; defaults to the canonical menu report.")
    parser.add_argument("--protocol", type=Path,
        help="Frozen menu protocol; defaults to the R16 protocol in --root.")
    parser.add_argument("--power", type=Path,
        help="Pre-data deterministic power/curvature account; defaults to R16 receipt.")
    parser.add_argument("--out", type=Path, required=True,
        help="New JSON audit result; never modifies the input report or protocol.")
    args = parser.parse_args(argv)
    ROOT = args.root.resolve()
    REPORT = (args.report or ROOT / REVISION / "results/continuation_menu/report/REPORT.json").resolve()
    PROTOCOL = (args.protocol or ROOT / REVISION / "protocols/menu_protocol.json").resolve()
    POWER = (args.power or ROOT / REVISION / "results/receipts/MENU_DATA_FREE_POWER.json").resolve()
    out = args.out.resolve()
    if out in {REPORT, PROTOCOL, POWER, Path(__file__).resolve()}:
        parser.error("--out must differ from every input and from the audit program")
    r=json.loads(REPORT.read_text());p=json.loads(PROTOCOL.read_text());power=json.loads(POWER.read_text())
    failures=[];checks=collections.Counter();scalar_summary={};cross_counts={};boundary=[]
    def check(ok,label,where=''):
     checks[label]+=1
     if not ok:failures.append(dict(check=label,where=where))
    def q(v):return F(float(v))
    def dec(v):return Decimal.from_float(float(v))
    def neighbor(v,towards):return math.nextafter(float(v),towards)
    def lower_decimal(v):return neighbor(float(v),-math.inf)
    def upper_decimal(v):return neighbor(float(v),math.inf)
    def true_quad_max(gL,gU,G,s):
     s=q(s);G=q(G);values=[F(0)]
     for gf in [gL,gU]:
      g=q(gf);ds=[-s,1-s]
      if G<0:
       v=-g/G
       if -s<=v<=1-s:ds.append(v)
      values.extend(g*d+G*d*d/2 for d in ds)
     return max(values)
    calibrations={c['id']:c for c in p['calibrations']}
    precurv={(a['calibration'],a['dimension']):a['scalar_curvature'] for a in power['accounts']}
    check(r['complete'] and r['protocol_sha256']==sha(PROTOCOL),'report protocol and completion')
    check(r['calibrations']==p['calibrations'],'exact frozen economic coefficients')
    check(r['primary_event_count']==216 and r['scalar_event_count']==128,'complete confidence family cardinality')
    check(q(.018)+q(.002)<=q(.02) and r['total_menu_alpha']==.02,'menu union budget')
    all_seen=[];all_scalar=[];expected_cells={f"{c}_d{d}" for c in calibrations for d in p['dimensions']}
    check(set(r['scalar_events'])==expected_cells and set(r['all_stages'])==expected_cells,'complete eight-cell design')
    for cell,group in r['scalar_events'].items():
     events=group['events'];seen=[];gaps=[];grades=[];mus=[];scalar_clips=0
     for z in events:
      c=z['calibration'];d=z['dimension'];seed=z['stream_seed'];where=f'{cell}/s{seed}'
      candidate=z['candidate'];curv=z['curvature'];ep=z['payoff_difference_interval'];rg=z['range'];seen.append(seed)
      check(cell==f'{c}_d{d}','scalar cell identity',where)
      check(z['source_commit']==r['numerical_source_commit'] and z['protocol_file_sha256']==sha(PROTOCOL),'scalar source and protocol',where)
      check(candidate['seed']==seed and candidate['stage']==3 and candidate['query_id']['state_index']==0 and candidate['query_id']['task_index']==4,'prescribed scalar seed/stage/query',where)
      check(candidate['state']==p['query_catalogs'][str(d)]['states'][0] and candidate['task']==p['tasks'][4],'exact scalar state and current task',where)
      m0=calibrations[c]['coefficients']['schedule'][0];lo=max(.02,m0-.1);hi=min(2.,m0+.1)
      check(candidate['a_left']==[lo]*d and candidate['a_right']==[hi]*d,'entire prescribed scalar action segment',where)
      check(candidate['primary_vector_candidate_unchanged'] and candidate['class_selected_before_fitting'],'separate scalar class',where)
      if not candidate['failed_fit']:
       check(candidate['candidate_grid_points']==257 and candidate['candidate_s']==candidate['selected_grid_index']/256,'critic-only candidate grid identity',where)
      check(curv==precurv[c,d],'exact pre-data curvature reproduction',where)
      G=curv['Q_second_derivative_upper'];mu=curv['strong_concavity_lower']
      check(mu==-G and curv['strong_concavity_verified']==(mu>0),'curvature sign interpretation',where)
      check(q(G)>=q(curv['continuation_second_derivative_upper'])-q(curv['current_negative_curvature_lower']),'outward curvature subtraction',where)
      check(z['independent_antithetic_pairs']==65536 and ep['paths']==65536 and rg['antithetic_pairs_per_observation']==1 and rg['gaussian_union_events']==1,'antithetic sampling denominator',where)
      ea=neighbor(.002/128,0.)
      check(z['confidence_family']['alpha']==.002 and z['confidence_family']['event_count']==128 and z['confidence_family']['event_alpha']==ea and ep['event_alpha']==ea and 128*q(ea)<=q(.002),'scalar simultaneous probability',where)
      b=rg['bounds'][0]
      check(b==ep['range_upper'] and -b==ep['range_lower'] and rg['tails'][0]==ep['clipping_tail'],'fixed population range/tail identity',where)
      check(z['accuracy_margin']==p['scalar_accuracy']['economic_margin']==.0001,'fixed scalar margin',where)
      # Reconstruct the EB formula independently at 100-digit precision. The
      # report rounds its exact-moment mean/variance to binary64, so these inputs
      # are enclosed by their immediate binary64 neighbors; no raw-bank equality
      # is claimed by this independent summary-only audit.
      with localcontext() as ctx:
       ctx.prec=100
       vlo=dec(max(0.,neighbor(ep['variance'],-math.inf)));vhi=dec(neighbor(ep['variance'],math.inf))
       ell=(Decimal(4)/dec(ea)).ln();n=Decimal(65536);B=dec(b)
       ml=(2*vlo*ell/n).sqrt()+14*B*ell/(3*(n-1))
       mh=(2*vhi*ell/n).sqrt()+14*B*ell/(3*(n-1))
       record_margin=ep['empirical_bernstein_margin']
       check(dec(record_margin)>=ml-Decimal('1e-90') and record_margin<=neighbor(upper_decimal(mh),math.inf),'independent empirical Bernstein formula',where)
       zl=dec(neighbor(ep['clipped_mean'],-math.inf));zh=dec(neighbor(ep['clipped_mean'],math.inf))
       allowance=dec(ep['bias'])+dec(ep['clipping_tail'])
       expected_lower=(lower_decimal(zl-mh-allowance),upper_decimal(zh-ml-allowance))
       expected_upper=(lower_decimal(zl+ml+allowance),upper_decimal(zh+mh+allowance))
       check(expected_lower[0]<=ep['lower']<=expected_lower[1] and expected_upper[0]<=ep['upper']<=expected_upper[1],'EB endpoints within exact-moment serialization enclosure',where)
      floor_bias=F(0)
      for side in ['left','right']:
       numeric=z['numerical_accounts'][side]
       floor_bias+=q(numeric['arithmetic_upper'][0])+q(numeric['gaussian_clipping_bias_upper'][0])+q(z['numerical_action_roundoff_allowances'][side])
      check(q(ep['bias'])>=floor_bias,'required numerical and Gaussian/action allowances retained',where)
      sl,sr=map(q,z['secant_parameters']);s=q(candidate['candidate_s']);width=sr-sl
      check(0<=sl<=s<=sr<=1 and width>0,'valid centered/boundary secant',where)
      knownL,knownU=map(q,z['known_secant_offset'])
      exact_secL=(q(ep['lower'])+knownL)/width;exact_secU=(q(ep['upper'])+knownU)/width
      secL,secU=map(q,z['secant_interval'])
      check(secL<=exact_secL and secU>=exact_secU,'exact rational payoff-to-secant enclosure',where)
      required_derivative=q(curv['absolute_second_derivative_upper'])*((s-sl)**2+(sr-s)**2)/(2*width)
      derr=q(z['secant_to_derivative_bias_upper'])
      check(derr>=required_derivative,'exact rational secant truncation allowance',where)
      gL,gU=map(q,z['gradient_interval'])
      check(gL<=secL-derr and gU>=secU+derr,'exact rational derivative interval',where)
      exact_gap=true_quad_max(*z['gradient_interval'],G,candidate['candidate_s'])
      protected_gap=q(z['scalar_optimum_gap']['gap_upper'])
      check(protected_gap>=exact_gap,'exact rational whole-interval quadratic maximization',where)
      check(z['scalar_optimum_gap']['gradient_interval']==z['gradient_interval'] and z['scalar_optimum_gap']['curvature_upper']==G and z['scalar_optimum_gap']['candidate_s']==candidate['candidate_s'],'quadratic inputs identity',where)
      check(z['scalar_optimum_gap']['strong_concavity_used']==(G<0),'quadratic curvature branch',where)
      gap=q(z['implemented_candidate_gap_upper'])
      check(gap>=protected_gap+q(z['numerical_action_roundoff_allowances']['candidate']),'implemented candidate rounding allowance',where)
      check(z['accuracy_at_margin']==(gap<=q(.0001)),'scalar attainment indicator',where)
      gaps.append(z['implemented_candidate_gap_upper']);grades.append(z['accuracy_at_margin']);mus.append(mu);scalar_clips+=ep['clipped_paths'];all_scalar.append(z)
      all_seen.append((cell,seed));
     check(len(events)==16 and set(seen)==set(p['training_streams']['seeds']) and len(seen)==len(set(seen)),'complete scalar streams',cell)
     check(group['attained']==sum(grades) and group['largest_gap_upper']==max(gaps) and group['smallest_gap_upper']==min(gaps) and group['strong_concavity_verified']==sum(v>0 for v in mus),'scalar aggregate identities',cell)
     scalar_summary[cell]=dict(attained=sum(grades),streams=16,strong_concavity_lower=mus[0],min_gap=min(gaps),max_gap=max(gaps),clipped_pairs=scalar_clips)
    methods=['vector_costate','raw_actor','dpo_actor','raw_saa'];totals={m:dict(positive=0,materially_superior=0,negative=0,equivalent=0,total=0,positive_and_equivalent=0,negative_and_equivalent=0) for m in methods}
    primary=0
    for cell,stages in r['all_stages'].items():
     check(set(stages)=={'1','2','3'},'all three work stages',cell)
     for stage,events in stages.items():
      check(len(events)==9,'nine method-level endpoints',cell+'/'+stage)
      for name,z in events.items():
       primary+=1;L=z['lower'];U=z['upper'];delta=.0001;where=f'{cell}/{stage}/{name}'
       check(math.isfinite(L) and math.isfinite(U) and L<=U,'valid protected primary interval',where)
       check(z['query_count']==384 and z['pairs_per_query']==512 and z['paths']==3145728 and z['seed_count']==16,'primary independent-pair count',where)
       check(z['economic_margin']==delta and z['confidence_family']['alpha']==.018 and z['confidence_family']['event_count']==216,'primary simultaneous family',where)
       flags=dict(statistical_superiority=L>0,economically_material_superiority=L>delta,noninferiority=L>-delta,practical_equivalence=L>-delta and U<delta,economically_material_inferiority=U<-delta,unresolved=not(L>delta or U<-delta or (L>-delta and U<delta)))
       check(z['economic_decision']==flags,'frozen strict comparison flags',where)
       if L in [-delta,0.,delta] or U in [-delta,0.,delta]:boundary.append(where)
       if name.startswith('nbo_minus_'):
        method=name[len('nbo_minus_'):];t=totals[method]
        t['positive']+=L>0;t['materially_superior']+=L>=delta;t['negative']+=U<0;t['equivalent']+=L>=-delta and U<=delta;t['total']+=1
        t['positive_and_equivalent']+=(L>0 and L>=-delta and U<=delta)
        t['negative_and_equivalent']+=(U<0 and L>=-delta and U<=delta)
    check(primary==216 and len(all_seen)==128 and len(set(all_seen))==128,'complete protected event accounting')
    for m,t in totals.items():check({k:t[k] for k in ['positive','materially_superior','negative','equivalent','total']}==r['all_stage_direct_decisions'][m],'independent direct-category aggregation',m)
    record=dict(schema='nbo-r16-final-menu-independent-math-audit-v1',status='PASS' if not failures else 'FAIL',
     audited_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),auditor='r16_math',
     report_file=display_path(REPORT, ROOT),report_sha256=sha(REPORT),protocol_sha256=sha(PROTOCOL),predata_power_sha256=sha(POWER),
     numerical_source_commit=r['numerical_source_commit'],audit_program_file=display_path(Path(__file__), ROOT),audit_program_sha256=sha(__file__),
     audit_phase='post-execution independent report audit; no fitting, random draws, or new inference',
     scalar_events=128,primary_events=216,scalar_attained=sum(x['accuracy_at_margin'] for x in all_scalar),
     exact_rational_checks=dict(checks),failures=failures,scalar_cells=scalar_summary,
     direct_categories=totals,endpoint_boundary_cases=boundary,
     scope='Independent exact-rational audit of protected endpoint-to-gradient-to-global-gap arithmetic and 100-digit EB formula audit from published protected summaries. Raw-observation replay was independently executed by the source-bound collector; this audit does not claim a second raw-bank download.',
     positive_equivalence_overlap_is_valid=True,no_frozen_scientific_source_changed=True,
     strong_concavity_failure_is_not_a_lower_bound_on_true_suboptimality=True,
     no_full_vector_adapted_or_continuous_time_near_optimality_claim=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": record["status"],
        "checks": sum(record["exact_rational_checks"].values()),
        "scalar_events": record["scalar_events"],
        "primary_events": record["primary_events"],
        "scalar_attained": record["scalar_attained"],
        "report_sha256": record["report_sha256"],
        "audit_program_sha256": record["audit_program_sha256"],
        "out": str(out), "failures": record["failures"]}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
