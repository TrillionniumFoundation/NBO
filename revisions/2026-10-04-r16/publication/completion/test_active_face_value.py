"""Exact finite-law checks of the stable-face decision-value proposition.

Manufactured algebraic tests only: no registered seeds, economic observations,
training outcomes, or wall-clock comparisons are regenerated or relabeled.
"""
import itertools
import unittest
import numpy as np


def constrained_action(H, b, h, q, lower, upper):
    """Solve a small strictly concave box quadratic by exhaustive KKT faces."""
    p = len(q)
    best = None
    for status in itertools.product((-1, 0, 1), repeat=p):
        free = np.array([i for i, s in enumerate(status) if s == 0], dtype=int)
        fixed = np.array([i for i, s in enumerate(status) if s != 0], dtype=int)
        a = np.zeros(p)
        for i in fixed:
            a[i] = lower[i] if status[i] == -1 else upper[i]
        if len(free):
            rhs = (b-h*q)[free] - H[np.ix_(free, fixed)] @ a[fixed]
            a[free] = np.linalg.solve(H[np.ix_(free, free)], rhs)
        if np.any(a < lower-1e-12) or np.any(a > upper+1e-12):
            continue
        grad = b-H@a-h*q
        if any((s == -1 and grad[i] > 1e-10) or
               (s == 1 and grad[i] < -1e-10) for i, s in enumerate(status)):
            continue
        value = (b-h*q) @ a - .5*a@H@a
        if best is None or value > best[0]:
            best = (value, a, status)
    if best is None:
        raise ValueError('No feasible KKT point')
    return best[1]


def exact_comparison(Hs, bs, hs, weights, q, noise, D, fixed_faces):
    p = len(q)
    Rs = []
    for H, fixed in zip(Hs, fixed_faces):
        free = [i for i in range(p) if i not in fixed]
        L = np.eye(p)[:, free]
        R = L @ np.linalg.inv(L.T@H@L) @ L.T if free else np.zeros_like(H)
        Rs.append(R)
    W = sum(w*h*h*R for w,h,R in zip(weights,hs,Rs))
    eig,U = np.linalg.eigh(W)
    if np.min(eig) <= 0:
        raise ValueError('Collective tangent space does not span the decision space')
    root = (U*np.sqrt(eig)) @ U.T
    inverse = (U*(1/np.sqrt(eig))) @ U.T
    A = root@D
    P = A@np.linalg.pinv(A)
    noise = np.asarray(noise)
    if not np.allclose(noise.mean(axis=0), 0, atol=1e-14):
        raise ValueError('Uncentered original observation law')
    Sigma = noise.T@noise/len(noise)
    y = root@q
    omega = root@Sigma@root
    prediction = .5*(np.trace((np.eye(p)-P)@omega) - np.linalg.norm((np.eye(p)-P)@y)**2)
    gains=[]
    for eps in noise:
        raw=q+eps
        critic=inverse@P@root@raw
        gain=0.
        for H,b,h,w,fixed in zip(Hs,bs,hs,weights,fixed_faces):
            values=[]
            for v in (q,raw,critic):
                a=constrained_action(H,b,h,v,-np.ones(p),np.ones(p))
                for i in range(p):
                    if i in fixed:
                        if not np.isclose(a[i],fixed[i],atol=1e-10):
                            raise ValueError('Stable-face condition fails')
                    elif abs(a[i]) >= 1-1e-10:
                        raise ValueError('Relative-interior condition fails')
                values.append((b-h*q)@a-.5*a@H@a)
            gain+=w*(values[2]-values[1])
        gains.append(gain)
    return float(np.mean(gains)),float(prediction)


class StableFaceDecisionValue(unittest.TestCase):
    def setup_case(self, coupling=0., weights=(1.,1.), D=None, noise_scale=.2):
        H=np.array([[1.,coupling],[coupling,2.]])
        return dict(Hs=[H,H],bs=[np.array([3.,.4]),np.array([.4,4.])],
                    hs=[.2,.2],weights=weights,q=np.ones(2),
                    noise=noise_scale*np.array(list(itertools.product((-1.,1.),repeat=2))),
                    D=np.ones((2,1)) if D is None else D,
                    fixed_faces=[{0:1.},{1:1.}])
    def check_identity(self, **kwargs):
        actual,predicted=exact_comparison(**kwargs)
        self.assertAlmostEqual(actual,predicted,places=12)
        return actual
    def test_complementary_binding_constraints_strict_gain(self):
        self.assertGreater(self.check_identity(**self.setup_case()),0)
    def test_off_diagonal_curvature(self):
        self.assertGreater(self.check_identity(**self.setup_case(coupling=.25)),0)
    def test_unequal_economic_weights(self):
        self.assertGreater(self.check_identity(**self.setup_case(weights=(.3,2.7))),0)
    def test_misspecification_is_charged_not_hidden(self):
        self.assertLess(self.check_identity(**self.setup_case(D=np.array([[1.],[0.]]))),0)
    def test_zero_noise_correct_specification(self):
        self.assertAlmostEqual(self.check_identity(**self.setup_case(noise_scale=0.)),0,places=12)
    def test_full_dictionary_identical_estimators(self):
        self.assertAlmostEqual(self.check_identity(**self.setup_case(D=np.eye(2))),0,places=12)
    def test_interior_is_a_special_case(self):
        case=self.setup_case(coupling=.1)
        case['bs']=[np.array([.4,.5]),np.array([.5,.4])]
        case['fixed_faces']=[{},{}]
        self.assertGreater(self.check_identity(**case),0)
    def test_face_switching_is_rejected(self):
        case=self.setup_case(noise_scale=100.)
        with self.assertRaisesRegex(ValueError,'face|interior'):
            exact_comparison(**case)
    def test_singular_tangent_metric_is_rejected(self):
        case=self.setup_case()
        case['fixed_faces']=[{0:1.},{0:1.}]
        with self.assertRaisesRegex(ValueError,'span'):
            exact_comparison(**case)
    def test_postselection_cannot_silently_recenter_noise(self):
        case=self.setup_case();case['noise']=case['noise'][:2]
        with self.assertRaisesRegex(ValueError,'Uncentered'):
            exact_comparison(**case)

if __name__=='__main__':
    unittest.main()
