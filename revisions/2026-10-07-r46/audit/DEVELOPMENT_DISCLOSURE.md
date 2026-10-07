# R46 development disclosure

Before the full catalogue, 14 exact/small-domain checks were run. The first invocation had three errors because serialized rational knots were passed as strings to the immutable R45 constructor, which accepts numeric values. The new adapter now parses every numerator/denominator string as Fraction before construction. No scientific primitive, target, ladder, or original R45 source was changed. This failure occurred only in development tests; no R46 full service record existed. The failed test summary is retained separately.

The first local manuscript audit parsed page counts from wrapped TeX log lines and rejected a successful PDF compilation. Page counts are now read from the actual PDFs using pdfinfo. This changes only metadata validation. All 41 regressions and all PDF compilations had completed; no scientific record or target was changed.
