"""Analytic and adversarial checks; development cases are not holdout evidence."""
from fractions import Fraction as F
import copy,json
from diffuse import construct,enc,generate
from check_diffuse import verify

def main():
    passed=[]
    for T in [1,2,4,8]:
        raw=dict(name='analytic',T=T,m=3,beta='9/10',epsilon='1/20',gamma=['0','1','1'],g=[['1','0'] for _ in range(T)],k=[[['0','0'],['1/2','0'],['1/2','0']] for _ in range(T)],kernel='uniform-independent-reset',initial_law='uniform[0,1]',data_status='analytic')
        e=enc(construct(raw,4));v=verify(e,raw)
        exact=sum((F(9,10)**t/2 for t in range(T)),F(0))-F(1,40)
        assert F(e['lower'])<=exact<=F(e['upper']) and F(v['width'])<F(1,10**8)
        passed.append(f'constant-affine-T{T}-known-optimum-and-optimal-face')
    raw=generate(seed=9001);e=enc(construct(raw,16));verify(e,raw)
    def must_reject(label,change):
        a=copy.deepcopy(e);change(a)
        try:verify(a,raw)
        except (AssertionError,ValueError,IndexError):passed.append(label);return
        raise AssertionError('accepted corrupt '+label)
    must_reject('inflated-lower',lambda a:a.update(lower=str(F(a['upper'])+1)))
    must_reject('negative-price',lambda a:a['lambda_density'][0].__setitem__(0,'-1'))
    must_reject('policy-normalization',lambda a:a['policy'][0][0].__setitem__(0,'2'))
    must_reject('cumulative-regret-recursion',lambda a:a['moments'].__setitem__(0,'0'))
    must_reject('altered-model',lambda a:a['model'].__setitem__('epsilon','1'))
    must_reject('whole-cell-infeasibility',lambda a:a['policy'][0].__setitem__(0,['1','0','0']))
    print(json.dumps({'passed':len(passed),'tests':passed},indent=2))
if __name__=='__main__':main()
