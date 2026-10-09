"""Simultaneous direct costs for first-crossing and finite-bit policies."""
from __future__ import annotations
import argparse,itertools,math,time,sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE.parent/'2026-10-08-r48/code'))
from common import *
from tensor import Model
import direct48 as inherited
inherited.FAMILY=300;inherited.LOG=13
PATHS=262144;BIN_BITS=40;LAWS=('uniform','1/8','1/2','7/8')

class Policy(inherited.Policy):
    def __init__(self,path):
        self.path=Path(path);self.raw=read(path);self.T=self.raw['T'];self.p=self.raw['price'];self.N=self.raw['N']
        self.models=[Model.load(m) for m in self.raw['models'][:-1]];self.actors=self.raw['actors']
        self.queries=0;self.ambiguities=0;self.measurement_ambiguities=0

def fee_account(lo,hi):
    lo,hi=F(lo),F(hi)
    return {'witness_to_fvi_gain':[str(lo),str(hi)],'fvi_to_witness_gain':[str(-hi),str(-lo)],'absolute_gain_interval':[str(0 if lo<=0<=hi else min(abs(lo),abs(hi))),str(max(abs(lo),abs(hi)))],'fee_certifying_both_not_profitable':str(max(F(0),hi,-lo)),'fee_removing_certified_profitability':str(max(F(0),lo,-hi))}

def group(spec,out,npaths=PATHS):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    start=time.perf_counter();cpu=time.process_time();paths=[HERE.parent/q for q in spec['paths']]
    for path,digest in zip(paths,spec['hashes']):assert H(path)==digest,str(path)
    policies=[Policy(p) for p in paths];T,p=policies[0].T,policies[0].p
    assert all(q.T==T and q.p==p for q in policies)
    identity=paths[0]==paths[1] and spec['bits'][0]==spec['bits'][1]
    if identity:
        record={'key':spec['key'],'spec':spec,'interval_exact':['0','0'],'interval':[0.,0.],'paths':0,'identity':True,'family_size':300,'family_error':'1/100','log_upper':13,'seconds_before_record':time.perf_counter()-start}
    else:
        a,b=inherited.support(T,p);A=c.enclosure(a)[0];B=c.enclosure(b)[1]
        seed=int.from_bytes(hashlib.sha256(('NBO-R49-DIRECT-v1:'+spec['key']).encode()).digest()[:8],'big')
        rng=np.random.Generator(np.random.PCG64(seed));stream=hashlib.sha256();left=np.empty(npaths);right=np.empty(npaths)
        first_actions=[]
        if spec['law']!='uniform':
            xx=I.point(np.full((1,2),float(F(spec['law']))))
            for policy,bits in zip(policies,spec['bits']):
                action=policy.action(0,xx,bits);first_actions.append([float(action.lo[0]),float(action.hi[0])])
        for begin in range(0,npaths,4096):
            n=min(4096,npaths-begin);bins=rng.integers(0,2**BIN_BITS,size=(T+2,n),dtype=np.uint64);stream.update(bins.tobytes());v=bins.astype(float)
            if spec['law']=='uniform':x=I(v[:2].T*2.**-BIN_BITS,(v[:2].T+1)*2.**-BIN_BITS)
            else:x=I.point(np.full((n,2),float(F(spec['law']))))
            z=[I(-1/32+v[t+2]*2.**(-BIN_BITS-4),-1/32+(v[t+2]+1)*2.**(-BIN_BITS-4)) for t in range(T)]
            score=[q.path_cost(x,z,bb) for q,bb in zip(policies,spec['bits'])];diff=score[0]-score[1]
            left[begin:begin+n]=np.maximum(A,diff.lo);right[begin:begin+n]=np.minimum(B,diff.hi)
            if np.any(left[begin:begin+n]>right[begin:begin+n]):raise AssertionError('Empty support')
        lstat=inherited.moments(left,A,B);rstat=inherited.moments(right,A,B);lo,hi=inherited.confidence(lstat,rstat,A,B)
        record={'key':spec['key'],'spec':spec,'identity':False,'paths':npaths,'bin_bits':BIN_BITS,'seed':seed,'stream_sha256':stream.hexdigest(),'family_size':300,'family_error':'1/100','log_upper':13,'support_exact':[str(a),str(b)],'lower_endpoint_moments':lstat,'upper_endpoint_moments':rstat,'interval_exact':[str(lo),str(hi)],'interval':[c.enclosure(lo)[0],c.enclosure(hi)[1]],'sign':'left-lower' if hi<0 else ('left-higher' if lo>0 else 'unresolved'),'mean_path_enclosure_width':float(np.mean(right-left)),'maximum_path_enclosure_width':float(np.max(right-left)),'actor_queries':[q.queries for q in policies],'ambiguous_actors':[q.ambiguities for q in policies],'ambiguous_measurements':[q.measurement_ambiguities for q in policies],'initial_actions':first_actions,'seconds_before_record':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'development_only':npaths!=PATHS}
    record['clock_scope']='joint policy loading, exact compilation, common interval paths, repaired actions, moments; fsync in clock sidecar'
    record['estimand']='expected actual discounted cost of left implementation minus right implementation; charges are added separately'
    if spec['kind']=='pair':record['replacement']=fee_account(*record['interval_exact'])
    digest=save(out,record);save(out.with_suffix('.clock.json'),{'record_sha256':digest,'seconds_through_record_fsync':time.perf_counter()-start})
    print(json.dumps({'key':spec['key'],'interval':record['interval'],'seconds':time.perf_counter()-start}),flush=True)
    return record

def catalogue():
    specs=[];missing=[]
    def add(paths,bits,law,key,kind,**meta):
        specs.append({'paths':[str(p.relative_to(HERE.parent)) for p in paths],'hashes':[H(p) for p in paths],'bits':bits,'law':law,'key':key,'kind':kind,**meta})
    def selected(T,p,method,target):
        folder=HERE/'results/services'/f'{method}-d2-T{T}-p{p}-r0';j=read(folder/'record.json');a=j['first_crossings'][str(target)]
        if a is None:return None
        path=folder/a['checkpoint'];assert H(path)==a['checkpoint_sha256'];return path
    for T,p,target in itertools.product((2,3),(1,4),(4,2,1)):
        paths=[selected(T,p,m,target) for m in ('compiled-witness','tensor-fvi')]
        if any(q is None for q in paths):
            missing.append({'T':T,'p':p,'target':target,'kind':'pair','reason':'at least one service misses target'});continue
        for law,bits in itertools.product(LAWS,(None,8)):
            key=f'new-T{T}-p{p}-eps{target}-law{law.replace("/","_")}-b{bits}'
            add(paths,[bits,bits],law,key,'pair',T=T,p=p,target=target,frontier='R49')
    paths=[HERE.parent/'2026-10-08-r48/results/services'/f'{m}-d2-T3-p4-r0'/f'checkpoint-N{N}.json' for m,N in [('compiled-witness',32),('tensor-fvi',64)]]
    for law,bits in itertools.product(LAWS,(None,8)):
        add(paths,[bits,bits],law,f'R48-favorable-law{law.replace("/","_")}-b{bits}','pair',T=3,p=4,target=2,frontier='R48')
    for T,p,method in itertools.product((2,3),(1,4),('compiled-witness','tensor-fvi')):
        path=selected(T,p,method,1)
        if path is None:
            missing.append({'T':T,'p':p,'method':method,'kind':'sensor','reason':'service misses target one'});continue
        for bits in range(4,17):
            add([path,path],[bits,16],'uniform',f'sensor-{method}-T{T}-p{p}-b{bits}','sensor',T=T,p=p,method=method,bit_prices=['1/16384','1/4096','1/1024'])
    assert sum(not(q['paths'][0]==q['paths'][1] and q['bits'][0]==q['bits'][1]) for q in specs)<=300
    save(HERE/'audit/DIRECT_CATALOGUE.json',{'specs':specs,'missing':missing,'selection_rule':'first crossing from construction only; frozen before any direct simulation','maximum_family_size':300})
    return specs

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--index',type=int);a.add_argument('--catalogue',action='store_true');v=a.parse_args()
    if v.catalogue:catalogue()
    else:
        spec=read(HERE/'audit/DIRECT_CATALOGUE.json')['specs'][v.index];group(spec,HERE/'results/direct'/(spec['key']+'.json'))
