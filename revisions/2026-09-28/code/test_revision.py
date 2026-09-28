#!/usr/bin/env python3
"""Regression tests for the revised graph, certificates, and recorded evidence."""
from __future__ import annotations
import json, unittest
from pathlib import Path
import numpy as np
import torch
from torch import nn
from nbo_core import HardTerminalValue,critic_loss,actor_loss,unilateral_actor_loss,ImplicitBellman

ROOT=Path(__file__).resolve().parents[3]
torch.set_default_dtype(torch.float64)

class RevisionTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(7)
        self.value=nn.Sequential(nn.Linear(2,8),nn.Tanh(),nn.Linear(8,1))
        self.actor=nn.Sequential(nn.Linear(2,5),nn.Tanh(),nn.Linear(5,1))
        self.tx=torch.randn(12,2)
        self.H=lambda tx,a,v,p,P:a*p+.02*P[:,0,0:1]-.1*v-a.square()

    def test_critic_does_not_update_actor(self):
        critic_loss(self.value,self.actor,self.tx,self.H).backward()
        self.assertTrue(all(p.grad is None for p in self.actor.parameters()))
        self.assertTrue(any(p.grad is not None for p in self.value.parameters()))

    def test_actor_detaches_all_critic_channels(self):
        actor_loss(self.value,self.actor,self.tx,self.H).backward()
        self.assertTrue(all(p.grad is None for p in self.value.parameters()))
        self.assertTrue(any(p.grad is not None for p in self.actor.parameters()))

    def test_terminal_exact(self):
        hard=HardTerminalValue(self.value,lambda x:x.square(),1.)
        tx=self.tx.clone();tx[:,0]=1
        torch.testing.assert_close(hard(tx),tx[:,1:].square(),rtol=0,atol=0)

    def test_unilateral_graph(self):
        other=nn.Sequential(nn.Linear(2,5),nn.Tanh(),nn.Linear(5,1))
        H=lambda i,tx,actions,v,p,P:actions[i]*(1-actions[0]-actions[1])+p*actions[i]-.1*v
        unilateral_actor_loss(0,[self.value,self.value],[self.actor,other],self.tx,H).backward()
        self.assertTrue(all(p.grad is None for p in other.parameters()))
        self.assertTrue(all(p.grad is None for p in self.value.parameters()))
        self.assertTrue(any(p.grad is not None for p in self.actor.parameters()))

    def test_recursive_certificate(self):
        rng=np.random.default_rng(91);P=rng.uniform(size=(4,3,4));P/=P.sum(axis=2,keepdims=True)
        rewards=rng.normal(size=(4,3))
        op=ImplicitBellman(P,lambda s,a,v:rewards[s,a]-.5*v-.1*np.tanh(v),.2,.5,(-100.,100.))
        vstar=np.zeros(4);vp=np.zeros(4);policy=np.array([0,1,2,0])
        for _ in range(450):
            vstar=op.action_values(vstar).max(axis=1)
            vp=op.action_values(vp)[np.arange(4),policy]
        candidate=rng.normal(size=4);c=op.certificate(candidate,policy)
        self.assertLessEqual(np.max(abs(candidate-vstar)),c['value_error_bound']+1e-10)
        self.assertLessEqual(np.max(vstar-vp),c['policy_regret_bound']+1e-10)
        v,w=rng.normal(size=(2,4))
        self.assertLessEqual(np.max(abs(op.action_values(v)-op.action_values(w))),op.q*np.max(abs(v-w))+1e-10)

    def test_recorded_lq_identity(self):
        files=list((ROOT/'revisions/2026-09-28/results').glob('lq_d*_seed*.npz'))
        self.assertEqual(len(files),15)
        for path in files:
            a=np.load(path);P,K,A,Q=a['P'],a['K'],a['A'],a['Q']
            residual=.1*P-Q-K.T@K-P@(A-K)-(A-K).T@P
            self.assertLess(np.linalg.norm(residual,2),1e-10)
            self.assertLess(np.linalg.norm(P-a['reference'],2),1e-10)
            self.assertGreater(np.linalg.norm(A@Q-Q@A,2),1e-5)

    def test_ndu_boundary_and_cost_order(self):
        base=ROOT/'revisions/2026-09-28/results'
        for shape in ('17x25','25x37'):
            lo=np.load(base/f'ndu_grid_{shape}_k1.npz');hi=np.load(base/f'ndu_grid_{shape}_k5.npz')
            self.assertTrue(np.all(hi['values']<=lo['values']+1e-12))
            U,Y=np.meshgrid(lo['u'],lo['logwealth'],indexing='ij');g=np.exp((1-U)*Y)/(1-U)
            np.testing.assert_allclose(lo['values'][-1],g,rtol=0,atol=0)
            np.testing.assert_allclose(lo['values'][:,:,0],np.broadcast_to(g[:,0],lo['values'][:,:,0].shape),rtol=0,atol=0)
            self.assertTrue(np.isfinite(lo['values']).all())

    def test_all_recorded_attempts_accounted_for(self):
        result=json.loads((ROOT/'revisions/2026-09-28/results/experiments.json').read_text())
        self.assertEqual(len(result['attempts']),29)
        self.assertTrue(all(a['execution_status']=='completed' and a['accepted'] for a in result['attempts']))

if __name__=='__main__':unittest.main(verbosity=2)
