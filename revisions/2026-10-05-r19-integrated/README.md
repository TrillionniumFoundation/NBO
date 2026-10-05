# Neural Bellman Operators

## R19 integrated revision — 5 October 2026

This revision answers the R18 advisory referee report at `74f0a278aeeb5c62fa556a65f758092621cedf02`, on the reviewed R18 paper `20afc6c1c4828e3c469e7906366bcc8730cc04d0`. It retains the original title, author, general controlled-economy problem, all historical results, and the complete economic applications. It builds on the pre-existing R19 response head and adds a complete integrated publication on a new branch; neither prior R19 branch is overwritten.

- [Main article](./build/ECTA.pdf), [LaTeX source](./ECTA.tex).
- [Technical supplement](./build/supp.pdf), [source](./supp.tex).
- [Complete economic applications](./build/applications.pdf), [source](./applications.tex).
- [Point-by-point response](./build/response.pdf), [response text](./RESPONSE_TO_REFEREE.md).
- [Execution and report audit](./results/REPORT_AUDIT.json), [all 252 records](./results/registered/), [complete protocol](./protocols/DESIGN.json).

### Additions

The revision proves a centered-risk decision-loss bound, a continuation-transport theorem for bounded changes in future economic primitives, an explicit sufficient amortization class with fitting and cache costs, and a true-objective strong-concavity certificate with explicit interval arithmetic. An exact replay of the already-frozen capital design executes seven procedures at query volumes 1, 4, 16, 64, 256, and 1024 in dimensions 10 and 50, across three complete fitting/cache streams. Every failed check and attempted fit is charged. Conventional quadratic and radial-basis continuation regressions, a shared conditional actor, cached SAA, and full-support enumeration remain in the comparison. Prediction risk, scalar-interval decision loss, original vector-catalogue regret, and full diffusion or equilibrium targets are not conflated.

### Replication

From the repository root, install the documented NumPy, CPU PyTorch and LaTeX dependencies, then run:

```sh
python ./code/study.py --out ./results/registered-replay
python -m unittest discover -s ./code -p 'test*.py' -v
python ./code/build.py
```

Do not overwrite an existing evidence directory. `report.py` generates publication tables from the declared `results/registered/SUMMARY.json`; a new timing environment must be labeled as a replay, not silently substituted into an old table.

The new integrated replay is not counted as extra independent streams. Its seven methods use three original streams, two dimensions, and six query volumes. The readable descriptive design is reconstructed from the frozen code, not a backdated replacement for the missing original design file.

The final publication uses the native `econsocart` class. Exact replaced roots and the answered report are retained in [./archive/](./archive/). No claim is made that the new finite-support scalar certificate validates an uncomputed continuous-time HJB or an unmeasured training-stream population.
