# Actual completed recovery artifact custody

The scientific recovery workflow 39691016040 completed successfully on source
6ab1f9d4f1f9eb70014a7d104b84a499b64ba84c. Its actual 630,176,089-byte artifact
12391656973 exceeds the GitHub connector's 536,870,912-byte download limit. The
connector rejected that download; this is not a scientific or CI failure.

This new administrative source retrieves that exact existing artifact on a
GitHub runner through the normal authenticated GitHub CLI, checks its API
metadata, complete size and SHA256, and reads only the original recovery admin
prefix. It runs no economic calculation, changes no sample, and cannot replace
a result with a different round. All final status, source, gate, publication and
log bytes are retained under a new artifact-custody run/attempt prefix. Every
publication and stage-log hash declared by the final status must match, including
the terminal publication 5635a3a0af330933b3ff1b9331ba4fe468eac628. The earlier
committed status remains unchanged.

The driver pins its source/trigger/workflow to its actual event commit and limits
normal publication to the new custody directory on the isolated R122 revision
branch. A temporary index starts from the actual current descendant parent;
non-fast-forward failures may retry at most three times and preserve their
clocks. No force push, historical branch write, numerical input modification or
scientific-success inference is permitted. Exact published native hashes are
read back. The completed original scientific workflow and this separate custody
workflow have distinct source and publication identities.

The enclosing driver wall clock includes retrieval, extraction, checking and
publication. Nested stage clocks must not be counted again. Checkout, setup,
artifact upload and unclocked historical work remain outside that observed
clock; whole-study exact cost remains unavailable. The driver's terminal receipt
is saved in a small separate Actions artifact, avoiding a commit/self-hash cycle.

The preceding attempted 5,908,641-byte diagnostic ZIP upload was interrupted
without a terminal publication result; local files and unpublished helper bytes
were then unavailable. Their earlier conversation observations do not replace
native files. Required auxiliary files are reconstructed under new source
identities, while actual published theory, author-response and scientific
checkpoints remain the controlling recoverable evidence.
