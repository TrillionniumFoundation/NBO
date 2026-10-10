"""Conservative complete-production charges from original component clocks.

The frozen per-method field is a component sum, not a complete isolated
runtime. All unallocated time in the observed outer production envelope is
charged in full to every method. No scientific observation is overwritten.
"""
from pathlib import Path
from fractions import Fraction as F
import json
import core62 as c
R=c.R

def read(p):return json.loads(Path(p).read_text())
def main():
    replay=read(R/'audit/SCIENCE_REPLAY62.json');envelope=read(R/'audit/PRODUCTION_ENVELOPE62.json');execution=read(R/'audit/EXECUTION62.json');compiler=read(R/'audit/COMPILER62.json')
    gross=F(envelope['charged_outer_envelope_seconds']);cold=F(compiler['seconds'])+F(compiler['retained_exact_backend']['seconds'])
    core=cold;parts={}
    for task in execution['tasks']:
        summary=read(R/'results62'/task/'summary.json');clock=read(R/'results62'/task/'clock.json')
        reference=sum((F(r['seconds_through_arrays']) for r in summary['reference']),F(0))
        fitting=sum((F(v) for v in summary['construction_seconds'].values()),F(0))
        verification=sum((F(r['seconds_through_arrays']) for rows in summary['methods'].values() for r in rows),F(0))
        inference=F(clock['seconds_through_record']);total=reference+fitting+verification+inference;core+=total
        parts[task]=dict(reference_exact=str(reference),fitting_exact=str(fitting),verification_exact=str(verification),shared_inference_exact=str(inference),core_seconds=float(total))
    c.need(core<=F(execution['elapsed_science_seconds'])+F(1,1000),'Recorded nonoverlapping components exceed inner production clock')
    c.need(F(execution['elapsed_science_seconds'])<=gross,'Observed production exceeds charged envelope')
    residual=gross-core;c.need(residual>=0,'Negative unallocated time')
    tasks={}
    for t in replay['tasks']:
        name=t['task'];summary=read(R/'results62'/name/'summary.json');raw=summary['full_catalogue_release_work_seconds'];charges={}
        for key,value in raw.items():
            c.need(F(value)<=core+F(1,1000),'A method component sum is not a subset of production work')
            charges[key]=c.up(F(value)+residual)
        t['recorded_component_sums_seconds']=raw
        t['full_catalogue_release_work_seconds']=charges
        t['complete_work_scope']='Conservative complete-production charge: original recorded component sum plus all unallocated outer-envelope time. Not an isolated measured method runtime or minimum-work stopping experiment.'
        tasks[name]=dict(component_sums_seconds=raw,complete_work_charges_seconds=charges)
    ledger=dict(status='passed',accounting='postproduction timing-boundary audit of immutable observations',observed_inner_production_seconds=execution['elapsed_science_seconds'],reported_outer_production_seconds=envelope['reported_elapsed_seconds'],outer_envelope_charge_seconds=float(gross),nonoverlapping_core_sum_exact=str(core),nonoverlapping_core_sum_seconds=float(core),unallocated_residual_charged_to_every_method_exact=str(residual),unallocated_residual_charged_to_every_method_seconds=c.up(residual),cold_compilation_exact=str(cold),parts=parts,tasks=tasks,envelope_receipt_sha256=c.digest(R/'audit/PRODUCTION_ENVELOPE62.json'),scope='Shared residual includes unallocated common-certificate evaluation, JSON bookkeeping, final actor-file serialization, startup and completion. Full residual is charged to every method. Outer reserve is a transparent billing convention, not a statistical timing confidence interval. Remote publication, document production and replay have separate receipts. No rerun or altered frozen clock.')
    c.save(R/'audit/COMPLETE_WORK62.json',ledger)
    replay['complete_work_ledger_sha256']=c.digest(R/'audit/COMPLETE_WORK62.json');replay['timing_scope']=ledger['scope'];c.save(R/'audit/SCIENCE_REPLAY62.json',replay)
    print(json.dumps({k:ledger[k] for k in ('status','observed_inner_production_seconds','outer_envelope_charge_seconds','nonoverlapping_core_sum_seconds','unallocated_residual_charged_to_every_method_seconds','scope')},indent=2),flush=True)
if __name__=='__main__':main()
