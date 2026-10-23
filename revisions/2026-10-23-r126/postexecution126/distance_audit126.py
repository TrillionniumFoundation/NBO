"""Post-execution exact square audit; no economic evaluation or source alteration.

The displayed action distance is a bound derived from mu=2 and q-regret.
Every saved binary floating-point number is converted to its exact Fraction;
no decimal tolerance or floating square comparison is used.
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code126'))
from common126 import *


def run(inputs,output):
    out,tick,info=start(output,'post-execution-exact-action-distance-square-audit')
    try:
        gate=verify_inputs(); checks=0; cases=[]
        for name in inputs:
            path=Path(name)/'records126.jsonl.gz'
            data=rows(path)
            for r in data:
                radius=F(r['action_distance_upper'])
                regret=F(r['certified_regret_upper'])
                assert radius>=0 and regret>=0
                assert radius*radius>=regret,(str(path),r['index'],r['budget'],r['arm'],r['training_loss'],r['mode'],r['row'])
                checks+=1
            cases.append(dict(input=str(path),sha256=sha(path),rows=len(data)))
        assert [x['rows'] for x in cases]==[1584,176,176,176]
        finish(out,tick,checks=checks,exact_square_comparisons=checks,
               original_economic_evaluations=0,assumption_mu='2',
               action_distance_is_upper_bound_not_actual_error=True,
               inputs=cases,postexecution_source_sha256=sha(Path(__file__)),source=gate)
    except BaseException:fail(out,tick);raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',action='append',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.input,a.output)
