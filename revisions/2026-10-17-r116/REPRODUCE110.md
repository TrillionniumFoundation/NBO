# R110 source, numerical reproduction and publication

## Exact scientific identities

Complete manuscript baseline: R99 f78d7fcec9f657dfec56a0af7899fe967948652d. Controlling report: R97 9723c6cd2cc8b3e071422f3e522d4a843946db63. Unchanged R108 source: 29180a4ce4a6db7298e7458ecdfff3da08abb08f. R110 protocol: f43602de6a29132feceb36d4b323c4c21a9e6ebe. Actual R110 executable freeze: 5e1eae8a7017dd728b71440de3368062700fd747 at 10:54:07 UTC, before primary start 10:54:47.058128 UTC on 16 October 2026.

## Materialize and build the exact current source

From this revision directory:

```sh
python3 materialize110.py
python3 -m pip install -r requirements110.txt
sh code110/build110.sh --publication-only
```

The first command validates archive, fragment and member hashes and restores native response/analysis/build support and the complete empirical table. It refuses to overwrite differing existing files. It does not fit a model or verify a theorem. The build requires pdfLaTeX/BibTeX plus the standard packages in the included preamble and ECTA class. It recompiles all four documents; it never copies historical PDFs into the current build path. Publication-only verification produces an explicitly separate typesetting report, not scientific success. PDF bit identity depends on the TeX/font environment; delivered hashes identify the actual checked PDFs.

## Reproduce both scientific campaigns

```sh
sh code110/reproduce110.sh /absolute/path/to/new-output
```

This refuses an existing output directory and sets one computational thread. It runs the unchanged R108 preflight, acquisition, four-service catalogue, reference and seven fresh timing processes, then its independent arithmetic/kernel audits. It next runs the new six-service gain-budget catalogue, all seven timing processes and the independent Fraction auditor. It preserves logs and stops on failure. The R108 scientific closure is in `frozen108/`. Actual frozen source hashes are checked; no fitted continuation or exact optimal labels are supplied free.

Each fresh run has its own source, host, actor payload, output and clock identities. Do not replace the deposited local measurements with fresh clocks, change theta/menu/catalogue/qualification thresholds under the frozen experiment name, or count a deterministic reproduction as a new population sample. Other frozen experiments are not completed by this run.

## Verify the delivered measured-data package

The accompanying local `NBO_R110_referee_package.zip` additionally contains all `raw110/` measurements, models, logs, full maps and actual checked PDFs. From its extracted root:

```sh
python3 code110/check_delivery110.py
```

This read-only check validates the deposited identities and data without refitting or retiming. To rerun an auditor that writes its new audit duration, first copy the archive to a distinct working directory:

```sh
python3 frozen108/code108/audit108.py records --output raw110/r108-reproduction
python3 code110/audit110.py --output raw110/gain-budget --inherited raw110/r108-reproduction
```

Full default `sh code110/build110.sh` includes the measured-data verification and therefore requires that complete package, not only the Git source checkout. Missing raw files must not be treated as passed tests.

## Limits and failures

Observed scientific versions are in requirements110.txt and all process records. Clock ranges are descriptive; CPU frequency/external load are not claimed controlled. Cumulative process RSS is not isolated arm memory. The broader historical replay ran 435 cases in 21 suites but retained twenty errors and one pinned-file failure. Original errors were not disabled or replaced with fixtures. The exact local PDF/raw archive is not claimed uploaded to GitHub; the final remote receipt distinguishes commits, source recovery and any independent CI runs.
