# Offline identity witness for the frozen R126 fitting audit

The independent fitting code requires exact `git show` readback at scientific source `769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b` before numerical imports. This folder makes that gate usable from the repository-layout referee archive without contacting GitHub.

This is a **minimal Git path witness**, not a full clone. The self-contained pack contains the authentic F126 commit, the 67 ancestor directory trees needed to reach the gate files, and 148 distinct blobs serving all 184 required paths. The original commit identity is unchanged. Its parent history and unrelated objects referenced by those authentic trees are intentionally absent. Consequently this transport does not claim a complete `git fsck` connectivity closure or provide every historical repository operation.

The pack contains 216 objects, occupies 1,834,756 bytes, and has SHA256 `62b974f8acb230307b84039ce033bf71a053702abe672059e27722cd6853d205`. `WITNESS_MANIFEST126.json` identifies every object and every gated file. It is supplementary transport prepared after the experiments, not a replacement scientific freeze.

## Install and verify

Extract the referee archive with its repository-relative layout intact:

```
<archive-root>/revisions/2026-10-23-r126/
```

From that revision directory run:

```bash
python offline_git126/bootstrap126.py
```

The script prints a JSON verification receipt. It first checks every gated working-file byte and the complete pack checksum. If the archive root has no Git identity, it initializes an otherwise empty local repository with no template hooks or remote. If an appropriate identity already exists, it adds only immutable object-pack data. It never updates an existing ref, `HEAD`, worktree index or working file; it checks those Git identities before and after installation. Git transport protocols are disabled during the operation. The pack is retained as an unreachable identity witness with a `.keep` marker; no branch is created for the original commit. An archive nested inside a different repository is rejected instead of silently choosing that ancestor.

The exact frozen source gate can then be checked without importing NumPy or SciPy or executing a fit:

```bash
python - <<'PY'
import json
from code126.independent_fit126 import source_gate
print(json.dumps(source_gate('769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b'), indent=2))
PY
```

To reexecute the actual historical-data audit, install the pinned dependencies and follow `../REPRODUCE126.md`. The original published actor bytes and the audit-only readouts remain separate. A new attempt must use a new output directory. Installing this witness does not execute economic evaluation or fitting, and it does not supply the separately frozen C episode's Git history. The C code validates its bundled immutable scientific manifest directly.

## Actual offline verification

`OFFLINE_VERIFICATION126.json` records successful verification in a fresh temporary repository with no remotes. Both the first installation and a repeated installation checked all 184 exact Git file reads and preserved refs, `HEAD` and index. The actual unchanged frozen `source_gate` then checked all 184 files with 365 assertions, before any numerical-library import. There were zero fits and zero economic evaluations. The two full bootstrap receipts and `FROZEN_GATE_OFFLINE_READBACK126.json` preserve the detailed paths and hashes. These transport checks do not repeat the scientific experiment.

`build_witness126.py` records the object's extraction procedure; it needs the authentic source repository and is not part of an archive recipient's required workflow. `verify_witness126.py` is the verification harness, which creates a separate temporary repository and never changes the source repository's refs or index.
