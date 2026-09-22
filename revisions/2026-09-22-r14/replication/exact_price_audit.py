"""Independent all-pairs rational envelope, policy regions and welfare resolution.
Not an import or re-execution of the historical stack's convex-hull algorithm.
The exact post-processing remains conditional on the supplied node enclosures.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse,json,time,hashlib
from interval64 import I,exp
Q=I.rational

def outward(q,upper=True):
    import math
    f=float(q)
    if upper and F(f)<q:return math.nextafter(f,math.inf)
    if not upper and F(f)>q:return math.nextafter(f,-math.inf)
    return f

def ratnodes(nodes):
    return [{'k':F(v['k']),'L':F(v['L']),'U':F(v['U']),'B':[F(x) for x in v['B']],'actor_path':v.get('actor_path','')} for v in nodes]

def lines_on(nodes,a,b):
    mid=(a+b)/2;lines=[]
    for i,n in enumerate(nodes):
        B=n['B'][1] if mid>=n['k'] else n['B'][0]
        lines.append((n['L']+n['k']*B,-B,i))
    return lines

def upper_line(left,right):
    slope=(right['U']-left['U'])/(right['k']-left['k']);return left['U']-slope*left['k'],slope

def build(nodes):
    pieces=[];worst=F(0);maximizer=None;tests=0
    for left,right in zip(nodes,nodes[1:]):
        a,b=left['k'],right['k'];ls=lines_on(nodes,a,b);uc,um=upper_line(left,right);points={a,b}
        for i,(c,m,_) in enumerate(ls):
            for d,n,_ in ls[i+1:]:
                if m!=n:
                    p=(d-c)/(m-n)
                    if a<p<b:points.add(p)
        points=sorted(points);tests+=len(points)
        for p in points:
            gap=uc+um*p-max(c+m*p for c,m,i in ls)
            if gap>worst:worst,maximizer=gap,p
        for a,b in zip(points,points[1:]):
            mid=(a+b)/2;c,m,i=max(ls,key=lambda q:(q[0]+q[1]*mid,-q[2]))
            rec={'a':a,'b':b,'Lc':c,'Lm':m,'Uc':uc,'Um':um,'actor':i}
            if pieces and all(pieces[-1][k]==rec[k] for k in ['Lc','Lm','Uc','Um','actor']) and pieces[-1]['b']==a:pieces[-1]['b']=b
            else:pieces.append(rec)
    return pieces,worst,maximizer,tests

def enclosure(p,nodes,pieces):
    assert nodes[0]['k']<=p<=nodes[-1]['k']
    lows=[]
    for n in nodes:
        B=n['B'][1] if p>=n['k'] else n['B'][0];lows.append(n['L']-(p-n['k'])*B)
    cell=next(s for s in pieces if s['a']<=p<=s['b'])
    return max(lows),cell['Uc']+cell['Um']*p

def positive_interval(c,m,a,b):
    # Closed endpoints may give equality. Strict positivity holds on interiors
    # except an explicitly returned equality boundary.
    if m==0:return (a,b) if c>0 else None
    root=-c/m
    if m>0:a=max(a,root)
    else:b=min(b,root)
    return (a,b) if a<b else None

def merge(intervals):
    res=[]
    for a,b in sorted(intervals):
        if res and a<=res[-1][1]:res[-1]=(res[-1][0],max(res[-1][1],b))
        else:res.append((a,b))
    return res

def audit(raw):
    start=time.perf_counter();nodes=ratnodes(raw);pieces,gap,arg,count=build(nodes)
    active=[]
    for s in pieces:
        a,b,i=s['a'],s['b'],s['actor']
        if active and active[-1]['actor_index']==i and active[-1]['right_rational']==str(a):
            active[-1]['right_rational']=str(b);active[-1]['right']=float(b)
        else:active.append({'actor_index':i,'policy_k':float(nodes[i]['k']),'left_rational':str(a),'right_rational':str(b),'left':float(a),'right':float(b),'actor_path':nodes[i]['actor_path']})
    for s in active:s['width_rational']=str(F(s['right_rational'])-F(s['left_rational']));s['width']=float(F(s['width_rational']))
    regions=[]
    for anchor in ['.5','2','4','6']:
        p=F(anchor);Lp,Up=enclosure(p,nodes,pieces);sign=[];magnitude=[]
        for s in pieces:
            a,b=max(p,s['a']),s['b']
            if a>=b:continue
            # Strict separation: L(p)-U(q)>0.
            iv=positive_interval(Lp-s['Uc'],-s['Um'],a,b)
            if iv:sign.append(iv)
            # Width <= lower endpoint, i.e. untruncated upper <= 2 lower.
            iv=positive_interval(2*Lp-Up-2*s['Uc']+s['Lc'],-2*s['Um']+s['Lm'],a,b)
            if iv:magnitude.append(iv)
        regions.append({'anchor':float(p),'strict_positive_loss_regions':[[str(a),str(b)] for a,b in merge(sign)],
          'relative_width_at_most_one_regions':[[str(a),str(b)] for a,b in merge(magnitude)],
          'endpoint_convention':'At an equality endpoint the strict assertion is omitted; interior points satisfy the displayed predicate.'})
    Bmax=F(float((Q('.02')*(1-exp(-Q('.04')))/Q('.04')).hi))
    queries=[]
    for p,q in [('.5','2'),('2','8'),('4','4.1'),('4','8'),('6','8')]:
        p,q=F(p),F(q);Lp,Up=enclosure(p,nodes,pieces);Lq,Uq=enclosure(q,nodes,pieces)
        low=max(F(0),Lp-Uq);high=min(Up-Lq,Bmax*(q-p))
        queries.append({'p':float(p),'q':float(q),'welfare_loss_interval':[outward(low,False),outward(high)],
          'strict_positive_certified':Lp>Uq,'relative_width_at_most_one':high-low<=low and low>0})
    tol=F('.01');margin=tol-gap;stress=[]
    for delta in ['0','.000001','.000002','.000005','.00001','.00002','.00005','.0001']:
        d=F(delta);g=gap+2*d;stress.append({'common_node_endpoint_inflation':delta,'regret_upper':outward(g),'passes_0.01':g<tol})
    return {'status':'EXACT_POSTPROCESSING_COMPLETE','node_count':len(nodes),'algorithm':'all pairwise affine intersections, no production convex-hull import',
      'uniform_regret_rational':str(gap),'uniform_regret_upper':outward(gap),'maximizer_rational':str(arg),'candidate_breakpoints_checked':count,
      'uniform_policy_scope':'cost in [0.5,8], central initial state (0,2,1.25)',
      'active_policy_regions':active,'economic_resolution_regions':regions,'welfare_queries':queries,
      'common_endpoint_inflation_budget_rational':str(margin/2),'endpoint_stress':stress,
      'interpretation':'Nonnegative loss follows from model monotonicity even outside strict-separation regions. Stress tests do not validate upstream primitive inequalities.',
      'seconds':time.perf_counter()-start}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--nodes',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();raw=json.loads(a.nodes.read_text());r=audit(raw['nodes'] if isinstance(raw,dict) else raw);r['input_sha256']=hashlib.sha256(a.nodes.read_bytes()).hexdigest();a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['uniform_regret_upper','common_endpoint_inflation_budget_rational','welfare_queries','economic_resolution_regions']},indent=2))
