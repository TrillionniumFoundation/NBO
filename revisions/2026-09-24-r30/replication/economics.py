"""Independent occupancy accounting and strong structural controls."""
from pathlib import Path
from fractions import Fraction as F
import json,time
import numpy as np
import adaptive as a
OUT=a.REV/'results/adaptive'

def decode_segments(path):
    z=json.loads(Path(path).read_text());return [(F(l),F(r),v) for l,r,v in z['segments']]
def policy_segments(cert):return [(F(z['l']),F(z['r']),z['action']) for z in cert['leaves']]
def overlay_cost(base,other,priority=True):
    i=j=0;total=F(0)
    while i<len(base) and j<len(other):
        l=max(base[i][0],other[j][0]);r=min(base[i][1],other[j][1])
        if l<r and base[i][2]!=other[j][2]:total+=a.mass(l,r,priority)
        x,y=base[i][1],other[j][1]
        if x<=y:i+=1
        if y<=x:j+=1
    return a.H*total

def mean_reward(c,segments):return a.H*sum(v*a.integral(c,l,r) for l,r,v in segments)
def compile_polynomial(c):
    rows=[]
    def rec(l,r):
        lo,hi=a.bernstein(c,l,r)
        if lo>=0:v=1
        elif hi<=0:v=0
        elif r-l<=F(1,2**40):v=int(a.val(c,(l+r)/2)>=0)
        else:
            m=(l+r)/2;rec(l,m);rec(m,r);return
        if rows and rows[-1][2]==v:rows[-1]=(rows[-1][0],r,v)
        else:rows.append((l,r,v))
    rec(F(0),F(1))
    # The comparator is this exact rational compiled policy, not an unverified
    # assertion that an irrational polynomial root is a dyadic boundary.
    points={l:v for l,r,v in rows};points[F(1)]=rows[-1][2]
    return rows,points

def main():
    rows=json.loads((OUT/'summary.json').read_text());economic=[];poly=[]
    for row in rows:
        tag=row['tag'];c=a.MODELS[row['model']]
        raw=decode_segments(OUT/'compiled'/f'{tag}.json')
        cert=json.loads((OUT/'certificates'/f'{tag}.json').read_text());completed=policy_segments(cert)
        ref=json.loads((OUT/'baselines'/f"{row['model']}_structured_near_exact.json").read_text());reference=policy_segments(ref)
        cr=overlay_cost(raw,reference);cc=overlay_cost(raw,completed)
        welfare_difference=mean_reward(c,reference)-mean_reward(c,completed);saved=cr-cc
        assert cc==F(row['priority_edits'])
        economic.append({'tag':tag,'reference_priority_cost':str(cr),'completion_priority_cost':str(cc),
            'saved_priority_cost':str(saved),'reference_minus_completion_payoff':str(welfare_difference),
            'break_even_revision_price':str(welfare_difference/saved) if saved>0 else None,
            'net_advantage_at_price_1_20':str(F(1,20)*saved-welfare_difference),
            'comparison':'same raw incumbent; structure-aware reference certified within H*1e-12; no CPU shadow price assumed'})
    for model,c in a.MODELS.items():
        x=(np.arange(512)+.5)/512;t=time.perf_counter()
        cf=np.polynomial.polynomial.polyfit(x,np.polynomial.polynomial.polyval(x,list(map(float,c))),len(c)-1)
        ft=time.perf_counter()-t;rawcoeff=[F(float(v)) for v in cf]
        a.save(OUT/'candidates'/f'{model}_polynomial.json',{'coefficients':rawcoeff,'seconds':ft,'grid':512,'degree':len(c)-1})
        t=time.perf_counter();s,p=compile_polynomial(rawcoeff);compiletime=time.perf_counter()-t
        a.save(OUT/'compiled'/f'{model}_polynomial.json',{'segments':s,'points':[[x,v] for x,v in p.items()]})
        t=time.perf_counter();cert=a.complete(c,s,p);ct=time.perf_counter()-t
        metrics=a.verify(c,cert);raw=a.raw_regret(c,s,p)
        a.save(OUT/'certificates'/f'{model}_polynomial.json',cert)
        poly.append(dict(model=model,fit_seconds=ft,compilation_seconds=compiletime,certification_seconds=ct,
                         bound_calls=cert['bound_calls'],**metrics,**raw))
    a.save(OUT/'economic_comparisons.json',economic);a.save(OUT/'polynomial_controls.json',poly)
    print('ECONOMIC ROWS',len(economic),'POLYNOMIAL CONTROLS',len(poly))

if __name__=='__main__':main()
