"""Strong conventional same-information action bounds, with the global cap.

This exact, low-dimensional envelope comparator receives every original
derivative interval, the same proved global derivative cap and every original
support/value observation. A separately obtained optimum lower bound is also
used. It makes no numerical optimization call or new economic query.
"""
from fractions import Fraction as F


def integral_envelope(case, left, right, upper):
    left, right = F(left), F(right)
    A, mu, L, M = (F(case[k]) for k in ('A','mu','L','gradient_cap'))
    if not 0 <= left <= right <= A:
        raise ValueError('Integral outside original feasible action domain')
    anchors = sorted({left,right} | {F(p['a']) for p in case['payloads'] if left < F(p['a']) < right})
    answer = F(0)
    for lo, hi in zip(anchors, anchors[1:]):
        mid = (lo+hi)/2
        lines = [(F(0), M if upper else -M)]
        for payload in case['payloads']:
            a = F(payload['a'])
            slope = (L if mid >= a else mu) if upper else (mu if mid >= a else L)
            level = F(payload['g_upper' if upper else 'g_lower'])
            lines.append((slope,level-slope*a))
        cuts = {lo,hi}
        for i,(s,c) in enumerate(lines):
            for v,w in lines[i+1:]:
                if s != v:
                    cross=(w-c)/(s-v)
                    if lo < cross < hi:cuts.add(cross)
        cuts=sorted(cuts)
        choose=min if upper else max
        for a,b in zip(cuts,cuts[1:]):
            midpoint=(a+b)/2
            slope,level=choose(lines,key=lambda item:(item[0]*midpoint+item[1],item))
            answer += slope*(b*b-a*a)/2+level*(b-a)
    return answer


def contrast(case, origin, target):
    a,b=F(origin),F(target)
    if a==b:return F(0),F(0)
    if a<b:return integral_envelope(case,a,b,False),integral_envelope(case,a,b,True)
    return -integral_envelope(case,b,a,True),-integral_envelope(case,b,a,False)


def original_levels(case, action):
    b=F(action); mu=F(case['mu'])
    lower=[F(case['old_optimum_lower'])]
    upper=[]
    for p in case['payloads']:
        a,W,U,pl,pu=(F(p[k]) for k in ('a','W','U','p_lower','p_upper'))
        dl,du=contrast(case,a,b)
        d=b-a
        lower += [W+min(pl*d,pu*d)+mu*d*d/2,W+dl]
        upper.append(U+du)
    lo,hi=max(lower),min(upper)
    if lo>hi:raise ArithmeticError('Inconsistent exact original value information')
    return lo,hi


def cheap_upper(case, origin, target):
    if F(origin)==F(target):return F(0)
    lower_origin,_=original_levels(case,origin)
    _,upper_target=original_levels(case,target)
    return min(contrast(case,origin,target)[1],upper_target-lower_origin)
