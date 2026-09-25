"""Non-benchmark regression tests for the non-strict-action fallback."""
from fractions import Fraction as F
from pathlib import Path
import json
from regret import solve,write_proof
from verify_regret import verify
R=Path(__file__).resolve().parents[1]
def main():
    d=dict(seed=-1,n=2,T=3,m=2,beta=F(19,20),epsilon=F(1,100),P=[[[F(1),F(0)],[F(1),F(0)]],[[F(0),F(1)],[F(0),F(1)]]],r=[[F(0),F(0)],[F(0),F(0)]],k=[[F(1),F(0)],[F(1),F(0)]],terminal=[F(0),F(0)],nu=[F(1,2),F(1,2)])
    out=[]
    for mode in ('unscaled','scaled'):
        proof,meta=solve(d,mode);p=R/'proofs'/('unit_tied_'+mode+'.json.gz');write_proof(p,proof);check=verify(p)
        assert not meta['strict'] and F(check['lower'])==F(check['upper'])==0
        out.append(dict(mode=mode,passed=True,strict_rate_inapplicable=True,check=check))
    (R/'results/unit_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Two exact-tie fallback checks passed; not counted as benchmark successes.')
if __name__=='__main__':main()
