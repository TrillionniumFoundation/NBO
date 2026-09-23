# R25 stochastic reference and secant protocol

This supplement fixes the reference economy and execution settings before running it. It does not alter the original-economy calibration/evaluation protocol.

## Nonreplicable stochastic investment benchmark

Time horizon 1, state domain x in (0.5,2), z in (-1,1), discount rho=0.04. Two independent Brownian motions W,B. Dynamics: dX=(0.02X+a+0.04 p X)dt+0.25 p X dW; dZ=0.3 dB. Investment a is in [0,2.2], portfolio p in [0,1]. Stop at the first state exit or time 1. Productivity risk B is unspanned by the traded W-risk. There is no exact-financing decoder.

Set A(t)=0.8+0.2t and v(t,x,z)=A(t)[log x+0.1xz-0.1z^2]. Settlement equals v on every stopping face. Define the manufactured state-dependent transfer
b=0.04v-v_t-0.02x v_x-(0.3^2/2)v_zz-v_x^2/2+(0.04^2 v_x^2)/(2*0.25^2*v_xx).
The running payoff is b-a^2/2. This constructed transfer makes the exact value independently verifiable by completing two Hamiltonian squares. Optimal actions are a*=A(t)(1/x+0.1z), p*=0.64(1+0.1xz), both interior. Regret is the stopped discounted integral of [(a-a*)^2+0.25^2 A(t)(p-p*)^2]/2.

Train two current-state tanh actors (3-12-12-2), seeds 25201 and 25202, with output scales (2.2,1) times sigmoid. Inputs normalize t and x affinely to [-1,1] and leave z unchanged. Use the tensor Gauss-Legendre rule with orders (5,9,7). Minimize the known-witness Hamiltonian deficit using L-BFGS-B, maxls 40, ftol 1e-15, gtol 1e-10 and a cap of 2500 function/gradient calls. This is an oracle-witness policy-improvement/verifier stress test; it is not an independent numerical discovery of the exact value. Retain both seeds and all failures. A direct degree-eight polynomial approximation to 1/x, fitted at the same x nodes, and the exact portfolio formula serve as a classical control. Do not claim neural efficiency from this deliberately constructed benchmark.

Verify all points of the closed state-time box using the inherited outward interval arithmetic. Use centered mean-value enclosures of actor-minus-optimal-action error, including interval first derivatives. Try covers (8,32,16), (16,64,32), (32,128,64), in that order. Stop at the first complete cover giving regret upper <=0.001 or after the third cover. Keep each attempted cover and store the full final cell-bound array and its hash. Bound each start time with its discounted remaining-horizon factor. Report restart slices t in {0,0.25,0.5,0.75,1}; these are evaluations of a complete state-time certificate, not sampled-point replacements. All benchmark numbers remain separately labelled from the original economy's 0.01 objective.

## Original-economy directed secants

After the frozen held-out study, take seed 25101, proposal orders (8,16), neural-Adam and direct-L-BFGS-B checkpoint-400 raw outputs. Evaluate the five fixed raw-output convex combinations alpha in {0,0.25,0.5,0.75,1}. Decode financing with the inherited proposal map and certify every candidate with the unchanged stopped-payoff checker. Report all adjacent secant intervals [(L_next-U_previous)/0.25,(U_next-L_previous)/0.25], along with ordinary automatic-differentiation directional derivatives of the proposal objective at the same nodes. A certified secant is a finite economic payoff comparison, not a pointwise stopped-gradient certificate. Do not convert these intervals into a rigorous gradient-error bound or use them for held-out method selection.
