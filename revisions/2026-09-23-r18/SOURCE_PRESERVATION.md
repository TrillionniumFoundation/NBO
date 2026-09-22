# Preservation and scientific identity

The base tree is the existing R17 result commit `982326994c8550db4e039d915c225a9ace8e3044`. The latest R16 report and all earlier manuscripts, derivations, proof appendices, experiments, raw neural weights, numerical results, and review reports remain at their original paths and blob identities.

The R18 paper directory begins from a copy of the R16 paper components. New sections and proofs are added, while historical sections are labeled by the experiment they describe. The R14 proof and supplement inputs remain included from their original, unchanged paths. The stationary finite-MDP policy-iteration lemma remains with its proof as auxiliary theory, rather than an analysis of an algorithm that was not executed. The quadratic inventory example remains, with its two-mode reduction explicit. The original price-library threshold result, unsuccessful 0.005 refinement, multi-seed adverse results, and independent-arithmetic qualifications remain available and discussed.

The original title, economic model, control set, author attribution, and neural `0.01` accuracy target are not changed. New nonlinear-planner results and budget-feasible library compensation are separate scientific objects. A successful software test is not treated as closure of the original accuracy requirement.

`replication/publish_manifest.py` checks that the tracked diff from the base has no deletions or modifications of historical paths; all changes must be additions under the declared new R18 paths. It additionally verifies the full R17 scientific SHA-256 manifest after computation. These two checks address different risks: tree preservation and scientific-input integrity.
