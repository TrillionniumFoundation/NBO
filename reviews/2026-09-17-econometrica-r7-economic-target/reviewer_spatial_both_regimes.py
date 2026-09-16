#!/usr/bin/env python3
"""Fixed-calendar reviewer point solves, not refined-grid regional certificates.
Uses the author transition constructor but a separate blockwise Bellman driver
and direct selected-policy replay. 'common' retains both historical menus.
'prolonged_full' adds bilinearly prolonged stored frozen proposals; original
nodes are copied exactly. This extension is reviewer-defined, not author-defined.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, sys, time
from pathlib import Path
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import numpy as np
from scipy.sparse import csr_matrix

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--grids',default='33x49,33x97,33x145')
    ap.add_argument('--corner-only',action='store_true')
    args=ap.parse_args();root=args.root.resolve()
    sys.path[:0]=[str(root/'replication/r5'),str(root/'replication/r4')]
    import contracts as c
    old=c.old
    menu=np.unique(np.concatenate((old.action_mesh((9,9,13)),old.action_mesh((7,7,11)))),axis=0)
    raw=[np.load(root/f'replication/r4/output/safe_policy_{seed}.npz')['policies'].reshape(8,33,49,3) for seed in (101,202,303)]
    refs=json.loads((root/'replication/r7/output/decision.json').read_text())['checks']
    result={'scope':'finite-model point solves; not a regional or diffusion certificate',
        'original_manuscript_commit':'fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17',
        'menu_actions':len(menu),'zero_adjustment_actions':int((menu[:,1]==0).sum()),
        'horizon':1.,'dates':8,'cost':2.,
        'extension':'bilinear control prolongation with exact original-node copying; reviewer-defined',
        'rows':[],'grids':[],
        'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ('replication/r4/solver.py','replication/r5/contracts.py')}}
    def save():
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    queries=[(0.,.4),(0.,.45),(.25,.4),(.25,.45),(.125,.425)]
    if args.corner_only:queries=[(.25,.45)]
    for spec in args.grids.split(','):
        shape=tuple(map(int,spec.split('x')));start=time.perf_counter()
        states=old.grid(*shape)[0].reshape(-1,2);ns=len(states)
        center=int(np.linalg.norm(states-[2.,1.25],axis=1).argmin())
        assert np.max(np.abs(states[center]-[2.,1.25]))<1e-14
        extra=[];coord=(states-old.LO)/(old.HI-old.LO)*np.array([32,48])
        node=np.rint(coord).astype(int);exact=np.max(np.abs(coord-node),axis=1)<1e-12
        for n in range(8):
            arrays=[]
            for p in raw:
                a=np.stack([old.interpolate(p[n,:,:,j],states) for j in range(3)],axis=1)
                a[exact]=p[n,node[exact,0],node[exact,1]]
                assert np.all(a>=old.ALO-1e-14) and np.all(a<=old.AHI+1e-14)
                arrays.append(a)
            extra.append(np.stack(arrays,axis=1))
        models=[old.Model(correlation=-.25),old.Model(correlation=.25)]
        backend_error=0.;blocks=[]
        for a in np.array_split(menu,int(np.ceil(len(menu)/64))):
            endpoints=[]
            for model in models:
                kernel=c.Kernel(states,a,shape,1/8,model);na=len(a)
                matrix=csr_matrix((kernel.weight.ravel().copy(),kernel.index.ravel().astype(np.int32),
                    np.arange(0,ns*na*16+1,16,dtype=np.int32)),shape=(ns*na,ns))
                matrix.sum_duplicates();matrix.eliminate_zeros();test=np.sin(np.arange(ns))
                error=float(np.max(np.abs((matrix@test).reshape(ns,na)-kernel.continuation(test))))
                backend_error=max(backend_error,error);assert error<2e-12
                endpoints.append((matrix,kernel.base.copy(),kernel.duration.copy(),kernel.effort.copy()))
                del kernel
            blocks.append((a,endpoints))
        ek=[[c.Kernel(states,extra[n],shape,1/8,model) for model in models] for n in range(8)]
        grid_record={'shape':list(shape),'states':ns,'backend_error':backend_error,
            'build_seconds':time.perf_counter()-start,'copied_original_nodes':int(exact.sum())}
        result['grids'].append(grid_record);print('BUILT',spec,grid_record,flush=True)
        def candidate(values,lam,d,a,endpoints):
            out=np.zeros((ns,len(a)))
            for prob,(matrix,base,dur,eff) in zip((1-lam,lam),endpoints):
                out+=prob*(base+d*dur-2*eff+(matrix@values).reshape(ns,len(a)))
            return out
        def solve(lam,d,adjust,full):
            v=np.empty((9,ns));v[-1]=old.terminal(states);policy=np.empty((8,ns,3))
            signs=('positive','nonpositive');first_values={s:np.full(ns,-np.inf) for s in signs}
            first_actions={s:np.empty((ns,3)) for s in signs}
            for n in range(7,-1,-1):
                best=np.full(ns,-np.inf);chosen=np.empty((ns,3))
                def consume(q,a):
                    nonlocal best,chosen
                    aa=np.broadcast_to(a,(ns,)+a.shape) if a.ndim==2 else a
                    allowed=np.ones(q.shape,bool) if adjust else np.abs(aa[:,:,1])<=1e-14
                    q=np.where(allowed,q,-np.inf);ix=q.argmax(1);val=q[np.arange(ns),ix];use=val>best
                    chosen[use]=aa[np.arange(ns),ix][use];best[use]=val[use]
                    if n==0:
                        for s in signs:
                            valid=aa[:,:,2]>0 if s=='positive' else aa[:,:,2]<=0
                            qs=np.where(valid,q,-np.inf);j=qs.argmax(1);vv=qs[np.arange(ns),j]
                            changed=vv>first_values[s];first_actions[s][changed]=aa[np.arange(ns),j][changed]
                            first_values[s][changed]=vv[changed]
                for a,ends in blocks:consume(candidate(v[n+1],lam,d,a,ends),a)
                if full:
                    q=sum(prob*(k.base+d*k.duration-2*k.effort+k.continuation(v[n+1])) for prob,k in zip((1-lam,lam),ek[n]))
                    consume(q,extra[n])
                assert np.isfinite(best).all();v[n]=best;policy[n]=chosen
            out={}
            for s in signs:
                vv=v.copy();vv[0]=first_values[s];pp=policy.copy();pp[0]=first_actions[s];out[s]=(vv,pp)
            return out
        def replay(pp,lam,d):
            vv=np.empty((9,ns));vv[-1]=old.terminal(states)
            features=np.zeros((4,9,ns));features[3,-1]=old.terminal(states)
            for n in range(7,-1,-1):
                vv[n]=0.
                for prob,model in zip((1-lam,lam),models):
                    y,live,disc,flow,eff,_,alpha=old.transition(states,pp[n],1/8,model)
                    ann=-np.expm1(-model.rho*alpha/8)/model.rho
                    continuing=old.interpolate(vv[n+1].reshape(shape),y)
                    vv[n]+=prob*np.mean(flow+d*ann+disc*np.where(live,continuing,old.terminal(y)),axis=-1)
                    rewards=(flow+2*eff,ann,eff,disc*(~live)*old.terminal(y))
                    for j in range(4):
                        continuation=old.interpolate(features[j,n+1].reshape(shape),y)
                        features[j,n]+=prob*np.mean(rewards[j]+disc*live*continuation,axis=-1)
            return vv,features[:,0,center]
        for lam,d in queries:
            for full in (False,True):
                rec={'shape':list(shape),'lambda':lam,'d':d,'arm':'prolonged_full' if full else 'common','regimes':{}}
                for adjust in (False,True):
                    t0=time.perf_counter();solved=solve(lam,d,adjust,full);vals={};maxerr=0.;errors=[]
                    for sign,(v,pp) in solved.items():
                        check,feat=replay(pp,lam,d);error=float(np.max(np.abs(v-check)));maxerr=max(maxerr,error)
                        assert error<5e-11
                        value=float(v[0,center]);assert abs(value-(feat[0]+d*feat[1]-2*feat[2]+feat[3]))<5e-11
                        vals[sign]={'value':value,'first_action':pp[0,center].tolist(),'feature_utility_duration_effort_liquidation':feat.tolist()}
                        if full and shape==(33,49):
                            for ref in refs:
                                if ref['theta']==lam and ref['d']==d and ref['adjustment']==adjust and ref['sign']==sign:errors.append(abs(value-ref['value']))
                    delta=vals['positive']['value']-vals['nonpositive']['value']
                    reg={'classes':vals,'delta':delta,'replay_max_error':maxerr,
                        'author_original_value_max_error':max(errors) if errors else None,'solve_and_replay_seconds':time.perf_counter()-t0}
                    if errors:assert max(errors)<5e-11
                    rec['regimes']['adjusted' if adjust else 'fixed']=reg
                    print('SOLVE',spec,lam,d,rec['arm'],adjust,delta,'replay',maxerr,flush=True)
                rec['relative_option']=rec['regimes']['adjusted']['delta']-rec['regimes']['fixed']['delta']
                result['rows'].append(rec);save()
        grid_record['total_seconds']=time.perf_counter()-start;del blocks,ek,extra;gc.collect();save()
    print('COMPLETE',args.output,flush=True)
if __name__=='__main__':main()
