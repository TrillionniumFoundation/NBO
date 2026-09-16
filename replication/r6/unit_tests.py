#!/usr/bin/env python3
"""Independent small-model tests of the transition-transfer identities.
Exhaustive regime sequences and policy enumeration are separate from the
Bernstein and Bellman implementations used for the main numerical example.
"""
from common import *
from types import SimpleNamespace
from itertools import product
from math import comb
from transport import Mixture,bernstein_value,envelope_certificate,unit_tests as subdivision_tests
from kernel_certificate import corrected_chord

class MatrixKernel:
    def __init__(self,K,R):
        self.K=K;self.base=R;self.duration=np.zeros_like(R);self.effort=np.zeros_like(R)
    def continuation(self,v):return np.einsum('sak,k->sa',self.K,v)
    def selected(self,p,v):return np.einsum('sk,k->s',self.K[np.arange(len(p)),p],v)

def make(rng,N=4,S=3,A=2):
    es=[]
    for _ in range(2):
        K=rng.uniform(.01,1,(S,A,S));K=K/K.sum(-1,keepdims=True)*rng.uniform(.6,1,(S,A,1))
        R=rng.normal(size=(S,A))
        es.append(SimpleNamespace(steps=N,ns=S,states=np.column_stack([np.full(S,2.),np.linspace(1.,2.,S)]),
            menu=np.zeros((A,3)),common=MatrixKernel(K,R),extra=[]))
    mix=Mixture(*es);mix.terminal=rng.normal(size=S);return mix

def sequence_value(mix,policy,labels):
    """Direct payoff recursion conditional on the ENTIRE exogenous label path."""
    v=mix.terminal.copy();r=np.arange(mix.ns)
    for n,k in reversed(list(enumerate(labels))):
        z=mix.e[k].common;p=policy[n]
        v=z.base[r,p]+np.array([z.K[s,p[s]]@v for s in range(mix.ns)])
    return v

def run():
    rng=np.random.default_rng(16092026);replay=0.;conditional=0.;upper_violation=0.;switch_violation=0.;tests=0
    for trial in range(20):
        mix=make(rng);bank=[mix.solve(t,0.) for t in (0.,.5,1.)]
        lo=[mix.policy_coefficients(z['policy'],0.) for z in bank];count=mix.upper_coefficients(0.)
        chord,_=corrected_chord(mix,0.,1.,bank[0]['value'],bank[-1]['value'])
        for i,z in enumerate(bank):
            for j in range(mix.steps+1):
                paths=[labels for labels in product((0,1),repeat=mix.steps) if sum(labels)==j]
                direct=np.mean([sequence_value(mix,z['policy'],labels) for labels in paths],axis=0)
                conditional=max(conditional,float(abs(direct-lo[i][0][j]).max()))
        pols=np.stack([z['policy'] for z in bank])
        cert=envelope_certificate(chord,lo,depth=3)['bound']
        for t in np.linspace(0,1,33):
            true=mix.solve(t,0.)['value'];pv=np.stack([[bernstein_value(co,t) for co in p] for p in lo])
            for i,z in enumerate(bank):replay=max(replay,float(abs(pv[i]-mix.evaluate(z['policy'],t,0.)).max()))
            for up in (chord,count):upper_violation=max(upper_violation,float((true-np.stack([bernstein_value(co,t) for co in up])).max()))
            sel=pv[:,:-1].argmax(0);pol=np.take_along_axis(pols,sel[None],0)[0];sw=mix.evaluate(pol,t,0.)
            switch_violation=max(switch_violation,float((pv.max(0)-sw).max()))
            assert (true-sw).max()<=cert+2e-10;tests+=1
    enumeration=0.
    for trial in range(10):
        mix=make(rng,N=2,S=2,A=2)
        policies=[np.array(bits).reshape(2,2) for bits in product((0,1),repeat=4)]
        for t in np.linspace(0,1,11):
            vals=[]
            for p in policies:
                v=sum(t**sum(labels)*(1-t)**(2-sum(labels))*sequence_value(mix,p,labels) for labels in product((0,1),repeat=2))
                vals.append(v)
            enumeration=max(enumeration,float(abs(np.max(vals,axis=0)-mix.solve(t,0.)['value'][0]).max()))
    neg=[sum(t**sum(z)*(1-t)**(2-sum(z))*(z==(1,0)) for z in product((0,1),repeat=2)) for t in (0.,.5,1.)]
    assert neg==[0.,.25,0.] and max(replay,conditional,upper_violation,switch_violation,enumeration)<2e-10
    save('unit_tests.json',dict(random_full_state_parameter_checks=tests,exhaustive_policy_checks=110,
        coefficient_direct_replay_error=replay,conditional_label_enumeration_error=conditional,
        corrected_and_count_upper_max_violation=upper_violation,switching_max_violation=switch_violation,
        complete_policy_enumeration_error=enumeration,invalid_uncorrected_kernel_chord=neg,
        subdivision=subdivision_tests(),source_sha256=sha(__file__)))
if __name__=='__main__':run()
