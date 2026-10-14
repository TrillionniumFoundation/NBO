# Completed R85 prospective original-law evaluation

Execution followed protocol commit 11bb69900bb31fef107f11aa9db66affc9f68a3a and scientific-code freeze e4d0b82fcd3f58729611064025f9ce31c6ded630. The runner source SHA-256 is 24de8fdca201fdb4b5186f6b2134d0559b6cd27691047ce5eec51e22b25c0dde. The controlling R84 review is b030d87d7e96440eb25a3178c94ee6a87940cdb0.

Nine unchanged complete R80 controllers were evaluated on 8192 calibration rows and 131072 distinct evaluation rows, with the frozen seeds and forty-bit original-law bins. There were zero new fits and 139264 new independent rows, counted once rather than per controller. Both full-bin propagation implementations ran on every actor and every row, with exact rational midpoint checks. The scientific interpreter completed successfully; the complete fresh process, including shutdown, took 57.84 seconds on this execution machine, with 56.87 user CPU seconds, 0.93 system seconds and peak RSS 186500 KiB. This is not a cross-machine timing comparison.

Calibration selected calibrated-bernstein-n16 before evaluation began. On the simultaneous evaluation event its regret relative to the best expected-cost member of the nine-controller menu is at most

8304472716111120793481 / 14506999154911107839164416,

which is less than 0.000573 and the declared noninferiority margin 1/256. The evaluation-event failure allowance is 288 exp(-11) < .005 for all 36 pairs and both estimators. Both streams jointly use 576 exp(-11) < .01.

Outward-rounded conditional original-law intervals for selected-minus-comparator:

| Comparator | Lower | Upper |
|---|---:|---:|
| zero | -0.177441 | -0.170788 |
| legacy ReLU n8 | -0.010137 | -0.005786 |
| legacy Bernstein n8 | -0.087292 | -0.081642 |
| legacy ReLU n16 | -0.009460 | -0.005046 |
| legacy Bernstein n16 | -0.086152 | -0.080530 |
| calibrated ReLU n8 | -0.009056 | -0.004812 |
| calibrated Bernstein n8 | -0.004823 | -0.000716 |
| calibrated ReLU n16 | -0.003559 | 0.000573 |

The fine calibrated basis contrast is NOT signed: it supports equivalence at the declared 1/256 margin, not strict Bernstein superiority. The resolution comparison within calibrated Bernstein is signed on the new independent sample. The crossed basis-by-qualification effect, obtained from already covered pairs, is positive at both resolutions. These statements identify the role of qualification and resolution in this original economy, not universal neural dominance.

Full integer moments, raw endpoint identities, all 144 stream-estimator contrasts, and all numerical width components are retained in the local execution archive and reconstructed by the frozen code. The final revision will bind the compact remote evidence, current tables and reproducible source to these outputs. This checkpoint is scientific evidence, not a claim that the revised typeset package or every requested hardware experiment is complete.
