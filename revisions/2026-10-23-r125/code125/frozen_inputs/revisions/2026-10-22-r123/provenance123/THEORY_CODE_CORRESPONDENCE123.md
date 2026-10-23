# R123 theory and code correspondence review

## Scope and conclusion

This review compares `new123/memory_main123.tex`, `new123/proofs123.tex`,
`code123/envelope123.py`, `code123/service123.py`, and `PROTOCOL123.md`.
It also inspects the vendored R122 support extraction, derivative recovery and
outward conversion used by the service, and the inherited definition of
`up`. No held-out states, economic outcomes, timing outcomes or adoption menus
were read for this review. This is a mathematical and source correspondence
review, not independent confirmation that a particular numerical run completed.

The normal certificate and selection paths match the stated theorems and
protocol. A partial-menu failure logging issue was identified before source
freeze, corrected by the implementation owner, and rechecked as described
below. No remaining mathematical/code mismatch was identified in this scope.
No theorem or experimental protocol was changed by this review.

## Correspondence

| Mathematical obligation | Executable implementation | Review finding |
| --- | --- | --- |
| Transport original derivative intervals using the correct curvature on each side of an anchor | `transport`, `partition`, `gradient` | The lower bound uses L left and mu right; the upper bound uses mu left and L right. All anchors and affine crossings are retained. Global interval compatibility is checked at every relevant partition endpoint. |
| Integrate signed action contrasts, including negative displacements | `contrast` | Moving left negates the upper-derivative integral for the lower contrast and the lower-derivative integral for the upper contrast. Identity contrast is exactly zero. `best_single` chooses the best bound over all anchors separately for each pair. |
| Compute the robust proposal and common feasible menu | `envelope_root`, `robust_proposal`, `candidate_menu` | Endpoint roots and zero-derivative cases match the theorem. Both modes use the same fused and individual proposals, six fractions, duplicates, and downward 30-bit realization. All certification is recomputed at the realized action. |
| Minimize the robust raw support envelope globally | `raw_support`, `support_minimum` | Interval slopes can create downward derivative jumps. The code partitions at anchors and crossings, checks each active quadratic's stationary point and all endpoints, and evaluates the actual maximum of raw supports. No global convexity assumption is used. |
| Qualify the original implemented policy | `candidate` | The absolute upper includes one future allowance. The changed-action gain uses one allowance; an identical action pays none and cannot be an accepted strict improvement. The common fused absolute lower and common optimum lower are used in both comparison modes. The incumbent bound and newly computed support bound are combined by maximum. |
| Preserve qualification after conversion to binary64 | `float_certificate`, `choose`, vendored `directed_float`, inherited `up` | Rational lower and optimum bounds are rounded down; the upper is rounded up. Regret and width differences are rounded upward again. A candidate must satisfy both exact and outward predicates. Its certified gain remains an exact rational string. |
| Purchase only the declared additional action information | probe branch in `service` | One 128-cell original query is started only after the initial fused menu has no accepted candidate, the optimizer bracket has positive width, and the rounded midpoint is not already an anchor. The initial ledger is retained and extended; no repeated-query or automatic-halving claim is made. |
| Preserve original source and economic identity | `make_case`, `payload`, inherited `recover` | State and risk are checked. Curvature, finite-radius recovery and the original gradient cap come from the inherited original-model construction. `original_q_upper` is formed before adding the separate future-policy allowance, preventing double counting. |

## Mathematical scope and stopping

The envelope extremal and randomized minimax propositions explicitly discard
absolute levels, raw support constraints, the global gradient cap beyond the
supplied anchor intervals, and investment formulas. Their sharpness therefore
concerns the reduced scalar derivative interface. The executable service uses
richer information, so those propositions are not claimed as full-payload
optimality or as a lower bound against every conventional algorithm.

The optimizer bracket concerns the original optimal-future objective q. It
need not contain the optimizer of q+eta when eta is arbitrary. The queried
midpoint may round outside a sufficiently narrow old bracket: intersection
with the old bracket still proves the stated bound with explicit rounding
radius r. A wide new derivative interval may establish only nonexpansion.
A duplicate midpoint purchases no information and earns no contraction claim.

The geometric repeated-query contraction and economically priced stopping
rule are conditional mathematical results. The current experiment implements
the frozen finite menu and at most one additional probe. It does not implement
an unrestricted precision search or calculate the theoretical remaining-gain
ceiling as a sampling policy. The protocol supplies no outcome-dependent
study stopping rule. Retention after an unresolved menu is an explicitly reported
qualified incumbent, not a successful improvement.

The original application has mu=2. Its reported root action-distance bound
sqrt(regret upper) follows from strong convexity and nonnegative future error.
The realized 30-bit dyadic action is exactly representable in binary64 over
the application's capacity range. The final outward square root uses the
inherited floating-point interval convention.

## Failure accounting disposition

In the initially inspected implementation, a recoverable error partway through
a locally constructed candidate menu could discard candidate records before
returning them to `service`. The complete elapsed service time still charged
that work, but candidate attempt counts could omit it. This was an accounting
issue, not a failure of an accepted certificate.

The owner corrected `choose` to update a persistent progress record before each
attempt and retain completed candidates, the current stage and a failed
attempt with its exception. `service` retains an incomplete menu and adds its
started attempts and completed refusals to the respective counts; it returns
the qualified incumbent after the recorded enhancement failure. Completed
successful cases retain their original schema and scientific rule.

A deterministic analytic quadratic fixture was executed after the correction,
without configuring the economic routines or reading outcomes. Its 12 successful
candidate records and selected tie were exactly identical to the earlier
normal calculation. An injected failure at candidate 3 retained 3 started and
2 completed records with failed index 2. An injected outward-conversion
failure at candidate 2 retained 2 started and 1 completed record with failed
index 1. All these assertions passed. These checks concern control flow and
arithmetic accounting; they are not economic experiment observations.

## Reviewed source hashes

The following SHA-256 digests bind the final source bytes reviewed here.
Subsequent changes to these files require a renewed correspondence check.

```text
bdfa0be3992c2ca8b2e50db3ff2ebeb315d3561f86627ef28c956ec961e5ff26  new123/memory_main123.tex
b1e15e0844e742cf8502f7fe69f9734770b549a6a75b37ebdf57ca62d340e8b5  new123/proofs123.tex
b5972471d46144fd2a858efd28b2f86bfe484e594557a8d206bd7c6d8472b749  code123/envelope123.py
5158afd322c70dd24d9da3ea922d2e41d2fc0add2d28dcc122113e6de576003a  code123/service123.py
6211b2a56f9d2ac9df06630426f4fa7006a633a16075781fa139f0e3366ad7f2  PROTOCOL123.md
28686ec3d59222bde4af772518a6b4b4bdfcbc6908584798011f9f17d55d3fd8  vendor/2026-10-20-r122/code122/service122.py
93dbb17a8fbe4ba69734b3be4e719312aa4f1138c47c93c8147cbb092924f5cf  vendor/2026-10-20-r121/code121/labels121.py
55cf99152dad7ebf25c0155810d93467f9c4bc9ffb566e4f0966d60d1bde6588  vendor/2026-10-20-r121/frozen108/code/interval94.py
```
