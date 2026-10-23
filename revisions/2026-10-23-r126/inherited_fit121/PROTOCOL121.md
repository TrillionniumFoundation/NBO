# R121 prospectively specified action-marginal learning experiment

## 1. Identity, question, and execution barriers

This is a new author experiment under the original Neural Bellman Operators investment economy. The completed author baseline is R120, final commit `f06f220aea525088e82228e8e9be4947fb81b1ca`. R120's actual same-objective policy improvements, adverse paired-service clocks, conventional wins, exact ReLU/hinge identities, failed attempts, and independent evaluation remain retained historical evidence. No R120 or independently committed R98/R115 states, learned actors, outcomes, or timings are observations of this experiment.

The question is whether constructive minimization of a paid original-action marginal error, instead of an ordinary value error in the same finite representation, changes original decisions, regret bounds, first-proposal rejection, and complete paid economic performance. The experiment is not designed to guarantee a favorable marginal-loss sign or a neural advantage. Fixed ReLU features have an exactly corresponding ordinary hinge implementation; any common representational geometry is not neural-exclusive.

The following barriers are mandatory and distinct:

1. **F: prospective source and protocol publication.** The complete scientific source closure, this protocol, independent validation/statistical specifications, and declared reporting rules are published at an immutable remote commit before original-economy label acquisition, fitted coefficients, or held-out entropy are generated. `SOURCE_FREEZE121.json` binds the files by SHA-256. Every campaign invocation checks its own local bytes, the source manifest, and the immutable Git blobs before importing scientific dependencies. Source-only reading, syntax checks, and explicitly labelled synthetic algebra/shape checks are permitted before F; they are not original-economy results.
2. **M: complete actor publication.** Two separate acquisition processes, one for budget 5 and one for budget 9, use F. Every label, fit, solver status, rejected/failed attempt, model and audit is retained. Both complete acquisition artifact manifests and all 56 actors are published at an immutable descendant M before any held-out draw. A failed acquisition aborts its attempt; no partial set or best subset is sampled.
3. **D: independent state publication.** Under F and after verifying M, acquire exactly 640 OS entropy bytes, five per coordinate, to construct 64 exact two-dimensional 40-bit dyadic states. Save the entropy, integers, binary64 values and hexadecimal identities before any held-out economic query. Publish the full state manifest at a distinct immutable descendant D before the primary run. Duplicate draws remain 64 observation rows; no draw is replaced.
4. **Complete evaluation.** Run all declared primary cells and the five serial timing repetitions with the same fixed actors and states. Then independently evaluate every distinct returned-policy and available first-proposal key, followed by the frozen statistical program and reporting specification. Deterministic presentation/aggregation source is deposited with the final author source; it cannot change the prospectively fixed selection, accounting or statistical criteria. No economic or timing outcome selects a new mesh, seed, model, coefficient box, loss, stopping rule, or reporting sign.

Any necessary post-F implementation correction receives its own visible failure record, source delta, new prospective boundary and explicit outcome-knowledge disclosure. Earlier attempts are not overwritten or renamed as successful runs.

## 2. Unchanged economic problem

The executed state dimension is two. Initial states lie in [0,1]^2. Original innovation risk remains the continuous uniform law on [-1/32,1/32], with nested AVaR levels 1/2 and 3/4. The state transition, stage loss, original discount beta=15/16, action cost h(a)=a^2+4a^4, and feasible capacity A(x)=1/8+(x0+x1)/16 are unchanged. The original date-zero action is a=A(x)v, with v in [0,1].

The continuation target is the original optimized one-date Bellman value V1*, computed from the original primitive terminal problem. The actual future controller is the unchanged `terminal_controller94.terminal_policy` with downward 40-bit observed states. Its uniform allowance epsilon1=2^-20 is included once, through beta*epsilon1, in implemented-policy evaluation. A 40-bit observation is not a claim of 40 optimizer iterations. Training labels for the optimized root Q use V1* enclosures without adding the implemented-future allowance. Policy certification and independent implemented-policy evaluation add the allowance with their declared scope.

The production final service must certify original regret at most tau=1/256 and implemented-policy interval width at most 1/8192. These are unchanged tolerances, applied to every representation and both training losses. A fitted loss, floating root residual, or optimizer success flag does not itself certify an original policy.

## 3. Two independent complete acquisition budgets

Budget 5 uses the endpoint state grid {0,1/4,1/2,3/4,1}^2. Budget 9 uses {0,1/8,...,1}^2. They are geometrically nested, but are acquired in separate complete processes. Shared geometric sites are recomputed and actually paid in both processes; a coarse acquisition clock is not reconstructed from the fine run.

At every state, the five main normalized action nodes are v=0,1/4,1/2,3/4,1. The fixed probe radius is h=2^-12. Retain v itself and every feasible v-h and v+h around these nodes, giving exactly 13 distinct Q contexts per state: 325 or 1,053 contexts per risk, respectively. Both risk levels are acquired in each budget process. Thus the complete acquisition has 2,756 original root Q contexts, 1,060 main marginal contexts and all their original terminal primitive payloads. These are newly acquired original-risk Bellman values, not free privileged V1 labels.

Each Q value uses a fixed 256-cell whole-support continuous-risk enclosure. At each cell midpoint obtain an independently feasible original terminal-value lower bound; at endpoints obtain terminal-value upper bounds, with repeated interior endpoints carrying their true half-cell mixture weights. For every hinge threshold, Jensen supplies the lower convex-order inequality and the endpoint secant supplies the upper inequality; minimize the corresponding AVaR variational objectives. The innovation law remains continuous. Both terminal lower/upper payloads, terminal gaps, original Q enclosures, operation counts and actual acquisition/trace times are saved.

The continuation critic is anchored at v=0. VALUE targets at **all 13 paid contexts**, including probes, are intervals for Q(x,A(x)v)-Q(x,0)-h(A(x)v). At v=0 the exact identical-key difference cancels to zero. The separately paid Q(x,0) anchor is stored on the state grid and interpolated bilinearly when a full root critic is requested. It is a state-only gauge and cancels from actor decisions. Both losses receive the same complete raw label payload, including anchors and all probes.

## 4. Original-action marginal intervals

Use the proved original constants, not empirical derivative fits. Let t=1-alpha, m_z=181/64,

    M = 1413/128 + (15/16)*(127/16 + 19625*alpha/(20480*t)),
    C = (4/5)*M,
    L_a = 5 + (15/16)*(5*M/16 + C*C*alpha/(m_z*t)).

The original fixed-state root Q is 2-strongly convex and its action derivative is L_a-Lipschitz. Constants are computed as exact rational numbers and outward converted for interval arithmetic. At a=A(x)v the original action step is d=A(x)h. Intersect every available sound derivative interval:

- Forward secant interval S+ plus [-L_a*d/2, -2*d/2].
- Backward secant interval S- plus [2*d/2, L_a*d/2].
- At interior nodes, the central secant interval plus/minus (L_a-2)*d/4.

Endpoints use only the feasible inward secant. Subtract the original h'(a)=2a+16a^3 to obtain the continuation marginal interval in original-action units. Preserve every component interval and the final intersection. An empty intersection is a failed acquisition, not a license to choose a looser post-outcome label. The compiler's global affine support slope is never called an exact derivative label.

The separate theory proves a global Lipschitz constant for the true continuation marginal and a finite-cover certificate using explicit feature-derivative ranges. Finite-node fitting and its rational optimization audit below do not alone establish that global certificate. The executed production qualification remains the original Bellman certificate. Any unexecuted finite-cover calculation is identified as a theoretical construction, not a numerical result.

## 5. Fixed representations, boxes and two losses

Every family uses the same original action cost plus an anchored continuation readout. The coefficient box is fixed at B=128 before acquisition, for both VALUE and MARGINAL. Unless specified otherwise, every coefficient lies in [-128,128]. There is no held-out hyperparameter search.

| Family | Exact anchored basis | Coarse/fine coefficient counts | Restrictions |
| --- | --- | ---: | --- |
| Quadratic | v, x0*v, x1*v, v^2 | 4/4 | v^2 coefficient is nonnegative |
| Polynomial 2 | The same four monomials | 4/4 | All signed |
| Polynomial 3 | Every x0^p*x1^q*v^r with r>=1 and total degree<=3; explicit degree/p/q order | 10/10 | All signed |
| ReLU | v,x0*v,x1*v plus 36 anchored hinges | 39/39 | Nonlinear readouts nonnegative; three base coefficients signed |
| Hinge | Exact coordinate-loop implementation of the same 39 ReLU features and stored readout | 39/39 | Full matching ReLU acquisition/fit charge plus own encoding/audit/storage |
| Cubic spline | Tensor clamped cubic B-splines; omit action-axis index zero | 48/100 | Coarse knots [0,0,0,0,1,1,1,1]; fine adds 1/2 on every axis |
| Linear grid | Tensor linear hats on the actual state grid and five action nodes; omit action-hat index zero | 100/324 | All signed; x0,x1,v tensor order, v fastest |

For each ReLU/hinge unit, wx,wy range in {-1,0,1}, threshold q ranges in {1/8,3/8,5/8,7/8}, and z=(wx*(x0-1/2)+wy*(x1-1/2)+v-q)/4. Its feature is max(z,0)-max(z at v=0,0). Threshold is the fastest unit index. Hidden directions are fixed before labels; only the bounded readout is learned. No neural-specific feature-search advantage is presumed.

**VALUE** minimizes ordinary squared errors to interval midpoints at every paid anchored value context, using `lsq_linear`, fixed tolerance and maximum iterations specified in `models121.py`, under the identical box. This control has access to all paid marginal/probe information; its deliberately declared fitted objective is ordinary value loss.

**MARGINAL** minimizes t under every robust finite-node inequality

    derivative_design_row * theta - t <= lower_target,
    -derivative_design_row * theta - t <= -upper_target,
    t >= 0,

and the same box. The derivative design is D_v(phi)/A(x), in original-action units. At ReLU and grid interior switches use both feasible one-sided branches; at endpoints use the inward branch. The canonical derivative at an exact switch is the right branch unless the specified row requests the left. Smooth families use their ordinary derivative. HiGHS's full constraint order, multipliers, residuals, status and unrounded solution are retained.

The final readout is rounded to 30-bit dyadics, nearest with ties to even, then projected into the declared box. Preserve original binary64 solver values and their actual rounded dyadic integers/denominator/hex identities. An unsuccessful or nonfinite acquisition solver aborts the complete attempt; no zero substitute, alternate architecture or outcome-selected restart is used.

Hinge copies the corresponding paid ReLU readout and raw solver record. It independently assembles the coordinate-loop VALUE and MARGINAL design matrices and requires exact binary equality before storage. It is not counted as an independent fit or independent scientific outcome. Its standalone cost pays its matching entire ReLU model phase in addition to its own identity/encoding/storage and full common labels.

## 6. Independent finite-design fit certification

`training_audit121.py` reads the serialized model, labels, complete `design.json.gz` and `fit.json`. It reconstructs feature values and derivatives using standard-library rational monomials, exact hinge branches, Cox-de Boor recursion and linear hats, with no production feature, optimizer or actor import. It verifies actual 30-bit coefficients, boxes, matrix assembly discrepancies and both losses for every stored model.

For MARGINAL, the rounded primal upper bound is the exact maximum robust node residual. Normalize the nonnegative parts of the stored negative HiGHS multipliers to a rational unit-mass dual witness; if their mass is zero, use the prospectively defined uniform rational weights. Its valid lower bound combines the label term with the exact minimum of the resulting linear form over the declared box. No floating stationarity or exact optimizer claim is needed. Retain the gap and every multiplier, including weak or uninformative witnesses. For VALUE, an exact convex first-order support over the same box gives a valid squared-loss lower bound and gap for the stored coefficient vector. These are finite-design/finite-box optimization certificates, not global neural approximation or economic regret certificates.

All independent fitting audit runtime and witness creation is paid in the full research ledger and separately disclosed in any deployment amortization scenario. The audits cannot modify actors or choose a model subset.

## 7. Actor and common complete original-policy service

For every learned critic at fixed state, list all known action-piece endpoints and every computed real root of each polynomial derivative, evaluate all candidates with the actual declared critic, choose the first minimum in increasing action order, and round the original action downward to 30 bits and downward original feasible capacity. Preserve each piece polynomial, derivative coefficients, every complex root, near-real/in-piece tests, candidate objectives, selected index, and rounded action. Cubic spline and polynomial derivative roots are all enumerated; nonconvex critics are not restricted to one monotone bisection. Floating root enumeration is a strong numerical proposal generator, not an asserted exact global optimizer.

The conventional online comparator uses the original semi-analytic terminal compiler and a 512-midpoint, 24-iteration original root derivative proposal. Every endpoint/bisection proposal value and derivative is retained as a proposal-only record. It uses no fitted critic or label acquisition. It has access to the same original primitive information as every learned arm, which pays every primitive it uses. Equal available information does not mean equal realized query counts.

Every policy receives the same whole-support original certificate initially at 128 cells. A first rejected learned proposal is retained and followed by the same paid online proposal. Unqualified intervals refine at 256,512,1024,2048,4096 cells. Every certificate, terminal payload, reason for refusal, refinement and cost is recorded. Final acceptance requires both original regret<=1/256 and implemented-policy width<=1/8192.

If finite refinement remains unqualified, execute the retained exact rational cover: 1,025 feasible actions, 256 risk cells and at most 80 terminal iterations. The separate Proposition `prop:totalservice121` proves uniform original qualification on the two-dimensional state cube: original root derivative magnitude<=771/128<7; terminal derivative magnitude<=273/64 and derivative Lipschitz constant<10; the terminal target is attained within 31 iterations. Before final directed float conversion the cover width is at most W+14*2^-40 and its admission gap at most W+7/(8*1024)+7*2^-40, where W=238095/2^33<2^-15. These satisfy the unchanged targets with ample slack.

Recoverable numerical `ArithmeticError` (including floating-point/overflow/zero-division subclasses) or `numpy.linalg.LinAlgError` in a valid frozen proposal/production certificate is also routed to this same exact fallback. Retain the failed traceback, partial roots/candidates/certificates, all attempted work and exact recovery cost. Source, domain, corrupt model, I/O and infrastructure failures abort. Failure of the exact fallback itself aborts and is never recursively retried. Acquisition failure behavior is unchanged.

If no finite feasible first proposal existed before a numerical failure, `first_proposal_action` is null and `proposal_numerical_failure` is true; no fictitious neural action is created. Count its nonacceptance as a first rejection with the numerical reason explicit. If a feasible first proposal existed before certificate failure, retain and independently evaluate that action. All final policies remain present. Mathematical totality is conditional on the specified valid input and arithmetic routines; machine/infrastructure failure remains a failed experiment, not a deleted observation.

Each initial-state service call has batch size one. Internal shock nodes may be vectorized. This prevents an inherited whole-batch compiler fallback from coupling distinct state observations. All models/risk levels share each state row, so cross-method contrasts are paired, not independent observations.

## 8. Complete primary and timing censuses

There are seven families times two losses times two budgets, plus the online comparator once per risk: 29 policies. Both risks and all 64 independent states give 58 policy cells and 3,712 primary rows. The canonical identity is `(index,row,budget,arm,loss)`. `index` is 0/1; stored-model budgets are 5/9; loss is lower-case `value`/`marginal`; online has budget 0, arm `online`, loss `online`.

Primary order is risk, then online, then increasing budget, declared arm order `(quadratic,relu,hinge,spline,poly2,poly3,grid)`, then value/marginal. Five fresh serial timing processes use the first 32 original rows, generating 1,856 rows each and 9,280 total. For repetition r and risk i, rotate the full 29-policy list by `(7*r+i) mod 29`. Every model is read afresh per risk/policy cohort; all original services remain singleton. No acquisition is repeated solely to produce timing samples. Preserve all five clocks, medians and ranges. They are descriptive same-machine timing observations, not confidence intervals or controlled CPU-frequency/cross-machine evidence.

After all clocks complete, compare every saved timing action, first-proposal identity, state, qualification and rejection status with its primary record. These 9,280 saved-record comparisons invoke no economic solver. A mismatch fails the attempt while retaining every clock; it does not trigger selective retiming.

## 9. Independent economic evaluation and inference

The separate frozen original-primitive evaluator examines every unique final action and every available first proposal from all 3,712 primary records. It reconstructs exact binary rational state/action identities, uses its fixed 64-cell whole-support midpoint/endpoint integration, exact terminal boundary-sign checks and 32 terminal bisections only for interior cases, and forms independent original-policy and all-action optimum bounds. Deduplication shares validation cost only; all 64 population rows and all method contrasts remain intact. Rejected first proposals are not thinned. The original compiler is not imported into the independent primitive implementation.

Interval overlap is compatibility, not proof of the narrower production endpoints. Original regret and action-error quantities are bounds, not actual errors. The implemented future allowance appears once. Identical original policy keys cancel exactly; broad, adverse and unresolved comparisons are retained. An unavailable raw first proposal remains explicitly missing with conservative scope, while its completed final policy is evaluated.

The held-out initial-state population is discrete product-uniform on the 40-bit grid, conditional on ideal independent OS entropy and frozen actors. It is not silently continuous uniform initial states. The original economic innovation law remains continuous. VALUE-to-MARGINAL gains are signed: uniform qualification permits support [-tau,tau], and no R120 safe-improvement clipping to zero is allowed.

The separate frozen statistical specification covers the two original optimum groups, 58 regret groups, 28 paired training-loss contrasts, 112 signed gain-threshold events and 116 one-sided first-rejection probability endpoints in the declared joint family. Numerical, sampling and timing scope remain separate. Cross-representation sample comparisons or price regions do not acquire undeclared population adoption coverage.

## 10. Full costs, failures and adoption

The program retains nonoverlapping label and per-model acquisition phase clocks, solver/design/rounding diagnostics, model/fit/design serialization times, source gates, imports, artifact verification, all rejected candidates, root searches, original primitive queries, production certificates, fallback, every audit/trace write, loads, complete cohorts and external process/shutdown receipts. Detailed event serialization is already inside the measured phase or singleton clock and must not be double-added.

A learned deployment's measured acquisition component subtotal is its complete risk-label phase plus its complete own model phase; hinge additionally pays its matching whole ReLU phase. Add the full common source/import/residual process overhead, as specified by the full external acquisition clock after subtracting the nonoverlapping label/model phases. Do not charge a model its competitors' fits or the other risk's labels as if it used them. These are declared sums of actual measured components, not a separately observed isolated single-model process. Report complete budget-process research totals independently of this allocation. Final summary/hash/manifest/shutdown costs remain in the actual outer process receipt.

Independent fitting and policy validation costs are actual full-study costs. Deployment reuse scenarios must explicitly state whether these one-time research validation costs are amortized or shown separately, while always paying production certification and refused candidates. Distinguish measured first-32 deployment clocks from hypothetical reuse volumes; reuse is not measured throughput scaling.

Any compute-price condition uses original objective bounds and actual declared cost differences. Retain negative or zero economic gain, unfavorable cost, empty and reversed-price domains, and all conventional alternatives. No neural adoption, full-menu superiority, monetary welfare calibration, higher-dimensional success, long-horizon scalability, or population method-selection advantage is assumed. The two budgets measure a specific acquisition/representation-size change in the unchanged d=2 economy.

All failed acquisition, audit, numerical service recovery, infrastructure and timing attempts retain append-only or exclusive immutable evidence. No first-proposal rejection is erased by successful final qualification. Historical negative results and frozen independent episodes remain separate.

## 11. Stable file and command interface

Each separate acquisition directory contains `labels-{index}.json`, primitive `events/labels-{index}.jsonl.gz`, and `models/{index}-{arm}-{loss}/{model.json,fit.json,design.json.gz,acquisition.json,fit-events.jsonl.gz}`. `ACQUISITION121.json` holds full phase clocks and model component allocations. `ACQUISITION_MANIFEST121.json` binds every file. Each successful mode writes `EXECUTION121.json`; failures append `FAILED121.jsonl` and preserve partial files.

Sampling writes `entropy121.bin`, `states121.json` and `STATE_MANIFEST121.json`. Primary and timing modes write `records121.jsonl`, `attempts121.jsonl`, `actors121.jsonl`, `events/*.jsonl.gz`, `batches/*.json`, `CATALOGUE121.json`, progress and error records. Primary also writes all five `timing/attempt-*/` outputs, launcher logs/receipts and `TIMING121.json`.

Commands, with actual immutable SHA values and exclusive attempt directories substituted by the launcher:

```text
python code121/campaign121.py acquire --budget 5 --source-commit F --output ACQ5
python code121/campaign121.py acquire --budget 9 --source-commit F --output ACQ9
python code121/training_audit121.py --source-commit F --acquisition ACQ5 --output FITAUDIT5
python code121/training_audit121.py --source-commit F --acquisition ACQ9 --output FITAUDIT9
# Publish both complete acquisitions and all actors at M before sampling.
python code121/campaign121.py sample --source-commit F --actors5 ACQ5 --actors9 ACQ9 --actor-commit M --output STATES
# Publish STATES at D before primary decisions.
python code121/campaign121.py primary --source-commit F --actors5 ACQ5 --actors9 ACQ9 --actor-commit M --states STATES --state-commit D --output PRIMARY
python code121/independent121.py --source-commit F --primary PRIMARY/records121.jsonl --output INDEPENDENT
python code121/stats121.py --source-commit F --primary PRIMARY/records121.jsonl --independent INDEPENDENT/comparisons121.jsonl --output STATS
```

All scientific commands are launched through the source-bound `launch121.py`, which records actual argv, dates, thread settings, exit code, stdout and process cost. No execution success is asserted by this prospective document.
