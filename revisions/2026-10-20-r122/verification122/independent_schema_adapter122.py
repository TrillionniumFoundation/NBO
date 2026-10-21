"""Disclosed post-F binding of a training label and a numerical regret alias.

The original campaign stores its training-loss label in top-level ``loss``.
The frozen algebra auditor additionally expects a numerical alias there for
accepted actions.  It already checks the same numerical value under
``certified_regret_upper``.  Validate both meanings, provide only a shallow
temporary alias to the unchanged auditor, and retain every native record.

Importing this module and calling make_audit performs no economic evaluation.
Actual independent execution requires the adapter's own published commit.
"""
from __future__ import annotations
import hashlib, json, math, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SOURCE_F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
FROZEN_AUDITOR_SHA256 = '0c99b501be4a7dafa8a6480408823442b613b52e4f179c834b0ef2309c36741b'
FROZEN_DRIVER_SHA256 = '318320e3944407656e0a3d5301822aa1a7b2771eadb5d43fe27101e13060d1eb'
ORIGINAL_FAILURE_SHA256 = '769f99215850fd61ea09e90d1b8cf916c8fccf7afde77ac4d8990a011fa6dcd2'
ARMS = ('quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid')
FIELDS = ('index', 'row', 'budget', 'arm', 'loss', 'service')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def make_audit(original_audit, checks):
    """Return a strict pure schema view; preserve original auditor counters."""
    def audit_native_row(row):
        identity = tuple(row.get(k) for k in FIELDS)

        def require(ok, message):
            if not ok:
                raise ArithmeticError('R122 independent schema adapter: ' + message + ' ' + repr(identity))

        label, arm, budget = row.get('loss'), row.get('arm'), row.get('budget')
        require((arm == 'online' and label == 'online' and budget == 0) or
                (arm in ARMS and label in ('value', 'marginal') and budget in (5, 9)),
                'declared training-loss label and actor identity')
        numeric = row.get('certified_regret_upper')
        require(type(numeric) in (float, int) and math.isfinite(numeric) and
                0 <= numeric <= 1 / 256, 'separate finite qualified numerical regret bound')
        accepted = row.get('accepted_improvement')
        require(type(accepted) is bool, 'explicit acceptance flag')
        if accepted:
            attempts = row.get('support_attempts')
            require(isinstance(attempts, list) and bool(attempts), 'accepted support menu exists')
            record = attempts[-1]
            selected = record.get('selected_fraction_index')
            require(type(selected) is int and 0 <= selected < 6, 'selected fraction index')
            matches = [z for z in record['candidate_menu'] if z.get('fraction_index') == selected]
            require(len(matches) == 1 and 'candidate_certificate' in matches[0],
                    'unique selected numerical certificate')
            candidate = matches[0]['candidate_certificate']
            require(candidate.get('qualified') is True and numeric == candidate.get('loss'),
                    'saved numerical regret equals selected qualified candidate')
        temporary = dict(row)
        temporary['loss'] = numeric
        try:
            result = original_audit(temporary)
        except Exception as error:
            raise ArithmeticError('Frozen audit rejected native identity ' + repr(identity)) from error
        require(row['loss'] == label, 'native training label preserved')
        for name, count in (('native_rows_checked', 1), ('training_labels_checked', 1),
                            ('finite_regret_bounds_checked', 1), ('shallow_numeric_alias_views', 1),
                            ('accepted_numeric_candidate_equalities', int(accepted)),
                            ('unchanged_native_training_labels', 1)):
            checks[name] = checks.get(name, 0) + count
        return result
    return audit_native_row


def install_adapter(frozen_algebra_module, checks):
    original = frozen_algebra_module.audit
    frozen_algebra_module.audit = make_audit(original, checks)
    return original


def main():
    original_argv = list(sys.argv)
    if '--repair-commit' not in sys.argv:
        raise ValueError('Separately published independent --repair-commit required')
    position = sys.argv.index('--repair-commit')
    commit = sys.argv[position + 1]
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('Full immutable independent schema repair commit required')
    own = Path(__file__).resolve()
    amendment = ROOT / 'provenance122/INDEPENDENT_SCHEMA_AMENDMENT122.md'
    failure = ROOT / 'results122/independent-attempt01/FAILURE122.json'
    for path in (own, own.with_name('test_independent_schema_adapter122.py'), amendment, failure):
        relative = str(path.relative_to(REPO))
        if subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=REPO) != path.read_bytes():
            raise ValueError('Independent repair source/evidence differs from published commit: ' + relative)
    if digest(failure) != ORIGINAL_FAILURE_SHA256:
        raise ValueError('Original failed independent attempt was changed')
    saved_failure = json.loads(failure.read_text())
    if saved_failure.get('status') != 'failed' or 'returned qualified candidate loss' not in saved_failure['traceback']:
        raise ValueError('Expected original schema failure not preserved')
    for name, expected in (('algebra_audit122.py', FROZEN_AUDITOR_SHA256),
                           ('independent122.py', FROZEN_DRIVER_SHA256)):
        if digest(ROOT / 'code122' / name) != expected:
            raise ValueError('Frozen independent source bytes changed: ' + name)
    del sys.argv[position:position + 2]
    if any(flag not in sys.argv for flag in ('--output', '--source-commit', '--primary')):
        raise ValueError('Original frozen independent CLI arguments required')
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    source = sys.argv[sys.argv.index('--source-commit') + 1]
    primary = Path(sys.argv[sys.argv.index('--primary') + 1]).resolve() / 'records122.jsonl'
    if source != SOURCE_F:
        raise ValueError('Schema repair is bound to the original R122 F')
    primary_hash = digest(primary)
    sys.path.insert(0, str(ROOT / 'code122'))
    import algebra_audit122 as frozen_algebra
    import independent122 as frozen_driver
    checks = {}
    original = install_adapter(frozen_algebra, checks)
    started = time.perf_counter()
    status = 'failed'
    try:
        frozen_driver.main()
        if any(checks.get(k) != 5568 for k in ('native_rows_checked', 'training_labels_checked',
                'finite_regret_bounds_checked', 'shallow_numeric_alias_views', 'unchanged_native_training_labels')):
            raise ArithmeticError('Complete primary schema audit census differs')
        algebra = json.loads((output / 'ALGEBRA_AUDIT122.json').read_text())
        if algebra['counts']['accepted_actions'] != checks['accepted_numeric_candidate_equalities']:
            raise ArithmeticError('Accepted numerical equality census differs from original algebra audit')
        if digest(primary) != primary_hash:
            raise ValueError('Native primary input bytes changed')
        status = 'executed'
    finally:
        frozen_algebra.audit = original
        if output.is_dir():
            receipt = dict(status=status, source_commit_F=source, independent_adapter_commit=commit,
                adapter_path=str(own.relative_to(REPO)), adapter_sha256=digest(own),
                frozen_auditor_sha256=FROZEN_AUDITOR_SHA256, frozen_driver_sha256=FROZEN_DRIVER_SHA256,
                amendment_sha256=digest(amendment), original_failure_sha256=digest(failure),
                primary_sha256=primary_hash, actual_command=original_argv, checks=checks,
                elapsed_seconds=time.perf_counter() - started,
                elapsed_includes_original_driver_and_postchecks=True,
                elapsed_nested_in_outer_launcher_not_additive=True,
                temporary_field_mapping={'loss': 'certified_regret_upper'},
                native_training_loss_field='loss', original_frozen_files_changed=False,
                saved_primary_records_changed=False, frozen_algebra_counter_semantics_changed=False,
                independent_mesh_or_action_or_state_selection_changed=False,
                new_population_states=0, new_training=0, adapter_economic_calls=0,
                original_failed_attempt_success_asserted=False,
                scope='Strict shallow schema binding before unchanged exact algebra auditor; unchanged independent driver performs all original-economic evaluation and emits its own execution/witness receipts.')
            with (output / 'INDEPENDENT_SCHEMA_ADAPTER122.json').open('x') as stream:
                json.dump(receipt, stream, indent=2, sort_keys=True, allow_nan=False)
                stream.write('\n')


if __name__ == '__main__':
    main()
