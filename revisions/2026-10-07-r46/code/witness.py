"""R46: retain the minimizing cone's feasible action witness.

Scientific dependencies are the immutable R45 constructive and interval modules.
All certificates concern ideal exact state acquisition, with a separate selector
allowance available in the theorem. No historical record is modified.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse, bisect, hashlib, json, math, platform, resource, sys, time
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE=R.parent/'2026-10-07-r45'
sys.path.insert(0,str(BASE/'code'))
import constructive as old
METHODS=('cone-witness','cone-nearest','spline-nearest')
TARGETS=(F(1,4),F(1,8),F(1,16))


def compile_witness(k,y,L):
    """Exact scalar envelope with an attaining ORIGINAL label on each cell."""
    k=list(map(F,k));y=list(map(F,y));L=F(L)
    if L<0 or len(k)!=len(y) or len(k)<2 or k[0]!=0 or k[-1]!=1:
        raise ValueError('Invalid witness inputs')
    if any(a>=b for a,b in zip(k,k[1:])):raise ValueError('Unordered grid')
    left=[(y[0],0)]
    for i in range(1,len(k)):
        left.append(min((y[i],i),(left[-1][0]+L*(k[i]-k[i-1]),left[-1][1])))
    right=[None]*len(k);right[-1]=(y[-1],len(k)-1)
    for i in range(len(k)-2,-1,-1):
        right[i]=min((y[i],i),(right[i+1][0]+L*(k[i+1]-k[i]),right[i+1][1]))
    cuts=[k[0]];owners=[]
    for i in range(len(k)-1):
        a,b=k[i:i+2];lv,li=left[i];rv,ri=right[i+1]
        cell=[a,b]
        if L:
            cross=(a+b)/2+(rv-lv)/(2*L)
            if a<cross<b:cell=[a,cross,b]
        for u,v in zip(cell,cell[1:]):
            mid=(u+v)/2
            owner=min((lv+L*(mid-a),li),(rv+L*(b-mid),ri))[1]
            cuts.append(v);owners.append(owner)
    return {'kind':'cone-witness','cuts':list(map(str,cuts)),'owners':owners,
            'tie_rule':'right cell, with both endpoints included in certificates',
            'exact_acquisition':True}


def witness_index(actor,x):
    cuts=list(map(F,actor['cuts']));x=F(x)
    if not 0<=x<=1:raise ValueError('State outside domain')
    j=min(len(cuts)-2,max(0,bisect.bisect_right(cuts,x)-1))
    return actor['owners'][j]


def load_pwl(model):
    return old.PWL(list(map(F,model['knots'])),list(map(F,model['values'])))


def nearest_excess(model,L):
    """Exact maximum of y_i+L|x-x_i|-f(x) on all closed nearest cells."""
    definition=model['definition'];k=list(map(F,definition['grid']))
    y=list(map(F,definition['labels']));N=len(k)-1
    if k!=[F(i,N) for i in range(N+1)]:raise ValueError('Uniform grid required')
    f=load_pwl(model);L=F(L)
    boundaries=[(a+b)/2 for a,b in zip(k,k[1:])]
    points=sorted(set(k+f.k+boundaries));best=None
    for x in points:
        i=min(N,int(x*N+F(1,2)));indices=[i]
        if i>0 and x==(k[i-1]+k[i])/2:indices.append(i-1)
        fx=f.exact(x)
        for j in indices:
            value=y[j]+L*abs(x-k[j])-fx
            if best is None or value>best:best=value
    return best,len(points)


def enhance(payload,method):
    if method not in METHODS:raise ValueError('Unknown method')
    expected='piecewise-linear-spline' if method=='spline-nearest' else 'min-plus-ReLU'
    if payload['method']!=expected:raise ValueError('Wrong defining generator')
    rows=[];actors=[];checks=0
    for t,row in enumerate(payload['rows']):
        e=F(row['oracle_error']);L=F(row['Lx']);model=payload['models'][t]
        if method=='cone-witness':
            d=model['definition'];actor=compile_witness(d['grid'],d['labels'],L)
            excess=F(0);checks+=2*(len(d['grid'])-1)
        else:
            excess,n=nearest_excess(model,L);checks+=n
            actor={'kind':'nearest-node','N':payload['N'],'tie_rule':'half-up'}
        actor['node_actions']=payload['actors'][t]
        delta=e+excess;u=F(row['residual_upper'])
        rows.append({'date':t,'optimal_residual_upper':str(u),
                     'selected_policy_upper':str(delta),'label_witness_excess':str(excess),
                     'joint_component':str(u+delta)})
        actors.append(actor)
    joint=sum((old.BETA**t*F(r['joint_component']) for t,r in enumerate(rows)),F(0))
    joint+=old.BETA**payload['T']*F(payload['terminal_width'])
    original=F(payload['policy_bound_exact']);bound=min(joint,original)
    return {'method':method,'N':payload['N'],'T':payload['T'],'price':payload['price'],
            'policy_actors':actors,'joint_rows':rows,'joint_bound_exact':str(joint),
            'policy_bound_exact':str(bound),'policy_bound_upper':old.upper(bound),
            'old_separated_bound_exact':str(original),
            'certificate_selected':'joint' if joint<=original else 'separated',
            'definition':payload,'witness_compilation_or_enclosure_points':checks,
            'actor_query_scope':'ideal exact state and exact rational comparisons; not unchecked floating lookup'}


def service(method,T,p,rep,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    affinity=None
    if hasattr(os,'sched_getaffinity'):
        affinity=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity})
    z=old.np.arange(4096,dtype=float)/4096
    for _ in range(8):z=(z+1)*.5
    start=time.perf_counter();cpu=time.process_time();out.mkdir(parents=True)
    attempts=[];first={str(e):None for e in TARGETS};cum=0
    generator='piecewise-linear-spline' if method=='spline-nearest' else 'min-plus-ReLU'
    for N in old.LADDER:
        begin=time.perf_counter();base,counts=old.rung(N,T,p,generator)
        payload=enhance(base,method)
        counts['witness_or_enclosure_points']=payload['witness_compilation_or_enclosure_points']
        counts['witness_cell_indices']=sum(len(a.get('owners',[])) for a in payload['policy_actors'])
        counts['witness_rational_cuts']=sum(len(a.get('cuts',[])) for a in payload['policy_actors'])
        counts['witness_max_rational_bit_length']=max([0]+[max(abs(F(q).numerator).bit_length(),F(q).denominator.bit_length()) for a in payload['policy_actors'] for q in a.get('cuts',[])])
        counts['policy_query_binary_search_comparison_upper']=sum(math.ceil(math.log2(len(a.get('cuts',[]))+1))+1 if a['kind']=='cone-witness' else 0 for a in payload['policy_actors'])
        checkpoint=out/f'checkpoint-N{N}.json';digest=old.write_new(checkpoint,payload)
        elapsed=time.perf_counter()-start;cum+=counts['q_evaluations']
        att={'N':N,'bound_exact':payload['policy_bound_exact'],'bound_upper':payload['policy_bound_upper'],
             'joint_bound_exact':payload['joint_bound_exact'],'old_bound_exact':payload['old_separated_bound_exact'],
             'checkpoint_sha256':digest,'checkpoint_bytes':checkpoint.stat().st_size,
             'prefix_seconds':elapsed,'rung_seconds':time.perf_counter()-begin,
             'prefix_q_evaluations':cum,'counts':counts}
        attempts.append(att)
        for e in TARGETS:
            if first[str(e)] is None and F(att['bound_exact'])<=e:
                first[str(e)]={key:att[key] for key in ('N','bound_exact','bound_upper','prefix_seconds','prefix_q_evaluations')}
    record={'method':method,'horizon':T,'price':p,'repeat':rep,'attempts':attempts,'first_crossings':first,
            'cpu_affinity':affinity,'frequency_controlled':False,'platform':platform.platform(),
            'python':platform.python_version(),'numpy':old.np.__version__,
            'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'cpu_seconds':time.process_time()-cpu,'seconds_before_record':time.perf_counter()-start,
            'source_sha256':{str(q.relative_to(R.parent)):hashlib.sha256(q.read_bytes()).hexdigest() for q in (Path(__file__),BASE/'code/constructive.py',BASE/'code/interval.py')},
            'comparison':'no new independent policy-cost comparison executed',
            'timing':'fresh targets, compilation, actors, joint certificates, failed rungs and checkpoint fsync; startup/warm-up excluded and process clocks separate'}
    digest=old.write_new(out/'record.json',record)
    old.write_new(out/'clock.json',{'record_sha256':digest,'seconds_through_record_fsync':time.perf_counter()-start})
    print(json.dumps({'method':method,'T':T,'p':p,'repeat':rep,'first':first}),flush=True)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--method',choices=METHODS,required=True)
    a.add_argument('--horizon',type=int,choices=(2,4),required=True);a.add_argument('--price',type=int,choices=(1,4),required=True)
    a.add_argument('--repeat',type=int,choices=(0,1,2),required=True);a.add_argument('--out',required=True)
    p=a.parse_args();service(p.method,p.horizon,p.price,p.repeat,p.out)
