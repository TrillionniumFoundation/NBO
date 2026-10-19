#!/usr/bin/env python3
"""Integrate completed R120 evidence into author documents; no science runs.

The exact advisory quotations and pre-outcome planned actions are retained.
All current routes are bound to actual existing files, without a self-S SHA.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_BODY = "38ebf60276328ae2dcf6ee14748eff4801932abf6519d5922267ef9d91a9e0a1"
BODY = "new120/response120_body.tex"
REQ = "provenance/R97_REQUIREMENTS120.json"
IDENTITY = "SOURCE_IDENTITY120.json"


def identity(rel):
    raw = (ROOT / rel).read_bytes()
    return {"path": rel, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def load(rel):
    return json.loads((ROOT / rel).read_text())


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


ACTION = {
"B1": r"""The completed study gives every representation the same four services and original-model information. The ordinary hinge receives the ReLU features and coefficients and pays the full learned-feature acquisition charge. All 512 ReLU--hinge action pairs are exactly equal. All 42 learned own-incumbent cells have strictly positive independent mean-gain lower bounds, but every one of the 14 learned completed cells has a strictly worse sample mean original objective than the online semi-analytic control. The paired service P is slower than inherited L in all 48 matched clocks. Every one of the 32 declared ReLU/full-conventional-menu price intersections is empty, including the intersections of upper not-ruled-out conditions. Thus the achieved contribution is an action-relevant Bellman comparison and original-policy correction; this equal-feature experiment supplies no neural-specific policy or adoption advantage.""",
"B2": r"""The new constrained-AVaR theorem supplies the original continuation gradient modulus and the action-distance modulus $E$. The fixed-known-tail information result has matching width order
\[
 \min\{KR(1-\alpha)N^{-2},\,ER(1-\alpha)N^{-1}\}.
\]
One exact scalar value is one query; the claim is deterministic and univariate. The original smooth model also gives the stronger separate-width coefficient $2M_\alpha R^2(1-\alpha)^2$. The nonsmooth lower-bound adversary therefore does not establish an original-primitives or smooth-class lower bound. Full policy comparisons pay both risk deficits, outward point uncertainty and the unchanged future allowance. In execution the mixed upper is necessary at two recorded accepted levels for one common Poly3 candidate at $m=4$; no wall-time gain or optimal general Bellman information complexity is inferred from that event. The full positive-margin refinement and future-information-floor propositions state when the interface can terminate successfully.""",
"B3": r"""The new comparison authorizes changes of the original investment policy. It treats a difference of convex continuations as Lipschitz, without assuming that the difference is convex. The independent original-policy and all-action-optimum witnesses now provide value, gain, regret and action-distance bounds for every returned decision. For ReLU at $\alpha=1/2$, P's mean original-policy gain over its own completed incumbent is approximately $[212.675,213.885]\times10^{-6}$; the mean-regret upper bound falls from $215.906\times10^{-6}$ to $2.626\times10^{-6}$. The RMS action-error upper bound falls from $0.01470$ to $0.001621$. L returns the same ReLU policies, and conventional hinge is identical as well. These are original-investment improvements with a shared correction; they neither establish a neural geometry advantage nor borrow economic improvements from the separate posted-price example.""",
"B4": r"""The acquired information now targets the original continuation difference at two feasible actions. A paid common-tail mismatch and a strict complete-policy gate connect this information to a permissible decision change, with the true future-controller allowance included once. Holding the three inherited support-gradient proposal rules fixed, P changes 391 of 1,024 actions and accepts 815 steps; L changes 388 and accepts 807. Their final actions differ in only 12 cases, and none of the 16 cell-mean comparisons resolves a strict incremental P advantage. The same paid pair primitive is supplied to the stronger direct conventional proposal. All fitted critics still use the ordinary original-$V_1$ value-label objective. We therefore complete an action-dependent certificate and its original-policy evaluation, while retaining action-aware training and acquisition as a distinct unresolved scientific requirement.""",
"B5": r"""The completed four-service/eight-arm comparison retains all 4,096 primary and 6,144 timing decisions and charges actual common-label acquisition, each standalone fit and audit, full hinge acquisition, loading, proposals, tail witnesses, precision ladders, rejected work, fallback and cohort bookkeeping. Summing complete standalone 64-state costs over the same 16 cells gives 94.478 seconds for L, 132.729 for P and 80.302 for direct refinement D. P purchases fewer compiled terminal rows than L, yet is slower in every primary cell and all 48 matched fresh clocks. D purchases substantially more terminal rows and is faster than P in all those clocks. The independent rational study costs a separate 1,806.153 seconds and remains charged as research validation. These complete scopes replace a point-count-only competitiveness claim; they retain the stronger traditional method and every adverse clock.""",
"B6": r"""The fixed 48-group, 192-event population calculation has actually completed on the prospectively drawn 64 states. Under its stated finite-uniform population and independent-entropy assumption, the simultaneous 95\% family gives positive event-staircase mean-gain lower bounds in all 42 learned own-incumbent groups, ranging from $2.661\times10^{-6}$ to $14.192\times10^{-6}$. The six online groups have zero observed gains and zero lower bounds; the ordinary bounded-mean lower bounds alone are zero. The reported price sets use actual paid work and the declared conventional menu. Positive own-incumbent price regions coexist with empty ReLU/full-menu regions. No calibrated monetary value, preference parameter, market demand or population adoption conclusion is supplied by those normalized-objective calculations.""",
"B7": r"""The source F, actual actors M and single 640-byte state draw D are separately and actually committed before evaluation. The recorded 64 exact 40-bit dyadic states are shared across all arms and risks, and singleton initial-state services prevent a batch fallback from making one row's rule depend on another row. All 4,096 original-policy comparisons and all 48-group/192-event statistics completed under these commitments. The 95\% guarantee uses the fixed one-sided binomial allocation and bounded-mean allocation from the frozen protocol; it conditions on the declared independent uniform entropy law and fixed actors. This supplies the new R120 population evidence. It neither completes an old R97 actor family nor imports R98/R115 actors, reserved states or inference into this experiment.""",
"B8": r"""The separately implemented rational validator actually evaluates all 861 unique returned policy keys, with 111,069 terminal contexts and 4,096 complete-policy comparisons. Its true Lagrange affine supports also give an original all-action optimum lower witness, rather than attaching an unproved slope to a scalar lower value. Thus the independent calculation covers regret and action-distance bounds as well as policy value. All 4,096 intervals overlap: 726 production intervals contain the independent enclosure, while 3,370 narrower production intervals are contained in it. Only the former direction inherits coverage from the independent enclosure; overlap or the latter direction does not independently prove fine production endpoints. The validator does not import the production terminal compiler, retains its exact rational traces and 1,806.153-second cost, and claims neither external authorship nor a complete historical fitting-optimizer replication.""",
"B9": r"""The active main argument now follows the original continuation/actor problem, the action-dependent modulus, a usable complete-policy improvement rule, the executed matched comparison and its economic interpretation. The supplement contains every new proof and the independently implemented original-optimum construction. The development tables retain all 64 objective/cost cells, 192 clocks, 192 threshold events, 992 sample contrasts and every prescribed price comparison. The 35 original report bodies and the 1,049 inherited item/parent routes remain accessible with exact R119 source bindings. Their presence does not replace the new evidence: the main text reports P's adverse timing, unresolved incremental economic advantage and the stronger conventional proposal alongside its valid gains and the one observed mixed-bound acceptance.""",
"B10": r"""The new method buys information about an original action contrast and can change the decision. The continuation modulus, fixed-tail information bounds and quantitative tail-defect/refinement analysis are proved; the completed-incumbent gate and the three support proposals retain their R108--R110 ownership. The completed diagnostics distinguish use from independent contribution: the mixed upper is active at 5,961 of 9,016 paid levels and necessary at two accepted levels representing one Poly3 candidate shared by P and D. The transferred incumbent tail-defect bound is inactive in all 2,290 acquired density pairs. P's final action differs from L in 12 cases, with nine exact cell identities and seven unresolved mean differences; its full cost is higher in all 16 primary cells. We claim the proved comparison and actual fixed-resolution decision example, while preserving the unresolved incremental competitiveness and the unfinished action-aware acquisition problem.""",
"M1": r"""Neural Bellman Operators remains the same original-economic-decision author project. The main question is how learned continuations, recursive feasible actors and action-relevant information can produce valid improvements at justified complete cost. The investment model now supplies actual policy changes, original-value/regret bounds and fixed-law gain inference, rather than an internal fit metric alone. Its continuous shock changes stock imbalance, while investment trades current adjustment cost against the original risk-sensitive continuation and capacity constraint. The main interpretation also confronts the strong online and direct controls and full paid work. The new safeguard is shared across representations; those facts preserve the neural Bellman research identity without assigning an unsupported architecture-exclusive mechanism.""",
"M2": r"""The novelty statement distinguishes the new original constrained-AVaR smoothness calculation, action-distance integral interface, matching fixed-tail query order and quantitative constrained-tail transfer from the inherited common-risk identity and strict policy gate. The original model's additional smoothness gives its own stronger upper coefficient and is excluded from the generic nonsmooth lower-class claim. The full finite-resolution theorem includes paid deficits and the true future-policy floor. Actual execution shows one Poly3 acceptance at a paid resolution that the separate convex upper cannot authorize at that same resolution. It does not measure a traditional method after another refinement, a counterfactual time saving, or general end-to-end Bellman optimality. The economic and timing comparisons retain those precise limits.""",
"M3": r"""All 16 stored model/risk artifacts were freshly acquired under the frozen ordinary original-$V_1$ interval-midpoint value-label rule, with 256 common sites per risk and complete fitting/audit costs. The new action-relevant acquisition occurs inside the paid policy-comparison interface; it does not change that training objective. Its original-policy consequences are independently evaluated, including 42 positive learned-incumbent gain groups and the unresolved P-versus-L incremental mean comparison. The item therefore separates the completed comparison-information theorem from the still-needed action-aligned loss, acquisition theorem and newly fitted-actor validation. R98's distinct seven-objective acquisition experiment remains preserved under its own unchanged actor and sample barriers.""",
"M4": r"""The contemporary frontier contains online semi-analytic, quadratic, ReLU, equal-feature hinge, spline, degree-two polynomial, degree-three polynomial and grid arms, each with C, L, P and D. All 992 unordered within-risk cell comparisons are retained. Every learned completed cell is strictly worse than online in sample original value, and all 512 ReLU--hinge policy pairs are identical under full equal acquisition charges. D has a strictly better independent mean than L and P in five cells, two exact online identities and nine unresolved comparisons; it is faster than P in every matched clock. Thus conventional geometry, direct original-formula access and the shared certificate all receive their actual competitors. A favorable comparison with only a neural arm's own incumbent is not used as the representation frontier.""",
"M5": r"""The main text and complete development tables retain P's 16 primary cost losses and all 48 fresh-clock losses to L, nine exact and seven unresolved P/L mean comparisons, and all six zero-gain online population groups. P retains 2,257 rejected candidates, including 785 exhausted precision ladders; D retains 633 rejections, including 194 exhausted ladders. The inactive transferred-deficit result and the distinction between 5,961 active mixed bounds and only one necessary economic candidate are reported directly. The older R97 residual-span mismatch, adverse R119 phases, conventional wins and unverified neural-adoption regions remain unchanged. No discarded clock, unresolved sign or failed attempt is removed to make the new mechanism appear uniformly favorable.""",
"M6": r"""The economic interpretation reports the original risk-sensitive investment objective, not a different loss or welfare surrogate. It shows how the independently bounded ReLU own-incumbent gains reduce original regret and action-distance ceilings, and why a larger spline gain can reflect a worse incumbent. The online semi-analytic policy is already strictly better than every learned completed policy on the sample, while direct refinement is a material traditional competitor. The simultaneous 42 positive learned-incumbent lower bounds and all actual price scenarios are reported with their population and cost scopes. The units remain normalized original-objective units: this two-date experiment adds decision-relevant evidence but does not claim monetary, consumption-equivalent or field-adoption calibration.""",
"M7": r"""The completed experiment is explicitly two-dimensional, two-date and evaluated at the two prescribed risk levels. It reports each service's full acquisition, original-value queries, candidate/refinement counters, raw process costs and complete resource-vector frontier. The four predeclared amortization volumes are conditions computed from these retained measurements; they are not measured throughput, higher-dimensional scaling or a horizon experiment. The new information theorem has a scalar-tail scope, and the generic lower bound excludes richer original-formula access. Existing higher-dimensional and application evidence retains its own source and limitations. Broader scaling and consequential application claims remain concrete research obligations rather than being filled by these 64 new initial states.""",
"M8": r"""All three 32-state timing processes completed, retaining 6,144 timed actions and 192 cohort clocks. Every timed action, interval and recorded query count matches its corresponding primary rule; no mismatch or clock was censored. P is slower than L in all 48 matched clocks; D is faster than P in all 48 and faster than L in 41, with seven losses and two adverse cell medians. Cohort measurements, standalone acquisition charges, loading and larger process/launcher scopes are labeled separately. These are descriptive engineering observations under the observed execution conditions. The clocks are not extra population observations and do not supply confidence bounds for future hardware, latency, energy prices or external load.""",
"M9": r"""The exact source F, actual actor M, new sample D and pre-outcome reporting specification R are preserved together with their real launch and publication receipts. Primary evidence was separately published as E0 before final reporting. Independent original-primitives validation, the fixed rational statistics and the first read-only reporter have all completed with exit zero; the reporter binds 777 unchanged input files and 36 stable products. The derivative algebra diagnostic preserves its first source-path failure and the corrected second attempt, without changing frozen science. The bounded package audit and source CI distinguish record/byte checks and statistical/report replays from a fresh primitive-economy rerun. Actual final source, PDFs, build logs and CI states belong to the separate source/PDF and publication declarations; no R119 success or future R120 job is asserted here as a completed R120 CI.""",
"M10": r"""The main paper concentrates on the original recursive decision, complete new mathematical argument, contemporaneous experiment and economic interpretation. Full assumptions, proofs, independent optimum verification and all detailed tables remain in the supplement/development companion. All 35 exact original reports are copied unchanged into the current source package; the 620 major, 394 additional and 35 overlapping-parent treatments retain their original identities and specific remaining requirements. The current response supplies an actual proof/evidence route for each of the 30 controlling items. This organization preserves NBO's learned continuation and actor problem, the strong traditional comparisons and every valid historical result, while keeping the current contribution assessable without treating document reorganization as scientific closure.""",
"minor-1": r"""The new result is called interval width versus scalar point information, with order $\min\{KR(1-\alpha)N^{-2},ER(1-\alpha)N^{-1}\}$. Original-policy contrast, certified gain, regret, value width, squared action-distance bound and complete work are separate quantities throughout the proofs and all 64 objective/cost cells. The independently computed optimum is an enclosure, so the displayed RMS quantities are upper bounds rather than measured errors to a known exact optimizer. The achieved R119 $N^{-2}$ tail-uniform AVaR width result retains its established attribution; the executed economic gains require their own policy evidence.""",
"minor-2": r"""Deterministic, exact scalar point-value, univariate, uniform-law, convex-Lipschitz and fixed-known-tail qualifiers appear with the new information statement. Purchasing the two continuation values at a point costs two queries. The original smooth investment formula is a narrower class than the lower adversary, and risk-tail localization, finite point precision, terminal solves and the future controller remain separately paid. R119's risk-level-uniform width theorem is retained under its own assumptions. The completed two-risk experiment does not establish randomized, multivariate or arbitrary-law oracle optimality.""",
"minor-3": r"""The achieved R119 order $KR(1-\alpha)N^{-2}$ is preserved. R120's fixed-tail comparison intersects widths bounded by $2KR(1-\alpha)/n^2$ and $ER(1-\alpha)/n$, with the original smooth coefficient supplied separately. The action modulus includes its explicit $\alpha/(1-\alpha)$ dependence; this prevents a small tail mass alone from implying a cheap original-model computation near $\alpha=1$. The full-support $\alpha=0$ boundary is separate and the normalized-tail statement excludes $\alpha=1$. Actual new observations use only the predeclared $1/2$ and $3/4$ risk levels and retain every paid tail/terminal operation.""",
"minor-4": r"""The actual actor artifacts and acquisition table preserve all prescribed feature counts, coefficient signs/bounds, rounding and ties. The constrained rank-six readouts are compared with the larger fixed polynomial and grid controls under the same 256 original-$V_1$ label sites per risk. ReLU and ordinary hinge have identical retained parameters and actions, with the full shared-fit charge assigned to each standalone deployment. These are acquired-model comparisons under known restrictions. They are not best-approximation results for unrestricted representation classes, and the experiment supplies no post-outcome coefficient or architecture sensitivity menu.""",
"minor-5": r"""Every primary group now has separate original-policy bounds, independent original-optimum bounds, mean regret, RMS action-error upper bound and own-incumbent gain, alongside production contrast and certificate counters. The independent validator supplies 55,104 retained all-action support rows and all 4,096 policy comparisons. For example, the ReLU P gain is economically positive against its incumbent while its mean difference from L is exactly zero. A narrower value interval, smaller fit residual or lower regret ceiling is therefore never counted as an observed policy-value decrease by itself. The 726 versus 3,370 containment directions also retain their different independent-verification implications.""",
"minor-6": r"""Every attempted candidate and resolution, rejection, exhausted ladder, unchanged action and fallback is retained in the actual traces and complete tables. P's 2,257 refusals and D's 633 refusals appear beside accepted-step counts, as do 785 and 194 exhausted ladders. Mixed-bound use is reported at all 9,016 paid levels: 5,961 active upper bounds and two necessary accepted records for one economic candidate. The transferred incumbent bound is inactive in all 2,290 density pairs. Its mathematical validity is not converted into an unobserved reduction of already purchased tail endpoints, candidate-upper work or total time. Every unresolved and adverse comparison remains included.""",
"minor-7": r"""The three process-specific measurements, all 192 cohort clocks and their medians/ranges are labeled descriptive engineering observations. All 6,144 action/interval/query-count comparisons match, so the reported conditional timing/economic pairing is actually checked rather than presumed. These clocks remain distinct from outward rational value enclosures and from the explicitly proved 95\% simultaneous 48-group/192-event population family. Timing replicates do not increase its 64 independent initial-state units. The inherited seven R119 clocks retain their separate episode and do not enlarge the current sample.""",
"minor-8": r"""The old zero-adoption-over-quadratic result and the R119 conventional frontier remain explicit. In the new fixed comparison, positive gains against learned incumbents coexist with an online advantage against all 14 learned completed means and exact ReLU--hinge identity. All 32 ReLU intersections against the predeclared full conventional menu, across four amortization volumes and three clocks, have empty sufficient-price sets and empty intersections of upper not-ruled-out sets. The 17 nonempty sufficient menu regions across representations belong to completed conventional policies. The 112 separate actual-64-state price domains retain the actual workload and charges. These strict recorded-menu conditions and own-incumbent gains do not assert population adoption or rule on every possible deployment criterion.""",
"minor-9": r"""The main text locates the mixed integration interface relative to retained verified approximation, Bellman/HJB residual ideas, constrained safeguards and the source-owned common-risk identity. Complete proofs retain the original filtration, boundaries and one-sided future-policy allowance. Exact binomial inversion and bounded-mean concentration are attributed as classical ingredients; the new population conclusion is the specified transfer from actual certified gains. The stopped Brownian verification subcase retains its hypotheses and complete boundary argument. The present two-date validation supplies no proof or experimental substitute for a general coupled NDU/FBSDE, nonlinear recursive-preference application, temporal-self equilibrium or game.""",
"minor-10": r"""The title and active main text retain Neural Bellman Operators as the study of learned original continuations, recursive operators and feasible actor/critic decisions. The new action-dependent comparison and safeguard are attributed to an eligible-method interface shared by the neural and conventional representations. Their original-policy gains are actually measured and independently bounded; conventional hinge remains identical to ReLU, and the strongest original-formula controls remain visible. This establishes a concrete shared numerical-methods result inside the NBO problem while leaving equal-information neural advantage and action-aware learning as explicit ongoing research requirements.""",
}

GROUPS = {
"economic": [
    ("new120/results120.tex", ["sec:results120", "tab:economic120"]),
    ("new120/economic_interpretation120.tex", ["sec:economicinterpretation120", "sec:incrementalevidence120", "sec:adoptioninterpretation120"]),
    ("tables120/groups120.json", []), ("tables120/sample_contrasts120.json", []),
],
"cost": [
    ("new120/results120.tex", ["sec:costresults120", "tab:cost120"]),
    ("new120/development120_results.tex", ["tab:allcost120", "tab:allclocks120"]),
    ("tables120/acquisition120.json", []), ("tables120/raw_timing_clocks120.json", []),
    ("tables120/timing_action_checks120.json", []), ("tables120/all_operation_dimensions120.json", []),
],
"population": [
    ("new120/results120.tex", ["sec:populationresults120", "tab:population120"]),
    ("tables120/population_groups120.json", []), ("tables120/threshold_events120.json", []),
    ("results120/stats-attempt01/EXECUTION120.json", []),
],
"independent": [
    ("results120/independent-attempt01/EXECUTION120.json", []),
    ("tables120/certificate_compatibility120.json", []),
    ("tables120/unique_independent_policy_costs120.json", []),
],
"mechanism": [
    ("new120/development120_results.tex", ["tab:alltrials120", "tab:allpairuse120"]),
    ("tables120/paired_bound_levels120.json", []), ("tables120/paired_bound_groups120.json", []),
],
"price": [
    ("new120/development120_results.tex", ["tab:allprices120", "tab:actualprices120", "tab:allfrontiers120"]),
    ("tables120/price_domains120.json", []), ("tables120/interval_frontiers120.json", []),
],
"identity": [
    ("provenance/SOURCE_PUBLICATION120.json", []), ("provenance/ACTOR_PUBLICATION120.json", []),
    ("provenance/STATE_PUBLICATION120.json", []), ("provenance/REPORTING_PUBLICATION120.json", []),
    ("provenance/PRIMARY_PUBLICATION120.json", []),
    ("results120/reporting-attempt01/EXECUTION_REPORT120.json", []),
    ("results120/reporting-attempt01/OUTPUT_MANIFEST120.json", []),
],
"history": [
    ("CONTENT_RETENTION_MAP120.md", []), ("REVISION_BOUNDARY120.md", []),
    ("provenance/reports120/REPORT_SOURCE_INDEX120.json", []),
    ("provenance/reports120/inherited_maps/INDEX120.json", []),
],
}
ITEM_GROUPS = {
"B1": ["economic", "cost", "price"], "B2": ["mechanism"],
"B3": ["economic", "independent"], "B4": ["economic", "mechanism"],
"B5": ["cost", "independent"], "B6": ["population", "price"],
"B7": ["identity", "population"], "B8": ["independent"],
"B9": ["economic", "history"], "B10": ["mechanism", "cost"],
"M1": ["economic"], "M2": ["mechanism"], "M3": ["economic", "cost"],
"M4": ["economic", "price"], "M5": ["mechanism", "cost"],
"M6": ["economic", "population"], "M7": ["cost", "price"],
"M8": ["cost"], "M9": ["identity", "independent"], "M10": ["history", "economic"],
"minor-1": ["economic", "independent"], "minor-2": ["mechanism"],
"minor-3": ["cost", "economic"], "minor-4": ["economic", "cost"],
"minor-5": ["economic", "independent"], "minor-6": ["mechanism"],
"minor-7": ["cost", "population"], "minor-8": ["price", "economic"],
"minor-9": ["population"], "minor-10": ["economic", "history"],
}

COMPLETED_OVERVIEW = r"""\paragraph{Completed scientific evidence.}
The campaign, independent validation, population analysis and first
read-only reporter have now completed. All 4,096 primary decisions qualify;
all 6,144 timing actions, intervals and recorded query counts match their
corresponding primary rules. The separate rational calculation covers all
861 unique policy keys, 111,069 terminal contexts and 4,096 comparisons,
including original all-action optimum bounds. The frozen 48-group,
192-event family gives 42 positive learned-incumbent event-staircase
mean-gain lower bounds with its stated simultaneous 95\% coverage.
These are fresh R120 observations under the committed sample and fixed
actors, not inherited R119 results.

We use C for the completed incumbent, L for inherited legacy-safe
refinement, P for the new paired service and D for direct refinement.
The substantive comparison is mixed. All learned own-incumbent gains are
positive, but P has nine exact cell identities and seven unresolved
cell-mean differences against L, and is slower in all 48 matched clocks.
D is faster than P in all those clocks and has a strictly better original
mean in five cells. The mixed bound is necessary at one actual Poly3
candidate, recorded once in each of P and D; the transferred incumbent
deficit is inactive in all 2,290 acquired density pairs. All 512
ReLU--hinge policies are identical and every learned completed mean is
strictly worse than the online control. Sections~\ref{sec:results120}--\ref{sec:populationresults120}
and \ref{sec:economicinterpretation120}--\ref{sec:adoptioninterpretation120}
develop these outcomes with all costs and remaining scientific boundaries.

Numerical decimals in this response summarize the retained exact rational
endpoints; those endpoints determine every sign and price domain. The 992
same-sample cross-cell contrasts are not added to the prospectively declared
population inference family. All older negative results, reserved studies
and failed attempts remain separately identified.

"""

FINAL_EVIDENCE = r"""\section{Evidence and source/PDF publication}
The primary and three timing processes completed with an external exit-zero
receipt at 08:09:59 UTC on 19 October 2026. Independent validation completed
at 08:42:24 UTC; the fixed statistics completed at 08:43:06 UTC. The first
read-only reporter completed at 08:44:13 UTC and binds 777 unchanged input
files and 36 stable output files. The original protocol and source F,
actual actors M, single sample D and pre-outcome reporting specification R
remain immutable. The primary evidence checkpoint is separately published
as \nolinkurl{a6f3b8278d4502b174b05b19fafd5aacabaa60a3}.
All exact launches, stdout, process receipts, primitive traces, refusals,
timing repetitions and output tables are retained. The reporter is a
read-only reaggregation of actual records, not a second economic experiment.

The independent evaluator supplies original-policy and original-optimum
enclosures from separately implemented rational primitives. Its
1,806.153-second inner process is charged separately from deployment, and
its wider enclosure does not validate every finer production endpoint.
The post-timing algebra diagnostic preserves its first derivative
source-path failure and the corrected second attempt's 17,039 checks over
1,333 cases; neither changes the frozen scientific source.

\nolinkurl{EVIDENCE_MANIFEST120.json} binds the complete current evidence,
archive transport, executed reporter products and source requirements.
The bounded verifier checks bytes, complete censuses and recorded rational
invariants, with separately identified statistics/report replays. It does
not claim to rerun acquisition, independent economic primitives or timings.
The source/PDF publication uses separate
\nolinkurl{SOURCE_PDF_MANIFEST120.json} and
\nolinkurl{PUBLICATION120.json} declarations for the actual author-source
commit, four PDFs, build receipts and dated remote CI observations. Those
later derivative receipts avoid an author-source hash self-reference and
preserve earlier status observations. No queued or future job, inherited
R119 success or merely prepared workflow is asserted by this source as an
R120 CI success. The original NBO/Econometrica research goal remains active
with the proved and executed advances, adverse costs, unresolved
incremental superiority and explicit remaining neural-learning obligations.
"""

COMPLETE_MD = """## Completed current R120 episode and its limits

The actual immutable barriers are F=`369d02724cf12ae0e54390b4e7b5f894f703892e`, M=`1c5e4dc7e04c108fe698d4c247a144b625db301c`, D=`aebc7a0175c0729b9ff5e833a7facc1ed5c4c2fd` and reporting specification R=`594d9336d89bedfd360e942146ae490e0fabd3a0`. Their direct ancestry and actual transport/launch records are distinct from Git committer dates. The reporting-publication receipt was written after primary launch and preserves the real successful operation order and recorded launch HEAD; its later write time is not represented as an earlier observed publication time. The primary-evidence checkpoint E0=`a6f3b8278d4502b174b05b19fafd5aacabaa60a3` preserves 549 raw files in ten verified archive parts. See [SOURCE_PUBLICATION120](provenance/SOURCE_PUBLICATION120.json), [ACTOR_PUBLICATION120](provenance/ACTOR_PUBLICATION120.json), [STATE_PUBLICATION120](provenance/STATE_PUBLICATION120.json), [REPORTING_PUBLICATION120](provenance/REPORTING_PUBLICATION120.json) and [PRIMARY_PUBLICATION120](provenance/PRIMARY_PUBLICATION120.json).

All **4,096 primary decisions, 6,144 timing decisions, 861 independently evaluated policy keys, 111,069 independent terminal contexts, 4,096 independent comparisons, 48 population groups and 192 threshold events** actually completed. Primary/timing ended at 08:09:59 UTC, independent validation at 08:42:24 UTC, statistics at 08:43:06 UTC and the first read-only reporter at 08:44:13 UTC on 19 October 2026. The reporter binds 777 unchanged input files and 36 stable derivatives. Exact authorities are the [primary launch](results120/launches/primary-attempt01/LAUNCH120.json), [independent execution](results120/independent-attempt01/EXECUTION120.json), [statistics execution](results120/stats-attempt01/EXECUTION120.json), [reporter execution](results120/reporting-attempt01/EXECUTION_REPORT120.json), [complete report summary](results120/reporting-attempt01/SUMMARY_REPORT120.json) and [report products](results120/reporting-attempt01/OUTPUT_MANIFEST120.json).

The new original-policy correction has real decision consequences: all 42 learned own-incumbent groups have positive independent sample mean-gain lower bounds and positive event-staircase lower bounds in the predeclared simultaneous 95% family. The six online groups retain zero observed gains and zero lower bounds. These are conclusions for the declared finite-uniform 40-bit initial-state law, conditional on frozen actors and ideal independent entropy. The original continuous innovation law remains unchanged, and the 992 cross-cell sample contrasts are not a new population family.

The stronger comparisons remain adverse or unresolved. P changes 391/1,024 actions versus L's 388 and differs from L in only 12 cases; their 16 mean comparisons are nine exact identities and seven unresolved signs. P is slower than L in all 16 primary cells and all 48 fresh matched clocks. D is faster than P in all 48 clocks and strictly improves the original mean in five cells relative to L/P, with two online identities and nine unresolved comparisons. The new mixed upper changes acceptance for one Poly3 candidate at a stored resolution, recorded in P and D; the transferred incumbent deficit is inactive in all 2,290 acquired density pairs. Every one of 512 ReLU--hinge policies is equal, every learned completed mean is worse than online, and all 32 strict ReLU/full-menu price intersections are empty. These results are reported in [the actual result source](new120/results120.tex), [economic interpretation](new120/economic_interpretation120.tex) and [complete development tables](new120/development120_results.tex).

Independent optimality/regret evidence is new to this episode. Its separately implemented rational supports cover all original actions; the returned-value intervals overlap all 4,096 production rows. The 726 production intervals containing the independent enclosure and 3,370 narrower production intervals contained in it retain different validation implications. The latter direction alone does not independently establish fine endpoints. The independent process costs 1,806.153 seconds at its recorded inner scope and is paid as research validation. The unchanged ordinary value-label training is not action-aware learning; equal-information neural advantage, incremental P competitiveness, higher-dimensional/horizon scaling and calibrated application value remain explicit research requirements.

"""


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    out = ROOT / "provenance/author_response120" / ("completed_findings_" + now.strftime("%Y%m%dT%H%M%S.%fZ"))
    out.mkdir(parents=True, exist_ok=False)
    targets = [BODY, REQ, IDENTITY, "CONTENT_RETENTION_MAP120.md", "REVISION_BOUNDARY120.md"]
    before = {rel: identity(rel) for rel in targets}
    assert before[BODY]["sha256"] == EXPECTED_BODY, "Author body changed; inspect before updating"
    for rel in targets:
        p = out / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / rel).read_bytes())
    stage_paths = {
        "independent": "results120/independent-attempt01/EXECUTION120.json",
        "stats": "results120/stats-attempt01/EXECUTION120.json",
        "reporting": "results120/reporting-attempt01/EXECUTION_REPORT120.json",
    }
    stages = {k: load(v) for k, v in stage_paths.items()}
    assert all(v["status"] == "executed" and v["exit_code"] == 0 for v in stages.values())
    summary = load("results120/reporting-attempt01/SUMMARY_REPORT120.json")
    assert (summary["primary_decisions"], summary["timing_decisions"], summary["population_gain_groups"], summary["threshold_events"]) == (4096, 6144, 48, 192)
    assert summary["independent_validation"]["unique_policy_keys"] == 861
    assert summary["independent_validation"]["independent_terminal_contexts"] == 111069
    assert summary["positive_staircase_groups"] == 42
    assert summary["timing_action_matches"] == 6144
    assert summary["relu_hinge_action_matches"] == 512
    req = load(REQ)
    assert set(ACTION) == {x["comment_id"] for x in req["items"]} == set(ITEM_GROUPS)
    for entries in GROUPS.values():
        for rel, labels in entries:
            assert (ROOT / rel).is_file(), rel
            if labels:
                source = (ROOT / rel).read_text()
                assert all("\\label{" + label + "}" in source for label in labels), (rel, labels)
    body = (ROOT / BODY).read_text()
    old_quotes = re.findall(r"\\begin\{quote\}.*?\\end\{quote\}", body, re.S)
    assert len(old_quotes) == 30
    body = body.replace(
        "% R120 author response. F/M/D/R and primary/timing are complete; independent findings and final publication remain pending.",
        "% R120 author response: completed source-bound science; final source/PDF identities are separate derivative declarations.")
    body = body.replace("The current complete author manuscript is R119 source", "This revision starts from the complete R119 author source")
    body = body.replace("These are written mathematical results,\nnot executed economic findings.", "Their mathematical validity and the separately executed economic findings\nare documented as distinct claims.")
    body = body.replace("\\paragraph{Prospective execution and current evidence status.}", "\\paragraph{Prospectively fixed execution design.}")
    body = body.replace("The two remotely frozen protocols specify", "The two remotely frozen protocols specified")
    body = body.replace("The source, actual actor and independent sample barriers precede the\nprescribed", "The source, actual actor and independent sample barriers preceded the\ncompleted")
    # Retain the actual M/D/R and launcher paragraphs preceding the old marker.
    start = body.index("At this dated author update, independent policy validation")
    end = body.index("\\section{Point-by-point response to the controlling advisory}", start)
    body = body[:start] + COMPLETED_OVERVIEW + body[end:]
    body = body.replace(
        "Economic contrasts and population findings require the independently\ncompleted validation and reporting stages.",
        "The independently completed validation and reporting stages now supply\nthe actual economic contrasts and population findings below.")
    for item in req["items"]:
        key = item["comment_id"]
        citations = []
        for group in ITEM_GROUPS[key]:
            labels = [label for _, ls in GROUPS[group] for label in ls if label.startswith("tab:")]
            if labels:
                citations.append("Table~\\ref{" + labels[0] + "}")
        citations = list(dict.fromkeys(citations))
        if citations:
            route_sentence = "The completed evidence for this item is in " + ", ".join(citations) + "; the exact row files and hashes are retained in the current response map."
        else:
            first_path = GROUPS[ITEM_GROUPS[key][0]][0][0]
            route_sentence = "The exact completed source/evidence route includes \\nolinkurl{" + first_path + "}; the current response map binds all corresponding files."
        actual_action = ACTION[key].strip() + "\n\n" + route_sentence
        if key == "B10":
            old_boundary = item["continuing_scientific_boundary"]
            new_boundary = "The R119 phases retain exact-zero within-arm policy gains. The executed R120 gains belong only to the new source and cannot retrospectively turn the R97 acquisition objective into successful action-aware learning."
            item["continuing_boundary_before_completed_results"] = old_boundary
            item["continuing_scientific_boundary"] = new_boundary
            assert old_boundary in body
            body = body.replace(old_boundary, new_boundary, 1)
        pattern = (r"(\\label\{response120:" + re.escape(key) +
                   r"\}.*?\\paragraph\{Concrete R120 author action\.\}\n).*?"
                   r"(?=\\paragraph\{R120 source route\.\})")
        body, n = re.subn(pattern, lambda m: m.group(1) + actual_action + "\n", body, count=1, flags=re.S)
        assert n == 1, key
        item["planned_action_history_retained"] = True
        item["r120_completed_author_action_latex"] = actual_action
        item["r120_resolution_scope"] = {
            "completed_treatment": actual_action,
            "remaining_scientific_requirement": item["continuing_scientific_boundary"],
            "broader_advisory_closure_asserted": False,
            "neural_exclusive_advantage_asserted": False,
        }
        item["r120_mathematical_status"] = "Written complete, source-checked propositions with original-objective assumptions and scope; no blanket closure of the report demand."
        item["r120_empirical_status"] = "Executed source F and actual M/D commitments: complete 4096/6144 decisions, independent 861-key evaluation and 48/192 population analysis. This item's completed treatment states its actual favorable, adverse, unresolved or non-empirical conclusion."
        item["r120_current_evidence_groups"] = ITEM_GROUPS[key]
        item["completed_findings_observed_utc"] = now.isoformat()
        item["closed"] = False
    # Preserve exact quotes while giving inherited A/B/C their episode names.
    pieces = re.split(r"(\\begin\{quote\}.*?\\end\{quote\})", body, flags=re.S)
    for k in range(0, len(pieces), 2):
        pieces[k] = pieces[k].replace("New A/B/C report", "R119 A/B/C report")
    body = "".join(pieces)
    cut = body.index("\\section{Evidence and publication completion}")
    body = body[:cut] + FINAL_EVIDENCE
    assert old_quotes == re.findall(r"\\begin\{quote\}.*?\\end\{quote\}", body, re.S)
    assert "PENDING" not in body
    assert len(re.findall(r"\\label\{response120:", body)) == 30
    (ROOT / BODY).write_text(body)

    for rel in ["CONTENT_RETENTION_MAP120.md", "REVISION_BOUNDARY120.md"]:
        s = (ROOT / rel).read_text()
        old_first = s.split("\n\n")[2]
        assert old_first.startswith("Source barrier **F=")
        first = old_first.replace("so R97 remains controlling and R119 remains the latest complete manuscript", "so R97 remained controlling and R119 was the complete inherited manuscript in that dated observation")
        first = first.replace("This source barrier supplies no actor/sample commitment, completed economic study or final source/PDF/CI result. All frozen scientific inputs remain unchanged; this update records source publication only.", "That receipt concerns source publication alone. The later actor/sample barriers and completed findings have their own actual records below; no frozen scientific input is changed by this author update.")
        s = s.replace(old_first, first, 1)
        insertion = s.index("\n\n", s.index(first)) + 2
        s = s[:insertion] + COMPLETE_MD + s[insertion:]
        s = s.replace("R119 is the current complete scientific manuscript, while", "R119 is the complete inherited scientific manuscript, while")
        s = s.replace("No action-aware learned fitting or numerical gain is inferred merely from these staged sources. Completed and failed execution outcomes must retain their own later receipts.", "The completed episode and its separate execution receipts are recorded above. The ordinary value-label fitting objective remains unchanged, and no action-aware learned fitting claim is made.")
        s = s.replace("give the next concrete author actions", "give each concrete completed R120 author action, its actual proof/evidence route and remaining scope")
        s = s.replace("The source barrier F is actually published and verified as recorded above. Completed R120 scientific observations, independent economic validation and the final source/PDF publication remain pending in this author update. This map preserves the full scientific vision and existing evidence while identifying the work still required; it does not certify a new empirical gain or a newly completed manuscript.", "The source, actor/sample commitments and completed original-policy, independent and inferential evidence have the actual receipts above. The separate [SOURCE_PDF_MANIFEST120.json](SOURCE_PDF_MANIFEST120.json) and [PUBLICATION120.json](PUBLICATION120.json) declarations bind later actual author-source/PDF/CI identities without a self-referential author-source SHA. This retention map does not pre-assert a future CI success. It preserves the full scientific vision, the attained gains and proofs, the strong conventional wins and the unresolved neural-learning and computational requirements.")
        s = s.replace("## New R120 written methods and prospective experiment", "## New R120 methods and the prospectively fixed experiment")
        s = s.replace("The staged protocols prescribe", "The frozen protocols prescribed")
        s = s.replace("These are preparation/source checks; they are not evidence that the new scientific campaign or independent validation completed. Later executions and any necessary separately identified amendment must be recorded without changing earlier evidence.", "Those preparation/source checks retain their original limited scope. The separately completed campaign, independent validation, statistics and reporting receipts now supply their own executed evidence, without changing any earlier source or observation.")
        s = s.replace("The R120 source barrier F is now actually published and bound as recorded above. Completed scientific observations, independent-validation outcomes, later actor/sample barriers, source/PDF bindings and final CI status still require their own actual records. Unfinished claims remain explicit research obligations while the original NBO/Econometrica goal continues.", "The actual F/M/D/R barriers, primary checkpoint and completed scientific/independent/statistical records are identified above. Final author-source/PDF and dated CI identities are supplied by the separate [SOURCE_PDF_MANIFEST120.json](SOURCE_PDF_MANIFEST120.json) and [PUBLICATION120.json](PUBLICATION120.json) declarations; this source does not claim a future CI success. The attained original-policy gains and new proofs coexist with adverse P costs, unresolved incremental mean improvement, conventional control wins and continuing action-aware learning obligations. The original NBO/Econometrica goal continues.")
        s += "\nThe exact original R119 major and additional response maps are also retained losslessly in [inherited_maps](provenance/reports120/inherited_maps/), with [their original and compressed byte identities](provenance/reports120/inherited_maps/INDEX120.json). They make the 1,049 source-specific routes independently readable from the R120 package without revising any old report or claiming 1,049 scientific closures.\n"
        assert "remain pending" not in s
        (ROOT / rel).write_text(s)

    # Hash the current routes only after author-only Markdown changes are final.
    for item in req["items"]:
        routes = {x["path"]: x for x in item["r120_current_source_routes"]}
        for group in ITEM_GROUPS[item["comment_id"]]:
            for rel, labels in GROUPS[group]:
                current = routes.get(rel, {"labels": []})
                labels = sorted(set(labels) | set(current.get("labels", [])))
                if labels:
                    text = (ROOT / rel).read_text()
                    assert all("\\label{" + label + "}" in text for label in labels), (rel, labels)
                routes[rel] = {**identity(rel), "labels": labels}
        for rel in routes:
            routes[rel].update(identity(rel))
        item["r120_current_source_routes"] = [routes[k] for k in sorted(routes)]
        item["r120_source_route_observed_utc"] = now.isoformat()
    req["updated_utc"] = now.isoformat()
    req["completed_findings_update_utc"] = now.isoformat()
    req["completed_findings_scope"] = "All current scientific stages and first read-only reporting actually completed. Thirty original requests and pre-outcome planned actions are unchanged; each current action states achieved claims and the specific remaining requirement."
    req["completed_findings_receipts"] = [identity(x) for x in stage_paths.values()]
    req["primary_evidence_checkpoint_commit"] = "a6f3b8278d4502b174b05b19fafd5aacabaa60a3"
    req["final_publication_declarations"] = ["SOURCE_PDF_MANIFEST120.json", "PUBLICATION120.json"]
    req["future_ci_success_asserted"] = False
    write_json(ROOT / REQ, req)

    ident = load(IDENTITY)
    ex = ident["r120_scientific_execution"]
    ex.update({
        "status": "Completed original scientific campaign, independent value/optimum validation, fixed population analysis and first read-only reporter; final publication identities are separate source/PDF declarations.",
        "new_result_claimed": True, "new_economic_gain_claimed": True,
        "new_economic_gain_scope": "Forty-two learned own-incumbent sample and simultaneous event-staircase mean-gain lower bounds are positive. This is not cross-representation population superiority, neural exclusivity or incremental P superiority over L.",
        "independent_validation_completed_in_this_author_update": True,
        "population_results_completed_in_this_author_update": True,
        "reporting_completed_in_this_author_update": True,
        "publication_completed_in_this_author_update": False,
        "publication_status_scope": "Actual later author-source, four-PDF/build and CI identities/statuses are in separate SOURCE_PDF_MANIFEST120.json and PUBLICATION120.json; no self-S SHA or future success is asserted.",
        "primary_evidence_checkpoint_commit": "a6f3b8278d4502b174b05b19fafd5aacabaa60a3",
        "primary_evidence_checkpoint_tree": "7fcd37b26c57d70812fc729b49e618adf894ea22",
        "primary_evidence_publication_receipt": identity("provenance/PRIMARY_PUBLICATION120.json"),
        "author_status_updated_utc": now.isoformat(),
    })
    for name, path in stage_paths.items():
        data = stages[name]
        ex["completed_executions"][name] = {
            "receipt": identity(path), "status": data["status"], "exit_code": data["exit_code"],
            "started_unix": data["started_unix"], "ended_unix": data["ended_unix"],
            "recorded_total_seconds": data["total_seconds"],
        }
    for name in ("independent", "stats"):
        rel = f"results120/launches/{name}-attempt01/LAUNCH120.json"
        data = load(rel)
        ex["completed_launches"][name] = {k: data[k] for k in ("status", "exit_code", "started_utc", "ended_utc", "elapsed_seconds", "head_at_launch")}
        ex["completed_launches"][name]["receipt"] = identity(rel)
        log = f"results120/launches/{name}-attempt01/stdout.log"
        ex["completed_launches"][name]["stdout"] = identity(log)
    ident["r120_actual_findings"] = {
        "independent_policy_keys": 861, "independent_terminal_contexts": 111069,
        "independent_policy_comparisons": 4096, "independent_all_action_support_rows": 55104,
        "population_groups": 48, "threshold_events": 192, "independent_state_units": 64,
        "positive_independent_sample_gain_groups": 42, "positive_staircase_groups": 42,
        "within_risk_sample_contrasts": 992, "sample_contrast_sign_counts": summary["sample_contrast_sign_counts"],
        "timing_action_matches": 6144, "timing_action_mismatches": 0,
        "relu_hinge_action_pairs_equal": 512,
        "production_contains_independent": 726, "independent_contains_production": 3370,
        "containment_scope": "Only a production interval containing the proved independent enclosure inherits coverage from it; overlap or the inverse inclusion does not prove finer production endpoints.",
        "P_vs_L": {"different_actions_of_1024": 12, "exact_cell_identities": 9, "unresolved_mean_cells": 7, "strict_resolved_mean_wins": 0, "P_slower_primary_cells": 16, "P_slower_matched_fresh_clocks": 48},
        "D_vs_P": {"faster_matched_fresh_clocks": 48, "strictly_better_original_mean_cells": 5, "exact_online_cells": 2, "unresolved_mean_cells": 9},
        "mixed_bound_necessary_accepted_level_records": 2, "distinct_economic_candidates_for_those_records": 1,
        "incumbent_transfer_active_density_pairs": 0, "acquired_density_pairs": 2290,
        "full_menu_relu_three_clock_price_intersections": 32, "nonempty_sufficient_full_menu_relu_intersections": 0,
        "ordinary_value_label_fitting_unchanged": True, "neural_exclusive_advantage_asserted": False,
        "economic_interpretation_is_post_outcome_author_text": True,
        "source": identity("results120/reporting-attempt01/SUMMARY_REPORT120.json"),
        "economic_interpretation": identity("new120/economic_interpretation120.tex"),
        "interpretation_bindings": identity("provenance/reporting_driver120/interpretation120/INTERPRETATION_BINDINGS120.json"),
    }
    ident["author_status_updated_utc"] = now.isoformat()
    ident["final_publication_declarations"] = ["SOURCE_PDF_MANIFEST120.json", "PUBLICATION120.json"]
    write_json(ROOT / IDENTITY, ident)
    after = {rel: identity(rel) for rel in targets}
    receipt = {
        "schema": "NBO_R120_COMPLETED_AUTHOR_RESPONSE_UPDATE_V1",
        "observed_utc": now.isoformat(), "script": identity(str(Path(__file__).resolve().relative_to(ROOT))),
        "before": list(before.values()), "after": list(after.values()),
        "actual_stage_receipts": [identity(x) for x in stage_paths.values()],
        "report_summary": identity("results120/reporting-attempt01/SUMMARY_REPORT120.json"),
        "interpretation_bindings": identity("provenance/reporting_driver120/interpretation120/INTERPRETATION_BINDINGS120.json"),
        "original_quote_blocks_preserved_exactly": 30,
        "current_comment_actions_updated": 30, "current_broader_closure_flags_false": 30,
        "unchanged_historical_route_binding": identity("provenance/HISTORICAL_ROUTE_BINDINGS120.json"),
        "pending_markers_in_current_response": 0,
        "scientific_execution_performed": False, "reporter_rerun": False, "build_performed": False,
        "remote_mutation_performed": False, "R119_file_written": False,
        "scope": "Author documents and current R97 response routes only; actual executed evidence was read without mutation. Final binding refresh remains necessary after later author layout edits.",
    }
    write_json(out / "AUTHOR_COMPLETED_FINDINGS_UPDATE120.json", receipt)
    print(json.dumps({"receipt": str((out / "AUTHOR_COMPLETED_FINDINGS_UPDATE120.json").relative_to(ROOT)), "after": list(after.values()), "quotes_preserved": 30}, indent=2))


if __name__ == "__main__":
    main()
