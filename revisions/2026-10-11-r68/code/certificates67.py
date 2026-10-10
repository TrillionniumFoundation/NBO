"""Exact-rational certificate-aware readout training and pre-query tests.

A fixed ReLU partition-of-unity feature map and a box-constrained readout
form a constructive neural selector. This is not the frozen R66/R67 L-BFGS
estimator; its optimizer and finite certificate examples are separate tests.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Sequence

@dataclass(frozen=True)
class Context:
    left: F
    right: F
    upper_left: F
    upper_right: F
    lower: F
    tolerance: F
    curvature: F=F(2)
    rounding_allowance: F=F(0)
    work_cap: F=F(1)
    def __post_init__(self):
        if not self.left<self.right or self.tolerance<=0 or self.curvature<=0 or self.rounding_allowance<0 or self.work_cap<0:
            raise ValueError('Invalid certified context')
    def chord(self,fraction:F)->F:
        if not 0<=fraction<=1:raise ValueError('Proposal outside interval')
        width=self.right-self.left
        return (1-fraction)*self.upper_left+fraction*self.upper_right-self.curvature*width*width*fraction*(1-fraction)/2
    def score(self,fraction:F)->F:
        return self.chord(fraction)+self.rounding_allowance-self.lower
    def derivative(self,fraction:F)->F:
        return self.upper_right-self.upper_left+self.curvature*(self.right-self.left)**2*(fraction-F(1,2))


def relu(x:F)->F:return max(F(0),x)
def hat_features(x:F,knots:Sequence[F])->tuple[F,...]:
    """Exact affine--ReLU nonnegative features summing to one on the domain."""
    knots=tuple(map(F,knots))
    if len(knots)<2 or any(a>=b for a,b in zip(knots,knots[1:])) or not knots[0]<=x<=knots[-1]:
        raise ValueError('Ordered knots and an in-domain point are required')
    phi=[1-(x-knots[0])/(knots[1]-knots[0])+relu(x-knots[1])/(knots[1]-knots[0])]
    for i in range(1,len(knots)-1):
        a,b,c=knots[i-1:i+2]
        phi.append(relu(x-a)/(b-a)-(1/(b-a)+1/(c-b))*relu(x-b)+relu(x-c)/(c-b))
    phi.append(relu(x-knots[-2])/(knots[-1]-knots[-2]))
    if min(phi)<0 or sum(phi)!=1:raise ArithmeticError('Feature identity failed')
    return tuple(phi)

def fraction(features:Sequence[F],weights:Sequence[F])->F:
    if len(features)!=len(weights) or not features or min(features)<0 or sum(features)!=1 or min(weights)<0 or max(weights)>1:
        raise ValueError('Simplex features and a box readout are required')
    return sum(a*b for a,b in zip(features,weights))

def objective(contexts:Sequence[Context],features:Sequence[Sequence[F]],weights:Sequence[F],margin:F,penalty:F=F(0)):
    if not contexts or len(contexts)!=len(features) or margin<=0 or penalty<0:raise ValueError('Invalid loss specification')
    gradient=[penalty*w for w in weights];value=penalty*sum(w*w for w in weights)/2;n=len(contexts)
    failures=0;residuals=[]
    for context,phi in zip(contexts,features):
        z=fraction(phi,weights);score=context.score(z);e=max(F(0),score-context.tolerance+margin)
        value+=context.work_cap*e*e/n
        for j,p in enumerate(phi):gradient[j]+=2*context.work_cap*e*context.derivative(z)*p/n
        failures+=int(score>context.tolerance);residuals.append(e)
    vertex=[F(0) if g>=0 else F(1) for g in gradient]
    gap=sum(g*(w-v) for g,w,v in zip(gradient,weights,vertex))
    if gap<0:raise ArithmeticError('Negative box dual gap')
    return dict(value=value,gradient=tuple(gradient),vertex=tuple(vertex),dual_gap=gap,failures=failures,residuals=tuple(residuals),
                average_work_upper=value/(margin*margin))

def fit_readout(contexts,features,margin,penalty=F(0),iterations=64):
    if iterations<0 or not features:raise ValueError('Nonnegative finite iteration cap required')
    weights=tuple(F(1,2) for _ in features[0]);history=[];best=None
    for j in range(iterations+1):
        result=objective(contexts,features,weights,F(margin),F(penalty))
        row=dict(iteration=j,weights=weights,**result);history.append(row)
        if best is None or row['value']<best['value']:best=row
        if j<iterations:
            gamma=F(2,j+2);weights=tuple((1-gamma)*w+gamma*v for w,v in zip(weights,result['vertex']))
    return dict(best=best,history=history,claim='Exact convex readout objective and primal-dual certificate; not nonconvex hidden-layer training')
