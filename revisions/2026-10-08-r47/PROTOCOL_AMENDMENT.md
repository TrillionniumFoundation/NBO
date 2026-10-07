# R47 pre-execution implementation amendment

The economic primitives, dimensions, horizons, prices, targets, sample sizes, margins and repetitions in STUDY_PROTOCOL.md are unchanged. No full R47 study has been executed at this amendment.

## Exact witness-preserving tensor compilation

The uniform tensor state grid permits an exact separable L1 min-convolution. Two rational sweeps along each coordinate compute the closed node labels and an ORIGINAL attaining witness index. At an off-grid state, the witnesses stored at the 2^d corners of its enclosing cell contain an attaining original cone. The defining continuation and action witness are therefore evaluated by at most 2^d original cone scores, not by all (N+1)^d scores. Prove this equality for arbitrary node labels, not only Lipschitz-consistent labels. Retain action identities and use a deterministic lexicographic tie convention in the compiler. This generalizes the retained exact scalar compiler; it is not a claim that distance transforms or min-convolution are new. Credit the distance-transform literature and give the SAME compiler to the non-neural implementation.

The construction benchmark uses the shared compiled min-plus evaluation, with an explicit affine/ReLU realization tested on the identical stored data. Representation benchmarks report flat min-plus, compiled min-plus and compiled ReLU separately. Shared compilation must not be attributed to an exclusively neural speed advantage. The circuit value is a continuous ReLU function; the cell lookup and witness selector remain numerical comparison operations and their work is charged.

## Feasible nets and arithmetic

Node action j*b(x)/N is rounded DOWN to 20 binary fractional bits using exact integer arithmetic. The action-cover radius is consequently bounded by 1/(4N)+2^-20; include this term in every certificate. State nodes are exact dyadics. Query labels are binary64 dyadics, and the maximum difference between a stored label and its outward continuous-law query enclosure is charged as the query error. The tensor compiler uses exact rational additions/comparisons and stores bit-length and operation counts. Ordinary query evaluation uses outward binary64 arithmetic. The continuous-law midpoint remainder is beta*L_future*d/(32M), where M=2N. The terminal quadratic is evaluated directly rather than approximated by a terminal grid.

For multilinear fitted-value iteration, certify its own Lipschitz constant from all cell-edge slopes. Strengthen the nearest-node actor allowance by evaluating the multi-affine expression on the complete half-grid cell corners, including all tied nearest nodes. Do not handicap this baseline with an unnecessarily separated critic/actor certificate.

Finite-acquisition evaluation chooses a witness by the least outward upper score. Charge a uniform score-evaluation allowance as well as the state-cell radius. For an uncertain simulated state spanning more than one acquisition cell, return a conservative interval containing all possible implemented actions and record the ambiguity; do not silently use a midpoint actor. The resulting path interval is used in inference. Exact integer moment reconstruction from outward dyadic endpoint arrays removes floating summation uncertainty from the statistical calculation.
