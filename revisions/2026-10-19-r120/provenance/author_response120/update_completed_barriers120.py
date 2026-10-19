"""Integrate actual completed barriers; leave uncompleted economic findings pending.

This author-source edit reads actual existing receipts. It executes no
scientific program, replay, build, workflow or Git mutation, and preserves the
thirty quoted advisory requests byte-for-byte.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re

REVISION=Path(__file__).resolve().parents[2]
F='369d02724cf12ae0e54390b4e7b5f894f703892e'
M='1c5e4dc7e04c108fe698d4c247a144b625db301c'
D='aebc7a0175c0729b9ff5e833a7facc1ed5c4c2fd'
R='594d9336d89bedfd360e942146ae490e0fabd3a0'

def readj(relative):return json.loads((REVISION/relative).read_text())
def binding(relative):
    path=REVISION/relative;raw=path.read_bytes()
    return dict(path=relative,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

def main():
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out=REVISION/'provenance/author_response120'/('completed_barriers_'+stamp)
    out.mkdir(parents=True,exist_ok=False)
    owned=['new120/response120_body.tex','SOURCE_IDENTITY120.json','provenance/R97_REQUIREMENTS120.json']
    before=[]
    for relative in owned:
        before.append(binding(relative));target=out/'before'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as stream:stream.write((REVISION/relative).read_bytes())
    receipts={}
    for kind,relative in [('source','provenance/SOURCE_PUBLICATION120.json'),('actors','provenance/ACTOR_PUBLICATION120.json'),
                          ('states','provenance/STATE_PUBLICATION120.json'),('reporting','provenance/REPORTING_PUBLICATION120.json')]:
        receipts[kind]=dict(data=readj(relative),binding=binding(relative))
    assert receipts['source']['data']['source_commit']==F
    assert receipts['actors']['data']['actor_commit']==M and receipts['actors']['data']['github_plugin_update_ref_success'] is True
    assert receipts['states']['data']['state_commit']==D and receipts['states']['data']['github_plugin_update_ref_success'] is True
    assert receipts['reporting']['data']['reporting_spec_commit']==R
    launches={};runs={};bound_inputs=[v['binding'] for v in receipts.values()]
    for label in ('acquisition','states','primary'):
        relative='results120/launches/'+label+'-attempt01/LAUNCH120.json';launch=readj(relative)
        assert launch['status']=='executed' and launch['exit_code']==0
        log_relative='results120/launches/'+label+'-attempt01/stdout.log'
        assert binding(log_relative)['sha256']==launch['stdout_sha256']
        execution_relative='results120/'+label+'-attempt01/EXECUTION120.json';run=readj(execution_relative)
        assert run['status']=='executed' and run['exit_code']==0 and run['source']['source_commit']==F
        launches[label]=dict(**{k:launch[k] for k in ['status','exit_code','started_utc','ended_utc','elapsed_seconds','head_at_launch']},
                             receipt=binding(relative),stdout=binding(log_relative))
        runs[label]=dict(receipt=binding(execution_relative),status=run['status'],exit_code=run['exit_code'],
                         started_unix=run['started_unix'],ended_unix=run['ended_unix'])
        bound_inputs.extend([binding(relative),binding(log_relative),binding(execution_relative)])
    assert launches['acquisition']['head_at_launch']==F and launches['states']['head_at_launch']==M
    assert launches['primary']['head_at_launch']==R
    catalogue=readj('results120/primary-attempt01/CATALOGUE120.json')
    timing=readj('results120/primary-attempt01/TIMING120.json')
    assert catalogue['decisions']==4096 and len(timing['repeats'])==3
    timing_count=0
    for repeat,launch in enumerate(timing['repeats']):
        assert launch['repeat']==repeat and launch['exit_code']==0
        relative=f'results120/primary-attempt01/timing/attempt-{repeat:02d}/CATALOGUE120.json'
        item=readj(relative);assert item['decisions']==2048;timing_count+=item['decisions'];bound_inputs.append(binding(relative))
    assert timing_count==6144
    bound_inputs.extend([binding('results120/primary-attempt01/CATALOGUE120.json'),binding('results120/primary-attempt01/TIMING120.json')])
    body_path=REVISION/'new120/response120_body.tex';body=body_path.read_text()
    old_quotes=re.findall(r'\\begin\{quote\}(.*?)\\end\{quote\}',body,re.S);assert len(old_quotes)==30
    def replace(old,new):
        nonlocal body
        assert body.count(old)==1,old[:100]
        body=body.replace(old,new)
    replace('% R120 author response draft. Source F is published; numerical and final-publication outcomes remain pending.',
            '% R120 author response. F/M/D/R and primary/timing are complete; independent findings and final publication remain pending.')
    start=body.index('This completed source barrier fixes the scientific study. Actor barrier')
    end=body.index('\\section{Point-by-point response to the controlling advisory}',start)
    body=body[:start]+r'''The source barrier fixes the scientific study; each subsequent barrier
retains its own actual artifact, publication and execution identity.

\paragraph{Actually completed actor, sample and decision stages.}
The original value-label acquisition and all sixteen model files completed
with exit zero under $F$. Their actual actor commit is
\nolinkurl{1c5e4dc7e04c108fe698d4c247a144b625db301c},
with publication receipt
\nolinkurl{provenance/ACTOR_PUBLICATION120.json}.
Only after this actor barrier did the program acquire the original
640 entropy bytes and construct the 64 two-coordinate, 40-bit states.
The sample completed with exit zero and was published as
\nolinkurl{aebc7a0175c0729b9ff5e833a7facc1ed5c4c2fd}; its receipt is
\nolinkurl{provenance/STATE_PUBLICATION120.json}.
The original acquisition and sample launch receipts remain in
\nolinkurl{results120/launches/acquisition-attempt01/LAUNCH120.json} and
\nolinkurl{results120/launches/states-attempt01/LAUNCH120.json}.

The fixed reporting specification was then published as
\nolinkurl{594d9336d89bedfd360e942146ae490e0fabd3a0}.
The primary launcher records this exact HEAD at 07:55:56.728551 UTC
on 19 October 2026. The separate reporting-publication transport receipt
was written at 08:00:26 UTC, after launch. It preserves the actual
successful publication-before-launch operation sequence; its later
recording time and Git committer date are not reported as independently
observed prelaunch push timestamps.

The primary process and all three prescribed timing processes completed
with exit zero at 08:09:59.755563 UTC. They retain all 4,096 primary
decisions and 6,144 descriptive timing decisions. The actual outer
primary-and-timing launch elapsed time is 843.024816 seconds, including
its declared nested stages; it must not be added to its child timings
as if those were disjoint costs. The full original receipt and stdout
are bound by
\nolinkurl{results120/launches/primary-attempt01/LAUNCH120.json}.
Execution completion alone does not supply an independently validated
gain, a population confidence statement or a neural adoption region.

At this dated author update, independent policy validation and the
prespecified inferential/reporting stages have not yet supplied their
completed results. The remaining fields are
\nolinkurl{R120_PENDING_COMPLETE_EXPERIMENT},
\nolinkurl{R120_PENDING_INDEPENDENT_VALIDATION} and
\nolinkurl{R120_PENDING_PUBLICATION}. They concern completion of the
economic account, independent evidence and final package, rather than
denying the now completed source, actor, sample and primary stages.
Every successful or failed attempt retains its own identity. Existing
R119 results and CI successes remain distinct from R120 evidence.

''' +body[end:]
    replace('below identify work now written and proved; the empirical actions retain\ntheir prospective status until actual completed records are available.',
            'below identify work now written and proved. The scientific actions were\nfixed before sampling; the completed execution stages are identified above.\nEconomic contrasts and population findings require the independently\ncompleted validation and reporting stages.')
    replace('The information result is strengthened by an implementable paid-localization upper algorithm matching the lower order KR(1-alpha)/N\\textasciicircum{}2 under one shared deterministic exact-point convention. The original investment certificate then carries the result into a real original-action calculation with finite-precision error paid.',
            r'The inherited information result includes an implementable algorithm that pays for tail localization and matches the lower order $KR(1-\alpha)N^{-2}$ under one shared deterministic exact-point convention. The original investment certificate carries this result into a feasible original-action calculation and pays its finite-precision error.')
    replace('The new original d=2 theorem proves a gradient modulus for the constrained AVaR continuation and an action-distance modulus for its difference. The fixed-known-tail information theorem gives matching interval-width order min(KR(1-alpha)/N\\textasciicircum{}2, ER(1-alpha)/N) under one scalar-value-per-query convention. The original smooth continuation also gives the stronger separate-width coefficient 2*M\\_alpha*R\\textasciicircum{}2*(1-alpha)\\textasciicircum{}2; the generic lower adversary does not establish a lower bound for that stronger smooth or formula-informed class. The full original-policy certificate separately pays both risk deficits, actual point uncertainty and the unchanged future allowance. The finite-refinement proposition states the full positive gain margin and cap; it does not rebrand the achieved R119 tail-uniform theorem as new.',
            r'''The original $d=2$ theorem proves a gradient modulus for the constrained
AVaR continuation and an action-distance modulus for its difference. With
a fixed known tail and one scalar value per query, the matching width order is
\[
\min\{KR(1-\alpha)N^{-2},\;ER(1-\alpha)N^{-1}\}.
\]
The original smooth continuation also gives the stronger separate-width
coefficient $2M_\alpha R^2(1-\alpha)^2$. The generic lower adversary does
not establish a lower bound for that smoother or formula-informed class.
The full original-policy certificate separately pays both risk deficits,
actual point uncertainty and the unchanged future allowance. The finite
refinement proposition states the full positive gain margin and cap.
The achieved R119 tail-uniform theorem retains its earlier attribution.''')
    replace('Optimal general randomized, nonuniform multivariate and complete learned Bellman complexity remain separate obligations unless actually proved. The scalar tail-uniform theorem does not pay for arbitrarily accurate floating-point values.',
            'Randomized information bounds, nonuniform and multivariate risks, and full learned Bellman complexity require further results. The current scalar theorem keeps the cost of acquiring accurate continuation values explicit.')
    replace('The revision adds explicit action-coupled certificates, continuation-error transport and original-policy all-action lower witnesses, and directly evaluates policy cost, rejections and complete work. It does not claim the unchanged inherited least-squares/span acquisition is now decision-aligned. D independently evaluates the full delivered-policy catalogue and reports all direct economic contrasts, including zero and unresolved values. It changes no labels, fitted coefficients, action proposals or selection criterion. The new value evidence therefore cannot be used to declare the unchanged acquisition objective action-aligned.',
            'R119 supplies certificates for action comparisons, continuation-error transport and original-policy all-action lower witnesses. It evaluates policy cost, rejections and complete work. The inherited least squares training objective remains unchanged.\n\nR119 validation D independently evaluates the full delivered-policy catalogue and retains every direct economic contrast, including zero and unresolved intervals. It changes no labels, fitted coefficients, proposals or selection criterion. This value evidence therefore leaves the separate request for an action-aware training objective open.')
    replace('Retain Neural Bellman Operators as the central learned-continuation and recursive-actor research identity. Attribute the action-dependent comparison theorem and policy safeguard to a method shared by every eligible representation. The protocol forbids inferring neural exclusivity from ordinary hinge geometry, common original-model formulas, common certificates or a gain against only the neural arm own incumbent.',
            'Retain Neural Bellman Operators as the study of learned continuations, recursive operators and actor/critic decisions. Attribute the action-dependent comparison theorem and policy safeguard to a method shared by every eligible representation.\n\nThe protocol requires neural representation claims to survive equal access to hinge features, original-model formulas and certificates. A gain over a neural method\'s own incumbent does not establish superiority over the conventional menu.')
    assert re.findall(r'\\begin\{quote\}(.*?)\\end\{quote\}',body,re.S)==old_quotes
    body_path.write_text(body)
    identity=readj('SOURCE_IDENTITY120.json');status=identity['r120_scientific_execution']
    status.update(status='F/M/D/reporting specification published; acquisition, sampling, primary and all three timing processes completed with exit zero. Independent, inferential and final-publication results are not yet integrated in this dated author update.',
        actor_commit=M,state_commit=D,reporting_spec_commit=R,actor_tree=receipts['actors']['data']['tree'],
        state_tree=receipts['states']['data']['tree'],reporting_spec_tree=receipts['reporting']['data']['tree'],
        actor_publication_receipt=receipts['actors']['binding'],state_publication_receipt=receipts['states']['binding'],
        reporting_publication_receipt=receipts['reporting']['binding'],completed_launches=launches,completed_executions=runs,
        completed_primary_decisions=4096,completed_timing_processes=3,completed_timing_decisions=6144,
        new_economic_gain_claimed=False,independent_validation_completed_in_this_author_update=False,
        population_results_completed_in_this_author_update=False,publication_completed_in_this_author_update=False,
        author_status_updated_utc=now,
        reporting_publication_timing_scope='Later-written transport receipt and Git committer date remain distinct from actual operation-order evidence and the launch recorder HEAD; no invented observed push timestamp.')
    identity['author_status_updated_utc']=now
    (REVISION/'SOURCE_IDENTITY120.json').write_text(json.dumps(identity,indent=2)+'\n')
    requirements=readj('provenance/R97_REQUIREMENTS120.json')
    requirements.update(actor_commit=M,state_commit=D,reporting_spec_commit=R,execution_status_update_utc=now,
        completed_stage_scope='Acquisition, sample, primary and all three timings have actual exit-zero receipts; independent economic and population outcomes are pending in this dated response update.',
        completed_stage_receipt_bindings=bound_inputs)
    for item in requirements['items']:
        item['r120_empirical_status']='The fixed acquisition, sampling,4096 primary and6144 timing decisions completed with exit zero. Independent original-policy comparisons and the prespecified population/reporting results remain pending in this dated author update; no favorable gain or neural advantage is asserted.'
    (REVISION/'provenance/R97_REQUIREMENTS120.json').write_text(json.dumps(requirements,indent=2,ensure_ascii=False)+'\n')
    receipt=dict(status='author_source_updated',observed_utc=now,before=before,after=[binding(p) for p in owned],
        actual_input_receipts=bound_inputs,original_quoted_requests_preserved=30,
        scientific_execution=False,statistics_or_reporting_replay=False,build_execution=False,
        Git_or_remote_mutation=False,independent_or_favorable_economic_success_asserted=False,
        scope='Integrates actual completed custody/primary stages and improves author-only typesetting; later economic, independent and final-publication evidence stays pending.')
    with (out/'AUTHOR_COMPLETED_BARRIERS_UPDATE120.json').open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':'author_source_updated','receipt':str(out.relative_to(REVISION)/'AUTHOR_COMPLETED_BARRIERS_UPDATE120.json'),
                      'original_quotes_preserved':30,'source':F,'actors':M,'states':D,'reporting':R}))

if __name__=='__main__':main()
