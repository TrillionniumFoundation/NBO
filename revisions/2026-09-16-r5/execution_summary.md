# R5 executed results

Source commit: `84a4f2ba53d301dbd08af96bc3f7018b43acb0ec`. Source-byte verification: `True`.

## Nonlinear stopped finite economy

Menu: 1565 common actions plus three frozen R4 policies, 1568 per node. Grid 33×49, eight dates. 47 anchors cover all `d` in `[0,1]` at `k=2`.

Maximum certified all-date, all-state, entire-interval welfare loss: **0.000930697560362**; target `0.001`. Independently evaluated repaired-policy feasible gain: **4.4408920985e-16**. Normalization identity error: 1.7763568394e-15.

| Original seed | Largest expanded-menu gain | Focal welfare loss | Population welfare loss | Largest all-date/state loss |
|---|---:|---:|---:|---:|
| 101 | 0.228318365 | 0.00105779455 | 0.000730229656 | 0.236121672 |
| 202 | 0.215071204 | 0.00140569526 | 0.000782837859 | 0.245815365 |
| 303 | 0.22856769 | 0.00121733068 | 0.000800292999 | 0.236109352 |

Entire-interval portfolio-sign groups (unrounded endpoints; focal state and date zero):

- negative: [0, 0.36101794261747294].
- unresolved: [0.36101794261747294, 0.37365383213921638].
- positive: [0.37365383213921638, 1].

## Executed contract-query workload

101 complete-policy queries. Preparation 87.474823s; reuse including full policy evaluation 1.432573s; direct backward solutions 184.862019s. Online ratio 129.0419; preparation-inclusive ratio 2.0793. Largest independently observed loss 0.000240922035234. Timing is machine-dependent.

## Same-weight resource ablation

| Dimension | Seed | Actor loss upper | Zero-start loss upper | Full PSD quadratic loss upper | Actor–zero cost difference |
|---|---|---:|---:|---:|---:|
| 4 | 101 | 0.000644631968 | 0.000644631968 | 0.00220339196 | 1.3302e-11 |
| 4 | 202 | 0.000488447419 | 0.000488447422 | 0.00206523724 | 4.6742e-11 |
| 4 | 303 | 0.00052328131 | 0.000523281306 | 0.00320259038 | 1.2556e-10 |
| 8 | 101 | 0.000428891332 | 0.000428891333 | 0.00669173704 | 5.3388e-11 |
| 8 | 202 | 0.000460682527 | 0.000460682545 | 0.00292674386 | 1.1039e-10 |
| 8 | 303 | 0.000202658095 | 0.000202658104 | 0.00166781216 | 4.7163e-11 |
| 16 | 101 | 0.00054098961 | 0.000540989605 | 0.00620477367 | 2.6795e-11 |
| 16 | 202 | 0.000566516267 | 0.000566516268 | 0.00677694151 | 2.3397e-11 |
| 16 | 303 | 0.000523545394 | 0.000523545395 | 0.00544414898 | 2.0111e-11 |

All actor and actor-free cases meet the `10^-3` declared target. The full convex-quadratic comparator is fitted by projected convex least squares; its reported failures are relative to this class and budget, not all non-neural approximations.

| Fresh queries | Loss upper | Critic training + query seconds | Matched reference seconds | End-to-end ratio |
|---|---:|---:|---:|---:|
| 32 | 0.000602443905 | 0.852085 | 0.151673 | 0.1780 |
| 128 | 0.000657372446 | 0.930791 | 0.420170 | 0.4514 |
| 512 | 0.000657372446 | 1.411624 | 1.476712 | 1.0461 |
| 2048 | 0.000675399489 | 3.411242 | 5.707676 | 1.6732 |

## Persistent capacity game

Survival 0.8, 12 dates, eight states, two players. All-date full unilateral gain 4.4408920985e-16; maximum product of best-response slopes 0.090397707211. Capacity-dependent policy range 0.654331085; early-date range 0.228983192. A deliberately distorted late-date action is detected independently.

## Verification scope

all declared assertions passed. See `replication/r5/output/validation.json` for individual replays and thresholds, and `manifest.json` for identities/environment. These are finite-model double-precision certificates and complete-tree pointwise certificates, not uncomputed diffusion or continuous-action guarantees. Source and build success do not assert editorial acceptance.
