# Amendment 01 — analytic global boundary optimization

The stopping model, restart, fixed controls, parameter interval and payoff target are unchanged. Before executing the new global certificate, we replace an expensive derivative-grid covering with a stronger analytic sufficient bound.

For the lower-killed Brownian motion, the derivative of survival is
S'_theta(t)=16 exp(-16 theta) Phi((theta*t-1/50)/((1/20)*sqrt(t))).
It is log-concave in theta. A bounded, increasing extension of the Dynkin integrand beyond the far upper boundary has h>=2 and h_y>0; monotone coupling therefore lower-bounds its distributional derivative by twice S'_theta(t). The direct parameter derivative is bounded below by -4/125 on [-1/5,0] and -54/125 on [0,1/5]. Integrating over respectively [1/25,1/5] and [1/4,1], and using a separately bounded opposite-boundary score error, gives two explicit half-interval derivative lower bounds. Ball arithmetic must prove both positive before any global-maximizer claim is made.

This is a change of proof technique, not a changed instance or post hoc selection of successful parameter points. The R30 failed integration and all inherited pointwise derivative records remain. The new endpoint payoff is recomputed with the unchanged validated oracle. The first R31 neural implementation attempt stopped before producing a candidate because python-flint fmpq does not define float(); it is logged and corrected by an explicit numerator/denominator conversion. The already executed all-defer maintenance pilots remain diagnostic records, including their zero dynamic-versus-pointwise cost savings.
