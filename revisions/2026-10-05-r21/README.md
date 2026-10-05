# Neural Bellman Operators — R21

This revision responds to all B1–B8 and M1–M10 items in the latest R18 advisory report while retaining the original title, controlled-economy problem, and complete economic applications. It integrates the R20 future-change evidence into the R19 publication rather than replacing the paper with a different topic.

## Publication

- [Main article, native Econometrica class](build/ECTA.pdf) — [source](ECTA.tex).
- [Technical supplement, complete proofs and records](build/supp.pdf) — [source](supp.tex).
- [Complete economic applications](build/applications.pdf) — [source](applications.tex).
- [Point-by-point referee response](build/response.pdf) — [readable response](RESPONSE_TO_REFEREE.md).

The original paper's 129 source components and 408 labels are retained. Six whole historical sections are relocated, not deleted. The article remains 51 pages; all applications remain 48 pages. New proofs and complete records are in the supplement. Original roots and expanded introduction/conclusion sources are archived.

## Substantive additions

The policy-composition theorem connects verified full-action advantages against a policy's own continuation to multiperiod economic accuracy under explicit order, domain, and Lipschitz conditions. An additive state envelope and a continuous-economy class/value-transfer bridge identify the additional coverage and approximation premises. A sufficient-cost allocation result distributes error allowances across dates. Standard Bellman stability and convex allocation arguments are credited as such.

The previously frozen R20 study contains 168 complete services and 840 future-specific outcomes across changing future policy, technology, and valuation. Check-and-refresh NBO certifies 120/120 outcomes with 48 successful refreshes; unchanged reuse leaves 48 outcomes uncertified. All conventional-surrogate and simulation outcomes remain. The recorded adaptive neural rule is more expensive than fresh neural refitting in every displayed dimension-volume cell; no favorable cost frontier is manufactured.

NBO's saved actions and derivative/curvature certificates imply negative mean optimal current-withdrawal responses to stronger future production and higher future valuation in both state dimensions. These are economic bands derived from neural decisions, not enumeration results relabeled as neural results. The common-action and own-action risk diagnostics preserve the distinction between level error, action-centered error, and decision loss.

## Verification

[Release audit](results/RELEASE_AUDIT.json), [all-certificate audit](results/FUTURE_AUDIT.json), [source preservation](results/PRESERVATION.json), [native compilation](results/COMPILATION.json), and [complete table data](results/FUTURE_TABLES.json) bind the publication to the saved source and evidence.

The full arithmetic audit recomputes all 984 attempted certificates covering 319,062 task actions, plus 120 zero-charge certificates, and compares every certificate field exactly with the original record. It verifies all 168 record digests and recorded timing decompositions. This replay generates no new fits or scientific observations and replaces none of the original clocks. The separate test logs contain 22 new tests and 34 inherited tests.

## Replication

Run from the repository root in the documented NumPy/CPU-PyTorch/LaTeX environment:

```sh
python revisions/2026-10-05-r21/code/report_future.py
python -m unittest discover -s revisions/2026-10-05-r21/code -p 'test*.py' -v
python -m unittest discover -s revisions/2026-10-05-r19-integrated/code -p 'test*.py' -v
python revisions/2026-10-05-r21/code/preservation.py
python revisions/2026-10-05-r21/code/audit_future.py
python revisions/2026-10-05-r21/code/build.py
```

The full certificate replay is CPU-intensive but performs no fitting. The publication workflow rechecks record hashes, regeneration, both test suites, preservation, and native compilation; its release audit also binds the completed full arithmetic replay stored here. Test logs must be saved at the paths read by `release_audit.py` when rebuilding that audit. Do not overwrite the historical R19 or R20 execution directories. A fresh scientific execution must have a new, explicitly labeled output directory and must not silently replace an old measured clock.

The new tables and optimal-response bands are deterministic post-execution analyses of previously frozen data. They are not a new prospective experiment or a general continuous-time HJB certificate. The general theorem's uniform coverage and transfer conditions are stated mathematical premises, not inferred from the finite catalogue. Journal suitability remains a scientific judgment for the next referee.
