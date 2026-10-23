"""Generate the exact-request R125 author response, with no inferred closure."""
from pathlib import Path
import collections, datetime, hashlib, json, re
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'response_inputs/R97_REQUESTS_AND_R122_RESPONSES125.json'
prior=json.loads(SOURCE.read_bytes())

def load_completed_evidence():
    names=['results125/primary/EXECUTION125.json','results125/verification/EXECUTION125.json',
           'results125/fixtures/EXECUTION125.json','results125/independent/EXECUTION125.json',
           'results125/independent/SUMMARY125.json','results125/report/EXECUTION125.json',
           'results125/report/SUMMARY125.json','results125/report/cohorts_summary125.jsonl',
           'results125/report/neural_adoption125.jsonl','BOUNDARIES125.json',
           'results125/postfreeze-terminal-diagnostic/DIAGNOSTIC125.json',
           'results125/presentation-directed/descriptive125.json',
           'results125/presentation-directed/PRESENTATION125.json',
           'results125/presentation-directed/WORK_ACCOUNTING_CLOSURE125.json']
    names += [f'results125/launch-timing{i}/PROCESS125.json' for i in range(3)]
    if not all((ROOT/n).exists() for n in names):return None
    primary=json.loads((ROOT/names[0]).read_bytes())
    verify=json.loads((ROOT/names[1]).read_bytes())
    independent=json.loads((ROOT/names[3]).read_bytes())
    report=json.loads((ROOT/names[6]).read_bytes())
    for d in [primary,verify,independent,json.loads((ROOT/names[5]).read_bytes())]:
        assert d['status']=='executed' and d['exit_code']==0
    assert primary['decisions']==936 and report['all_original_qualified']==936
    assert verify['strict_improvements']==251 and verify['checks']==16162
    assert (independent['contained'],independent['accepted_gain_confirmed'],independent['contradictions'])==(850,193,0)
    bymode=collections.defaultdict(lambda:collections.Counter())
    for line in (ROOT/names[7]).read_text().splitlines():
        if line:
            r=json.loads(line)
            for k in ['n','accepted','new_terminal_nodes','query_attempts','stronger_target']:
                bymode[r['mode']][k]+=r[k]
    price=[json.loads(line) for line in (ROOT/names[8]).read_text().splitlines() if line]
    assert len(price)==128 and not any(not r['sufficient']['empty'] for r in price)
    assert all(not r['optimistic']['empty'] for r in price)
    descriptive=json.loads((ROOT/'results125/presentation-directed/descriptive125.json').read_bytes())
    mode_details={row['mode']:row for row in descriptive['modes']}
    assert all(mode_details[m]['first_state_enhancement_queries']==0 for m in
               ['fused_control','warm_adaptive','cold_adaptive','warm_fixed512'])
    work=json.loads((ROOT/'results125/presentation-directed/WORK_ACCOUNTING_CLOSURE125.json').read_bytes())
    assert work['all_match'] is True and work['rows']==696
    warm=mode_details['warm_adaptive']; fixed=mode_details['warm_fixed512']
    work_reduction=1-Fraction(warm['new_terminal_contexts'],fixed['new_terminal_contexts'])
    time_increase=Fraction(warm['complete_primary_parent_allocated_seconds'])/Fraction(fixed['complete_primary_parent_allocated_seconds'])-1
    assert work_reduction>0 and time_increase>0
    timing_parents=[json.loads((ROOT/f'results125/launch-timing{i}/PROCESS125.json').read_bytes()) for i in range(3)]
    return {'source_commit':json.loads((ROOT/'BOUNDARIES125.json').read_bytes())['source_commit'],
            'primary_decisions':936,'timing_decisions':702,'ordinary_qualified':936,
            'accepted_additional_gains':251,'certified_contractions':559,
            'original_frozen_independent_audit':{'unique_actions':157,'evaluations':467,
              'contained':850,'unresolved_containment':86,'accepted_gain_confirmed':193,
              'unresolved_gain_claims':58,'contradictions':0,'terminal_contexts':52195,
              'seconds':independent['seconds'],'maximum_bins':128},
            'by_mode':dict(bymode),'sufficient_neural_regions_nonempty':0,
            'optimistic_neural_regions_nonempty':128,'neural_region_scenarios':128,
            'complete_primary_parent_allocated_seconds':{
                m:row['complete_primary_parent_allocated_seconds'] for m,row in mode_details.items()},
            'warm_adaptive_versus_warm_fixed512':{
                'fraction_fewer_extra_terminal_contexts':str(work_reduction),
                'fraction_more_complete_primary_elapsed':str(time_increase),
                'paired_comparison':descriptive['warm_fixed_paired_comparison']},
            'first_state_enhancement_queries_by_mode':{
                m:row['first_state_enhancement_queries'] for m,row in mode_details.items()},
            'first_state_repeat_scope':'All 58 fused prefixes already meet the stronger target; the four prefix-based modes make zero enhancement queries. These repeats cannot establish acquisition-runtime superiority.',
            'exact_recorded_work_accounting':{'all_match':True,'rows':696},
            'complete_timing_parent_receipts':timing_parents,
            'inputs_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},
            'scope':'Completed original F125 experiment and original capped independent audit. Any later follow-up retains a separate public source identity and never replaces these outcomes.'}

EVIDENCE=load_completed_evidence()

def load_followup_and_postexecution():
    followup_names=['POSTFREEZE_AUDIT_BOUNDARY125.json','POSTFREEZE_AUDIT_FREEZE125.json',
        'results125/independent-followup512/SUMMARY125.json',
        'results125/independent-followup512/EXECUTION125.json',
        'results125/launch-independent-followup512/PROCESS125.json',
        'provenance/FOLLOWUP_CHRONOLOGY_REVIEW125.json','provenance/FOLLOWUP_RESULT_REVIEW125.json',
        'results125/followup-presentation/RECONCILIATION125.json',
        'results125/followup-presentation/EXECUTION125.json',
        'results125/followup-presentation/COMPLETION125.json']
    post_names=['results125/ADOPTION_SUPPORT_DIAGNOSTIC125.json',
        'results125/ADOPTION_BLOCKER_COMPARABILITY125.json',
        'results125/BALANCED_WEIGHTING125.json','results125/SAVED_CLOCK_PROFILE125.json',
        'provenance/IDENTITY_ADOPTION_REVIEW125.json','new125/identity_adoption125.tex']
    if not all((ROOT/n).exists() for n in followup_names+post_names):return None,None
    read=lambda n:json.loads((ROOT/n).read_bytes())
    summary=read(followup_names[2]);execution=read(followup_names[3]);parent=read(followup_names[4])
    assert execution['status']=='executed' and execution['exit_code']==parent['returncode']==0
    assert (summary['contained'],summary['accepted_gain_confirmed'],summary['contradictions'])==(934,251,0)
    assert (summary['initial_contained'],summary['initial_accepted_gain_confirmed'])==(850,193)
    assert summary['initial_audit_unchanged'] and summary['new_unique_actions']==110
    assert summary['source_boundary']==read(followup_names[0])
    assert summary['source_boundary']['source_commit']=='a5f2047222751217b9660b241b9e63f36d87c53a'
    assert summary['source_boundary']['manifest_sha256']==hashlib.sha256((ROOT/followup_names[1]).read_bytes()).hexdigest()
    assert summary['counts']['terminal_contexts']+summary['counts']['reused_independent_terminal_contexts']==112750
    followup=dict(summary,child_seconds=execution['seconds'],parent_seconds=parent['seconds'],
        peak_rss_kib=parent['peak_child_rss_kib'],
        inputs_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in followup_names})
    identity=read(post_names[0]);comparability=read(post_names[1]);balance=read(post_names[2]);clocks=read(post_names[3])
    assert identity['status']=='executed' and identity['identity_blocked_positive_price_scenarios']==128
    assert identity['original_classifications_unchanged'] and identity['economic_evaluations']==identity['services_retimed']==0
    assert comparability['selected_blocker_roles']=={'online':64,'poly2':64}
    assert comparability['matching_counts']['same_acquired_training_label_digest']==32
    assert comparability['matching_counts']['same_budget_and_fitting_loss']==16
    assert comparability['matching_counts']['same_feature_dictionary']==0
    for document in (identity,comparability,balance,clocks):
        assert document['status']=='executed' and document['economic_evaluations']==0
    for row in clocks['rows']:
        assert sum(Fraction(row[k]) for k in ('prefix_seconds','query_and_gradient_recovery_seconds',
            'remaining_service_seconds','cohort_and_parent_residual_seconds'))==Fraction(row['complete_primary_parent_allocated_seconds'])
    post={'identity_diagnostic':identity,'comparability':comparability,'balanced_weighting':balance,
          'saved_clock_profile':clocks,'scope':'Post-execution deductions from saved records, with zero new economics or re-timing; frozen experimental classifications remain unchanged.',
          'inputs_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in post_names}}
    return followup,post

FOLLOWUP,POSTEXEC=load_followup_and_postexecution()

# Each addition is deliberately bounded to an actual mathematical amendment or
# the published design. Outcome integration is a separate, evidence-bound step.
A={
'B1':(
 'We retain the original NBO continuation critic, feasible actor, recursive Bellman target and economic decision problem. Theorem fullinterpolation125 gives an exact finite convex representation of the information in every paid original quadratic support, including an uncertain but globally valid supporting slope. This closes the explicit raw-support omission in the R124 information class. Theorem paidwork125 links original support precision to feasible action localization, its declared work bound and a separate returned-policy gate. Both mechanisms are available to every representation under the same information. The R125 protocol retains all 56 original actors and the exactly matched ordinary-hinge control.',
 'Neural-specific economic or information superiority remains unestablished. The support-complete program has not been implemented in the production R125 service census. A strict analytic witness demonstrates lost information, but cheap direct support evaluation attains its improvement. Neither that witness nor a shared decision safeguard establishes an advantage over an equally informed conventional method.',
 ['sec:core49','sec:construction49','sec:fullsupport125','sec:paidresolution125','sec:experiment125']),
'B2':(
 'Theorem fullinterpolation125 identifies the exact worst compatible action contrast for a fixed pair under a scalar, smooth strongly convex, complete-support information interface. It explicitly excludes additional economic formulas unless encoded. The support inequalities are convex bounded-domain conjugate constraints; necessity, constructive sufficiency, compactness, degenerate cases and rational residual certification are proved. The terminal bracket proposition separately gives a matching randomized-action minimax result for its reduced stationary-bracket interface.',
 'These exact local information results are not end-to-end Bellman complexity lower bounds. Randomized acquisition, multivariate innovations, arbitrary derivative oracles, nonuniform laws and uniform extreme-tail constants require additional adversarial classes and matching algorithms. The conditional power-law oracle premise in paidwork125 is not inferred from observed runtime.',
 ['sec:fullsupport125','sec:paidresolution125','sec:discussion125']),
'B3':(
 'The new optimized quantity is the original action contrast q(b)-q(a), followed by the explicit implemented-future allowance and the original regret and objective-width gates. It is therefore a decision quantity. The exact witness changes the worst compatible contrast from -1/4 to -5/8 when a previously discarded support is retained, and states exactly which conventional calculation already achieves the same result. No new neural representation separation is claimed.',
 'A neural-versus-conventional policy or service-work separation with equal features, information, feasible policies and full costs still requires evidence. The current representation-neutral certificate cannot supply that separation merely because a neural actor provides the incumbent.',
 ['sec:fullsupport125','sec:supportaction122','sec:experiment125']),
'B4':(
 'We preserve the R97 result that residual span improved in all 36 cells while aggregate rejections rose from 644 to 757. The new complete-support objective controls a worst compatible original action contrast directly. The acquisition theorem specifies finite feasible support radii, required level and slope precision, a guaranteed optimizer-width contraction and the independent absolute-value gate. The prospective operational census records strong-target attainment, accepted changes, rejection and stopping outcomes and complete work.',
 'This is a post-acquisition decision and information mechanism. It is not a theorem that the old span-training loss, or any newly trained neural loss, controls expected service cost. The production census tests the frozen adaptive localization service, not a conic solver implementing the new complete-support program. Any empirical claim must distinguish those objects.',
 ['sec:fullsupport125','sec:paidresolution125','sec:results125']),
'B5':(
 'Quadratic least squares remains the recorded R97 complete-work winner. R125 preserves all original acquisition bills and compares seven stored representations, online original-model controls and a 33-action dynamic-programming control specified for fresh original-model evaluation. The four prefix-based services pay their completed strong fused prefixes, rejected candidates, discarded precision levels and fallbacks; the grid control pays its full action scan, refinements and any required fallback. The reporting protocol adds load, serialization, bookkeeping and parent-clock allocation to the recorded service cost.',
 'The experimental complete-work frontier can be stated only from the completed R125 evidence. Historical interrupted parent costs remain unknown. Three shared-host timing observations are descriptive brackets, and the ideal work-bound-minimizing schedule is not the executed finite ladder. No unmeasured neural speedup or universal cost advantage is inferred.',
 ['sec:experiment125','sec:results125','sec:discussion125']),
'B6':(
 'The R125 design keeps the same continuous-risk investment primitives, constrained decisions and implemented future controller. Its adoption calculations use the first-state workload for which the timing observations were collected, the full traditional comparator menu, original policy-value intervals and explicit acquisition amortization. Sufficient and optimistic regions are separate. Proposition policyidentity125 proves that equality of complete realized policies implies equality of the original recursive objective; a strict complete-cost ordering then excludes positive compute prices for the more costly service, conditional on the declared timing ranges. This post-execution deduction preserves the frozen price-region classifications.',
 'Compute prices, workload volumes and willingness to pay are declared scenarios, not identified economic parameters. The four deterministic states are not a field population. A calibrated consequential application remains a substantive research obligation; conditional price regions cannot establish field adoption or neural superiority.',
 ['sec:continuous95','sec:experiment125','sec:results125','sec:policyidentity125','sec:discussion125']),
'B7':(
 'The R97 actors retain their own identities; R96 intervals are not transferred to them. The R125 census uses four predetermined dyadic states and reports deterministic original-model bounds for those states. It makes no population-mean claim and creates no confidence interval from timing repetitions. The later R124-B experiment remains a separate protected source/state/execution identity and supplies no substitute outcome to R125.',
 'Direct population ordering for the new R97 actors remains unsupported by the R96 intervals. The R125 deterministic census also does not close that population-inference request. Any new population claim requires its own sampling law, actor freeze, prospective source and independent execution.',
 ['sec:experiment125','sec:results125','sec:discussion125']),
'B8':(
 'R125 freezes and reuses all 56 actual M121 actor files, with their original features and acquisition bills. It performs no new fitting. Its separate rational economic evaluator is specified to audit every distinct final and prefix action using original primitives and a fixed precision ladder and global cap. Independently implemented Fraction diagnostics test the new interpolation construction without importing the production solver.',
 'Saved actor custody, exact certificate algebra, independent economic evaluation and independent fitting are distinct. R125 does not independently reproduce feature selection, interval-aware fitting, rounding, whole-domain fitting validation and serialization for the R97 acquisition stack. Unresolved capped economic checks must remain unresolved.',
 ['sec:experiment125','sec:results125','supp:fullsupport125']),
'B9':(
 'The new main text is organized around the original recursive economic problem, the complete-support information theorem, its acquisition implications and the current prospective comparison. The full mathematical supplement and development companion retain the earlier proofs, corrections, failures and negative outcomes. A new source census pins all 366 original branch heads and separates the complete R122 manuscript from later R123/R124 research states.',
 'Presentation and a clean source/PDF build do not resolve novelty, neural specificity, scaling or consequential economics. Final document lengths and cross-references are taken from the actual R125 build receipt. Historical preservation remains extensive but does not determine which claims are active.',
 ['sec:introduction125','sec:fullsupport125','sec:experiment125','dev:revision125','dev:retained122']),
'B10':(
 'The residual-versus-decision mismatch determines the revision priority. We add an exact action-contrast information program and a finite support-precision/work theorem. The latter distinguishes optimizer localization, original regret, absolute policy-value width and strict same-future policy improvement. This prevents a reduction in internal fit or optimizer width from being called a delivered economic gain.',
 'These results advance the original NBO research program without declaring its neural-specific objective complete. Competitive acquisition, a production complete-support solver and a decision-aligned training theorem remain distinct tasks. Negative outcomes and gains against a method\'s own incumbent cannot establish comparative superiority.',
 ['sec:fullsupport125','sec:paidresolution125','sec:results125','sec:discussion125']),
'M1':(
 'The manuscript remains Neural Bellman Operators and retains the Econometrica numerical-methods aim. The economic question is how learned continuation values and feasible actor proposals can deliver better original recursive decisions with defensible complete costs. The new mathematics isolates the information and certification operations shared with conventional representations, so the neural contribution is tested rather than assumed.',
 'The reviewer\'s proposed change of research topic or venue is not adopted. Mathematical validity of a shared safeguard and an independently established neural advantage remain separate scientific questions. The original objective, information set and model are not changed to manufacture a favorable comparison.',
 ['sec:introduction125','sec:core49','sec:construction49','sec:discussion125']),
'M2':(
 'The new proof identifies the specific extension beyond smooth convex interpolation and R124: all original quadratic supports are retained through exact node-conjugate inequalities and a constructive global interpolant. It distinguishes the shared-slope lifting from the equivalent full pointwise robust obstacle. The R123 midpoint theorem, the R124 residual certificate and the inherited fixed-alpha value-oracle rate remain attributed to their prior sources.',
 'The finite contrast program is exact for the stated scalar record, not a universal information-complexity theorem. The new stationary-bracket randomized-action lower bound is likewise scoped to its reduced interface. A broader randomized or multidimensional Bellman acquisition lower bound remains open.',
 ['sec:fullsupport125','sec:paidresolution125','dev:inherited123124']),
'M3':(
 'The new action objective is the largest compatible original contrast, and its support-complete feasible set is exact. The acquisition theorem gives a finite-radius precision requirement and, conditional on a separately verified oracle-cost bound, an optimal guaranteed-width schedule for that declared planning problem. The frozen census compares warm adaptive, cold adaptive and fixed-precision acquisition against a fully paid strong fused control, with a stronger original-regret target stated in advance.',
 'The executed finite ladder is not the theorem\'s ideal schedule, and the full conic program is not the production service. Actual prospective outcomes are evaluated separately from those idealized objects. A learned loss with a proved expected rejection or complete-work guarantee under a context law remains to be developed and independently validated.',
 ['sec:fullsupport125','sec:paidresolution125','sec:experiment125','sec:results125']),
'M4':(
 'R125 retains quadratic, degree-two and degree-three polynomial, spline, grid, ReLU and the exact ordinary-hinge realization, together with online controls and a 33-action original-model DP control. Every stored actor receives the same four service rules and target gates. The matched hinge inherits the actual parent ReLU acquisition cost where required, so equal geometry does not create a fictitious free comparator or a fictitious neural feature advantage.',
 'This fixed menu is not an exhaustive conventional frontier. Adaptive triangulation, convex regression, other basis-selection rules and tuned model-specific algorithms require a separately designed comparison. They cannot be added or removed after observing this experiment\'s outcomes.',
 ['sec:construction49','sec:experiment125','sec:results125']),
'M5':(
 'R97\'s 36/36 span reductions, rejection increase, quadratic work victory and zero adopted neural regions remain visible and source-bound. Later negative acquisition and full-menu outcomes remain attached to their own campaign identities. Current reporting separates accepted same-incumbent gains, stronger-target attainment, action errors, service work and comparative purchase conditions.',
 'Neither favorable internal diagnostics nor a safe local replacement erase an earlier comparative failure. The new results must be interpreted against the full traditional menu and their original economic target. Negative evidence guides further algorithm design without being relabeled as completion of the neural objective.',
 ['sec:results125','sec:discussion125','dev:retained122']),
'M6':(
 'The investment economy remains an actual constrained recursive decision problem with continuous innovations, nested AVaR, original objective values, regret and computation bills. The new theorem explains when original information can license an economically meaningful action change, and the protocol keeps monetary computation scenarios separate from observed policy-value bounds. The post-execution Proposition policyidentity125 couples equal complete policies before comparing their costs, rather than treating their objective intervals as independent unknown values.',
 'No new calibrated field application is supplied by R125. Empirical identification, economically justified policy margins, market compute prices, fees and actual workload demand remain required for consequential adoption. The NBO research ambition is retained while those uncompleted claims remain explicit.',
 ['sec:continuous95','sec:experiment125','sec:policyidentity125','sec:discussion125']),
'M7':(
 'The R125 study varies representation, original risk level, information budget and service precision strategy within the same economy. It records requested terminal contexts, actual operation counters, all refinement and fallback work, and the implemented stopping outcomes. The theory distinguishes scalar action information from unrestricted Bellman complexity.',
 'Horizon, number of controls and innovation dimension are not varied in this census. Amortization over deployment volumes is not a scaling experiment. Genuine multidimensional and longer-horizon competitiveness remains open and requires matched strong conventional algorithms and a new prospective design.',
 ['sec:experiment125','sec:results125','sec:discussion125']),
'M8':(
 'The frozen protocol specifies exactly three serial timing processes, all 234 service cohorts on the same first state, deterministic cohort-order rotation and one-thread numerical settings. It requires action, certificate, stopping and operation identity against the primary first-state decisions, retains every timing, records parent and child clocks and charges parent residuals.',
 'Processor frequency and shared-host load are uncontrolled. Three observed times do not support a probabilistic deployment-clock claim. Operation counts and scope-matched clock brackets must remain primary, and missing historical interrupted clocks stay unknown rather than zero.',
 ['sec:experiment125','sec:results125']),
'M9':(
 'The prospective R125 source manifest includes scientific code, public frozen dependencies and all 56 actor files. A remote source readback gate precedes economics. The independent evaluator uses the separately implemented rational original primitives; replay, mathematical fixtures, actual economics, source verification and CI each retain their own status and receipt.',
 'R125 is not an independent refit of the original acquisition stack. A reproducible artifact does not prove every historical scientific claim or external acceptance. CI success is reported only after a real completed run, and source-freeze corrections, if needed, require a distinct public boundary.',
 ['sec:experiment125','dev:revision125','dev:inherited123124']),
'M10':(
 'The active article presents the economic operator, current complete-support and acquisition results, the matched original-model comparison and supported economic interpretation. The supplement contains complete proofs; the development companion retains historical material, including the original 620 major-response blocks and additional inherited item responses. All 35 genuine report bodies and their manifests are preserved.',
 'Editorial compression cannot substitute for mathematical or numerical improvement. Exact final page counts and cross-reference status belong to the completed R125 build. The historical route catalogue records treatment and remaining obligations, not hundreds of independent issue closures.',
 ['sec:introduction125','sec:fullsupport125','sec:experiment125','dev:revision125','dev:retained122']),
'Minor 1':(
 'The inherited N^{-2} statement is described as an error-versus-information rate. The new complete-support program instead gives an exact finite-record contrast bound, and the work theorem has a conditional exponent p fixed by its stated oracle premise.',
 'These are different objects and units. Neither the inherited error rate nor a fitted runtime exponent may be transferred to the other interface.',
 ['sec:fullsupport125','sec:paidresolution125','sec:discussion125']),
'Minor 2':(
 'Every current summary of the inherited lower-bound rate retains its deterministic, point-value, univariate, fixed-alpha qualifications. The separate new randomized-action bracket statement gives its own information class explicitly.',
 'The new local statement does not remove the inherited lower bound\'s qualifications or establish general randomized acquisition complexity.',
 ['sec:discussion125','sec:paidresolution125']),
'Minor 3':(
 'The inherited fixed-alpha result and its differing upper and lower tail constants remain in the retained information discussion. R125 continues to use the two predeclared original risk levels 1/2 and 3/4 and does not infer behavior as alpha tends to one.',
 'A tail-uniform matching rate or extreme-tail numerical performance remains unproved. The support theorem\'s action curvature assumptions do not by themselves establish such a result.',
 ['sec:continuous95','sec:discussion125','dev:retained122']),
'Minor 4':(
 'All inherited fitted actors, coefficient restrictions and acquisition bills remain frozen. The new finite value/gradient boxes are derived from valid original bounds and a derivative cap; they are not outcome-tuned representation restrictions. The source explicitly separates the exact information class from additional unencoded model formulas.',
 'R125 adds no new coefficient-box sensitivity experiment or claim of globally best approximation. Sensitivity that changes acquisition or selected actors requires a separate prospective downstream comparison.',
 ['sec:regularity122','sec:fullsupport125','sec:experiment125']),
'Minor 5':(
 'Residual span, original action contrast, optimizer bracket, original regret and absolute implemented-policy interval width are separate quantities throughout the new theorems and service protocol. An upper contrast must still include the unchanged future-controller allowance before an action is accepted.',
 'A narrow optimizer bracket, improved fit or small residual does not alone supply the absolute policy-value certificate, strict same-future gain or comparative economic superiority.',
 ['sec:fullsupport125','sec:paidresolution125','sec:results125']),
'Minor 6':(
 'The historical 36/36 span improvement is stated together with the rejection increase from 644 to 757. The new protocol reports action acceptance, failed precision and stopping outcomes with the costs that produced them.',
 'No method is declared better from a span reduction alone. Current comparisons require the original regret/width gates and complete workload outcomes.',
 ['sec:results125','dev:retained122']),
'Minor 7':(
 'The minimum and maximum of the three R125 times are labeled descriptive shared-host timing brackets. The four-state census is deterministic and no confidence interval is constructed from these repeats.',
 'Engineering ranges, historical component allocations and unknown interrupted-process costs are not statistical intervals or measured whole-history totals.',
 ['sec:experiment125','sec:results125']),
'Minor 8':(
 'The zero R97 neural adoption count over quadratic least squares is retained explicitly with its original 1,800-cell sensitivity scope. R125 defines its own full-menu sufficient and optimistic comparisons on a matching first-state workload and does not transplant older regions into the new experiment. The separate post-execution Proposition policyidentity125 establishes the stronger conditional exclusion available when actual complete-policy equality and strictly lower conventional complete costs are known.',
 'The conditional identity-cost exclusion is specific to the recorded first-state services and timing ranges. It does not establish population dominance, future-runtime guarantees or equal-feature neural representation inferiority. The original interval-only optimistic classifications remain unchanged as outer relaxations.',
 ['sec:results125','sec:policyidentity125','sec:discussion125','dev:retained122']),
'Minor 9':(
 'The complete-support theorem is placed in relation to smooth convex interpolation and the inherited verified Bellman/HJB literature. Its contribution is the exact finite retention of the original global support payload and its action-contrast interpretation, with a constructive proof and a rational residual correction. The stochastic-control and nonlinear-recursive bridges retain their own assumptions.',
 'The new scalar theorem does not validate arbitrary learned HJB/FBSDE residuals or transfer welfare claims between different objectives and models. A production computational comparison of the complete-support solver remains to be supplied.',
 ['sec:fullsupport125','sec:discussion125','dev:retained122']),
'Minor 10':(
 'The title retains Neural Bellman Operators, as the original learned recursive-operator research identity requires. The text states which theorems are shared with conventional representations and which comparisons would be needed to establish neural-specific value.',
 'The title is not evidence of neural superiority. That claim remains subject to equal information, features, feasible policies, complete costs and original economic outcomes.',
 ['sec:introduction125','sec:construction49','sec:discussion125']),
}

NUMERIC_ADDITIONS={
'B1':'The executed census has 936 primary decisions and 702 timed decisions. All 128 matched ReLU/hinge identities pass, and none of the 128 first-state full-menu sufficient neural adoption regions is nonempty. Thus the observed service improvement does not establish neural-specific superiority.',
'B2':'The completed census records 559 certified contractions, with 37,557 extra requested terminal contexts for warm adaptive acquisition, 73,015 for cold adaptive acquisition and 181,425 for fixed-512 warm acquisition. These are observed operation counts in this scalar economy, not a measured asymptotic exponent or a universal oracle lower bound.',
'B3':'The operational census accepts 251 additional strict same-future action changes. The independently implemented original audit directly confirms 193 of those gain bounds; 58 remain unresolved at its frozen maximum precision, with no contradiction. The analytic support witness and these production-service outcomes remain separate forms of evidence.',
'B4':'The frozen stronger-target count rises from 147/232 for the fully paid fused control to 231/232 for warm adaptive acquisition, at the same original service requirements. A separate post-freeze saved-support diagnosis identifies a capacity action already known to be optimal although its stored value-level regret bound misses the stronger target. That analytic diagnosis leaves the recorded 231/232 count unchanged and reports no new policy gain.',
'B5':'The completed four-state census obtains 231/232 stronger-target successes with warm adaptive acquisition and 231/232 with warm fixed-512 acquisition, using 37,557 versus 181,425 extra requested terminal contexts. Warm adaptive requests 79.30 percent fewer contexts but makes 309 rather than 177 extra query attempts and takes 15.03145 rather than 13.37580 seconds of complete primary parent-allocated service time, 12.38 percent more. All 58 first-state prefixes already satisfy the stronger target, so the three prescribed repeats make zero enhancement queries in these modes and cannot establish acquisition-runtime superiority. All 128 full-menu sufficient neural adoption regions are empty. The new result is improved action resolution and fewer requested contexts, accompanied by a measured runtime loss against fixed precision.',
'B6':'All 128 originally computed sufficient neural price regions are empty; all 128 original interval-only optimistic outer regions remain nonempty. Their separate value boxes do not encode the known equality of the realized policies. These original classifications are preserved separately from the stronger post-execution identity deduction, the older R97 zero count and any population inference.',
'B7':'The executed study retains all 936 predetermined primary decisions and all 702 timing repeats. It creates zero independent population samples. The independent evaluator audits 157 distinct realized state/risk/action keys from the final and prefix decisions; it does not make those four deterministic states into a population sample.',
'B8':'The original independent audit completed 467 original-policy evaluations for 157 distinct state/risk/action keys, using 52,195 terminal contexts, 1,515,424 terminal bisection iterations and 419,430 assertions. It confirms 850/936 reported interval containments and 193/251 accepted gain bounds; 86 and 58 remain unresolved, respectively, at the frozen 128-bin maximum. There are zero contradictions. Completion of that capped audit is not complete confirmation of all claims and is not independent fitting.',
'B9':'The original F125 source was remotely read back before the first economic evaluation. The complete numerical census, timing passes, exact fixtures, replay and capped independent reconstruction now have actual receipts. Their distinct roles are preserved in the active results and the development companion.',
'B10':'The executed method resolves the stronger original-regret target in 231/232 warm-adaptive decisions compared with 147/232 for the strong completed control, while preserving every ordinary-qualified decision. The post-freeze singleton diagnosis shows why a loose value-level certificate can still misclassify an already optimal action. It motivates a separately prospective gate improvement and does not retroactively change the frozen experiment.',
'M1':'The current result improves original-action resolution under the same economy and unchanged controller. Exact neural/hinge equality and zero certified neural purchase regions remain visible, so a shared mathematical contribution is not attributed exclusively to the neural representation.',
'M2':'The independent rational interpolation diagnostic passes 4,080 support cases, and the separately frozen mathematical fixtures execute 266 checks. Those finite diagnostics support the stated construction and witnesses; they are not an information-complexity experiment or a substitute for the complete proof.',
'M3':'The prospective census now reports 251 accepted additional gains, 559 certified contractions and the complete warm/cold/fixed-precision operation counts. Original independent reconstruction confirms 193 gain claims and leaves 58 unresolved at its predetermined cap. A later analytic terminal-gate diagnosis is explicitly post-freeze and changes no experimental target or success count.',
'M4':'All 234 service cohorts were executed, including every stored actor, the online controls and the original-model grid control. The latter attains the stronger target in 6/8 decisions after 83,216 requested terminal contexts; its full costs and fallback remain in the report. All 128 ReLU/hinge output identity checks pass.',
'M5':'The new negative comparative finding is equally explicit: 0/128 sufficient neural adoption regions are nonempty even though the adaptive service improves action resolution and accepts safe own-incumbent changes. The 86 unresolved original-audit containments and 58 unresolved gain checks are retained alongside the zero contradictions.',
'M6':'The completed study provides original objective intervals, certified regret and complete first-state price comparisons, but its sufficient neural adoption regions are empty and its economic setting remains uncalibrated. The actual action-resolution improvement does not substitute for a consequential field application.',
'M7':'The actual experiment contains 936 primary and 702 timed decisions in the same two-state, scalar-control economy. Its 375,213 extra requested terminal contexts and per-service operation ledgers document this workload; they are not observations of additional dimensions or horizons.',
'M8':'All three prescribed timing passes completed with 234 first-state decisions each. Saved-algebra/timing replay performed 16,162 checks, and a separate exact accounting replay matches all 696 enhancement-decision counter deltas. The complete primary child ran for 69.988865 seconds and the three complete timing parents took approximately 6.5493, 6.6966 and 7.5240 seconds. Every first-state prefix already meets the stronger target, so the four prefix-based modes perform zero enhancement queries in those repeats; these timings do not measure the cost of additional localization. In the complete primary census warm adaptive instead takes 12.38 percent more parent-allocated time than fixed-512. The independent original audit cost a separate 798.411727 seconds and is charged separately from deployed services.',
'M9':'The F125 source boundary is a94e1f43bf64d8cb90af21e4b53d07335c615576. The completed exact replay and independent original audit have separate receipts, with the original capped audit retaining 86 unresolved containment and 58 unresolved gain checks. The separate follow-up is reported under its own actual source and execution receipts. None of these checks grants an advance success status to CI or a later experiment.',
'M10':'The current main/supplement and separate development companion now reference the actual completed experiment and the original capped audit, including unresolved checks and the zero sufficient adoption count. The historical record is preserved in its own source-bound routes rather than used to inflate current evidence.',
'Minor 1':'The reported 559 contractions and observed requested-context totals are finite execution statistics, not estimates of the inherited error-versus-information exponent.',
'Minor 2':'The new executed data do not add randomized acquisition or high-dimensional evidence to the inherited lower bound; the only randomization minimax statement is the separately scoped analytic terminal-bracket result.',
'Minor 3':'The completed numerical census uses only the predeclared risk levels 1/2 and 3/4; it supplies no new extreme-tail limit evidence.',
'Minor 4':'All 56 original actor files were used without refitting or coefficient-box changes. The actual completed comparison therefore does not add a new coefficient-restriction sensitivity study.',
'Minor 5':'The observed singleton-capacity case is explicit: exact original-action localization implies a post-freeze analytic regret bound no larger than delta for the unchanged action, while the frozen value-level gate records a stronger-target miss. Its original recorded classification remains a miss; the sharper analytic bound is reported separately.',
'Minor 6':'Current reports retain 251 additional accepted changes, all 936 ordinary-qualified decisions, the per-mode stronger-target misses and every paid rejected/refined query. These are original-action outcomes, not a renamed residual-span score.',
'Minor 7':'All 702 timing decisions are preserved. The three observed complete-parent times and the per-cohort minimum/maximum brackets remain descriptive, and the four-state study produces no sampling confidence interval. Because all first-state prefixes already satisfy the stronger target, the prescribed repeats perform zero enhancement queries in the four prefix-based modes and cannot be used to claim acquisition-runtime superiority.',
'Minor 8':'The original R125 classifications remain 0/128 nonempty sufficient regions and 128/128 nonempty interval-only optimistic outer regions under the declared traditional menu. Those outer classifications alone do not exclude adoption; the separate policy-identity deduction supplies a stronger conditional conclusion for this first-state workload.',
'Minor 9':'The executed original-economy study uses the frozen localization implementation. It does not execute the newly proved conic information program, and the separate exact fixtures are not a verified HJB/FBSDE computation.',
'Minor 10':'The completed evidence preserves exact neural/hinge identities and zero sufficient neural adoption regions. Retaining the original research title does not change that comparative result.'
}

FOLLOWUP_TEXT=(
 'A separately published 512-bin follow-up at source a5f2047222751217b9660b241b9e63f36d87c53a '
 'then evaluated every one of the 110 unresolved final/prefix keys. It confirms 934/936 interval '
 'containments and all 251/251 accepted gain bounds, with zero contradictions. The two remaining '
 'containments are the original-model grid decisions at risk 1/2 and states (3/4,1/4) and (3/4,3/4); '
 'they remain unresolved at the separately frozen cap. The original 850/936 and 193/251 outcomes '
 'remain unchanged. This follow-up changes no production policy and supplies no new population sample.')
IDENTITY_TEXT=(
 'A distinct post-execution saved-record deduction applies Proposition policyidentity125. All 128 '
 'neural/workload scenarios have a conventional service with the exact same first action and complete '
 'implemented continuation policy, hence the same original objective, and with a strictly smaller '
 'upper complete cost than the neural lower complete cost. Conditional on the recorded timing ranges, '
 'each neural service is therefore strictly dominated for every positive compute price; zero price '
 'gives a tie with that comparator only, not global optimality against different policies. The 128 '
 'original nonempty optimistic outer regions remain unchanged. The selected blockers are 64 online '
 'and 64 degree-two polynomial services: 32 share stored acquired-training-label digests, 16 also '
 'match both budget and fitting-loss labels, and none shares the neural feature dictionary. '
 'Historical raw training-label bytes were not rehashed in this diagnostic. This is a conditional '
 'complete-service comparison, not a general equal-information or equal-feature representation result. '
 'No economic evaluation or timing repetition was added.')
FOLLOWUP_KEYS={'B1','B3','B5','B7','B8','B9','B10','M3','M5','M8','M9','M10','Minor 6'}
IDENTITY_KEYS={'B1','B3','B5','B6','B10','M1','M4','M5','M6','M9','M10','Minor 8','Minor 10'}
SAVED_CLOCK_TEXT=(
 'A reporting-only replay of saved clocks separates warm-adaptive prefix, query/recovery, remaining '
 'service and cohort/parent residual times as 5.631801, 3.195700, 5.469696 and 0.734253 seconds; '
 'fixed-512 gives 5.745743, 5.348735, 1.563042 and 0.718276 seconds. These sum exactly to their '
 'complete primary allocations. The remaining-service bucket includes setup, ledger reconstruction, '
 'bounds, candidate selection and bookkeeping, not just algebra. This explains the observed cost '
 'composition without claiming a controlled causal decomposition or performing re-timing. '
 'The descriptive economic means use the same one-eighth weight for each risk/state cell.')

def exact_request(r):
    lines=[]
    for line in r['exact_request_as_retained_in_r122'].splitlines():
        line=re.sub(r'^>\s?', '', line)
        if not line.startswith('### '):lines.append(line)
    return '\n'.join(lines).strip()

def tex(s):
    # Quote source text faithfully in plain text, avoiding interpretation of
    # Markdown/code metacharacters as LaTeX commands.
    special={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    out=''.join(special.get(c,c) for c in s)
    return out.replace('–','--').replace('—','---').replace('“','``').replace('”',"''").replace('’',"'").replace('`',"'")

def author_tex(s):
    t=tex(s)
    t=t.replace('Theorem fullinterpolation125',r'Theorem~\ref{thm:fullinterpolation125}')
    t=t.replace('Theorem paidwork125',r'Theorem~\ref{thm:paidwork125}')
    t=t.replace('in paidwork125',r'in Theorem~\ref{thm:paidwork125}')
    t=t.replace('The terminal bracket proposition',r'Proposition~\ref{prop:terminalminimax125}')
    t=t.replace('Proposition policyidentity125',r'Proposition~\ref{prop:policyidentity125}')
    return t

report=ROOT/'provenance/review_sources/2026-10-14-econometrica-numerical-methods-r97/referee_report.md'
original=report.read_text()
records=[]
for old in prior['request_records']:
    key=old['request_id'];request=exact_request(old)
    assert request in original, f'Exact original request mismatch: {key}'
    action,remaining,routes=A[key]
    records.append({
      'request_id':key,'title':old['title'],'exact_original_request':request,
      'exact_request_sha256':hashlib.sha256(request.encode()).hexdigest(),
      'r125_author_amendment':action,'r125_remaining_scientific_requirement':remaining,
      'current_chapter_labels':routes,
      'previous_r122_action':old['r122_author_action'],
      'previous_r122_remaining_requirement':old['r122_explicitly_remaining_science'],
      'closure_claim':False,
      'status':'amended_with_separately_bound_original_followup_and_postexecution_evidence_and_explicit_residual_obligation' if FOLLOWUP and POSTEXEC else 'amended_with_completed_original_evidence_and_explicit_residual_obligation' if EVIDENCE else 'substantive_amendment_or_preservation_with_explicit_open_requirement',
      'executed_r125_evidence':NUMERIC_ADDITIONS[key] if EVIDENCE else None,
      'separately_frozen_followup_evidence':FOLLOWUP_TEXT if FOLLOWUP and key in FOLLOWUP_KEYS else None,
      'post_execution_policy_identity_evidence':IDENTITY_TEXT if POSTEXEC and key in IDENTITY_KEYS else None,
      'saved_work_accounting_evidence':SAVED_CLOCK_TEXT if POSTEXEC and key in {'B5','M8'} else None,
    })
out={
 'schema':'r125-current-request-response-v1',
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'role':'Author response and exact request mapping; not a new external referee report',
 'controlling_report_commit':prior['controlling_report_commit'],
 'controlling_report_sha256':prior['controlling_report_sha256'],
 'exact_requests_verified_against_original_report':True,
 'records':records,
 'numerical_evidence_status_at_generation':'Original F125 audit remains 850/936 containments and 193/251 gains. Separately published and completed 512-bin follow-up confirms 934/936 containments and all 251 gains, with two unresolved containments and zero contradictions. Post-execution policy identity and complete-cost deductions conditionally exclude positive-price neural adoption in all 128 recorded first-state scenarios without changing the original outer-region classifications. None is a population, future-runtime, independent-refit or equal-feature representation claim.' if FOLLOWUP and POSTEXEC else 'Original F125 experiment and its frozen capped independent audit completed; incomplete containment/gain confirmation is explicitly retained. No later follow-up replaces those initial outcomes.' if EVIDENCE else 'Prospective protocol and source freeze exist; numerical outcomes are not inferred by this response. Integrate only completed source-bound execution receipts.',
 'completed_original_evidence':EVIDENCE,
 'completed_separately_frozen_followup':FOLLOWUP,
 'post_execution_saved_evidence_analysis':POSTEXEC,
 'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL125.md').read_bytes()).hexdigest(),
 'source_freeze_sha256':hashlib.sha256((ROOT/'SOURCE_FREEZE125.json').read_bytes()).hexdigest(),
 'actual_independent_mathematical_diagnostic':'provenance/OBSTACLE_INTERPOLATION_DIAGNOSTIC125.json',
}
(ROOT/'response_inputs/CURRENT_RESPONSE125.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
header=r'''% Exact current R97 requests and R125 author response.
% Generated by reporting125/build_response125.py from exact original requests
% and actual source-bound R125 execution receipts.
\section{Response to the controlling R97 advisory}
\label{response:current125}

This is an author revision of \emph{Neural Bellman Operators} for the
Econometrica numerical-methods objective. The controlling persisted report is
the repository-owner-commissioned R97 advisory at commit
\nolinkurl{9723c6cd2cc8b3e071422f3e522d4a843946db63}. It reviewed source
\nolinkurl{f802fe64d91d9f5c1c8f86123b0fbe114e622279}; it is not a journal
decision or a report on R122--R125. We preserve its exact 30 requests below,
the 35 genuine historical report bodies, and the earlier item responses.
R16 added no new report; R50 is a threshold screen. The original 366-head
source census, report identities and complete R122 baseline are bound in
the provenance files.

The new mathematical amendments are the exact support-complete action
information theorem and the finite precision/work account, with full proofs
and explicitly scoped terminal information bounds. The production numerical
study separately tests the frozen original-economy localization service; it
does not implement the complete-support conic program. The exact rational
interpolation diagnostic passed 4,080 support cases and the separate affine
edge cases. This is a mathematical diagnostic, not an economic experiment
or an external referee endorsement. Actual numerical results, independent
audit outcomes, failed executions, costs and final CI status are governed
by their own source-bound receipts and the current results section. No
item below is declared fully closed by a proof, source check or protocol
alone.

'''
parts=[header]
if EVIDENCE:
    parts.append(r'''\subsection{Completed original R125 execution and its limits}

The prospective scientific source is
\nolinkurl{a94e1f43bf64d8cb90af21e4b53d07335c615576}, read back remotely
before economic execution. All 936 primary and 702 timing decisions were
executed. Every primary decision meets the original service qualification;
251 additional strict same-future changes were accepted, and 559 bracket
contractions were verified. The frozen stronger-regret target is a separate
outcome:

\begin{center}\small
\begin{tabular}{lrrr}
\hline
Service & Stronger target & Extra contexts & Extra attempts\\
\hline
Fused control & 147/232 & 0 & 0\\
Warm adaptive & 231/232 & 37,557 & 309\\
Cold adaptive & 229/232 & 73,015 & 567\\
Warm fixed 512 & 231/232 & 181,425 & 177\\
Grid 33 & 6/8 & 83,216 & 272\\
\hline
\end{tabular}
\end{center}

Extra contexts count requested terminal midpoint/endpoint information;
they exclude neither failed precision levels nor discarded queries. They
are not the complete service cost: the four prefix-based services also pay
their original fused prefix, acquisition, actual operations and recorded
processing work. The grid control pays every action query, scan, refinement
and any required fallback in its own full service.
Warm adaptive requests 79.30\% fewer extra contexts than fixed 512 while
retaining the same target count. It nevertheless makes more query attempts
and takes 15.03145 rather than 13.37580 seconds of complete primary
parent-allocated service time, a 12.38\% runtime increase. All 58 first-state
prefixes already satisfy the stronger target, so the four prefix-based
modes make zero enhancement queries in the three timing repeats. These
repeats cannot establish acquisition-runtime superiority. The primary
runtime loss and this timing limitation remain part of the result.

The original independent audit completed all 157 distinct state/risk/action
keys from final and prefix decisions and 467 original-policy evaluations.
At its frozen maximum of
128 bins it directly confirms 850/936 interval containments and 193/251
accepted gain bounds. The remaining 86 containments and 58 gain checks
are unresolved; there are zero contradictions. Its 798.411727 seconds and
52,195 terminal contexts are retained as separate research costs.
Completion of this original capped audit is not complete independent
confirmation. Its outcomes are preserved unchanged alongside the separately
published follow-up described below.

All 128 originally computed sufficient first-state neural adoption regions
are empty; all 128 original interval-only optimistic outer regions remain
nonempty. These original calculations omit the coupling implied by equal
realized policies; the stronger post-execution deduction is reported
separately below. All 128 matched ReLU/hinge
identity checks pass. The four-state design is deterministic and supplies
no population confidence interval. The post-freeze singleton-capacity
diagnosis reports a sharper analytic regret bound for an unchanged action;
it changes neither the recorded 231/232 warm counts nor a measured policy gain.

''')
if FOLLOWUP:
    parts.append(r'''\subsection{Separately frozen and completed precision follow-up}

The follow-up scientific source is
\nolinkurl{a5f2047222751217b9660b241b9e63f36d87c53a}. Its distinct
manifest was frozen before remote readback at 07:52:04 UTC and child launch
at 07:52:25 UTC on October 23, 2026. It includes all 110 unresolved
final/prefix keys and ends at its declared 512-bin cap. The combined
original and refined intervals confirm 934/936 reported containments and
all 251/251 accepted gain bounds, with zero contradictions. Two containments
remain unresolved: the original-model grid decisions at risk $1/2$ and
states $(3/4,1/4)$ and $(3/4,3/4)$. No production policy, success flag,
original audit outcome or population sample was changed.

The follow-up requested 112,750 contexts: 84,480 newly evaluated contexts
and 28,270 exact reuses. It executed 2,586,336 terminal bisection iterations,
704,552 assertions and 9,020 duplicate-cache identity checks. Its child
time is 1,457.383213 seconds and its complete parent time is 1,459.236044
seconds; the 5.310521 seconds of cache loading are included in the child
time. Peak child resident memory is 229,796 KiB. These are additional
research verification costs. This separate follow-up confirms every
accepted gain bound while explicitly retaining the two unresolved
containments; it does not rewrite the original 128-bin results.

''')
if POSTEXEC:
    parts.append(r'''\subsection{Post-execution policy identity and purchase conditions}

Proposition~\ref{prop:policyidentity125} uses equality of the complete
implemented policy, on the queried state and all reachable continuation
histories, to identify the original recursive objective exactly. This
requires more than a common first action. The saved records establish both
identities for every selected comparator. In all 128 neural/workload
scenarios a conventional service has an upper complete cost strictly below
the neural lower complete cost. Conditional on the recorded timing ranges,
the neural priced objective is therefore strictly worse for every positive
compute price. At zero price it ties that same-policy comparator; this is
not a claim of global optimality against the different-policy grid control.

The original 128 nonempty optimistic outer regions remain unchanged as
uncoupled interval relaxations. The policy-identity deduction is a separate
post-execution analysis with no new economic evaluation or re-timing. The
128 selected blockers comprise 64 online and 64 degree-two polynomial
services. Thirty-two share stored acquired-training-label digests with
their neural comparators, sixteen match both acquisition budget and
fitting-loss labels, and none shares the neural feature dictionary. The
historical training-label byte streams were not materialized and rehashed
in this diagnostic. Equal economic information and complete policy do not
imply equal computational acquisition, fitting loss, features or all
subsequent oracle information. This is a conditional complete-service
comparison for the recorded first-state workload; no equal-feature
representation theorem, population ordering or future timing guarantee
is inferred.

''')
group=None
for r in records:
    g='Blocking concerns' if r['request_id'].startswith('B') else 'Major requested changes' if r['request_id'].startswith('M') and not r['request_id'].startswith('Minor') else 'Minor comments'
    if group!=g:parts.append('\\subsection{'+g+'}\n\n');group=g
    parts.append('\\subsubsection{'+tex(r['title'])+'}\n\n')
    parts.append('\\begin{quote}\\small\n'+tex(r['exact_original_request'])+'\n\\end{quote}\n\n')
    parts.append('\\noindent\\textbf{Author amendment.} '+author_tex(r['r125_author_amendment'])+'\n\n')
    if r.get('executed_r125_evidence'):
        parts.append('\\noindent\\textbf{Executed R125 evidence.} '+author_tex(r['executed_r125_evidence'])+'\n\n')
    for field,title in [('separately_frozen_followup_evidence','Separate completed precision follow-up'),
                        ('post_execution_policy_identity_evidence','Post-execution identity deduction'),
                        ('saved_work_accounting_evidence','Saved-work accounting')]:
        if r.get(field):
            parts.append('\\noindent\\textbf{'+title+'.} '+author_tex(r[field])+'\n\n')
    parts.append('\\noindent\\textbf{Remaining requirement.} '+author_tex(r['r125_remaining_scientific_requirement'])+'\n\n')
    parts.append('\\noindent\\textbf{Current routes.} Sections '+', '.join('\\ref{'+x+'}' for x in r['current_chapter_labels'])+'.\n\n')
parts.append(r'''\section{Earlier reports and preserved item responses}

The machine-readable current response preserves each exact request and its
R122 author action and remaining obligation. The historical route companion
maps all 684 indexed report sections: 620 explicit major comment blocks and
64 overlapping requirement/minor parent sections. This is an indexing
count, not 684 independent issues or 684 closures. The inherited development
response retains its more detailed 1,014 item records and overlapping parent
treatments. Exact report text remains authoritative.

The new companion copies the source-specific prior action and remaining
requirement for every one of the 620 major blocks, binds the inherited
response bytes, and adds current scientific routes without certifying
historical claims by association. Broader applications, neural-specific
advantages, unconstrained information complexity and high-dimensional
scaling remain open wherever the corresponding direct evidence is absent.
Earlier preregistrations and the live R124-B research identity remain
protected; R125 is neither their completion nor a substitute for their data.
''')
(ROOT/'new125/response125_body.tex').write_text(''.join(parts))
print(json.dumps({'current_requests':len(records),'exact_original_requests_verified':True,'latex_bytes':(ROOT/'new125/response125_body.tex').stat().st_size}))
