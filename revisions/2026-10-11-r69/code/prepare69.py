"""One-time preparation of ordinary sources, always before the science freeze.

The R67 implementation remains unchanged. New vector variants differ only
in paid optional upper witnesses and triangle selection for protected splits.
"""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r67'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace_once(text,old,new):
    if text.count(old)!=1:raise AssertionError(('Unexpected preparation anchor',old,text.count(old)))
    return text.replace(old,new,1)
def main():
    if (R/'audit/SOURCE_FREEZE69.json').exists():
        print('Ordinary scientific sources already frozen; preparation makes no changes.');return
    source=OLD/'code/vector66.py';text=source.read_text()
    anchor="        triangles=[[(0,1,2)] for _ in x];running=np.zeros(N);active=np.arange(N)"
    insertion="""        proposal=self.proposal(x,r,cap) if hasattr(self,'proposal') else None
        if proposal is not None:
            if proposal.shape!=(N,2) or np.any(proposal<0) or np.any(proposal.sum(axis=1)>cap):
                raise ValueError('Invalid optional vector witness')
            points[:,3]=proposal
            value=self.qbound(x,proposal,r,tol)
            lows[:,3]=value.lo;highs[:,3]=value.hi;sizes+=1
        # The optional witness changes only the upper certificate. The
        # original triangle still covers every feasible continuous action.
"""+anchor
    text=replace_once(text,anchor,insertion)
    anchor="                    tri=triangles[row][loc];j,h=max(((0,1),(1,2),(2,0)),key=lambda e:np.sum((points[row,tri[e[0]]]-points[row,tri[e[1]]])**2))"
    insertion="""                    splitloc=loc
                    if getattr(self,'uniform',False):
                        splitloc=max(range(len(triangles[row])),key=lambda n:max(
                            np.sum((points[row,triangles[row][n][j]]-points[row,triangles[row][n][h]])**2)
                            for j,h in ((0,1),(1,2),(2,0))))
                    tri=triangles[row][splitloc];j,h=max(((0,1),(1,2),(2,0)),key=lambda e:np.sum((points[row,tri[e[0]]]-points[row,tri[e[1]]])**2))"""
    text=replace_once(text,anchor,insertion)
    text=replace_once(text,"triangles[row][loc]=(pa,sz,pc)","triangles[row][splitloc]=(pa,sz,pc)")
    generated=R/'code/vector_base69.py';generated.write_text(text)
    center=R/'code/center69.py';text=center.read_text()
    if "N=len(lo);R=F(support_hi)-F(support_lo)" in text:
        text=replace_once(text,"N=len(lo);R=F(support_hi)-F(support_lo)","N=len(lo);support_lo=-q.up(-F(support_lo));support_hi=q.up(F(support_hi));R=F(support_hi)-F(support_lo)")
    text=text.replace('policy_work=policy.counts,evaluation_work=evaluator.counts','policy_work=policy.counts.copy(),evaluation_work=evaluator.counts.copy()')
    center.write_text(text)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
    (R/'audit').mkdir(exist_ok=True)
    (R/'audit/PREPARATION69.json').write_text(json.dumps(dict(status='passed',
        inherited_vector_sha256=sha(source),ordinary_vector_sha256=sha(generated),
        changes=['Optional paid upper witness; original continuous-action triangle remains intact',
                 'Uniform arm changes split triangle only; global lower certificate remains minimum over all triangles',
                 'Round both support endpoints outward before bounding the range of endpoint samples',
                 'Snapshot mutable operation counters in each inference batch'],
        old_source_modified=False),indent=2)+'\n')
    print('R69 ordinary sources prepared and parsed; no experiment executed.')
if __name__=='__main__':main()
