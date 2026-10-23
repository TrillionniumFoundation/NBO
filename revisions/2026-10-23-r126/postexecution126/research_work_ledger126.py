"""Inventory measured parent clocks once; never add their child clocks again."""
from pathlib import Path
from fractions import Fraction as F
import collections,datetime as dt,hashlib,json
ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text())
def classify(command):
    joined=' '.join(command)
    if 'campaign126c.py' in joined or 'code126/campaign126.py' in joined:
        if '--repeat' in command:return 'timing_economic_execution','Fresh original-economic decision service timing; all model and certificate work charged',True
        return 'primary_economic_execution','Fresh original-economic census; C executes both uncached and cached routes',True
    if 'code126/independent126.py' in joined:return 'independent_economic_reconstruction','Fresh exact rational original-continuous-risk economic reconstruction',True
    if 'independent_fit126.py' in joined:return 'independent_fitting_fixed_labels','Independent refitting and finite-design certificates on unchanged paid historical labels; no fresh acquisition',False
    if 'support_campaign126.py' in joined:return 'support_program_fixed_information','New convex support-program and rational certificate work on already paid support records; no economic queries',False
    if any(x in joined for x in ('verify126.py','verify126c.py','audit_support126.py','distance_audit126.py','independent_width_audit126.py')):
        return 'algebra_and_equality_audit','Saved-record or independent certificate algebra; no new original-economic evaluations',False
    if any(x in joined for x in ('report126.py','report126c.py','summarize_fit126.py')):
        return 'reporting','Reporting and complete-cost arithmetic on saved artifacts; no new economics',False
    return 'unclassified','Command retained verbatim; scientific scope not inferred',None

entries=[];missing=[]
for base in ('results126','results126c'):
    for folder in sorted((ROOT/base).glob('launch-*')):
        if not folder.is_dir():continue
        process=folder/'PROCESS126.json';start=folder/'START126.json'
        if not process.exists():
            missing.append(dict(path=folder.relative_to(ROOT).as_posix(),start_present=start.exists(),
                failure_present=(folder/'FAILURE126.json').exists(),seconds=None,unknown_not_zero=True))
            continue
        receipt=load(process);initial=load(start) if start.exists() else {}
        category,scope,new_queries=classify(receipt['command'])
        child=None
        if '--output' in receipt['command']:
            i=receipt['command'].index('--output');candidate=ROOT/receipt['command'][i+1]
            child=candidate/'EXECUTION126.json'
        entry=dict(process_receipt=process.relative_to(ROOT).as_posix(),process_sha256=digest(process),
            command=receipt['command'],returncode=receipt['returncode'],parent_wall_seconds=receipt['seconds'],
            exact_binary_parent_wall_seconds=str(F(receipt['seconds'])),peak_child_rss_kib=receipt.get('peak_child_rss_kib'),
            category=category,scientific_scope=scope,fresh_original_economic_queries=new_queries,
            started_utc=initial.get('started_utc'),started_unix=initial.get('started_unix'),
            parent_completion_present=(folder/'EXECUTION126.json').exists(),parent_failure_present=(folder/'FAILURE126.json').exists(),
            child_completion_receipt=None if child is None or not child.exists() else child.relative_to(ROOT).as_posix(),
            child_seconds_added_to_total=False)
        entries.append(entry)
entries.sort(key=lambda r:(r['started_unix'] is None,r['started_unix'] or 0,r['process_receipt']))
groups=collections.defaultdict(list)
for entry in entries:groups[entry['category']].append(entry)
summary=[]
for category,rr in sorted(groups.items()):
    seconds=sum((F(r['parent_wall_seconds']) for r in rr),F(0))
    summary.append(dict(category=category,parent_processes=len(rr),successful_returncodes=sum(r['returncode']==0 for r in rr),
        nonzero_returncodes=sum(r['returncode']!=0 for r in rr),parent_wall_seconds=float(seconds),exact_binary_parent_wall_seconds=str(seconds)))
total=sum((F(r['parent_wall_seconds']) for r in entries),F(0))
# Detect interval overlap explicitly. A sum of process wall clocks is not the
# user's elapsed turn time, even when no single child clock is counted twice.
overlap=[]
for i,a in enumerate(entries):
    if a['started_unix'] is None:continue
    for b in entries[i+1:]:
        if b['started_unix'] is None:continue
        lo=max(a['started_unix'],b['started_unix']);hi=min(a['started_unix']+a['parent_wall_seconds'],b['started_unix']+b['parent_wall_seconds'])
        if hi>lo:overlap.append(dict(first=a['process_receipt'],second=b['process_receipt'],overlap_wall_seconds=hi-lo))
limitations=[
 'Only measured parent PROCESS126.json receipts under results126 and results126c at this snapshot are summed. Every path and return code is retained.',
 'Child service/cohort/EXECUTION126 times are nested components and are not added again. Full first-state and C primary service allocations are decompositions of these parent totals, not extra work.',
 'The total is a sum of observed process wall durations on one shared host. Some launches overlapped; it is neither end-to-end elapsed time nor CPU time, core-hours, monetary expenditure or a confidence interval.',
 'Pre-freeze development, ad hoc source/schema checks, publication formatting, GitHub publication, PDF building and CI outside these launch receipts are outside this measured subtotal. Missing clocks are unknown, never zero.',
 'The preserved initial cache schema failure occurred before cache economics and outside the parent launcher; its elapsed clock is unknown and is not imputed zero.',
 'Historical acquired-label/training allocations remain in inherited125/code125/frozen_inputs/revisions/2026-10-22-r123/provenance123/inherited_costs121/fit_and_acquisition121.jsonl. Their scenario allocations are not summed as if they were a measured all-history research wall clock.',
 'Older interrupted or unavailable historical parent-process costs remain unknown. This ledger does not claim a complete all-history research total.',
 'Re-running this reporting-only inventory after additional launches updates the snapshot without re-executing science or changing the frozen outcomes.'
]
value=dict(kind='single-counted-current-parent-research-work-ledger',snapshot_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
    parent_processes=len(entries),successful_returncodes=sum(r['returncode']==0 for r in entries),
    nonzero_returncodes=sum(r['returncode']!=0 for r in entries),sum_observed_parent_wall_seconds=float(total),
    exact_binary_sum_observed_parent_wall_seconds=str(total),observed_overlapping_parent_pairs=overlap,
    child_clock_double_counting=False,unknown_costs_imputed_zero=False,uncompleted_or_unmeasured_launches=missing,
    category_totals=summary,entries=entries,scope_and_limitations=limitations,
    generator_sha256=digest(Path(__file__)),F126_source_commit=load(ROOT/'BOUNDARIES126.json')['source_commit'],
    F126C_source_commit=load(ROOT/'BOUNDARIES126C.json')['source_commit'])
out=ROOT/'provenance126';out.mkdir(exist_ok=True)
(out/'RESEARCH_WORK_LEDGER126.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
lines=['# R126 measured research work','',
 f"Snapshot: {value['snapshot_utc']}. The {len(entries)} recorded parent processes have {value['successful_returncodes']} zero and {value['nonzero_returncodes']} nonzero return codes. Their measured wall durations sum to **{float(total):.6f} seconds**. The sum includes each parent once and adds no nested child clock. This is the measured current-run subtotal, not an all-history total or the elapsed conversation time.",'',
 '| Scientific scope | Parent processes | Zero / nonzero return codes | Parent seconds |','|---|---:|---:|---:|']
for r in summary:lines.append(f"| {r['category']} | {r['parent_processes']} | {r['successful_returncodes']} / {r['nonzero_returncodes']} | {r['parent_wall_seconds']:.6f} |")
lines+=['','## Every measured parent receipt','', '| Receipt | Return code | Parent seconds | Scientific scope |','|---|---:|---:|---|']
for r in entries:lines.append(f"| `{r['process_receipt']}` | {r['returncode']} | {r['parent_wall_seconds']:.6f} | {r['scientific_scope']} |")
lines+=['','## Accounting scope','']+['- '+x for x in limitations]
lines+=['',f"The parent start/stop intervals contain {len(overlap)} overlapping pairs. The JSON ledger retains every overlap, command, artifact hash, exact binary-clock fraction, resource receipt and child-receipt linkage. Historical missing clocks are preserved as unknown. The independent arithmetic checks in the two post-execution audit scripts purchase zero economic observations, but their measured process work is charged here.",'']
(out/'RESEARCH_WORK_LEDGER126.md').write_text('\n'.join(lines))
print(json.dumps({k:value[k] for k in ('parent_processes','successful_returncodes','nonzero_returncodes','sum_observed_parent_wall_seconds','snapshot_utc')}))
