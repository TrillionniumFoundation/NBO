# R34 referee reading entry

**Certified Bellman Operators with Neural Proposals: All-Restart Bounds for Costly Policy Revision**

Based on the complete latest available R30 report, the executed R32 record, and the staged R33 source archive. This branch contains a fresh exact execution and a new theorem and experiment exploiting simultaneous operating feasibility at every restart.

## Documents

- [ECTA_R34.pdf](ECTA_R34.pdf) — 22 pages; [LaTeX source](ECTA_R34.tex).
- [SUPP_R34.pdf](SUPP_R34.pdf) — 12 pages; [LaTeX source](SUPP_R34.tex).
- [RESPONSE_R34.pdf](RESPONSE_R34.pdf) — 6 pages; [LaTeX source](RESPONSE_R34.tex).
- [COMPUTATION_R34.pdf](COMPUTATION_R34.pdf) — 3 pages; [LaTeX source](COMPUTATION_R34.tex).
- [HISTORY_R34.pdf](HISTORY_R34.pdf) — 305 pages; [LaTeX source](HISTORY_R34.tex).

## New theorem and complete audit
The new restart-propagated certificate constructs a global cost lower bound from two-sided operating witnesses and unrestricted support values. It retains every action, covers randomized Markov rules, states the precise feasible-history extension, and is checked using whole-cell inequalities and exact proof selectors without invoking the envelope optimizer.

**294 independently checked certificate objects:** 168 support solves, 42 freshly reconstructed class controls, 42 primal-dual summaries, and 42 new propagated bounds. All 42 deployments satisfy their unchanged operating tolerance and preserve installed returns. All 18 installed-neural cases reduce cost relative to the class minimum. The new propagation tightens 22 global intervals and leaves 20 unchanged, with no extra unrestricted support solve. Twelve spline cases have exact zero cost and global gap; none of the 30 previously positive gaps is claimed closed.

The largest absolute tightening is for horizon 12, epsilon .01, installed seed 31003: the integrated lower bound rises by approximately .261684 while the upper deployment is unchanged. All 42 rows, including zero improvements, and all 28 malformed-certificate tests are retained. Finite-tree tests include randomized mixtures. Remote publication must reproduce all 294 canonical certificate hashes from the locally audited reference.

The original stopped-control all-domain .01 objective and full scalar-boundary proof remain intact. Rational boundary inequalities are rerun; endpoint quadrature is inherited, not relabeled. Neural-specific speedup and the all-domain stopped-feedback target are not claimed as newly solved.

## Reading and replication
Main theorem: Section 6 (restart propagation); results: the section titled "Computed effect of the restart restriction". The supplement includes the precise feasibility class, checker contract, complete 42-case table, and all prior technical details. The response covers F1–F12 and T1–T10 individually.

[Protocol](revisions/2026-09-24-r34/PROTOCOL.md) · [Implementation and provenance](revisions/2026-09-24-r34/IMPLEMENTATION_NOTES.md) · [Publication manifest](revisions/2026-09-24-r34/PUBLICATION_MANIFEST.json) · [Exact reproduction check](revisions/2026-09-24-r34/results/EXACT_REPRODUCTION_CHECK.json) · [Restart results](revisions/2026-09-24-r34/results/restart_summary.json) · [Final independent audit](revisions/2026-09-24-r34/results/restart_independent_audit.json) · [Preservation map](revisions/2026-09-24-r34/PRESERVATION_MAP.json)

Reproduce with `python revisions/2026-09-24-r34/run_study.py`, `python revisions/2026-09-24-r34/run_closure.py`, then the report/build commands in COMPUTATION_R34. All computation uses the Python standard library on fixed installed proposals. Full stage timings, repeated audit costs, and raw exact outputs are recorded.

Frozen parent: `88015b77a0c26e7b883156410b684b229fd7e86f`. Build-source commit: `47cbd3987ec2e56aa7409fbcb6a0c2f8db089902`. Workflow run: `35982984072`. The publication commit is the commit containing this index; it is not embedded in a file hashed into itself. Main, review, and previous revision branches are not modified.
