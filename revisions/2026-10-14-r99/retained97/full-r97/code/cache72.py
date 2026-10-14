"""Paid root-query witness cache, with exact transport and bounded storage.

A miss invokes the unchanged inherited recursive verifier. No descendant
cache, fitted endpoint, uncharged training, or statistical claim is hidden
inside this adapter. Geometric retrieval is a proposal; rational inequalities
and a feasible repaired witness alone authorize reuse.
"""
from pathlib import Path
from fractions import Fraction as F
import json,math,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT.parent/'2026-10-10-r67/code'),str(ROOT.parent/'2026-10-11-r69/code')]
import kernel66 as scalar
import vector_base69 as vector
from certificates72 import Witness,transport


def down(x):
    y=float(x)
    return float(np.nextafter(y,-np.inf)) if F(y)>x else y


def up(x):
    y=float(x)
    return float(np.nextafter(y,np.inf)) if F(y)<x else y


class Cache:
    def __init__(self,controls=1,mode='geometric',capacity=128):
        if controls not in (1,2) or mode not in ('none','exact','geometric') or capacity<1:raise ValueError('cache configuration')
        self.controls=controls;self.mode=mode;self.capacity=capacity
        self.oracle=scalar.Oracle('adaptive') if controls==1 else vector.Oracle(batch=512)
        self.records=[];self.trace=[];self.epoch='original-v1'
        self.counts=dict(requests=0,hits=0,exact_hits=0,geometric_hits=0,misses=0,checks=0,
                         invalidations=0,rejected_stale_records=0,evictions=0,max_records=0,
                         lookup_seconds=0.,fill_seconds=0.,invalidations_seconds=0.)

    def invalidate(self,new_epoch):
        begin=time.perf_counter()
        if new_epoch!=self.epoch:
            self.counts['invalidations']+=1;self.counts['rejected_stale_records']+=len(self.records)
            self.records=[];self.epoch=new_epoch
        self.counts['invalidations_seconds']+=time.perf_counter()-begin

    def solve(self,row,remaining,tolerance):
        x=np.asarray(row,dtype=float);tol=F(tolerance)
        if x.ndim!=1 or not np.isfinite(x).all():raise ValueError('query state')
        state=tuple(F(float(z)) for z in x);self.counts['requests']+=1
        begin=time.perf_counter();chosen=None;source=None
        candidates=[]
        if self.mode!='none':
            candidates=[z for z in self.records if z.remaining==remaining and len(z.state)==len(state)]
            if self.mode=='exact':candidates=[z for z in candidates if z.state==state]
            # Untrusted ordering only. Every possible hit passes exact transport.
            candidates.sort(key=lambda z:float(z.upper-z.lower)+sum(abs(float(a)-float(b)) for a,b in zip(z.state,state)))
            for record in candidates:
                self.counts['checks']+=1;answer=transport(record,state,tol,self.epoch)
                if answer is not None:
                    lo,hi=down(answer['lower']),up(answer['upper'])
                    if F(hi)-F(lo)<=tol:chosen=answer;source=record;break
        self.counts['lookup_seconds']+=time.perf_counter()-begin
        if chosen is not None:
            self.counts['hits']+=1
            self.counts['exact_hits' if source.state==state else 'geometric_hits']+=1
            action=[float(z) for z in chosen['action']]
            record=dict(kind='hit',remaining=remaining,context=self.epoch,state=list(map(str,state)),tolerance=str(tol),
                        source_state=list(map(str,source.state)),source_action=list(map(str,source.action)),
                        source_lower=str(source.lower),source_upper=str(source.upper),
                        action=list(map(str,chosen['action'])),lower=lo,upper=hi,
                        exact_lower=str(chosen['lower']),exact_upper=str(chosen['upper']),
                        distance=str(chosen['state_distance']),repair=str(chosen['action_displacement']))
        else:
            self.counts['misses']+=1;begin=time.perf_counter()
            result=self.oracle.solve(x[None,:],remaining,float(tol))
            self.counts['fill_seconds']+=time.perf_counter()-begin
            lo=float(result['lower'][0]);hi=float(result['upper'][0]);action=np.atleast_1d(result['action'][0]).tolist()
            if F(hi)-F(lo)>tol:raise ArithmeticError('fill width')
            source=Witness(state,tuple(F(float(z)) for z in action),F(lo),F(hi),remaining,self.epoch);source.validate()
            if self.mode!='none':
                if len(self.records)==self.capacity:self.records.pop(0);self.counts['evictions']+=1
                self.records.append(source);self.counts['max_records']=max(self.counts['max_records'],len(self.records))
            record=dict(kind='fill',remaining=remaining,context=self.epoch,state=list(map(str,state)),tolerance=str(tol),
                        action=list(map(lambda z:str(F(float(z))),action)),lower=lo,upper=hi)
        self.trace.append(record)
        return dict(lower=lo,upper=hi,action=action,gap=hi-lo)

    def payload(self):
        return [dict(state=list(map(str,z.state)),action=list(map(str,z.action)),lower=str(z.lower),upper=str(z.upper),remaining=z.remaining,context=z.context) for z in self.records]

    def load(self,payload,context):
        begin=time.perf_counter();out=[]
        for p in payload:
            z=Witness(tuple(map(F,p['state'])),tuple(map(F,p['action'])),F(p['lower']),F(p['upper']),p['remaining'],p['context']);z.validate()
            if z.context!=context:raise ValueError('stale cache context')
            out.append(z)
        if len(out)>self.capacity:raise ValueError('cache capacity')
        self.records=out;self.epoch=context
        self.counts['lookup_seconds']+=time.perf_counter()-begin
