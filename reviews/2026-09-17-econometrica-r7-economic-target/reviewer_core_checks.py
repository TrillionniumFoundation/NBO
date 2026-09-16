#!/usr/bin/env python3
"""Rerun author checks without overwriting author evidence; verify source inputs.
The author routines are explicitly labelled as reruns, not reviewer-written proofs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    inventory = json.loads((root / 'revisions/2026-09-16-r7/source_inventory.json').read_text())
    matches = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
               for name, digest in inventory.items()}
    assert all(matches.values()), 'The authored source does not match the pinned inventory.'
    sys.path.insert(0, str(root / 'replication/r7'))
    import core
    import importlib.util
    def load(name, filename):
        spec = importlib.util.spec_from_file_location(name, root / "replication/r7" / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    validate = load("review_author_r7_validate", "validate.py")
    primitive = load("review_author_r7_primitive", "primitive.py")
    import numpy
    import scipy
    captured = {}
    def capture(name, data):
        captured[name] = core.serial(data)
    validate.save = capture
    primitive.save = capture
    validate.run()
    validate.replay_decision()
    primitive.run()
    decision = json.loads((root / 'replication/r7/output/decision.json').read_text())
    output = {
        'scope': 'rerun of author validation, primitive calculation, and coefficient-only replay; not a new proof',
        'manuscript_commit': 'fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17',
        'environment': {'python': platform.python_version(), 'numpy': numpy.__version__,
                        'scipy': scipy.__version__, 'platform': platform.platform()},
        'authored_source_inventory_matches': matches,
        'author_check_reruns': captured,
        'deposited_per_class_arithmetic_allowance': decision['roundoff']['per_class_allowance'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + '\n')
    print('PASS: all source inventory entries, author checks, and coefficient replay')
    print(json.dumps(captured['validation.json'], indent=2))
    print(json.dumps(captured['decision_replay.json'], indent=2))
    print(json.dumps(captured['primitive.json']['continuous_family'], indent=2))

if __name__ == '__main__':
    main()
