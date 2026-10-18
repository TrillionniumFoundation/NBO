"""Exact rational point-information study, not the investment experiment.

The algorithms see a counted point oracle. Formula integration is a separate
reference calculation, implemented twice without calling the quadrature rule.
"""
from fractions import Fraction as F
from pathlib import Path
import time,json,hashlib
BETA=F(15,16);MU=F(8);QUANTUM=F(1,2**30)
NAMES=('linear','square','quartic','hinge','hinge-square','mixed')


def value(name,z):
    if name=='linear':return z
    if name=='square':return z*z
    if name=='quartic':return z**4
    if name=='hinge':return max(F(0),z-F(1,3))
    if name=='hinge-square':return max(F(0),z-F(1,3))**2
    if name=='mixed':return z*z+max(F(0),z-F(1,2))/4
    raise ValueError(name)


def reference(name,alpha):
    """Closed-form tail primitives; no point-oracle calls."""
    def power(k):return (1-alpha**(k+1))/F(k+1)/(1-alpha)
    def hinge(c,k):return ((1-c)**(k+1)-max(F(0),alpha-c)**(k+1))/F(k+1)/(1-alpha)
    if name=='linear':return power(1)
    if name=='square':return power(2)
    if name=='quartic':return power(4)
    if name=='hinge':return hinge(F(1,3),1)
    if name=='hinge-square':return hinge(F(1,3),2)
    if name=='mixed':return power(2)+hinge(F(1,2),1)/4
    raise ValueError(name)


def independent_reference(name,alpha):
    """Separate power-basis assembly and exact segment integration."""
    cuts=[alpha,F(1)]
    if name in ('hinge','hinge-square') and alpha<F(1,3):cuts.append(F(1,3))
    if name=='mixed' and alpha<F(1,2):cuts.append(F(1,2))
    cuts=sorted(set(cuts));total=F(0)
    for l,r in zip(cuts,cuts[1:]):
        m=(l+r)/2
        if name=='linear':coeff={1:F(1)}
        elif name=='square':coeff={2:F(1)}
        elif name=='quartic':coeff={4:F(1)}
        elif name=='hinge':coeff={0:-F(1,3),1:F(1)} if m>F(1,3) else {}
        elif name=='hinge-square':coeff={0:F(1,9),1:-F(2,3),2:F(1)} if m>F(1,3) else {}
        elif name=='mixed':
            coeff={2:F(1)}
            if m>F(1,2):coeff.update({0:-F(1,8),1:F(1,4)})
        else:raise ValueError(name)
        total+=sum((v*(r**(k+1)-l**(k+1))/F(k+1) for k,v in coeff.items()),F(0))
    return total/(1-alpha)


class Oracle:
    def __init__(self,name):self.name=name;self.cache={};self.requests=0
    def __call__(self,z):
        self.requests+=1
        if z not in self.cache:self.cache[z]=value(self.name,z)
        return self.cache[z]


def interval(oracle,alpha,n):
    """Full-domain equal grid, exact monotone tail-cell midpoint/secant rules.

    All 2n+1 full-domain locations are charged; known monotonicity gives the
    tail cells, since these alpha*n are integers. No formula access is used.
    """
    if n<4 or n&(n-1) or (alpha*n).denominator!=1:raise ValueError('Dyadic aligned grid required')
    edges=[oracle(F(i,n)) for i in range(n+1)]
    mids=[oracle(F(2*i+1,2*n)) for i in range(n)]
    k=int(alpha*n);den=F(n)*(1-alpha)
    lo=sum(mids[k:],F(0))/den
    hi=sum(((edges[i]+edges[i+1])/2 for i in range(k,n)),F(0))/den
    if lo>hi:raise ArithmeticError('Invalid convex enclosure')
    return lo,hi


def action(lo,hi):
    raw=F(1,2)-BETA*(lo+hi)/(2*MU)
    return max(F(0),min(F(1),F(raw//QUANTUM)*QUANTUM))


def certificate(lo,hi):
    if lo>hi:raise ValueError('Reversed risk interval')
    return MU/2*(BETA*(hi-lo)/(2*MU)+QUANTUM)**2


def objective(a,risk):return 4*(a-F(1,2))**2+BETA*a*risk


def run(out):
    start=time.perf_counter();rows=[];checks=0;reference_seconds=0.
    for name in NAMES:
        for alpha in (F(1,2),F(3,4)):
            t=time.perf_counter();truth=reference(name,alpha);ind=independent_reference(name,alpha)
            if truth!=ind:raise ArithmeticError('Independent reference disagreement')
            opt=F(1,2)-BETA*truth/MU
            if not F(0)<opt<F(1):raise ArithmeticError('Interior hypothesis fails')
            optimum=objective(opt,truth);reference_seconds+=time.perf_counter()-t;checks+=2
            for exponent in (12,16,20,24,28):
                eps=F(1,2**exponent)
                for rule in ('risk-width','decision-gap'):
                    oracle=Oracle(name);trace=[];t=time.perf_counter()
                    for power in range(2,13):
                        n=2**power;lo,hi=interval(oracle,alpha,n)
                        a=action(lo,hi);bound=certificate(lo,hi)
                        predicate=BETA*(hi-lo)<=eps if rule=='risk-width' else bound<=eps
                        trace.append(dict(bins=n,lower=str(lo),upper=str(hi),action=str(a),
                            regret_bound=str(bound),accepted=predicate,unique_queries=len(oracle.cache),requests=oracle.requests))
                        if not lo<=truth<=hi:raise ArithmeticError('Reference outside enclosure')
                        checks+=1
                        if predicate:break
                    regret=objective(a,truth)-optimum
                    if not F(0)<=regret<=bound:raise ArithmeticError('False decision certificate')
                    if predicate and regret>eps:raise ArithmeticError('Unsound stopping rule')
                    checks+=2
                    rows.append(dict(name=name,alpha=str(alpha),epsilon=str(eps),epsilon_exponent=exponent,
                        rule=rule,bins=n,risk=str(truth),optimal_action=str(opt),action=str(a),
                        original_cost=str(objective(a,truth)),optimal_cost=str(optimum),regret=str(regret),
                        regret_bound=str(bound),qualified=predicate,unique_queries=len(oracle.cache),
                        requests=oracle.requests,seconds=time.perf_counter()-t,trace=trace))
    obj=dict(status='executed',rows=rows,exact_checks=checks,seconds=time.perf_counter()-start,
        independent_reference_seconds=reference_seconds,method_rows=len(rows),
        population_inference=False,original_investment=False,point_oracle_formula_access=False,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if len(rows)!=120:raise ArithmeticError('Incomplete fixed catalogue')
    Path(out).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    return obj

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output.exists():raise FileExistsError('Never overwrite an attempted experiment')
    print({k:v for k,v in run(a.output).items() if k!='rows'})
