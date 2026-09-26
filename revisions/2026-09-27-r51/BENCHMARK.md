# Controlled-density benchmark specification (R51)

The target is an infimum over Borel Markov policies with fresh row randomization, not over a root lottery of persistent plans. There are two dates, two actions (0 installed; 1 revision), state [0,1], uniform initial law, discount beta and all-state operating allowance eps. All JSON numbers are exact rational strings. `g`, `h`, and `k` list intercept and slope; `c` is positive; `theta` has one coefficient per action.

At date 1, rewards are (0,h(y)), costs (0,c*h(y)), terminal reward and cost zero. At date 0 the density is 1+theta[a]*(2*x-1)*(2*y-1). Rewards are -beta*P[a]h-g(x) for action 0 and -beta*P[a]h for action 1; costs are (0,k(x)). Thus V1=h and V0=0. The checker verifies positivity, h>=eps, 0<beta<1 and |theta[a]|<=1.

For D1 in [0,eps], let u=integral(D1)/eps and v=integral((2y-1)D1)/eps. The EXACT feasible moment set is 0<=u<=1 and |v|<=u(1-u). No policy discretization is needed. An explicit realization is D1=eps*(alpha*1[y>=1-u]+(1-alpha)*1[y<=u]) with alpha=(1+v/(u(1-u)))/2; handle u=0,1 separately. Installed probability is D1/h. At date zero, the same (u,v) enters both actions and every state. With A=h0+h1/2 and B=h1/6,

    regret[a] = g(x)*1[a==0] + beta*eps*(u+theta[a]*(2x-1)*v)
    cost[a] = k(x)*1[a==1] + beta*c*(A-eps*u+theta[a]*(2x-1)*(B-eps*v))

Minimize expected row cost subject to the row simplex and row regret<=eps, then integrate x uniformly. Optimize over the two-dimensional moment set. The pure operating-best action has slack (1-beta)*eps everywhere. The v=0 run gives the exact counterfactual with spatially uniform terminal regret, not an external solver benchmark.

A certificate contains raw primitives, a feasible moment, an outward upper integral and a complete binary rectangle cover with independently recomputable outward lower integrals. Rational roots partition the state integral into affine and quadratic-over-affine pieces. The only transcendental is a logarithm of a positive rational; explicit atanh-series remainder bounds enclose it. No floating optimizer or quadrature establishes an endpoint. `check_controlled.py` can be copied with a proof JSON into an otherwise empty directory; it imports only the Python standard library.

The 27 cases are designed numerical models. Three seeds are paired across seven one-factor cells for family A; two further families have three seeds each. Three no-control cases are negative controls, and 24 have genuinely state/action-dependent densities. `SOURCE_FREEZE.json` fixes hashes before formal generation; its development statement discloses pilot selection. It is internal provenance, not independent preregistration. Runtime caps apply to construction only; worker all-in time includes serialization and independent replay, but excludes interpreter startup. Independent Python reader means code-path separation, not an independent research group. Proportional final costs, two periods and exact operating values delimit these executed results. Original R48 finite failures and R50 results are retained separately.
