"""Verify saved validation actions without assuming bitwise BLAS identity."""
from fractions import Fraction as F
import numpy as np

def verify(v,proposed,models,r,kind,readout,tol):
    delta=F(1,2**32);evaluation_allowance=F(1,2**36)
    mismatch=set(map(int,np.flatnonzero(proposed!=v['action'])));reports=[]
    for index in range(len(v['action'])):
        action=F(float(v['action'][index]));cap=F(float(v['cap'][index]));s=action/cap
        if not 0<=action<=cap or (action/delta).denominator!=1:raise AssertionError('Invalid saved validation action')
        chord=(1-s)*F(float(v['left_hi'][index]))+s*F(float(v['right_hi'][index]))-action*(cap-action)
        score=chord-F(float(v['lower'][index]))
        if F(float(v['score'][index]))<score:raise AssertionError('Saved score fails exact chord upper check')
        fixed=kind in ('hat-relu','bernstein4','label-relu')
        if fixed:
            weights=models[str(r)]['weights'];features=readout.exact_phi(v['x'][index],kind)
            ideal=cap*sum((a*F(float(w)) for a,w in zip(features,weights)),F(0))
            ideal_rounded=(ideal/delta).__floor__()*delta
            if not -evaluation_allowance<=ideal-action<=delta+evaluation_allowance:
                raise AssertionError(('Saved readout exceeds its declared allowance',index,str(ideal-action)))
        if index in mismatch:
            if not fixed:raise AssertionError('Unexplained non-readout discrepancy')
            if abs(F(float(proposed[index]))-action)>delta:raise AssertionError('More than one action quantum changed')
            reports.append(dict(row=index,saved_action=str(action),recomputed_action=str(F(float(proposed[index]))),exact_unrounded_action=str(ideal),exact_rounded_action=str(ideal_rounded),saved_score=str(F(float(v['score'][index]))),exact_chord_score=str(score),status='within_declared_allowance_and_exact_gate_verified'))
    return reports
