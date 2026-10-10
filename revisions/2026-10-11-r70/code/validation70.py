"""Verify saved validation actions without assuming bitwise BLAS identity."""
from fractions import Fraction as F
import numpy as np

def verify(v,proposed,models,r,kind,readout,tol):
    delta=F(1,2**32);evaluation_allowance=F(1,2**36)
    mismatch=np.flatnonzero(proposed!=v['action']);reports=[]
    for i in range(len(v['action'])):
        action=F(float(v['action'][i]));cap=F(float(v['cap'][i]));s=action/cap
        if not 0<=action<=cap or (action/delta).denominator!=1:raise AssertionError('Invalid saved validation action')
        chord=(1-s)*F(float(v['left_hi'][i]))+s*F(float(v['right_hi'][i]))-action*(cap-action)
        score=chord-F(float(v['lower'][i]))
        if F(float(v['score'][i]))<score:raise AssertionError('Saved score fails exact chord upper check')
        if i in mismatch:
            if kind not in ('hat-relu','bernstein4','label-relu'):raise AssertionError('Unexplained non-readout discrepancy')
            weights=models[str(r)]['weights'];features=readout.exact_phi(v['x'][i],kind)
            ideal=cap*sum((a*F(float(w)) for a,w in zip(features,weights)),F(0))
            ideal_rounded=(ideal/delta).__floor__()*delta
            # The published training allowance explicitly includes both a
            # 32-bit downward action quantum and a 2^-36 prediction allowance.
            if not -evaluation_allowance<=ideal-action<=delta+evaluation_allowance:
                raise AssertionError(('Prediction discrepancy exceeds the declared readout allowance',i,str(ideal-action)))
            if abs(F(float(proposed[i]))-action)>delta:raise AssertionError('More than one action quantum changed')
            reports.append(dict(row=int(i),saved_action=str(action),recomputed_action=str(F(float(proposed[i]))),exact_unrounded_action=str(ideal),exact_rounded_action=str(ideal_rounded),saved_score=str(F(float(v['score'][i]))),exact_chord_score=str(score),status='within_declared_allowance_and_exact_gate_verified'))
    return reports
