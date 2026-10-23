"""Exact rational reuse of a finite ledger of original Bellman certificates.

Only serialized original-objective supports and proved curvature enter here.
No neural model, quadrature, optimizer, or random generator is imported.
"""
from fractions import Fraction as F


def exact(x):
    return x if isinstance(x, F) else F(x)


def normalize(case):
    out = {k: exact(case[k]) for k in ("A", "incumbent", "mu", "L", "delta", "tau", "omega", "old_optimum_lower")}
    out["payloads"] = [{k: exact(p[k]) for k in ("a", "W", "U", "p_lower", "p_upper", "g_lower", "g_upper")} for p in case["payloads"]]
    for key in ("gradient_rule","gradient_cap","radius_indices"):
        if key in case:out[key]=case[key]
    if not (out["A"] > 0 and 0 < out["mu"] <= out["L"] and 0 <= out["incumbent"] <= out["A"] and
            min(out["delta"],out["tau"],out["omega"])>=0):
        raise ValueError("Invalid original action domain/curvature")
    if not out["payloads"]:
        raise ValueError("An original support ledger is required")
    for p in out["payloads"]:
        if not (0 <= p["a"] <= out["A"] and p["W"] <= p["U"] and p["p_lower"] <= p["p_upper"] and p["g_lower"] <= p["g_upper"]):
            raise ArithmeticError("Invalid support payload")
    cuts={F(0),out["A"]}
    for upper in (False,True):
        for l,r,_,_ in partition(out,F(0),out["A"],upper):cuts.update((l,r))
    if any(gradient(out,t,False)>gradient(out,t,True) for t in cuts):
        raise ArithmeticError("Incompatible global derivative intervals")
    return out


def transport(p, t, mu, L, upper):
    if upper:
        slope = L if t >= p["a"] else mu
        level = p["g_upper"]
    else:
        slope = mu if t >= p["a"] else L
        level = p["g_lower"]
    return slope, level - slope*p["a"]


def partition(case, lo, hi, upper, subset=None):
    """Exact affine envelope pieces, with every crossing and anchor retained."""
    ps = case["payloads"] if subset is None else subset
    lo, hi = exact(lo), exact(hi)
    if not 0 <= lo <= hi <= case["A"]:
        raise ValueError("Integral outside feasible domain")
    base = sorted({lo, hi} | {p["a"] for p in ps if lo < p["a"] < hi})
    result = []
    for left, right in zip(base, base[1:]):
        mid = (left+right)/2
        lines = [transport(p, mid, case["mu"], case["L"], upper) for p in ps]
        cuts = {left, right}
        for i, (s, c) in enumerate(lines):
            for v, w in lines[i+1:]:
                if s != v:
                    x = (w-c)/(s-v)
                    if left < x < right:
                        cuts.add(x)
        cuts = sorted(cuts)
        for a, b in zip(cuts, cuts[1:]):
            m = (a+b)/2
            choose = min if upper else max
            slope, intercept = choose(lines, key=lambda z: (z[0]*m+z[1], z[0], z[1]))
            result.append((a, b, slope, intercept))
    return result


def integral(pieces):
    return sum((s*(b*b-a*a)/2+c*(b-a) for a,b,s,c in pieces), F(0))


def contrast(case, origin, target, mode="fused"):
    a,b = exact(origin),exact(target)
    if a == b:
        return F(0),F(0)
    if mode == "best_single":
        pairs = []
        for p in case["payloads"]:
            reduced = dict(case, payloads=[p])
            pairs.append(contrast(reduced,a,b,"fused"))
        return max(v[0] for v in pairs),min(v[1] for v in pairs)
    if mode != "fused":
        raise ValueError("Unknown contrast mode")
    if a < b:
        return integral(partition(case,a,b,False)),integral(partition(case,a,b,True))
    return -integral(partition(case,b,a,True)),-integral(partition(case,b,a,False))


def raw_support(p,b,mu):
    d=b-p["a"]
    return p["W"]+min(p["p_lower"]*d,p["p_upper"]*d)+mu*d*d/2


def support_minimum(case):
    """Global minimum of max of interval-slope supports; no convexity assumed.

    Each piece has common quadratic curvature. The anchor kinks can point
    downwards because the support slope is enclosed, so all pieces are checked.
    """
    ps, mu, A = case["payloads"],case["mu"],case["A"]
    bases=sorted({F(0),A}|{p["a"] for p in ps})
    candidates={F(0),A}
    for left,right in zip(bases,bases[1:]):
        mid=(left+right)/2
        lines=[]
        for p in ps:
            slope=p["p_lower"] if mid>=p["a"] else p["p_upper"]
            lines.append((slope-mu*p["a"],p["W"]-slope*p["a"]+mu*p["a"]**2/2))
        cuts={left,right}
        for i,(s,c) in enumerate(lines):
            for v,w in lines[i+1:]:
                if s!=v:
                    x=(w-c)/(s-v)
                    if left<x<right:cuts.add(x)
        cuts=sorted(cuts)
        candidates.update(cuts)
        for l,r in zip(cuts,cuts[1:]):
            m=(l+r)/2
            s,c=max(lines,key=lambda z:(z[0]*m+z[1],z[0],z[1]))
            candidates.add(max(l,min(r,-s/mu)))
    x=min(candidates,key=lambda b:(max(raw_support(p,b,mu) for p in ps),b))
    value=max(raw_support(p,x,mu) for p in ps)
    return value,x


def gradient(case,b,upper):
    values=[s*b+c for s,c in [transport(p,b,case["mu"],case["L"],upper) for p in case["payloads"]]]
    return min(values) if upper else max(values)


def envelope_root(case,upper):
    A=case["A"]
    if gradient(case,F(0),upper)>=0:return F(0)
    if gradient(case,A,upper)<=0:return A
    for l,r,s,c in partition(case,F(0),A,upper):
        x=-c/s
        if l<=x<=r:return x
    raise ArithmeticError("A monotone derivative envelope lost its zero")


def robust_proposal(case):
    a=case["incumbent"]
    if gradient(case,a,False)>0:return min(a,envelope_root(case,False))
    if gradient(case,a,True)<0:return max(a,envelope_root(case,True))
    return a


def rounded_action(b,A):
    scale=2**30
    return F(max(0,min(int(b*scale),int(A*scale))),scale)


def candidate_menu(case):
    """Common finite menu for both modes, derived from the same ledger."""
    a,A=case["incumbent"],case["A"]
    proposals=[("fused",robust_proposal(case))]
    for i,p in enumerate(case["payloads"]):
        proposals.append(("anchor-"+str(i),robust_proposal(dict(case,payloads=[p]))))
    choices=[]
    for label,point in proposals:
        for power in range(6):
            b=rounded_action(a+(point-a)/2**power,A)
            choices.append(dict(source=label,fraction=F(1,2**power),b=b))
    return choices


def candidate(case,b,mode="fused",common=None):
    a=case["incumbent"];b=exact(b)
    if not 0<=b<=case["A"]:raise ValueError("Infeasible realized candidate")
    change_low,change_high=contrast(case,a,b,mode)
    upper_q=min(p["U"]+contrast(case,p["a"],b,mode)[1] for p in case["payloads"])
    lower_q=max(max(raw_support(p,b,case["mu"]) for p in case["payloads"]),
                max(p["W"]+contrast(case,p["a"],b,"fused")[0] for p in case["payloads"]))
    raw_B,where=support_minimum(case) if common is None else common
    B=max(raw_B,case["old_optimum_lower"])
    pad=case["delta"] if b!=a else F(0)
    gain_lower=-change_high-pad
    gain_upper=-change_low+pad
    lo=lower_q;hi=upper_q+case["delta"]
    if lower_q>upper_q or upper_q<B or change_low>change_high:
        raise ArithmeticError("Inconsistent original support ledger or envelope")
    return dict(b=b,change_lower=change_low,change_upper=change_high,
                gain_lower=gain_lower,gain_upper=gain_upper,
                lower=lo,upper=hi,optimum_lower=B,loss=hi-B,width=hi-lo,
                raw_envelope_minimum=raw_B,raw_envelope_minimizer=where,
                qualified=hi-B<=case["tau"] and hi-lo<=case["omega"],
                accepted=b!=a and gain_lower>0 and hi-B<=case["tau"] and hi-lo<=case["omega"])


def evaluate_menu(case,mode):
    common=support_minimum(case)
    records=[]
    for row in candidate_menu(case):
        records.append(dict(row,certificate=candidate(case,row["b"],mode,common)))
    good=[(i,r) for i,r in enumerate(records) if r["certificate"]["accepted"]]
    selected=min(good,key=lambda z:(-z[1]["certificate"]["gain_lower"],z[1]["b"],z[0])) if good else None
    return records,selected
