"""One-time preproduction correction caught by the original-primitive fixture.

No R62 production run or freeze preceded this correction. The failed fixture
is retained on its execution-attempt branch. Ordinary corrected sources are
committed before the production freeze; this script is not a runtime patch.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def main():
    if (R/'audit/SOURCE_FREEZE62.json').exists():
        raise RuntimeError('Never edit an already frozen scientific source')
    changes={
        'code/core62.py': [('B=F(3,4)','B=F(15,16)'),('F(19,d)','F(27,d)'),('F(42,d)','F(54,d)')],
        'code/tests62.py':[('F(19,d)','F(27,d)'),('F(42,d)','F(54,d)'),('F(71,32*d)','F(107,128*d)'),('F(71,64*d)','F(107,256*d)')],
        'code/proposals62.py':[('+.75*','+float(c.B)*')],
        'PROTOCOL62.md':[('beta=3/4','beta=15/16')],
        'sections/accuracy62.tex':[(r'\beta=3/4',r'\beta=15/16'),('19/d','27/d'),('42/d','54/d'),('71/(32d)','107/(128d)')]
    }
    records=[]
    for name,pairs in changes.items():
        path=R/name;old=path.read_text();new=old
        for before,after in pairs:new=new.replace(before,after)
        path.write_text(new);records.append(dict(file=name,changed=old!=new))
    path=R/'code/core62.py';text=path.read_text();marker='TASKS=('
    guard="if F(n.BETA)!=B:raise AssertionError('R62 discount differs from the unchanged inherited economic primitives')\n"
    if guard not in text:text=text.replace(marker,guard+marker,1);path.write_text(text)
    (R/'audit').mkdir(exist_ok=True)
    (R/'audit/PREPRODUCTION_CORRECTION62.json').write_text(json.dumps(dict(scope='Original-primitive compatibility fixture caught a proposed discount mismatch before any source freeze or production observation. Correct discount 15/16; uniform bounds G<=27/d, M<=54/d; state curvature >=107/(128d).',failed_fixture_run=38016562929,changes=records),indent=2)+'\n')
    print('Corrected ordinary sources before production: beta=15/16, G<=27/d, M<=54/d.',flush=True)
if __name__=='__main__':main()
