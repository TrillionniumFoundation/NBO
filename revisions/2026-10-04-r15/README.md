# R15: Neural Bellman Operators

This revision responds to the referee report on R14 commit
`f5021cefa71492babfcbfa580e0c984f59a9de26`. The report was committed at
`7aff61a41a3d28e5eaff73c9fe21e9856110f422` on
`review/econometrica-numerical-methods-r14-2026-10-04-f5021ce`.
Its four original files and exact source identities are retained in
[review_source](review_source/).

The paper retains **Neural Bellman Operators** as its topic. The revision
connects continuation evaluation, a feasible action change, the candidate's
occupation law, implementation error, economic payoff, and complete work.
Endogenous preference formation, recursive utility, temporal selves, and
dynamic games remain in the current manuscript and supplement.

## Reading order

1. [Main article](build/ECTA.pdf), whose authoritative source is
   [the root ECTA.tex](../../ECTA.tex).
2. [Supplement](build/supp.pdf), with full proofs, applications, operation
   counts, every primary stream endpoint, and complete mechanism accounts.
3. [Response to the R14 referee](build/response.pdf), also available as
   [response source](manuscript/response_body.tex).
4. [Source ledger](SOURCE_LEDGER.json), [final publication audit](FINAL_AUDIT.json),
   and [payload hashes](EVIDENCE_MANIFEST.json).

The publisher's `econsocart` class, configuration, and bibliography style are
retained. The article has one authoritative NBO algorithm. The current sources
are reconstructed by [integrate.py](code/integrate.py); they are not a sequence
of appended revision articles.

## Scientific evidence and its scope

### Primary method comparison

[PROTOCOL.json](PROTOCOL.json) fixes two dimensions (10 and 50), four methods,
16 complete execution streams, three possible online checkpoints, and an
independent final assessment. All 128 method executions remain in the evidence.
The four methods are NBO, direct raw-costate learning with four antithetic
continuations per label, direct policy optimization, and a direct neural HJB
method. The HJB baseline includes its derivative and action-search deployment
work. Raw-costate data may be reused; the comparison imposes no one-use handicap.

The primary economy has idiosyncratic volatility 0.6 and common volatility 0.3.
The economic model and topic remain the original capital model. The R14
comparisons at volatilities 0.15 and 0.10 are retained as separate evidence;
they are not pooled with the new environment.

Each method draws uniformly from the **explicitly declared set of 16 complete
execution streams**. Every member is executed. A method mean therefore
averages the entire support of this declared randomized implementation. It
does not estimate an unrestricted distribution over unseen random seeds.
Independent confirmation paths quantify simulation error after all stopping
and selection decisions. Missing or failed fits cannot be dropped: a failed
fit returns the feasible analytical schedule and retains its status and work.

The primary stopping target is a certified gain of 0.0005; 0.001 is a secondary
final-attainment target. The equivalence and material-difference margin is
0.0001 in payoff units, fixed before execution. A confidence interval containing
zero alone does not establish equivalence. The complete work account includes
process launch, setup, unsuccessful checks, fitting, saved-policy reload,
independent confirmation, and durable output. Nonattainment has infinite time
to target and contributes 900 seconds to the prespecified restricted mean.
Recorded operation counts are distinct from claims of equal FLOPs.
Dependency installation and source-artifact extraction precede the measured
method process. Imports, model setup, bound construction, fitting, all attempted
checks, policy reload, independent final confirmation, and durable numerical
output are included in that process clock.

The complete primary run contains 128 successful method executions and no
analytical-schedule fallbacks. Its simultaneous final report is as follows.
The reported endpoints below are rounded outward; decisions use the original
unrounded values.

| Dimension | Method | Mean gain | Simultaneous gain interval | Online stops | Final target certificates | Mean complete seconds |
|---:|---|---:|---|---:|---:|---:|
| 10 | NBO | 0.001268 | [0.000943, 0.001592] | 0/16 | 16/16 | 134.82 |
| 10 | Raw-costate | 0.001267 | [0.000942, 0.001592] | 0/16 | 16/16 | 122.67 |
| 10 | Direct policy | 0.001262 | [0.000938, 0.001587] | 0/16 | 16/16 | 285.53 |
| 10 | Neural HJB | 0.000973 | [0.000647, 0.001299] | 0/16 | 0/16 | 373.35 |
| 50 | NBO | 0.001342 | [0.000957, 0.001727] | 16/16 | 16/16 | 357.80 |
| 50 | Raw-costate | 0.001343 | [0.000958, 0.001728] | 16/16 | 16/16 | 346.22 |
| 50 | Direct policy | 0.001347 | [0.000962, 0.001732] | 16/16 | 16/16 | 596.94 |
| 50 | Neural HJB | -0.000156 | [-0.000558, 0.000246] | 0/16 | 0/16 | 1690.10 |

Online stopping and independent final attainment are separate outcomes. In
dimension 10 none of the procedures stopped at an online check, although every
NBO, Raw-costate, and direct-policy stream met the 0.0005 target in its final
independent confirmation. In dimension 50 all sixteen streams of each of those
three methods actually stopped; no neural HJB stream stopped in either
dimension. No final certificate is used to rewrite this stopping history.
The secondary 0.001 target remains unresolved for every NBO, Raw-costate, and
direct-policy stream in both dimensions.

In the original frozen direct report, the dimension-50 NBO-minus-HJB interval
is [0.001051, 0.001945], which exceeds the declared 0.0001 economic margin.
The direct NBO-minus-Raw and NBO-minus-direct-policy comparisons remain
unresolved in both dimensions. The separate proved paired-transfer account
below retains those original endpoints and reports its own deterministic
refinement on the same statistical events.

At the recorded dimension-50 stopping target, mean complete work is 357.80
seconds for NBO, 346.22 for Raw-costate, and 596.94 for direct policy. Neural
HJB consumes 1,690.10 seconds on average without a successful online stop.
NBO therefore uses less recorded complete work than direct policy in this
experiment; the cached Raw comparator uses less than NBO. These are measured
finite-stream work comparisons, without a claim of identical FLOPs or a
hardware-independent speed ratio.

The raw record and frozen report are in [results/experiment](results/experiment/).
[METHOD_INFERENCE.md](METHOD_INFERENCE.md) states the estimands, simultaneous
events, pairing identities, fallbacks, and work definitions in detail.
The [publication tables](results/publication_tables/) print lower endpoints
downward and upper endpoints upward to six decimal places; method decisions
use the unrounded endpoints. Their manifest binds the original report,
protocol, source manifest, and presentation program. The original numerical
report and its original tables remain unchanged.

The [paired-transfer refinement](PAIRED_TRANSFER_REFINEMENT.md) proves a tighter
deterministic error bound for two held policies driven by common innovations.
It was developed after the numerical source freeze and inspection of the
first trial's transfer width. Its separate proof and postprocessor retain
the original confidence event, samples, clipping thresholds and tails,
arithmetic charges, economic margin, and actual stopping history. Both old
and refined direct endpoints are reported. An analytical fallback keeps its
original complete schedule-relative account. This is a disclosed subsequent
theorem refinement, not a change described as prospectively registered.

The complete refinement replays all 96 stream contrasts and six method
contrasts on the same original events. No samples, probability allocation,
economic margin, or stopping decision change.

| Dimension | Comparison | Refined simultaneous interval | Decision at 0.0001 |
|---:|---|---|---|
| 10 | NBO minus Raw-costate | [-0.000110, 0.000112] | Unresolved |
| 10 | NBO minus direct policy | [-0.000106, 0.000117] | Unresolved |
| 10 | NBO minus neural HJB | [0.000179, 0.000411] | Material superiority |
| 50 | NBO minus Raw-costate | [-0.000133, 0.000130] | Unresolved |
| 50 | NBO minus direct policy | [-0.000137, 0.000127] | Unresolved |
| 50 | NBO minus neural HJB | [0.001347, 0.001650] | Material superiority |

All displayed endpoints are rounded outward. The four unresolved comparisons
establish neither practical equivalence nor the registered noninferiority
condition. The two HJB comparisons establish economically material superiority
for the specified NBO and neural-HJB implementations in the declared finite
stream population. They do not compare all possible HJB algorithms.

### Evaluation mechanism on the deployed candidate's occupation

[MECHANISM_PROTOCOL.json](MECHANISM_PROTOCOL.json) fixes 256 independent action
bridges for each of the 32 returned NBO policies. Each bridge receives two
independent four-path antithetic continuation banks on the 2,048-cell global
assessment grid. The reference continuation excludes the current reward.
The measured costate error includes disagreement between the critic's training
mesh and the assessment continuation.

The finite Bellman bridge gives the gain account

\[
\mathcal R_h(a)-\mathcal R_h(\pi)
\geq \mathcal M_h-\sqrt{\mathcal A_h\mathcal E_h}.
\]

The candidate's actual action also receives an explicit maximization-gap
bound. The account does not substitute a training loss for that gap or assume
that the discrete costate equals the continuous-time costate. Protected
sample arithmetic, clipping tails, representation errors, holding costs, and
payoff transfer enter the final economic endpoint. Individual unbiased
costate-risk statistics may be negative and are retained with their sign.

The raw-costate comparison here measures the risk of one direct continuation
bank on the **same NBO occupation and bridge queries**. The welfare of the
separately trained Raw policy is measured by the primary experiment. These
are different estimands. All mechanism records are in
[results/mechanism](results/mechanism/).

The complete independent assessment covers all 32 returned NBO policies, with
4,096 bridges per dimension and no fallback. The verified curvature modulus is
at least 1.056123 in both dimensions, so the actor-gap branch based on strong
concavity is applicable. The continuous-economy mechanism lower bounds are
approximately -0.006778 and -0.004800 for dimensions 10 and 50. This completed
account therefore does not independently certify a positive mechanism gain.
Its comparison with one Raw continuation bank is also unresolved in both
dimensions: the outward printed risk-difference intervals are
[-0.034445, 0.034394] and [-0.022569, 0.022597].

The cross-bank critic-risk estimate is lower than its Raw-bank counterpart in
dimension 10 (approximately 0.000004499 versus 0.000030179), and higher in
dimension 50 (0.000039793 versus 0.000025923). These are descriptive estimates;
the protected intervals do not establish risk dominance. All range, tail,
arithmetic, holding, and actor-gap terms remain in the report. The mechanism
assessment consumes 901.01 additional process seconds across the 32 policies,
reported separately from the main fitting and stopping work.

### Classical reference and finite observations

The scalar Howard study solves the original-volatility economy on eight
prespecified action/domain/grid configurations. The saved policy tables are
deployed alongside the original scalar NBO and direct policies on common
paths. Its outward algebraic residual bounds concern the finite grid
equations. Grid refinement and domain extension remain separately reported
diagnostics; they are not renamed diffusion-optimality bounds. Full tables,
value arrays, action arrays, and payoffs are in
[results/experiment/scalar](results/experiment/scalar/), with the independent
replay in [results/scalar_report](results/scalar_report/).

On each of the four matched grids, the full-box and radius-0.1 solutions have
identical saved value and action arrays. The monotone comparison principle
and the two independent outward algebraic enclosures give a uniform
time-zero finite-grid restriction-loss upper bound below `1.788e-11`.
The domain-six to domain-nine comparison holds spatial spacing and time
steps fixed. These statements concern the declared common-boundary grid
problems. The classical policies also have higher observed population payoff
than the two frozen neural policies on the fine deployment mesh; the
state-specific NBO-minus-DPO ranking reversal remains in the tables.

The protected-observation study also uses the original volatility regime and
the disclosed R14 parent weights. It assesses four parent/dimension/grid
combinations and all twelve prespecified measurement specifications. The
corresponding parent is reevaluated on each actual implementation grid.
All four parent lower gains are positive; six of twelve measurement
specifications retain a positive lower gain after their sensing allowance.
The complete record is in [results/observation](results/observation/).

### Simultaneous probability and absolute economic accuracy

The R15 error budget is 0.05: online checking 0.01, primary final confirmation
0.02, mechanism assessment 0.01, and protected observations 0.01. The maximum
online family contains 384 two-sided events; the primary final family contains
238; the mechanism family contains 12. Unused events do not recycle probability.
The protected-observation family reserves eight one-sided statements for its
four parent intervals; the sensor transfers use their same parent event.
R14 retains its separate historical probability statement.

The full-class upper gap subtracts an existing method lower gain from the
analytical schedule's population regret bound. This is a deterministic
consequence of the same event and spends no further probability. The resulting
gap is displayed against the economic margin in
[results/economic_bounds](results/economic_bounds/). A positive schedule gain,
a direct method comparison, and a small gap to the original adapted-control
optimum are separate economic conclusions.

The completed NBO upper gaps to the original full adapted-control optimum are
0.025970104 in dimension 10 and 0.036842066 in dimension 50, rounded upward.
They come from the existing population anchor bounds minus the corresponding
method lower gains, without a new probability allocation. The full eight-method
table makes their scale relative to the 0.0001 margin explicit; these bounds do
not establish near-optimality at that margin. The much smaller scalar grid
restriction-loss bound is for a different, explicitly stated finite-grid
problem and is not transferred to this high-dimensional economic optimum.

## Immutable generating sources

| Numerical family | Generating commit | Generating workflow |
|---|---|---|
| Protected observations | `9f968785ac3cccab2bc37b1ec4096a1f5b8301b2` | [37187332674](https://github.com/TrillionniumFoundation/NBO/actions/runs/37187332674) |
| Primary methods and scalar Howard study | `9142f404bb9c5163aa94d3a4ded4d0fa48a49c50` | [37188544814](https://github.com/TrillionniumFoundation/NBO/actions/runs/37188544814) |
| Candidate-occupation mechanism | `b6b63511f5f76308d9073c373a889effe0e9a0c3` | [37195290898](https://github.com/TrillionniumFoundation/NBO/actions/runs/37195290898) |

[PUBLICATION_SOURCES.json](PUBLICATION_SOURCES.json) identifies all generating
and evidence commits. Every family has its own source manifest, original
worker inventories, evidence manifest, and final audit. The mechanism evidence
joins the exact main-experiment Git subtree and records its main-evidence
parent; it does not duplicate or relabel primary training. The publication
source is recorded externally in the source ledger, avoiding a commit that
purports to contain its own identity.

## Reproduction

### Rebuild documents and audit retained evidence

Use Python 3.12 with the exact dependency versions in the frozen workflows:
NumPy 2.3.5, SciPy 1.17.0, Numba 0.65.1, Torch 2.10.0 (CPU), and mpmath 1.3.0.
LaTeX needs the existing publisher files, `pdflatex`, `bibtex`, and Poppler.
The delivery workflow installs its recorded TeX packages and uses fresh
processes for the scientific test modules so that their model constants cannot
leak across tests.

From the repository root:

```bash
python revisions/2026-10-04-r15/code/integrate.py --write-roots
python revisions/2026-10-04-r15/code/build.py
```

The build compiles the main article, supplement, and response with repeated
cross-document reference passes. Undefined references or citations, duplicate
labels or PDF destinations, and overfull boxes fail the gate. The published
PDF hashes and page counts are in [COMPILATION.json](results/COMPILATION.json).

The independent audit takes the immutable publication source from the
delivered ledger, rather than guessing that the evidence commit generated the
simulations:

```bash
NBO_R15_PUBLICATION_SOURCE_COMMIT=$(python -c 'import json; print(json.load(open("revisions/2026-10-04-r15/SOURCE_LEDGER.json"))["publication_source_commit"])')
python revisions/2026-10-04-r15/code/publication_audit.py \
  --repo . \
  --publication-source "$NBO_R15_PUBLICATION_SOURCE_COMMIT" \
  --sources revisions/2026-10-04-r15/PUBLICATION_SOURCES.json \
  --strict
```

The audit compares the original worker file inventories and all source Git
blobs, reconstructs the primary and mechanism reports from the original
arrays in temporary directories, independently replays editorial integration,
and verifies the compiled files. An economic outcome is never an audit pass
condition. Rebuilding PDFs can change their metadata and hashes; the audit
must then regenerate the publication manifests for that local rebuild.

### Reexecute numerical studies

Use the exact generating commits above and their retained workflows.
`pipeline_observation.py`, `pipeline_experiment.py`, and
`pipeline_mechanism.py` pack each numerical dependency closure with its
immutable Git identities and execute fresh workers from that bundle. Their
`--help` subcommands document source packing, individual runs, and collection.
The main protocol specifies the complete matrix and balanced within-trial
method order. The mechanism execution contract pins the main workflow and
selected-checkpoint identities. Reproducing a numerical study must use its
generating source, not treat later manuscript edits as the historical source.

[REPRODUCTION.md](REPRODUCTION.md) gives explicit commands for complete
source-isolated main, scalar, and mechanism runs, and for report-only replay
against the committed arrays. The mechanism replay uses the exact published
NBO checkpoints and their original main-study source manifest.

## Preservation and exploratory work

All 8,652 blobs from the reviewed R14 tree are preserved byte for byte. The
three previous root reading files are archived as
[r14-ECTA.tex](archive/r14-ECTA.tex), [r14-supp.tex](archive/r14-supp.tex), and
[r14-README.md](archive/r14-README.md). All original mathematical statements and
proofs remain in the current paper under the documented editorial
normalization. [EDITORIAL_MAP.json](EDITORIAL_MAP.json) maps every historical
label; [MATHEMATICAL_PRESERVATION.json](MATHEMATICAL_PRESERVATION.json) records
the independent statement-level comparison. Repeated raw-configuration tables
remain in the exact indexed archive.

[exploratory](exploratory/) retains successful and unsuccessful development
fits, arrays, configurations, and their hashes. Its disclosure distinguishes
exploratory feasibility evidence from the frozen confirmatory design. The
early exploratory script was not separately committed before those runs;
the archive states this limitation explicitly. These fits do not enter the
primary confidence family or replace any declared execution stream.

## Delivery branches

- `revision/econometrica-nbo-r15-source-2026-10-04`: frozen publication inputs.
- `revision/econometrica-nbo-r15-2026-10-04`: complete current revision.
- `revision/econometrica-nbo-r15-evidence-2026-10-04`: identical complete
  publication and original evidence.
- `revision/econometrica-nbo-r15-referee-2026-10-04`: identical review copy.

The final three branches are created together at one audited commit. The
historical paper, numerical sources, and review branches keep their original
identities.
