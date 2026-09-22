"""Uniform initial-state AND cost certificate by concavity and four vertices.

The deployed time controls depend on initial wealth through an exact budget
shift; no state-feedback neural interpretation is attached to this result.
Each corner primal is re-evaluated by the new original-utility quadrature.
The continuum upper follows convexity in k, and every state interior follows
joint concavity of utility and convexity of the affine-dual localization.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import json,time,argparse,hashlib
from interval64 import I,exp,log,stack,add_reduce
from validated_gauss import Q
from independent_primal import evaluate
from exact_price_audit import outward
ROOT=Path(__file__).resolve().parents[3]
CORNERS=[('1.98','1.24'),('1.98','1.26'),('2.02','1.24'),('2.02','1.26')]

def corner_upper(d,u,x):
    du=Q(u)-2;zdelta=8*exp(-Q(18))*(exp(120*du)+exp(-120*du)-2)
    return I(d['optimal_value_upper'])+du*I(*d['b0_interval'])+(Q(x)-Q('1.25'))*I(d['y0'])+zdelta

def full_budget(actor):
    data=json.loads(Path(actor).read_text());th=I(data['theta']);n=len(th.lo);mass=stack([(exp(-Q('.04')*Q(F(j,n)))-exp(-Q('.04')*Q(F(j+1,n))))/Q('.04') for j in range(n)])
    return add_reduce(th.square()/2*mass)

def envelope(records):
    nodes=[{'k':F(r['k']),'L':[F(c['L']) for c in r['corners']],'U':[F(c['U']) for c in r['corners']],
       'B':[F(b) for b in r['full_budget']]} for r in records]
    worst=F(0);arg=None;active=[];count=0
    for a0,a1 in zip(nodes,nodes[1:]):
        a,b=a0['k'],a1['k'];mid=(a+b)/2;all_lines=[];by_policy=[]
        for j,p in enumerate(nodes):
            B=p['B'][1] if mid>=p['k'] else p['B'][0]
            ls=[]
            for v in range(4):
                um=(a1['U'][v]-a0['U'][v])/(b-a);uc=a0['U'][v]-um*a
                # upper chord minus policy lower line
                ls.append((uc-p['L'][v]-p['k']*B,um+B,j,v))
            by_policy.append(ls)
            # Drop a corner only if another dominates it on the ENTIRE cell.
            for z,l in enumerate(ls):
                c,m,_,_=l
                dominated=False
                for w,r in enumerate(ls):
                    if z==w:continue
                    d,n,_,_=r
                    if d+n*a>=c+m*a and d+n*b>=c+m*b and (d+n*a>c+m*a or d+n*b>c+m*b or w<z):
                        dominated=True;break
                if not dominated:all_lines.append(l)
        points={a,b}
        for z,(c,m,_,_) in enumerate(all_lines):
            for d,n,_,_ in all_lines[z+1:]:
                if m!=n:
                    p=(d-c)/(m-n)
                    if a<p<b:points.add(p)
        points=sorted(points);count+=len(points)
        def best(p):
            g=[max(c+m*p for c,m,j,v in ls) for ls in by_policy]
            j=min(range(len(g)),key=lambda j:(g[j],j));return g[j],j
        for p in points:
            g,j=best(p)
            if g>worst:worst,arg=g,p
        for p,q in zip(points,points[1:]):
            _,j=best((p+q)/2)
            if active and active[-1]['policy']==j and active[-1]['right']==str(p):active[-1]['right']=str(q)
            else:active.append({'left':str(p),'right':str(q),'policy':j,'policy_k':float(nodes[j]['k'])})
    return {'uniform_regret_upper':outward(worst),'uniform_regret_rational':str(worst),'maximizer_rational':str(arg),
      'active_state_uniform_policy_regions':active,'exact_breakpoints_checked':count,
      'domain':{'time':0,'u':['1.98','2.02'],'x':['1.24','1.26'],'k':['.5','8']},
      'proof':'four-corner concavity/convexity transfer, affine objective continuation, all pairwise active line intersections',
      'policy':'Choose price-indexed stored theta and consumption vector; shift each consumption by (x0-1.25)/Q_r; hold 16 time controls; p=0.',
      'not_claimed':'This is not a near-optimal full-state neural actor/critic certificate or a guarantee at all initial times.'}

def main(library,out):
    start=time.perf_counter();out.mkdir(parents=True,exist_ok=False);nodes=json.loads((library/'nodes.json').read_text());records=[]
    for r in nodes:
        k=r['k'];tag=f'{k:g}';d=json.loads((library/f'dual_k{tag}.json').read_text());actor=ROOT/r['actor_path'];corners=[]
        for u,x in CORNERS:
            p=evaluate(actor,str(k),u0=u,x0=x);U=corner_upper(d,u,x)
            p['dual_state_upper']=float(U.hi);p['dual_state_upper_expression_interval']=U.pair()
            p['regret_upper']=float((I(U.hi)-I(p['value_interval'][0])).hi)
            (out/f'k{tag}_u{u}_x{x}.json').write_text(json.dumps(p,indent=2)+'\n')
            corners.append({'u':u,'x':x,'L':p['value_interval'][0],'U':float(U.hi),'gap':p['regret_upper']})
        row={'k':k,'corners':corners,'full_budget':full_budget(actor).pair(),'uniform_state_gap_at_node':max(c['gap'] for c in corners)}
        records.append(row);(out/'corners.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(row),flush=True)
    result=envelope(records);result['seconds']=time.perf_counter()-start;result['status']='VALID_UNIFORM_STATE_COST_ENCLOSURE'
    (out/'envelope.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--library',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();main(a.library,a.out)
