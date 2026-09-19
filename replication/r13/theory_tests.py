"""Executable exact witnesses for the new oracle and open-mandate results."""
from fractions import Fraction as Q
from pathlib import Path
import copy,json,types
import numpy as np
from oracle_polytope import response_polytope,exact_vertex,encode,RationalLP
from certified_arithmetic import positive_witness,verify_positive

def run():
    h=Q(1,10);rows=[]
    for diag in (False,True):
        t=[(Q(0),Q(0)),(h,0),(-h,0),(0,h),(0,-h)]+([(h,h),(-h,-h)] if diag else [])
        W=[max(a,b) for a,b in t]
        for eps in (Q(0),Q(1,10000)):
            for eta in (Q(0),Q(1,100000)):
                L=[w-eps for w in W];U=[w+eps for w in W]
                lp,ix=response_polytope(t,L,U,[(0,1),(0,1)],eta)
                c=[Q(0)]*len(lp.box);c[2]=c[3]=Q(1)
                ans=lp.maximize(c);v=exact_vertex(lp,ans['proposed_point']);actual=sum(a*x for a,x in zip(c,v));upper=lp.validate(c,ans)
                assert actual<=upper and upper-actual<Q(1,10**10)
                # Construct an actual finite affine-response economy attaining
                # the proposed feature, and validate every oracle interval.
                planes=[(v[1],v[2:4])]+[(v[i],v[i+1:i+3]) for i in ix['support_planes']]
                for tt,l,u in zip(t,L,U):
                    ww=max(a+sum(x*z for x,z in zip(tt,zz)) for a,zz in planes)
                    assert l<=ww<=u
                w0=max(a for a,z in planes);assert w0==v[0] and v[1]>=w0-eta
                if eps==eta==0:assert actual==(1 if diag else 2)
                rows.append(dict(diagonal_queries=diag,error=encode(eps),response_tolerance=encode(eta),sharp_upper=encode(actual),LP=lp.json(),objective=[encode(x) for x in c],dual=ans,exact_primal=[encode(x) for x in v],constructed_menu=[dict(intercept=encode(a),features=[encode(x) for x in z]) for a,z in planes]))
    negatives={}
    def reject(name,f):
        try:f()
        except (ValueError,AssertionError,KeyError,IndexError) as e:negatives[name]=dict(rejected=True,reason=str(e))
        else:raise AssertionError('negative fixture was accepted: '+name)
    reject('negative_dual_multiplier',lambda:lp.dual_bound(c,[-1]*len(lp.b)))
    broken=copy.deepcopy(ans);broken['exact_upper']='0/1'
    reject('false_rational_dual_bound',lambda:lp.validate(c,broken))
    # Exercise the nonattainment branch, which the actual procurement optimum
    # need not happen to visit. The upper supremum is at zero; the lower action
    # is strictly positive and its slack is explicitly propagated.
    fm=types.SimpleNamespace(actions=np.array([[.8,0.,0.],[.8,0.,.2],[.8,0.,.8]]))
    q=np.array([1.,.8,.7]);rec=positive_witness(fm,q,0,.8,False)
    assert not rec['attained'] and rec['positivity_margin']>0
    gap=verify_positive(fm,q,rec,.8,False);assert 0<gap<1e-9
    bad=copy.deepcopy(rec);bad['action'][2]=0.;bad['positivity_margin']=0.
    reject('open_class_zero_boundary',lambda:verify_positive(fm,q,bad,.8,False))
    badgap=copy.deepcopy(rec);badgap['closure_gap']=.1
    reject('wrong_open_class_value_slack',lambda:verify_positive(fm,q,badgap,.8,False))
    return dict(schema='nbo-r13-exact-theory-witnesses-v1',sharp_oracle_examples=rows,open_boundary_example=rec,negative_tests=negatives,all_passed=True)

if __name__=='__main__':
    out=Path(__file__).parent/'extensions';out.mkdir(exist_ok=True);z=run()
    (out/'theory_tests.json').write_text(json.dumps(z,indent=2)+'\n');print('EXACT ORACLE TESTS',len(z['sharp_oracle_examples']),z['all_passed'])
