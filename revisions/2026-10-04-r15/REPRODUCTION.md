# Reproducing the R15 evidence

The commands below distinguish **recomputing a report from retained raw
evidence** from **executing a numerical method again**. They use a complete
checkout of a delivered R15 branch as a read-only reference and create new
worktrees and output directories for every reproduction. None overwrites a
published `WORK.json`, selected policy, raw array, report, or evidence manifest.

## 1. Sources, environment, and isolated directories

The three numerical sources are separate from the later manuscript source.

| Family | Immutable numerical source |
|---|---|
| Protected observations | `9f968785ac3cccab2bc37b1ec4096a1f5b8301b2` |
| Primary methods and scalar study, denoted S below | `9142f404bb9c5163aa94d3a4ded4d0fa48a49c50` |
| Candidate-occupation assessment, denoted M below | `b6b63511f5f76308d9073c373a889effe0e9a0c3` |

The [publication configuration](PUBLICATION_SOURCES.json) identifies the
corresponding complete evidence commits. The manuscript source D is recorded
in [SOURCE_LEDGER.json](SOURCE_LEDGER.json). S generated the fitted policies;
M generated their separate mechanism assessment. D does not replace either
numerical identity.

Run the following in an ordinary Linux Bash shell, starting inside a complete
delivered R15 checkout with its Git history. Python 3.12 is required. Within
GitHub Actions, use the corresponding fixed-source workflow instead, preserve
the existing provenance environment variables, and let the source identity
guards validate that execution context. The new directory made by `mktemp`
is outside the reference checkout. All subsequent examples use these variables
in the same shell.

```bash
set -euo pipefail
NBO_R15_REPO=$(git rev-parse --show-toplevel)
NBO_R15_PATH=revisions/2026-10-04-r15
NBO_R15_DELIVERED_COMMIT=$(git -C "$NBO_R15_REPO" rev-parse HEAD)
NBO_R15_S=9142f404bb9c5163aa94d3a4ded4d0fa48a49c50
NBO_R15_M=b6b63511f5f76308d9073c373a889effe0e9a0c3
NBO_R15_RUN_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/nbo-r15-reproduction.XXXXXXXX")
NBO_R15_ORIGINAL_MAIN="$NBO_R15_REPO/$NBO_R15_PATH/results/experiment"
NBO_R15_ORIGINAL_MECHANISM="$NBO_R15_REPO/$NBO_R15_PATH/results/mechanism"

python3.12 -m venv "$NBO_R15_RUN_ROOT/venv"
NBO_R15_PYTHON="$NBO_R15_RUN_ROOT/venv/bin/python"
"$NBO_R15_PYTHON" -m pip install \
  numpy==2.3.5 scipy==1.17.0 numba==0.65.1 mpmath==1.3.0
"$NBO_R15_PYTHON" -m pip install \
  torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu

export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export NUMBA_NUM_THREADS=1 PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
export NUMBA_CACHE_DIR="$NBO_R15_RUN_ROOT/report-numba-cache"

for NBO_R15_SOURCE in "$NBO_R15_S" "$NBO_R15_M"; do
  if ! git -C "$NBO_R15_REPO" cat-file -e "$NBO_R15_SOURCE^{commit}"; then
    git -C "$NBO_R15_REPO" fetch --no-tags origin "$NBO_R15_SOURCE"
  fi
done
```

The official CPU wheel reports `torch==2.10.0+cpu`. The execution wrappers
check this version, all other pinned package versions, Linux, Python 3.12,
the source archive, protocols, and complete method fingerprints. They start
each measured method or assessment in a fresh process with its own Numba
cache. Report processes use the separate cache above.

Create two sparse worktrees containing exactly the dependencies listed in the
original source manifests. Git objects are shared with the reference checkout;
the numerical worktrees do not materialize the large historical result trees.
The main package has 29 files and the mechanism package has 23 files. The
source packers verify their bytes against the pinned commits.

```bash
nbo_r15_source_worktree() {
  local nbo_r15_destination="$1"
  local nbo_r15_source="$2"
  local nbo_r15_manifest="$3"
  git -C "$NBO_R15_REPO" worktree add --detach --no-checkout \
    "$nbo_r15_destination" "$nbo_r15_source"
  "$NBO_R15_PYTHON" - "$nbo_r15_manifest" <<'PY' > "$nbo_r15_destination.patterns"
import json, sys
from pathlib import PurePosixPath
manifest = json.load(open(sys.argv[1]))
for name in sorted(manifest['files']):
    relative = PurePosixPath(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    print('/' + name)
PY
  git -C "$nbo_r15_destination" sparse-checkout set --no-cone --stdin \
    < "$nbo_r15_destination.patterns"
  git -C "$nbo_r15_destination" checkout --detach "$nbo_r15_source"
}

NBO_R15_MAIN_WT="$NBO_R15_RUN_ROOT/source-main"
NBO_R15_MECHANISM_WT="$NBO_R15_RUN_ROOT/source-mechanism"
nbo_r15_source_worktree "$NBO_R15_MAIN_WT" "$NBO_R15_S" \
  "$NBO_R15_ORIGINAL_MAIN/SOURCE_MANIFEST.json"
nbo_r15_source_worktree "$NBO_R15_MECHANISM_WT" "$NBO_R15_M" \
  "$NBO_R15_ORIGINAL_MECHANISM/SOURCE_MANIFEST.json"
```

## 2. Report-only replay of the original numerical evidence

These commands read the original arrays and original work records. They do not
train a policy, simulate new paths, make a new selection, or spend additional
probability. The primary reporter requires all 32 trial directories, containing
all 128 method executions. The mechanism reporter requires all 32 assessment
directories. Missing or duplicated streams fail the checks.

```bash
"$NBO_R15_PYTHON" "$NBO_R15_MAIN_WT/$NBO_R15_PATH/code/report_experiment.py" \
  --protocol "$NBO_R15_MAIN_WT/$NBO_R15_PATH/PROTOCOL.json" \
  --results "$NBO_R15_ORIGINAL_MAIN/trials" \
  --out "$NBO_R15_RUN_ROOT/reports/original-main"

"$NBO_R15_PYTHON" "$NBO_R15_MECHANISM_WT/$NBO_R15_PATH/code/report_mechanism.py" \
  --protocol "$NBO_R15_MECHANISM_WT/$NBO_R15_PATH/MECHANISM_PROTOCOL.json" \
  --results "$NBO_R15_ORIGINAL_MECHANISM/trials" \
  --out "$NBO_R15_RUN_ROOT/reports/original-mechanism"
```

The primary reporter recomputes the 238 confirmation events, including the
paired contrasts and the analytical-fallback cases. It retains the original
inclusive clocks and stopping histories. The mechanism reporter recomputes
the 12 pooled protected events and the complete work account. Generated TeX
may contain the new output-directory prefix in its `\input` paths; a byte
comparison must normalize that path alone. The publication audit performs
this controlled report comparison in fresh temporary directories.

The scalar, absolute-gap, and paired-transfer reports are later publication
programs. For their replay, use another private worktree at the delivered
commit. The scalar and absolute-gap reporters intentionally require their
input evidence and output tables to lie inside the supplied repository root.
Their new output directories below are inside this private worktree, outside
every original numerical evidence directory.

```bash
NBO_R15_REPORT_WT="$NBO_R15_RUN_ROOT/publication-reports"
git -C "$NBO_R15_REPO" worktree add --detach \
  "$NBO_R15_REPORT_WT" "$NBO_R15_DELIVERED_COMMIT"
NBO_R15_REPORT_MAIN="$NBO_R15_REPORT_WT/$NBO_R15_PATH/results/experiment"
NBO_R15_DERIVED="$NBO_R15_REPORT_WT/$NBO_R15_PATH/results/reproduction-checks"

"$NBO_R15_PYTHON" "$NBO_R15_REPORT_WT/$NBO_R15_PATH/code/report_scalar.py" \
  --protocol "$NBO_R15_REPORT_WT/$NBO_R15_PATH/SCALAR_PROTOCOL.json" \
  --scalar "$NBO_R15_REPORT_MAIN/scalar" \
  --manifest "$NBO_R15_REPORT_MAIN/SOURCE_MANIFEST.json" \
  --evidence-manifest "$NBO_R15_REPORT_MAIN/EVIDENCE_MANIFEST.json" \
  --repo "$NBO_R15_REPORT_WT" --out "$NBO_R15_DERIVED/scalar"

"$NBO_R15_PYTHON" "$NBO_R15_REPORT_WT/$NBO_R15_PATH/code/report_economic_bounds.py" \
  --protocol "$NBO_R15_REPORT_WT/$NBO_R15_PATH/PROTOCOL.json" \
  --results "$NBO_R15_REPORT_MAIN/trials" \
  --report "$NBO_R15_REPORT_MAIN/report/REPORT.json" \
  --manifest "$NBO_R15_REPORT_MAIN/SOURCE_MANIFEST.json" \
  --evidence-manifest "$NBO_R15_REPORT_MAIN/EVIDENCE_MANIFEST.json" \
  --repo "$NBO_R15_REPORT_WT" --out "$NBO_R15_DERIVED/economic-bounds"

"$NBO_R15_PYTHON" "$NBO_R15_REPORT_WT/$NBO_R15_PATH/code/report_paired_transfer.py" \
  --protocol "$NBO_R15_REPORT_WT/$NBO_R15_PATH/PROTOCOL.json" \
  --results "$NBO_R15_REPORT_MAIN/trials" \
  --original-report "$NBO_R15_REPORT_MAIN/report/REPORT.json" \
  --coefficient-record "$NBO_R15_REPORT_WT/$NBO_R15_PATH/results/paired_transfer_constants/PAIRED_TRANSFER_CONSTANTS.json" \
  --out "$NBO_R15_DERIVED/paired-transfer"
```

The scalar replay checks the complete original scalar inventory, eight value
and action grids, the outward algebraic recurrence, both deployment banks,
and all 110 pairwise numerical comparisons. The absolute-gap calculation is
a deterministic transformation of existing lower gains. The paired-transfer
program revalidates the retained coefficient proposals without obtaining new
SVD proposals, and recomputes the disclosed subsequent deterministic bound
using the original confidence events and samples. Its new `generated_utc`
and postprocessing clock describe this replay, not the original production
process. Neither calculation changes the original frozen report.

## 3. Reexecute the complete primary experiment and scalar study

This section performs new computation. It preserves the frozen design and
source S, but creates new worker records. Package S from its own worktree:

```bash
"$NBO_R15_PYTHON" "$NBO_R15_MAIN_WT/$NBO_R15_PATH/code/pipeline_experiment.py" \
  check --repo "$NBO_R15_MAIN_WT"
"$NBO_R15_PYTHON" "$NBO_R15_MAIN_WT/$NBO_R15_PATH/code/pipeline_experiment.py" \
  pack --repo "$NBO_R15_MAIN_WT" --source-commit "$NBO_R15_S" \
  --out "$NBO_R15_RUN_ROOT/main-bundle"

"$NBO_R15_PYTHON" - "$NBO_R15_RUN_ROOT/main-bundle/SOURCE_MANIFEST.json" <<'PY' \
  > "$NBO_R15_RUN_ROOT/main-trials.txt"
import json, sys
rows = json.load(open(sys.argv[1]))['matrix']['include']
assert len(rows) == 32 and len({x['trial_id'] for x in rows}) == 32
for row in rows:
    print(row['trial_id'])
PY

while IFS= read -r NBO_R15_TRIAL; do
  "$NBO_R15_PYTHON" "$NBO_R15_RUN_ROOT/main-bundle/pipeline_experiment.py" \
    run-trial --bundle "$NBO_R15_RUN_ROOT/main-bundle" \
    --workspace "$NBO_R15_RUN_ROOT/main-workspaces/$NBO_R15_TRIAL" \
    --out "$NBO_R15_RUN_ROOT/main-rerun/trials/$NBO_R15_TRIAL" \
    --trial-id "$NBO_R15_TRIAL"
done < "$NBO_R15_RUN_ROOT/main-trials.txt"

"$NBO_R15_PYTHON" "$NBO_R15_RUN_ROOT/main-bundle/pipeline_experiment.py" \
  run-scalar --bundle "$NBO_R15_RUN_ROOT/main-bundle" \
  --workspace "$NBO_R15_RUN_ROOT/scalar-workspace" \
  --out "$NBO_R15_RUN_ROOT/main-rerun/scalar"

"$NBO_R15_PYTHON" "$NBO_R15_MAIN_WT/$NBO_R15_PATH/code/pipeline_experiment.py" \
  collect --repo "$NBO_R15_MAIN_WT" \
  --bundle "$NBO_R15_RUN_ROOT/main-bundle" \
  --input-dir "$NBO_R15_RUN_ROOT/main-rerun/trials" \
  --scalar-dir "$NBO_R15_RUN_ROOT/main-rerun/scalar"
```

The shell loop executes every declared stream. Each `run-trial` executes all
four methods in the protocol's fixed rotation, with fresh child processes;
there is no method filter in the wrapper. The wrapper also preserves failed
fits and analytical fallbacks. For one development check, invoke the same
`run-trial` command with one declared ID, such as `d10_s2095568532`, and new
workspace/output paths. A partial run cannot pass `collect` or support the
reported complete method distribution.

Collection writes a new `results/experiment` **inside the private S worktree**,
checks all 128 executions and the scalar study, and creates their new report
and manifests. The original delivered directory remains untouched. The serial
loop is a portable execution order; the frozen
[main workflow](../../.github/workflows/nbo-r15-experiment.yml) distributes
32 trials over separate runners, with at most 12 simultaneous trial jobs.
Within-trial method order and fresh-process boundaries are unchanged.

## 4. Reexecute the mechanism on the original selected policies

The mechanism design was committed in S before the primary outcomes. Its
separate producer was frozen at M. The execution workflow is activated only
after the complete primary run and collector succeed. Its source and execute
branches point at the same M commit. Offline reproduction below uses the
complete original primary evidence and its original source manifest.

In particular, `--primary-bundle` here points to the **original** main evidence
directory. The mechanism packer checks that its source manifest identifies
S and original Actions run `37188544814`. A newly packed main bundle has a
new packaging record and is not a substitute for this original input manifest.

```bash
"$NBO_R15_PYTHON" - "$NBO_R15_ORIGINAL_MAIN/FINAL_AUDIT.json" "$NBO_R15_S" <<'PY'
import json, sys
audit = json.load(open(sys.argv[1]))
assert audit['complete'] is True
assert audit['numerical_source_commit'] == sys.argv[2]
assert audit['trial_count'] == 32 and audit['method_executions'] == 128
PY

"$NBO_R15_PYTHON" "$NBO_R15_MECHANISM_WT/$NBO_R15_PATH/code/pipeline_mechanism.py" \
  check --repo "$NBO_R15_MECHANISM_WT"
"$NBO_R15_PYTHON" "$NBO_R15_MECHANISM_WT/$NBO_R15_PATH/code/pipeline_mechanism.py" \
  pack --repo "$NBO_R15_MECHANISM_WT" --source-commit "$NBO_R15_M" \
  --primary-bundle "$NBO_R15_ORIGINAL_MAIN" \
  --out "$NBO_R15_RUN_ROOT/mechanism-bundle"

"$NBO_R15_PYTHON" - "$NBO_R15_RUN_ROOT/mechanism-bundle/SOURCE_MANIFEST.json" <<'PY' \
  > "$NBO_R15_RUN_ROOT/mechanism-trials.txt"
import json, sys
rows = json.load(open(sys.argv[1]))['matrix']['include']
assert len(rows) == 32 and len({x['trial_id'] for x in rows}) == 32
for row in rows:
    print(row['trial_id'])
PY

while IFS= read -r NBO_R15_TRIAL; do
  "$NBO_R15_PYTHON" "$NBO_R15_RUN_ROOT/mechanism-bundle/pipeline_mechanism.py" \
    run --bundle "$NBO_R15_RUN_ROOT/mechanism-bundle" \
    --workspace "$NBO_R15_RUN_ROOT/mechanism-workspaces/$NBO_R15_TRIAL" \
    --primary-dir "$NBO_R15_ORIGINAL_MAIN/trials/$NBO_R15_TRIAL" \
    --out "$NBO_R15_RUN_ROOT/mechanism-rerun/trials/$NBO_R15_TRIAL" \
    --trial-id "$NBO_R15_TRIAL"
done < "$NBO_R15_RUN_ROOT/mechanism-trials.txt"

"$NBO_R15_PYTHON" "$NBO_R15_MECHANISM_WT/$NBO_R15_PATH/code/report_mechanism.py" \
  --protocol "$NBO_R15_MECHANISM_WT/$NBO_R15_PATH/MECHANISM_PROTOCOL.json" \
  --results "$NBO_R15_RUN_ROOT/mechanism-rerun/trials" \
  --out "$NBO_R15_RUN_ROOT/reports/rerun-mechanism"
```

For each trial the input directory is precisely
`results/experiment/trials/<trial_id>`: it contains `TRIAL.json` and the
`nbo/RESULT.json`, `nbo/WORK.json`, and selected checkpoint. The wrapper verifies
their source, full method fingerprint, trial identity, and exact byte hashes
before the assessment. The saved fit retains source S; `BRIDGE.json` and the
new assessment `WORK.json` identify M. No fit is relabeled as produced by M.

To exercise the mechanism collector as well, join the exact original primary
Git subtree into the private M worktree, then collect all 32 new assessments.
This is the same subtree operation used by the frozen workflow. It does not
change the original evidence commit or create a second hierarchy of primary
results inside the mechanism directory.

```bash
NBO_R15_PRIMARY_EVIDENCE=$(
  "$NBO_R15_PYTHON" - "$NBO_R15_REPO/$NBO_R15_PATH/PUBLICATION_SOURCES.json" <<'PY'
import json, re, sys
commit = json.load(open(sys.argv[1]))['roles']['main']['evidence_commit']
assert re.fullmatch('[0-9a-f]{40}', commit)
print(commit)
PY
)
if ! git -C "$NBO_R15_REPO" cat-file -e "$NBO_R15_PRIMARY_EVIDENCE^{commit}"; then
  git -C "$NBO_R15_REPO" fetch --no-tags origin "$NBO_R15_PRIMARY_EVIDENCE"
fi
NBO_R15_PRIMARY_TREE=$(git -C "$NBO_R15_REPO" rev-parse \
  "$NBO_R15_PRIMARY_EVIDENCE:$NBO_R15_PATH/results/experiment")
git -C "$NBO_R15_MECHANISM_WT" sparse-checkout add \
  "/$NBO_R15_PATH/results/experiment/"
git -C "$NBO_R15_MECHANISM_WT" read-tree \
  --prefix="$NBO_R15_PATH/results/experiment/" -u "$NBO_R15_PRIMARY_TREE"

"$NBO_R15_PYTHON" "$NBO_R15_MECHANISM_WT/$NBO_R15_PATH/code/pipeline_mechanism.py" \
  collect --repo "$NBO_R15_MECHANISM_WT" \
  --bundle "$NBO_R15_RUN_ROOT/mechanism-bundle" \
  --input-dir "$NBO_R15_RUN_ROOT/mechanism-rerun/trials" \
  --primary-evidence-commit "$NBO_R15_PRIMARY_EVIDENCE" \
  --primary-evidence-tree "$NBO_R15_PRIMARY_TREE"
```

The collector checks every selected checkpoint against the joined primary
subtree and records `primary_evidence_commit` and
`primary_experiment_git_tree`. Its local manifests describe the new assessment
execution. They do not claim that those fresh assessment clocks occurred in
the original Actions run. The original mechanism publication uses both the M
source and original primary evidence commit as Git parents; the commands above
leave the isolated reproduction uncommitted and do not push any branch.

## 5. Rebuild the manuscript and run the complete publication audit

The publication audit writes three new audit records. Document compilation
also writes files and can change PDF metadata. Use a separate worktree at the
recorded manuscript source D, leaving both the delivered checkout and the
numerical reruns above intact. This worktree needs the complete historical and
current evidence because the audit verifies their actual bytes.

```bash
NBO_R15_D=$(
  "$NBO_R15_PYTHON" - "$NBO_R15_REPO/$NBO_R15_PATH/SOURCE_LEDGER.json" <<'PY'
import json, re, sys
commit = json.load(open(sys.argv[1]))['publication_source_commit']
assert re.fullmatch('[0-9a-f]{40}', commit)
print(commit)
PY
)
NBO_R15_BUILD_WT="$NBO_R15_RUN_ROOT/publication-build"
git -C "$NBO_R15_REPO" worktree add --detach "$NBO_R15_BUILD_WT" "$NBO_R15_D"

sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
  texlive-latex-base texlive-latex-extra texlive-science \
  texlive-fonts-recommended cm-super latexmk poppler-utils

(
  cd "$NBO_R15_BUILD_WT"
  for NBO_R15_TEST in "$NBO_R15_PATH"/code/test_*.py; do
    "$NBO_R15_PYTHON" -m unittest discover -s "$NBO_R15_PATH/code" \
      -p "$(basename "$NBO_R15_TEST")" -v
  done
  "$NBO_R15_PYTHON" -m unittest discover -s "$NBO_R15_PATH/code" \
    -p publication_audit_tests.py -v
  "$NBO_R15_PYTHON" -m unittest discover -s "$NBO_R15_PATH/code" \
    -p publication_tables_checks.py -v
  "$NBO_R15_PYTHON" "$NBO_R15_PATH/code/paired_transfer_checks.py" \
    --out "$NBO_R15_PATH/build/reproduction_paired_transfer_checks.json"
  "$NBO_R15_PYTHON" "$NBO_R15_PATH/code/integrate.py" --write-roots
  "$NBO_R15_PYTHON" "$NBO_R15_PATH/code/build.py"
  "$NBO_R15_PYTHON" "$NBO_R15_PATH/code/publication_audit.py" \
    --repo . --publication-source "$NBO_R15_D" \
    --sources "$NBO_R15_PATH/PUBLICATION_SOURCES.json" --strict
)
```

Each test module runs in a fresh interpreter to prevent inherited global
model constants from leaking between calibrations. The publication audit
requires the configured generating/evidence commits and reviewed commit
`7aff61a41a3d28e5eaff73c9fe21e9856110f422` to be present in Git; fetch any missing
commit by its complete recorded SHA before running it. The delivery workflow
does this explicitly. The build checks all three PDFs for undefined references
or citations, duplicate labels or destinations, and overfull boxes.

## 6. Interpreting reproducibility and work records

| Operation | Preserved original record | Newly created record |
|---|---|---|
| Report-only replay | Original arrays, checkpoint selection, confidence allocation, stopping decisions, work clocks and environments | Derived report files and, where recorded, the replay's own generation time |
| New main or scalar execution | Source S, design, complete stream support, method fingerprints and declared randomization rules | New process clocks, CPU/RSS, UTC times, machine/environment records, outputs and their manifests |
| New mechanism execution | Original S checkpoints and input hashes; M assessment source and fixed bridge protocol | New assessment clocks, protected samples and output inventory |
| Local document rebuild | Numerical evidence and its generating source identities | New build logs, PDF bytes, compilation record and publication audit hashes |

A source pack's `packed_at_utc` and local run metadata are newly generated;
its code/protocol identity is determined by the committed file hashes and
environment contract. Offline packing must not be assigned the original
Actions run number. Reexecuted clocks measure the new machine and scheduling
conditions, so they are not expected to equal the original work measurements.
Newly trained weights and floating-point trajectories can also differ across
hardware and numerical environments, even when the source and pinned package
versions agree. Exact byte preservation of the original evidence does not
assert that training in every new environment produces identical bytes.
Do not copy original clock or UTC fields into newly computed worker records.

The primary method clock includes process setup, fitting, all attempted online
checks, saved-policy reload, independent confirmation, and final output.
Mechanism assessment is an additional scientific audit of returned NBO
policies; its full cost is reported separately and is not added selectively
to NBO's primary time-to-target statistic. A newly computed report from the
original evidence continues to use the original measured work.

The original protected-observation implementation and its four-cell execution
recipe remain in the frozen
[observation workflow](../../.github/workflows/nbo-r15-observation.yml).
Historical R12--R14 artifacts remain at their original paths and under their
original source records. The final
[delivery workflow](../../.github/workflows/nbo-r15-delivery.yml) performs no
training: it builds the three documents, verifies all evidence families and
historical preservation, then publishes the same audited commit to three new
revision branches. Its creation-only atomic push cannot overwrite an existing
destination. The retained
[workflow validation receipt](results/receipts/DELIVERY_WORKFLOW_VALIDATION.json)
records the independent schema, tampering, shell, and Git transaction checks.
