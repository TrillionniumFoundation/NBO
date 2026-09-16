# Result-by-result literature comparison

The citations below were checked against primary publisher/proceedings sources. This comparison identifies the result claimed here; it is not an exhaustive novelty search or a claim that no related argument exists elsewhere.

| Object | Closest comparison | R6 treatment |
|---|---|---|
| Fixed-policy affine reward features and reward-weight transfer | Nemecek and Parr (2021), policy caches; Alegre, Bazzan, and da Silva (2022), optimistic linear support and successor features | Credited as prior foundations, not claimed as new. |
| Exact scalar anchor construction using optimistic upper information | Scalar OLS geometry in the above literature | New manuscript proposition establishes the precise full-line/adjacent-pair equivalence used by this implementation. Same-oracle execution compares initial-distribution and simultaneous state/date objectives, not unequal oracle counts disguised as novelty. |
| Full action-value GPI or trained SFOLS implementation | Alegre et al. (2022), Algorithms 1–2 and Theorems 3.2, 3.5, 4.1 | Not equated to this paper's policy-action switching rule; no claim that the R6 scalar experiment reimplements the full trained algorithm. |
| Sensitivity to changing transition laws | Csáji and Monostori (2008), value-function Lipschitz bounds in changing Markov environments | Cited. Lipschitz sensitivity is not itself new; assumptions are used explicitly to bound the additional endpoint cross-term correction. |
| Upper bound from advance information about regime count | Brown, Smith, and Sun (2010), information relaxation and duality | Described as a particular zero-penalty information relaxation; its looser observed bound is retained. No new general duality theorem is claimed. |
| Endpoint reuse when both rewards and positive kernels vary affinely | Corrected-chord theorem in R6 | Derives the signed cross term, a positive backward supersolution correction, and its conditional second-order interval-width bound. A counterexample shows why the fixed-kernel reward chord is invalid here. |
| Uniform welfare gap for fixed feasible policies over a transition-mixture interval | Bernstein conditional-count policy recursion in R6, with ordinary convex-hull/subdivision facts | Exact polynomial identity plus a computable state/date coefficient gap; combined with corrected supersolutions and policy switching, not based on convexity of the optimal value in the transition parameter. |
| Risk-indifference comparative statics | Milgrom and Segal (2002), envelope theorem | General envelope logic is credited. Economic result specializes it to a risk-class duration/effort ratio, gives an explicit sufficient crossing condition and error-to-location implication, and connects it to a matched preference-option decomposition. |

## Primary references

Alegre, L. N., A. L. C. Bazzan, and B. C. da Silva (2022), “Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer,” *Proceedings of ICML*, PMLR 162, 394–413. https://proceedings.mlr.press/v162/alegre22a.html

Brown, D. B., J. E. Smith, and P. Sun (2010), “Information Relaxations and Duality in Stochastic Dynamic Programs,” *Operations Research*, 58, 785–801. https://doi.org/10.1287/opre.1090.0796

Csáji, B. C., and L. Monostori (2008), “Value Function Based Reinforcement Learning in Changing Markovian Environments,” *Journal of Machine Learning Research*, 9, 1679–1709. https://www.jmlr.org/papers/v9/csaji08a.html

Milgrom, P., and I. Segal (2002), “Envelope Theorems for Arbitrary Choice Sets,” *Econometrica*, 70, 583–601. https://doi.org/10.1111/1468-0262.00296

Nemecek, M., and R. Parr (2021), “Policy Caches with Successor Features,” *Proceedings of ICML*, PMLR 139, 8025–8033. https://proceedings.mlr.press/v139/nemecek21a.html
