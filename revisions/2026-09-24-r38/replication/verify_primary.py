"""Independent SymPy Rational verifier; imports no constructor or PW arithmetic.
Checks primitive rows on their actual pullback partition, including isolated points.
This module deliberately duplicates the model contract, not optimization code.
"""
from __future__ import annotations
import bisect,copy,gzip,hashlib,json,platform,re,sys,time
from pathlib import Path
from sympy import Rational as Q
import sympy
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PAT=re.compile(r'^-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?$')
Z,O=Q(0),Q(1)
BETA=Q(19,20);PROBS=(Q(3,5),Q(2,5));COST=(Z,Q(3,20),Q(9,20))
TRANS=(((Q(3,4),Z),(Q(3,4),Q(1,20))),((Q(17,20),Q(1,10)),(Q(17,20),Q(7,50))),((Q(1,10),Q(4,5)),(Q(1,10),Q(17,20))))
MODEL={'beta':'19/20','probabilities':['3/5','2/5'],'costs':['0','3/20','9/20'],
 'transitions':[[['3/4','0'],['3/4','1/20']],[['17/20','1/10'],['17/20','7/50']],[['1/10','4/5'],['1/10','17/20']]],
 'terminal':'x/2','reward':'x-cost[action]','revision_cost':'(1+x)*1[action!=raw]','domain':['0','1']}
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
def sha(d):return hashlib.sha256(canon(d)).hexdigest()
def rat(s):
    assert isinstance(s,str) and PAT.fullmatch(s),('invalid rational',str(s)[:80])
    return Q(s)
def read(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def parse(d):
    assert set(d)=={'knots','affine','points'}
    xs=tuple(map(rat,d['knots']));ab=tuple(tuple(map(rat,row)) for row in d['affine']);ys=tuple(map(rat,d['points']))
    assert xs[0]==0 and xs[-1]==1 and len(xs)==len(ys)==len(ab)+1
    assert all(l<r for l,r in zip(xs,xs[1:])) and all(len(row)==2 for row in ab)
    return xs,ab,ys
def value(f,x):
    xs,ab,ys=f;i=bisect.bisect_left(xs,x)
    if i<len(xs) and xs[i]==x:return ys[i]
    a,b=ab[i-1];return a*x+b
def line(f,x,point=False):
    if point:return Z,value(f,x)
    i=bisect.bisect_right(f[0],x)-1;return f[1][i]
def plus(*args):return sum((f[0] for f in args),Z),sum((f[1] for f in args),Z)
def scale(f,c):return f[0]*c,f[1]*c
def subtract(f,g):return f[0]-g[0],f[1]-g[1]
def at(f,x):return f[0]*x+f[1]
def qrow(f,a,x,point,operating):
    total=(Z,Z)
    for p,(m,b) in zip(PROBS,TRANS[a]):
        if point:term=(Z,value(f,m*x+b))
        else:
            u,v=line(f,m*x+b);term=(u*m,u*b+v)
        total=plus(total,scale(term,BETA*p))
    reward=(Z,x-COST[a]) if point else (O,-COST[a])
    return plus(total,reward) if operating else total
def integral(f):return sum((a*(r*r-l*l)/2+b*(r-l) for (a,b),l,r in zip(f[1],f[0],f[0][1:])),Z)
def act(f,x):
    v=value(f,x);assert v in (0,1,2),('illegal action',v);return int(v)
def policy_shape(f):
    assert all(m==0 and b in (0,1,2) for m,b in f[1]) and all(y in (0,1,2) for y in f[2])
def verify(d,check_base=True):
    tic=time.perf_counter();assert d['schema']=='NBO-R38-primary-v1' and d['model']==MODEL
    T=d['T'];assert type(T) is int and T in (4,8,12)
    eps=rat(d['epsilon']);assert eps in (Q(1,100),Q(1,20))
    assert d['policy_class']=='deterministic_Markov' and d['constraint']=='all_state_all_restart'
    assert d['objective']=='uniform_initial_integrated_discounted_revision_cost'
    fields=('V','lower','U','L','safe_lower','J','C','raw','operating_policy','lower_policy','safe_lower_policy','policy','gamma')
    f={name:list(map(parse,d[name])) for name in fields}
    for name,fs in f.items():
        assert len(fs)==T+(name in ('V','lower','U','L','safe_lower','J','C')),(name,'length')
        if name in ('raw','operating_policy','lower_policy','safe_lower_policy','policy','gamma'):
            for ff in fs:policy_shape(ff)
    assert sha(d['policy'])==d['policy_sha256'] and sha(d['raw'])==d['raw_sha256'] and sha(d['lower'])==d['lower_sha256']
    if check_base:
        p=(REPO/d['base_file']).resolve();assert p.is_relative_to((ROOT.parent/'2026-09-24-r34/results/certificates').resolve())
        assert hashlib.sha256(p.read_bytes()).hexdigest()==d['base_file_sha256']
        base=read(p);assert base['raw']==d['raw'] and base['T']==T and base['epsilon']==d['epsilon'] and base['proposal']==d['proposal']
    defects=list(map(rat,d['defects']));assert len(defects)==T and min(defects)>=0
    b=[Z]*(T+1)
    for t in reversed(range(T)):b[t]=defects[t]+BETA*b[t+1]
    # Terminal conditions include all open pieces and isolated values.
    for name in ('V','U','L','J','lower','safe_lower','C'):
        ff=f[name][-1];slope=Q(1,2) if name in ('V','U','L','J') else Z
        assert all(a==slope and z==0 for a,z in ff[1]) and all(y==slope*x for x,y in zip(ff[0],ff[2])),('terminal',name)
    counts={'intervals':0,'isolated_points':0,'affine_comparisons':0};maxreg=Z;pointwise=True
    def le(h,l,r):
        counts['affine_comparisons']+=1
        assert at(h,l)<=0 and at(h,r)<=0,('inequality',str(l),str(r),str(at(h,l)),str(at(h,r)))
    def eq(h,l,r):
        counts['affine_comparisons']+=1
        assert at(h,l)==0 and at(h,r)==0,('equality',str(l),str(r),str(at(h,l)),str(at(h,r)))
    for t in reversed(range(T)):
        knots={Z,O}
        for name in fields:knots.update(f[name][t][0])
        for name in ('V','U','J','C','lower','safe_lower'):
            for row in TRANS:
                for m,c in row:
                    knots.update((u-c)/m for u in f[name][t+1][0] if 0<(u-c)/m<1)
        coarse=sorted(knots)
        for l,r in zip(coarse,coarse[1:]):
            x=(l+r)/2
            for left,nextname in (('V','V'),('L','U')):
                for a in range(3):
                    gap=plus(subtract(line(f[left][t],x),qrow(f[nextname][t+1],a,x,False,True)),(Z,-eps))
                    if gap[0]:
                        root=-gap[1]/gap[0]
                        if l<root<r:knots.add(root)
        knots=sorted(knots)
        cells=[(l,r,False) for l,r in zip(knots,knots[1:])]+[(x,x,True) for x in knots]
        for l,r,point in cells:
            x=(l+r)/2;counts['isolated_points' if point else 'intervals']+=1
            cur={name:line(f[name][t],x,point) for name in fields}
            ra=act(f['raw'][t],x)
            def kr(a):return (Z,Z) if a==ra else ((Z,1+x) if point else (O,O))
            qv=[qrow(f['V'][t+1],a,x,point,True) for a in range(3)]
            qu=[qrow(f['U'][t+1],a,x,point,True) for a in range(3)]
            for a in range(3):le(subtract(qv[a],cur['V']),l,r);le(subtract(qu[a],cur['U']),l,r)
            eq(subtract(cur['V'],qv[act(f['operating_policy'][t],x)]),l,r)
            le(plus(subtract(cur['U'],qu[act(f['gamma'][t],x)]),(Z,-defects[t])),l,r)
            eq(plus(subtract(cur['L'],cur['U']),(Z,b[t])),l,r)
            le(subtract(cur['L'],cur['V']),l,r);le(subtract(cur['V'],cur['U']),l,r)
            for name,left,qs,sel in (('lower','V',qv,'lower_policy'),('safe_lower','L',qu,'safe_lower_policy')):
                eligible=[a for a in range(3) if at(subtract(cur[left],qs[a]),x)<=eps]
                assert eligible
                z=[plus(kr(a),qrow(f[name][t+1],a,x,point,False)) for a in range(3)]
                a=act(f[sel][t],x);assert a in eligible
                for aa in eligible:le(subtract(cur[name],z[aa]),l,r)
                eq(subtract(cur[name],z[a]),l,r);le(scale(cur[name],-O),l,r)
            a=act(f['policy'][t],x)
            eq(subtract(cur['J'],qrow(f['J'][t+1],a,x,point,True)),l,r)
            eq(subtract(cur['C'],plus(kr(a),qrow(f['C'][t+1],a,x,point,False))),l,r)
            regret=subtract(cur['V'],cur['J']);le(plus(regret,(Z,-eps)),l,r)
            maxreg=max(maxreg,at(regret,l),at(regret,r))
            le(subtract(cur['safe_lower'],cur['lower']),l,r);le(subtract(cur['lower'],cur['C']),l,r)
            diff=subtract(cur['C'],cur['lower'])
            pointwise=pointwise and at(diff,l)==0 and at(diff,r)==0
    lower=integral(f['lower'][0]);cost=integral(f['C'][0]);safe=integral(f['safe_lower'][0])
    assert (lower,cost,safe)==tuple(rat(d[n]) for n in ('lower_integral','upper_integral','safe_lower_integral'))
    assert maxreg==rat(d['operating_regret'])
    assert type(d['exact_integrated']) is bool and d['exact_integrated']==(lower==cost)
    assert type(d['exact_pointwise']) is bool and d['exact_pointwise']==pointwise
    return {'passed':True,'seconds':time.perf_counter()-tic,**counts,'exact_integrated':bool(lower==cost),'exact_pointwise':bool(pointwise)}
def mutations(original):
    tests={
      'primitive_discount':lambda d:d['model'].__setitem__('beta','1'),
      'primitive_transition':lambda d:d['model']['transitions'][0][0].__setitem__(0,'1/2'),
      'primitive_shock_probability':lambda d:d['model']['probabilities'].__setitem__(0,'1/2'),
      'primitive_reward_cost':lambda d:d['model']['costs'].__setitem__(1,'1/10'),
      'policy_class':lambda d:d.__setitem__('policy_class','randomized_Markov'),
      'objective_scope':lambda d:d.__setitem__('objective','all_restart_cost_optimal'),
      'terminal_operating_point':lambda d:d['V'][-1]['points'].__setitem__(0,'1'),
      'terminal_cost_piece':lambda d:d['C'][-1]['affine'][0].__setitem__(1,'1'),
      'missing_date':lambda d:d['J'].pop(),
      'unordered_knots':lambda d:d['V'][0]['knots'].__setitem__(0,'1'),
      'malformed_rational':lambda d:d['J'][0]['points'].__setitem__(0,'nan'),
      'illegal_action_label':lambda d:d['policy'][0]['points'].__setitem__(0,'3'),
      'fractional_action':lambda d:d['lower_policy'][0]['points'].__setitem__(0,'1/2'),
      'isolated_cost_point':lambda d:d['C'][0]['points'].__setitem__(0,str(rat(d['C'][0]['points'][0])+1)),
      'open_cost_coefficient':lambda d:d['C'][0]['affine'][0].__setitem__(1,str(rat(d['C'][0]['affine'][0][1])+1)),
      'false_lower_integral':lambda d:d.__setitem__('lower_integral',str(rat(d['lower_integral'])+1)),
      'false_exactness':lambda d:d.__setitem__('exact_integrated',not d['exact_integrated']),
      'forged_deployment_hash':lambda d:d.__setitem__('policy_sha256','0'*64),
      'negative_witness_defect':lambda d:d['defects'].__setitem__(0,'-1'),
      'frozen_input_digest':lambda d:d.__setitem__('base_file_sha256','0'*64),
    }
    result=[]
    for name,change in tests.items():
        d=copy.deepcopy(original);change(d)
        try:verify(d)
        except (AssertionError,ValueError,KeyError,IndexError,TypeError) as e:result.append({'category':name,'rejected':True,'diagnostic':str(e)[:160]})
        else:raise RuntimeError('Mutation was accepted: '+name)
    return result

def run():
    tic=time.perf_counter();rows=[]
    for p in sorted((ROOT/'results/primary').glob('*.json.gz')):
        d=read(p);r=verify(d);r.update({'file':p.name,'canonical_sha256':sha(d)});rows.append(r)
        print(p.name,r,flush=True)
    assert len(rows)==42
    original=read(next((ROOT/'results/primary').glob('H4_neural31001*')))
    checks=mutations(original)
    out={'passed':True,'objects':len(rows),'records':rows,'mutation_categories':checks,'seconds':time.perf_counter()-tic,
       'dependencies':{'python':sys.version,'sympy':sympy.__version__},'implementation_imports':['bisect','copy','gzip','hashlib','json','platform','re','sys','time','pathlib','sympy.Rational'],
       'shared_components':'JSON schema and economic specification only; no constructor, composition, envelope, or Fraction/PW import. Frozen inputs checked against retained R34 file bytes.'}
    (ROOT/'results/independent_verification.json').write_text(json.dumps(out,indent=2,sort_keys=True))
    print('ALL VERIFIED',len(rows),'MUTATIONS REJECTED',len(checks),flush=True)
if __name__=='__main__':run()
