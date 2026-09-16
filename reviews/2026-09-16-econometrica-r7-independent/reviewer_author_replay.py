#!/usr/bin/env python3
"""Rerun R7 small-model validation and primitive/coefficient checks.

Only save hooks are replaced; author evidence remains read-only. This does not
retrain neural policies, rebuild regional upper tensors, or rerun author timing
experiments. The production modules are imported from --root.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();root=args.root.resolve();sys.path.insert(0,str(root/'replication/r7'))
    import validate
    import primitive
    records={}
    def capture(name: str, data: dict) -> None:
        records[name]=data
    validate.save=capture;primitive.save=capture
    validate.run();validate.replay_decision();primitive.run()
    def encode(value):
        if isinstance(value,np.ndarray):return value.tolist()
        if isinstance(value,np.generic):return value.item()
        raise TypeError(type(value).__name__)
    paths=['replication/r7/validate.py','replication/r7/primitive.py','replication/r7/core.py',
           'replication/r7/output/decision.json','replication/r7/output/decision_coefficients.npz']
    result={'scope':'Author small-model suite, primitive calculation, and coefficient-only decision replay rerun by the reviewer; no neural training or full regional construction rerun.',
            'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},'records':records}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,default=encode)+'\n')
    print('PASS',sorted(records));print(records['validation.json']);print(records['decision_replay.json'])
