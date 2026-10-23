# R124 experiment A: executed evidence checkpoint

This checkpoint preserves the independently frozen and executed first R124
experiment. It does not promote a completed author manuscript or replace the
independently frozen R123 or R98 experiments.

Source F124: `2f0485174e7f518909ab73311e00251647ed6b47`.
Independent-state D124: `a78ee67f386b2b547ecfb5f1986119c199c4fd68`.
The complete 891 native evidence files (98,300,511 bytes) are preserved losslessly
in `transport124/experiment-a/`, with a SHA-256 for every native member and
every transport part. Restore or verify without performing economics:

```sh
python verification124/transport124.py materialize transport124/experiment-a/TRANSPORT124.json
```

The frozen exact certificate reader passed 302,866 assertions and checked all
404 dual witnesses. The separately implemented original-economic reader passed
621,822 assertions: all 314 accepted gain claims were confirmed and all 314
candidate intervals were contained. All1,856 primary decisions and1,392 serial
timing decisions remain available, including unsuccessful optimization flags.
There were no joint-specific action changes among 928 matched decisions.
The simultaneous lower bound on own-incumbent mean gain is positive for 82/116
policy cells; no signed cross-policy population ordering is established among 290
predeclared comparisons. All 64 full three-clock sufficient and optimistic
neural adoption domains remain empty.

`provenance124/PUBLICATION_AUDIT124.json` records a separate post-execution
standard-library publication audit with 280,418 assertions. Its role is to
recompute saved arithmetic and custody, not to replace original economics or
claim a remote CI run. Historical unknown research costs remain unknown.

A separately designed follow-up may use the diagnosis of A, but must publish
its own frozen source and new independent states before its economics. No A
state, outcome or runtime will be relabelled as that follow-up's execution.
