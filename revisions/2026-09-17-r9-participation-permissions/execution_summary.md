# Executed R9 evidence and complete manuscript build

Review baseline: `8c20474bca5b7388f5ba4640ec165f1ad8f5e91a`.
Verified historical/numerical input entries: **398**.

## Manuscripts

- `ECTA_R9.pdf`: **66 pages**; SHA-256 `7e08cd9e5f4b91d6e9595c415ecb2c854303eaffa61b7591516535c1e37eb9fd`; no overfull boxes or unresolved-reference warnings.
- `SUPP_R9.pdf`: **39 pages**; SHA-256 `7cc0fe2a4cd1f97417dcdca70e162e1fee8b9490b3c0ccdf5b95d5992b57c623`; no overfull boxes or unresolved-reference warnings.

## New executed evidence

Small models: 12 models, 120 class-point comparisons, 81 enumerated policies per class and point; maximum error 4.44e-16.
Full-model validation: 80 class-point comparisons; selected-control reconstruction error 4.44e-16; polynomial replay error 4.44e-16.

Economic runs: 19 central fee/term specifications and 20 additional fee/contract rows, each with four class values and moments; 16 all-action supersolution checks; eight sufficient enforcement bounds; nine two-regime permission comparisons; eighteen reoptimized benefit roots.

The noncancellable center participation saving is 0.035247995981 utility-numeraire units.
The sufficient one-interval regional fee bound is 0.834859280561, rounded upward in the manuscript.

## Regional certificates

`noncancellable_certificate`: chord: adjusted [6.869488335715121e-05, 0.00032472964534823714], no-adjustment [-0.00036967726438774087, -5.2801250905126975e-05], both signs = True; count: adjusted [6.869488335715121e-05, 0.00032472964534823714], no-adjustment [-0.00036967726438774087, -5.2801250905126975e-05], both signs = True
`fee_080_certificate`: chord: adjusted [6.869488335715121e-05, 0.00032472964534823714], no-adjustment [-0.00036967726438774087, 0.0013925796303003665], both signs = False; count: adjusted [6.869488335715121e-05, 0.00032472964534823714], no-adjustment [-0.00036967726438774087, 0.0013925796303003665], both signs = False
`fee_085_090_certificate`: chord: adjusted [6.869488335715121e-05, 0.00032472964534823714], no-adjustment [-0.00036967726438774087, -5.2801250905126975e-05], both signs = True; count: adjusted [6.869488335715121e-05, 0.00032472964534823714], no-adjustment [-0.00036967726438774087, -5.2801250905126975e-05], both signs = True

The negative intermediate-fee relative option, failed fee-0.80 region and adverse corner, free surrender, and both adverse initial-permission extensions are retained. The fee-0.85-to-0.90 certificate uses the original law/benefit rectangle.

## Preservation and target boundary

Every inherited main/supplement input is retained, with the four R9 integration copies mapped to their R8 origins. The previous active index remains unchanged as a suffix. The git preservation record, when built on GitHub, additionally checks the entire diff against the reviewed baseline.

These runs do not retrain a network, rerun historical fine settlement grids, establish an optimal contract-design result, enclose the exact transition constructor, certify global uniqueness of benefit roots, or transfer a sign to the diffusion. Numerical targets and assumptions are stated in the paper, response, and replication README. The source inventory and output hashes identify this actual execution; timing and environment fields can differ across executions.
