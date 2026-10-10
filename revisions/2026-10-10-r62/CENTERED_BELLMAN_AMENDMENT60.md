# R60 common-reference Bellman extension — 9 October 2026

The initial R60 uncentered interval calculation was observed before this extension was designed. Its maximum datewise bounds at state resolutions 8, 16, 32 and 64 were approximately 2.18231, 1.12578, 0.59109 and 0.30286. It attained the declared tolerance 1/2, but not 1/4, 1/8 or 1/16. These outcomes and their full work records remain part of the revision. The following extension is not retrospectively described as part of that prespecified first experiment.

## Mathematical intervention

The economic primitives, original continuous state and innovation laws, d=2 and T=2 are unchanged. Let h_t be the value of the installed zero-investment policy, and let A_t^0(x,a)=c_t(x,a)+beta P_t^a h_{t+1}(x)-h_t(x). Instead of storing unrelated extrema of absolute values, store lower and upper excess-value bounds relative to the same h_t. A lower action cover encloses A_t^0+beta P lower_excess; an implementable upper candidate encloses A_t^0+beta P upper_excess. The common h_t cancels in the difference of upper and lower bounds at the same true state.

The reference value is not observed or fitted as an oracle. At the final date the original analytic action-difference identity computes A_t^0. At the preceding date common-innovation, centered polynomial state differences compute its exact signed integral enclosure from primitives. These are the previously verified identities in directed53.py. Only the excess-value endpoints require rectangle range tables. All proposed actions remain feasible throughout their state cells, and the lower intervals still cover every continuous feasible action.

## Frozen execution

After disjoint exact checks, SOURCE_FREEZE60C.json binds centered60.py, tests_centered60.py and this amendment to the unchanged R60 source freeze. The five (state resolution, action cover count, innovation bin count) rungs are (8,8,4), (16,16,8), (32,32,16), (64,64,32), (128,64,32). Every rung is executed; none is omitted after seeing a favorable outcome. The fixed tolerance catalogue is 1/2, 1/4, 1/8, 1/16 and 1/32. First attainment uses the unrounded outward maximum datewise bound. Every earlier rung and its serialized arrays are charged. Timing is a single-host observation; it is not combined with prior hosts into an invented controlled comparison.

The upper policy is nonworsening relative to zero. For the zero current action, a continuation already verified nonworsening has a nonpositive true excess; this exact fact may tighten an outward endpoint at zero. No other candidate is clipped to a favorable sign. Both lower and upper tables, every chosen policy, raw hashes, target classifications, environment and cumulative clocks are retained.

## Deterministic revalidation of existing returned policies

Publication reconstruction may additionally apply the same fixed N=128, A=64, q=32 verification cover to each distinct already returned d=2,T=2 R60 policy. It uses the original acquired actor's full rectangle action range, not a smooth interpolation, to enclose its true excess value. Subtracting the centered lower Bellman endpoint gives a bound for that particular returned policy against the original optimum. This is deterministic post-selection certification of a fixed policy, not new training, a new policy, or an additional independent cost sample. Its verification work is separately recorded and is not silently added to or subtracted from the original prospective stopping clock.

The manuscript reports the original uncentered, centered-construction and fixed-policy revalidation results separately. A tighter constructive conventional benchmark is not relabeled as a neural-only accuracy or scaling advantage. All unsuccessful declared tolerances remain unsuccessful, and all hypotheses of the common-reference bracket are stated in the paper.
