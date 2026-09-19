"""Integrate the general institutional query theorem and check its cap witness.

The proof is analytic; these rational fixtures verify a boundary case where all
coordinate messages agree, a joint message differs, and the regret is positive
including nonprocurement. No floating-point angular decision is used.
"""
from __future__ import annotations
import json
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];REL='revisions/2026-09-20-r19/paper';P=ROOT/REL;O=ROOT/'replication/r19/output'

def once(path,old,new):
    s=path.read_text()
    if new in s:return
    if s.count(old)!=1:raise ValueError('ambiguous information integration '+str(path))
    path.write_text(s.replace(old,new))

def main():
    c=P/'information_complexity.tex'
    s=c.read_text().replace('\\min_Z w^j\\cdot z','\\min_{z\\in Z} w^j\\cdot z')
    note='A known common additive purchaser receipt may be attached to the two compared offers. When necessary, take it large enough to make both offers strictly preferable to nonprocurement. It changes neither the private value queries nor the regret between offers.\n\n'
    if note not in s:s=s.replace('\\begin{theorem}[Menu information and institutional flexibility]',note+'\\begin{theorem}[Menu information and institutional flexibility]')
    c.write_text(s)
    marker='\\input{'+REL+'/main_information_theorem}\n'
    once(P/'main.tex',marker,marker+'\\input{'+REL+'/information_complexity}\n')
    marker='\\input{'+REL+'/proofs_new}\n'
    once(P/'supplement.tex',marker,marker+'\\input{'+REL+'/information_complexity_proof}\n')
    marker='\\section{Initial-state versus uniform enforcement (Report Section 10)}'
    paragraph='Theorem~\\ref{paper-thm:r19-query-complexity} further supplies a general query-complexity result. For $m$ distinct institutional payoff rays, exactly $m$ queries are necessary in the worst case to identify all robust returns, and one query on each adverse ray is sufficient. The lower bound allows deterministic adaptive acquisition and concerns identification against every safe-offer level, not an already trivial fixed comparison. When the institution is chosen only after information acquisition, a hidden support cap gives a positive conditional minimax regret and a necessary spherical-cover bound. For fixed feature dimension $k$, its query requirement grows at least as $(r/\\varepsilon)^{(k-1)/2}$. The complete ball-and-spike proof is in the supplement. A rational boundary fixture checks identical coordinate messages, the separating joint message, and positive regret after a common purchaser receipt makes nonprocurement irrelevant. This strengthens the information contribution beyond the two-simplex example without recasting an information lower bound as a known-model solver lower bound.\n\n'
    once(P/'response.tex',marker,paragraph+marker)
    # Exact two-dimensional cap, including equality at the exclusion boundary.
    center=(Q(1),Q(1));r=Q(1,4);R=Q(1,2);delta=Q(1,16);u=(Q(3,5),Q(4,5))
    if sum(x*x for x in u)!=1:raise ValueError('unit direction')
    qs=((Q(1),Q(0)),(Q(-1),Q(0)),(Q(0),Q(1)),(Q(0),Q(-1)))
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    records=[]
    for q in qs:
      base=dot(q,center)+r;other=max(base,dot(q,center)+(r+delta)*dot(q,u))
      if base!=other:raise ValueError('cap should be hidden from coordinate query')
      records.append(dict(direction=list(map(str,q)),ball=str(base),spike=str(other)))
    joint=dot(u,center)+r;other=dot(u,center)+r+delta
    common=Q(2);b=common-dot(u,center)-r;bad=b-delta;safe=b-delta/2
    regret1=(b-safe)/2;regret0=(safe-bad)/2
    if not (0<bad<safe<b and regret1==regret0==delta/4 and other-joint==delta and (r+delta)*max(dot(q,u) for q in qs)==r):
      raise ValueError('joint regret or cap boundary')
    record=dict(schema='nbo-r19-query-complexity-fixture-v1',passed=True,coordinate_queries=records,
      unit_hidden_direction=list(map(str,u)),inner_radius=str(r),outer_radius=str(R),spike_gap=str(delta),
      directed_query_values=[str(joint),str(other)],purchaser_common_receipt=str(common),
      robust_returns=[str(b),str(bad)],safe_return=str(safe),minimax_regret=str(delta/4),
      scope='Exact rational boundary fixture for the analytic menu and spherical-cover theorem. Query acquisition is not a known-model computational lower bound.')
    (O/'complexity_validation.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    status=ROOT/'revisions/2026-09-20-r19/response_status.json';j=json.loads(status.read_text());item='menu-information query complexity and institutional-flexibility lower bound'
    if item not in j['new_science']:j['new_science'].append(item)
    status.write_text(json.dumps(j,indent=2)+'\n')
    print('Institutional query-complexity theorem integrated; rational support-cap and regret fixtures passed.')
if __name__=='__main__':main()
