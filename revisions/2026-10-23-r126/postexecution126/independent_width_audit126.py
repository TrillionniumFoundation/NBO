"""Additional saved-bound width audit; no new independent economic acquisition."""
from pathlib import Path
import sys,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code126'))
from common126 import *


def run(independent,output):
    out,tick,info=start(output,'post-execution-independent-absolute-width-audit')
    try:
        gate=verify_inputs();path=Path(independent)/'checks126.jsonl';data=rows(path)
        widths=[F(r['j_upper'])-F(r['j_lower']) for r in data]
        assert len(data)==1584 and all(w>=0 for w in widths)
        ordinary=sum(F(r['regret_upper'])<=TAU and w<=OMEGA for r,w in zip(data,widths))
        stronger=sum(F(r['regret_upper'])<=TARGET and w<=OMEGA for r,w in zip(data,widths))
        finish(out,tick,rows=len(data),absolute_width_passes=sum(w<=OMEGA for w in widths),
            ordinary_regret_and_absolute_width_passes=ordinary,stronger_regret_and_absolute_width_passes=stronger,
            maximum_independent_width=max(widths),absolute_width_threshold=OMEGA,
            original_economic_evaluations=0,postexecution_analysis=True,
            frozen_regret_only_summary_not_modified=True,source_sha256=sha(Path(__file__)),input=str(path),input_sha256=sha(path),source=gate)
    except BaseException:fail(out,tick);raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--independent',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.independent,a.output)
