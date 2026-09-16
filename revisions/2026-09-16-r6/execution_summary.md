# R6 executed evidence

All numbers below are generated from the actual JSON outputs. Timing is not a scientific superiority claim.

- Exact-oracle scalar OLS: initial-distribution 3 anchors, all-state/date 47 anchors; respective global bounds 0.05296881548624227 and 0.0009306975603620149.
- Removing neural lower actions: same original-target uniform bound 0.0009306975845364551; maximum anchor loss 3.871247522413412e-05.
- Reusable QP (query count; learned total seconds; QP total seconds; independent maximum gap):
  - 32; 0.884792273; 0.007591944; 0.000633260645458
  - 128; 0.964309472; 0.014002997; 0.000664161784322
  - 512; 1.57164783; 0.040575294; 0.000664161784322
  - 2048; 3.66747814; 0.143247756; 0.000677426362523
- Corrected transition-law certificates (fixed d; anchors; all-state/date/lambda bound):
  - 0.0; 19; 0.0009045733003105738
  - 0.5; 18; 0.0008998289604379428
  - 1.0; 17; 0.0009414120278261606
- Matched adjustment restriction (d; adjustable risk advantage; no-adjustment risk advantage):
  - 0.0; -0.000875904977093; -0.00133454353711
  - 0.25; -0.000276561700985; -0.000730716482961
  - 0.35; -4.62573114236e-05; -0.000489849363735
  - 0.365; -1.17116529894e-05; -0.000453737733931
  - 0.375; 1.13187859667e-05; -0.000429663314062
  - 0.4; 6.8894883357e-05; -0.000369477264388
  - 0.5; 0.000299199272918; -0.00013568398165
  - 1.0; 0.00128125592829; 0.000950467206985

The policy values, upper certificates, finite-model scope, timing samples, conditional slope interpretation, and unresolved global-uniqueness question are retained in the underlying records.
