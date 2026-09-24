# R32: constructive coupled certificates and global boundary optimization

## Submission objects

- `ECTA_R32.pdf` / `.tex`: main Econometrica-class article.
- `SUPP_R32.pdf` / `.tex`: full analytic proofs and every registered configuration.
- `RESPONSE_R32.pdf` / `.tex`: separate responses to R30-F1--F12 and T1--T10.
- `COMPUTATION_R32.pdf` / `.tex`: exact reproduction and accounting.
- `HISTORY_R32.pdf` / `.tex`: lossless inclusion of all five R30 documents and their earlier lineage.

The referee source is `reviews/2026-09-24-econometrica-r30/referee_report.md`, commit `e9bc144fbb6843d6a3436825a28584efb64fb8f1`, reviewing `3394815f4ccbf5917582c8f756b535adf87783cc`. The revision preserves the R31 protocol/amendments at parent `6ea1e2fd8ab1928ded4ea98dc74ba6e1e72cf9d0`. Work is isolated to `revision/econometrica-r32-constructive-certificates-2026-09-24`.

## Scientific additions

The action-dependent maintenance example constructs its upper Bellman witnesses, exact own-policy values, admissible action class, and minimum intervention costs from the economic primitives. Shape-preserving dyadic encoding has an explicit global error check. The independent checker does not call the optimizing envelope constructor. The 42 primary configurations all pass; six separately labeled occupancy-stress cases exhibit strict dynamic-versus-pointwise cost savings, while 36 equality cases remain. Twelve spline cases additionally have globally optimal zero-intervention certificates. No neural raw candidate passes its operating target (0/18). No neural-specific speed advantage is claimed.

The original active-boundary constant-control problem now has a complete global optimizer theorem: positive derivative bounds 8163/125000 and 47251/125000 cover the two halves of [-1/5,1/5], including the distant-boundary error, so the unique scalar optimizer is theta=1/5. The endpoint payoff enclosure is explicitly inherited from R30; it was not recomputed.

The original whole-domain current-state target remains .01 with retained bound 7.181834580823298. The auxiliary model and scalar theorem do not instantiate the original 47-coordinate derivative/residual bridge or establish a high-dimensional speedup. These distinctions are explicit, not hidden failures.

## Reproduce

Use Python without `-O`. Install NumPy 2.3.5 and CPU PyTorch 2.10.0. From the repository root:

```bash
R=revisions/2026-09-24-r32
for H in 4 8 12; do
  python "$R/replication/study.py" "$R/results" --horizon "$H"
done
python "$R/replication/boundary.py" --output "$R/results/boundary.json"
python "$R/replication/audit.py" --folder "$R/results"
python "$R/replication/report.py"
bash "$R/build.sh"
```

`results/H*.json` retain exact fractions, complete stage costs, every raw policy, all price intersections and ties, and matched controls. The gzip files under `results/certificates/` contain complete proof objects. `results/independent_audit.json`, `tests.json`, and `boundary.json` are the independent checks. `PUBLICATION_MANIFEST.json` hashes sources and evidence; `DELIVERY_MANIFEST.json` hashes the final PDFs. Main tables are generated from the complete records, not hand-edited numbers.

The original local exploratory/timing attempts are preserved separately. A clean remote reproduction is stored as the primary execution; it does not erase those local records. Timings are single-machine descriptive measurements, including fresh-process neural initialization, not a statistical claim of machine-independent speed.
