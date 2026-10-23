# Neural Bellman Operators — R125 author revision

This is an author revision for the Econometrica numerical-methods research objective. It retains the original recursive Bellman operators, learned continuation critics, feasible actors, original-optimum decisions and their economic interpretation. It is not an external referee report or a change of research topic.

## Read the current paper

| Document | Source | Compiled PDF |
|---|---|---|
| Current ECTA article | `ECTA.tex` | `build/ECTA.pdf` |
| Complete technical supplement | `supp.tex` | `build/supp.pdf` |
| Development and numerical companion | `appendix.tex` | `build/appendix.pdf` |
| Point-by-point author response | `RESPONSE_TO_REFEREE.tex` | `build/RESPONSE_TO_REFEREE.pdf` |

The main article develops the current economic question and mathematical contributions. The supplement contains the full proof chains. The development companion retains earlier statements, proofs, models, numerical records, failures and negative evidence with their own original scope. Exact original R122 wrappers remain in `historical_wrappers122/`.

## Scientific baseline and protected work

The initial audit catalogued all 366 remote heads, 308 distinct head commits and 268 distinct revision directory trees. The latest complete author manuscript is R122 at `a4c22b50087430cdd42d07b161d696ebce54a858`; its revision subtree is unchanged in the R124 custody parent `51cc45d33f0ecb4ce7aebcdcdd9c5ff6a34637ec`. The later R123/R124 directories contain additional research but no replacement complete four-document author wrapper set. Root README and root LaTeX pointers are not the controlling manuscript.

The latest genuinely deposited controlling advisory is R97 at `9723c6cd2cc8b3e071422f3e522d4a843946db63`, which reviewed `f802fe64d91d9f5c1c8f86123b0fbe114e622279`. All 35 real report bodies and their source manifests are preserved. The nominal R16 branch adds no report; R50 is a threshold screen. This owner-commissioned AI advisory is not an Econometric Society editorial decision.

R123 and R124B retain separate experimental identities and prospective restrictions. R125 did not stop their processes, inspect unpublished B outcomes, reuse their samples, or relabel R124A results as B. Public frozen code imports are explicitly source imports. Runtime observations and publication status are recorded with their as-of times; absence of a process does not establish successful completion. See `provenance/BASELINE_IDENTITIES125.json`, `provenance/REVIEW_PROVENANCE_FINDINGS.md`, and `RUNTIME_ISOLATION125.json`.

## What is new

1. **Complete original Bellman support information.** The new finite convex representation retains every global quadratic minorant. Its bounded-domain conjugate constraints are necessary and sufficient, with a constructive interpolation proof, exact worst compatible action contrasts and a rational residual certificate. The exact action witness improves a guaranteed contrast from −1/4 to −5/8 when the previously omitted support is restored. A direct conventional support calculation also achieves that witness; no neural-specific or conic-runtime advantage is inferred.
2. **Action precision and complete work.** The current theorem connects finite feasible support precision, scalar optimizer localization, complete declared oracle work, terminal action regret and the independent absolute-value-width gate. Its schedule is optimal only for the stated guaranteed-width planning interface. Its oracle cost assumption is not estimated into truth from realized clocks.
3. **A separately frozen executed acquisition study.** The production services compare warm adaptive, cold adaptive and fixed-512 precision with a fully paid strong original-model fused control, all 56 acquired neural and traditional actors, online controls and a fresh 33-action DP control. The new complete-support convex program and the theorem's ideal precision schedule are not falsely described as executed production services.

`provenance/THEORY_CODE_CORRESPONDENCE125.md` separates implemented, inherited, analytic-only and post-freeze diagnostic components. It also records the classical interpolation and tunable-oracle methods on which the new proofs build.

## Prospective numerical identity

The immutable scientific freeze is **`a94e1f43bf64d8cb90af21e4b53d07335c615576`**. Before the first economic evaluation, all 338 published entries were independently read back. `SOURCE_FREEZE125.json` binds 336 scientific files; the two additional published entries are the manifest itself and its file list. `BOUNDARIES125.json` records the actual remote boundary.

The complete four-state census has 234 cohorts and 936 primary decisions; three separate first-state timing processes have 702 decisions. There is no random population sample and no population confidence interval. The original continuous innovation, nested AVaR, constraints, future controller, ordinary qualification and stronger regret target are fixed in `PROTOCOL125.md`. All stored actors and their historical acquisition allocations are included. The cohort identifiers 5 and 9 refer to state-mesh sizes, not a total of five or nine observations.

Read the executed results in `results125/report/RESULTS125.md`, its exact `SUMMARY125.json`, and the current manuscript tables. Raw records include every candidate, precision level, refusal, stop and retained policy. The independent original-economy audit and the saved-certificate algebra replay are separate receipts. Unresolved numerical checks remain unresolved. The post-freeze terminal-gate diagnostic leaves the original service outputs and prospective target counts unchanged.

First-state adoption regions combine first-state economic values with first-state complete timing. Their compute price and amortization volumes are declared sensitivity scenarios, not calibrated demand. Matched hinge identities, traditional winners and empty certified neural adoption regions remain reportable results. No complete all-history research time is fabricated where interrupted historical parent clocks are missing.

A separately labeled post-execution diagnostic exploits exact policy identity. Within each risk, all 116 learned/online services return the same first-state action and implemented future controller, so their true original economic values coincide. Every one of the 128 neural-service/amortization scenarios has an explicit conventional same-policy cost blocker under the recorded acquisition allocations and timing ranges. Positive computation prices therefore exclude those neural services in that conditional scenario; zero price supplies a tie with the blocker, not a victory over other policies. The original 128 nonempty optimistic interval-only regions and 128 empty sufficient regions remain unchanged. The blocker routes are 64 online and 64 degree-two polynomial services, not a matched-feature architectural comparison. Full assumptions and proof are in supplement Proposition `prop:policyidentity125`; exact witnesses are in `results125/ADOPTION_SUPPORT_DIAGNOSTIC125.json`.

## Reproduce and verify

Use Python 3.12 and install `requirements125.txt`. The current experiment's executable dependencies and actor bytes are vendored and hashed; no download from a moving branch is needed. Use a new output directory for every attempt. Existing evidence directories are exclusive and must not be overwritten.

```bash
python -m pip install -r requirements125.txt
python verification125/verify_package125.py --output verification_runs/readback01
python code125/fixtures125.py --output reproduction125/fixtures01
python code125/launch125.py --receipt reproduction125/launch-primary01 -- \
  python code125/campaign125.py --output reproduction125/primary01
```

Execute three timing repetitions with `campaign125.py --repeat 0`, `--repeat 1`, and `--repeat 2`, each through `launch125.py` and into its own output directory. The report adapter expects each timing directory `NAME` to have a sibling `launch-NAME` receipt. Then run the saved algebra replay and independent original economics:

```bash
python code125/verify125.py --primary reproduction125/primary01 \
  --timing reproduction125/timing0 --timing reproduction125/timing1 \
  --timing reproduction125/timing2 --output reproduction125/verification01
python code125/launch125.py --receipt reproduction125/launch-independent01 -- \
  python code125/independent125.py --primary reproduction125/primary01 \
  --output reproduction125/independent01
python code125/report125.py --primary reproduction125/primary01 \
  --timing reproduction125/timing0 --timing reproduction125/timing1 \
  --timing reproduction125/timing2 --independent reproduction125/independent01 \
  --verification reproduction125/verification01 --output reproduction125/report01
```

The independent evaluator uses its declared 8/32/128 bin ladder, terminal bisection budget and total work cap. A repeat can have different elapsed times; it must not replace the original timing record or become an additional independent policy sample.

### Separate post-primary independent audit

The original audit completed with 850/936 interval containments and 193/251 accepted-gain confirmations, with zero contradictions and explicitly unresolved remaining checks. A separate follow-up was designed after those results and frozen at `a5f2047222751217b9660b241b9e63f36d87c53a`; all 20 published entries were read back before its first new economic evaluation at 07:52:25 UTC on 23 October 2026. Its protocol includes all 110 distinct final/prefix action keys from every unresolved record, exactly 512 bins per key, and a cap of 112,750 requested contexts. Exact previously computed terminal witnesses can be reused only at identical state/risk/support identities, with the entire prior audit still charged. This follow-up is not the original prospective experiment or an independent policy sample.

The follow-up actually completed all 110 keys. Together with the unchanged original audit it confirms 934/936 production interval containments and all 251/251 accepted gain bounds, with zero contradictions. Two grid-control containments remain unresolved at the frozen 512-bin cap. It requests 112,750 terminal contexts, reuses 28,270 exact original witnesses and computes 84,480 new contexts with 2,586,336 bisection iterations. The complete parent process takes 1459.236044 seconds, charged in addition to the original audit's 798.515007 seconds. These are verification costs, not production-service times or an independent policy sample. The original 850/936 and 193/251 results remain separately reported. `results125/followup-presentation/RECONCILIATION125.json` reconciles every saved trace row and the phase-cost ledger.

The earlier `primary-checkpoint` manifest at `bac6f997b98cb03c37b81663738b90589cec907b` excluded then-ongoing follow-up outputs. The final `complete` manifest includes the actual completed follow-up and its independent chronology. Neither workflow submission nor an archive's existence is evidence of successful remote CI.

Large witness files use lossless binary transport parts to stay below publication request limits. `verification125/verify_package125.py` reconstructs exact original bytes, verifies all part and logical-file hashes, and refuses to overwrite differing evidence. This transport operation is not a new economic evaluation.

For the four native documents, install a TeX distribution with `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-science`, and Poppler, then run:

```bash
python build125.py --passes 4
```

The build records all commands, tool versions, actual TeX input closures, bibliography inputs, graphic hashes, final PDF hashes and layout/reference diagnostics. It does not execute the economy or regenerate result tables. `verification125/ci_verify125.py` runs the package gate, exact algebra and fixture replays, and all four document builds. It does not claim a fresh original-economy experiment. Actual remote CI state is recorded after the run, never inferred from workflow submission.

### Referee-ready archive

The final release records its exact published author commit, delivery-manifest hash, four PDF hashes, archive hash and the dated actual CI status. `verification125/package_release125.py` builds and verifies the full archive from the complete manifest; the two large logical witness files are represented by their exact transport parts. The archive contains all current source files, full retained source, protocols, response maps and executed numerical evidence. A separately recorded release receipt prevents source/PDF/archive hashes from being self-referential.

When the archive itself is delivered in ordered transport parts, reconstruct it without changing its bytes:

```bash
python verification125/package_release125.py --assemble release125/referee-ready/RELEASE_ARCHIVE125.json
```

Then extract `NBO-R125-referee-ready.zip` and run the package verifier from the extracted `NBO-R125` directory. Reconstructing or checking an archive does not count as rerunning a scientific experiment.

## Preservation and research scope

`CONTENT_RETENTION125.md` and its machine-readable map route every copied original source and the later inherited developments. `response_inputs/HISTORICAL_ITEM_ROUTES125.md` routes all 684 extraction records to preserved report text and author responses; those records are not 684 independent closed issues. The current 30 controlling requests have their own exact response map.

The revision advances action information and complete decision services in the original NBO programme. Neural-specific superiority under matched information, a production complete-support solver, a general multidimensional Bellman information bound, independent refitting, longer-horizon/multi-control/multi-innovation scaling and a calibrated consequential application remain distinct scientific requirements. A successful source build, a negative comparison or a shared certificate is not presented as satisfying those requirements.
