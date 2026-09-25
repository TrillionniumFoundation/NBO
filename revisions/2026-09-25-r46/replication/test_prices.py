"""Finite exact properties and adversarial price-certificate checks.

No optimizer or constructor imports; tests do not constitute a theorem proof.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import copy,gzip,json,random,time
from verify_prices import Model,verify_object,scalar_product,ROOT,BASE,R

def run():
    started=time.perf_counter();rng=random.Random(460025)
    tested=0;feasible=0;inequalities=0;nonuniform=0
    for model_index in range(12):
        n,m,T=2,2,2
        P=[]
        for i in range(n):
            P.append([])
            for a in range(m):
                q=Q(rng.randrange(5),4);P[-1].append([str(q),str(1-q)])
        initial=['1','0'] if model_index%3==0 else (['1/4','3/4'] if model_index%3==1 else ['1/2','1/2'])
        nonuniform+=initial!=['1/2','1/2']
        raw=dict(n=n,m=m,T=T,beta='3/4',epsilon='1/2',P=P,
                 r=[[str(Q(rng.randrange(-2,3),4)) for a in range(m)] for i in range(n)],
                 k=[[str(Q(rng.randrange(5),4)) for a in range(m)] for i in range(n)],
                 terminal=['0','1/4'],nu=initial)
        model=Model(raw)
        fields=[[[str(Q(rng.randrange(9),2)) for i in range(n)] for t in range(T)] for _ in range(5)]
        for coords in product([Q(0),Q(1,2),Q(1)],repeat=n*T):
            p=[[[str(coords[t*n+i]),str(1-coords[t*n+i])] for i in range(n)] for t in range(T)]
            upper,loss=model.policy(p,require_feasible=False);tested+=1
            if loss>model.epsilon:continue
            feasible+=1
            for prices in fields:
                lower,_,checks=model.support(prices,44)
                assert lower<=upper,(model_index,p,prices,lower,upper)
                inequalities+=1
    path=R/'proofs/tie0/restart.json.gz';obj=json.loads(gzip.decompress(path.read_bytes()))
    base=BASE/'models/tie0.json';protocol=BASE/'PROTOCOL.json'
    mutations={
      'negative_price':lambda x:x['prices'][0].__setitem__(0,'-1'),
      'price_changed_without_bellman_update':lambda x:x['prices'][0].__setitem__(0,str(Q(x['prices'][0][0])+1)),
      'transformed_lower_forgery':lambda x:x['transformed_lower'][0].__setitem__(0,str(Q(x['transformed_lower'][0][0])+1)),
      'lower_endpoint_forgery':lambda x:x.__setitem__('lower',str(Q(x['lower'])+1)),
      'upper_endpoint_forgery':lambda x:x.__setitem__('upper',str(Q(x['upper'])-1)),
      'negative_action_probability':lambda x:x['policy'][0][0].__setitem__(0,'-1'),
      'operating_infeasible_policy':lambda x:x.__setitem__('policy',[[['0','0','1'] for _ in range(4)] for _ in range(8)]),
      'model_hash':lambda x:x.__setitem__('model_sha256','0'*64),
      'protocol_hash':lambda x:x.__setitem__('protocol_sha256','0'*64),
      'target_changed':lambda x:x.__setitem__('target','1'),
      'discount_changed':lambda x:x['model'].__setitem__('beta','1/2'),
      'initial_law_changed':lambda x:x['model'].__setitem__('nu',['1','0','0','0']),
      'cost_objective_changed':lambda x:x['model']['k'][0].__setitem__(0,'0'),
      'operating_reward_changed':lambda x:x['model']['r'][0].__setitem__(0,'1'),
      'kernel_changed':lambda x:x['model']['P'][0][0].__setitem__(0,'1'),
      'price_state_omitted':lambda x:x['prices'][0].pop(),
    }
    rejected={}
    verify_object(obj,base,protocol)
    for name,mutate in mutations.items():
        changed=copy.deepcopy(obj);mutate(changed)
        try:verify_object(changed,base,protocol)
        except (ValueError,IndexError,KeyError,TypeError) as exc:rejected[name]=str(exc)
        else:raise AssertionError('accepted mutation: '+name)
    result=dict(passed=True,model_count=12,enumerated_policies=tested,feasible_policies=feasible,
                arbitrary_price_inequalities=inequalities,models_with_nonuniform_or_atomic_initial_law=nonuniform,
                mutations_rejected=len(rejected),mutation_reasons=rejected,seed=460025,
                seconds=time.perf_counter()-started,
                scope='finite exact properties and malformed-object rejection, not machine proof of the general theorem')
    (R/'results/price_property_tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':run()
