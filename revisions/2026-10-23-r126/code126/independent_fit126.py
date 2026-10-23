"""Independent finite-design refitting audit of the immutable R121 acquisitions.

No production feature, fit, actor, or economic implementation is imported.
VALUE: independently assembled design + SciPy BVLS (historical fit used TRF).
MARGINAL: independently formulated shifted-box LP + shared HiGHS dual simplex.
The LP solver library is NOT independently implemented. All post-rounding
objective bounds and serialization checks use exact standard-library rationals.
No refitted coefficient is deployed and no new economic observation is acquired.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SCALE = 1 << 30
FAMILIES = ('quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid')
LOSSES = ('value', 'marginal')
INPUTS = ROOT / 'inherited_fit121'
COUNTS = {}


def count(key, n=1):
    COUNTS[key] = COUNTS.get(key, 0) + n


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as s:
        for b in iter(lambda: s.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def rational(x):
    return Q(x)


def serial(x):
    if isinstance(x, Q):
        return {'numerator': str(x.numerator), 'denominator': str(x.denominator)}
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [serial(v) for v in x]
    if hasattr(x, 'item'):
        return x.item()
    return x


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as s:
        json.dump(serial(obj), s, sort_keys=True, indent=2, allow_nan=False)
        s.write('\n')


def append(path, obj):
    with Path(path).open('a', encoding='utf-8') as s:
        s.write(json.dumps(serial(obj), sort_keys=True, allow_nan=False) + '\n')
        s.flush()


def read(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as s:
        return json.load(s)


def require(ok, message):
    count('assertions')
    if not ok:
        raise ArithmeticError(message)


def source_gate(commit):
    """Exact Git-byte gate before scientific imports or historical refitting."""
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('An exact 40-character source-freeze commit is mandatory')
    manifest = read(INPUTS / 'INPUT_MANIFEST126.json')
    paths = [ROOT / 'code126/independent_fit126.py', ROOT / 'FIT_AUDIT_PROTOCOL126.md',
             INPUTS / 'INPUT_MANIFEST126.json']
    for row in manifest['files']:
        p = ROOT / row['path']
        require(p.is_file() and sha(p) == row['sha256'], 'Historical input hash: ' + row['path'])
        paths.append(p)
    verified = []
    for p in paths:
        relative = p.relative_to(REPO).as_posix()
        stored = subprocess.check_output(['git', '-C', str(REPO), 'show', commit + ':' + relative])
        require(hashlib.sha256(stored).hexdigest() == sha(p), 'Frozen Git bytes: ' + relative)
        verified.append({'path': relative, 'sha256': sha(p), 'bytes': len(stored)})
    return {'source_commit': commit, 'verified_files': verified,
            'input_manifest_sha256': sha(INPUTS / 'INPUT_MANIFEST126.json'),
            'historical_actor_publication_commit': manifest['historical_actor_publication_commit'],
            'historical_source_head': manifest['historical_source_head']}


def expected_basis(family, budget):
    """Reconstruct the pre-label feature specification from PROTOCOL121."""
    require(family in FAMILIES and budget in (5, 9), 'Declared family and budget')
    if family in ('quadratic', 'poly2', 'poly3'):
        exponents = [[0, 0, 1], [1, 0, 1], [0, 1, 1], [0, 0, 2]]
        if family == 'poly3':
            exponents = [[a, b, t-a-b] for t in (1, 2, 3)
                         for a in range(t+1) for b in range(t-a+1) if t-a-b >= 1]
        n = len(exponents); low = [-128] * n
        if family == 'quadratic': low[3] = 0
        return {'type': 'monomial', 'exponents': exponents}, low, [128] * n
    if family in ('relu', 'hinge'):
        units = [{'direction': [a, b, 1], 'state_center': [.5, .5],
                  'threshold': q, 'scale': .25} for a in (-1, 0, 1)
                 for b in (-1, 0, 1) for q in (.125, .375, .625, .875)]
        return {'type': 'anchored_relu', 'base_exponents': [[0, 0, 1], [1, 0, 1], [0, 1, 1]],
                'units': units}, [-128]*3 + [0]*36, [128]*39
    if family == 'spline':
        knots = [0.]*4 + ([.5] if budget == 9 else []) + [1.]*4
        n = len(knots)-4
        columns = [[a, b, c] for a in range(n) for b in range(n) for c in range(1, n)]
        spec = {'type': 'tensor_bspline', 'degree': 3, 'knots': [knots, knots, knots],
                'axis_basis_counts': [n, n, n], 'columns': columns}
    else:
        state = [k/(budget-1) for k in range(budget)]
        columns = [[a, b, c] for a in range(budget) for b in range(budget) for c in range(1, 5)]
        spec = {'type': 'tensor_hat', 'degree': 1,
                'knots': [state, state, [0., .25, .5, .75, 1.]],
                'axis_basis_counts': [budget, budget, 5], 'columns': columns}
    return spec, [-128]*len(columns), [128]*len(columns)


def validate_basis(desc, family, budget):
    spec, low, high = expected_basis(family, budget)
    for key, value in spec.items(): require(desc[key] == value, 'Prospective feature specification: '+key)
    require(desc['coefficient_lower'] == low and desc['coefficient_upper'] == high, 'Prospective coefficient box')
    require(desc['feature_count'] == len(low), 'Feature count')
    require(desc['coefficient_bits'] == 30 and desc['anchored_at_v_zero'], 'Anchor and readout precision')
    if family in ('relu', 'hinge'):
        require(desc['neural_feature_search_performed'] is False, 'No unrecorded feature search')
        require(desc['hidden_directions_are_fixed_before_labels'] is True, 'Pre-label directions')
    return tuple(map(Q, low)), tuple(map(Q, high))


@lru_cache(maxsize=20000)
def spline_axis(knots, degree, point, derivative=False):
    """Exact Cox--de Boor recurrence, with the feasible inward right endpoint."""
    knots = tuple(map(Q, knots)); x = Q(point)
    require(knots[0] <= x <= knots[-1], 'Spline coordinate domain')
    nonempty = [j for j in range(len(knots)-1) if knots[j] < knots[j+1]]
    cell = nonempty[-1] if x == knots[-1] else next(j for j in nonempty if knots[j] <= x < knots[j+1])
    level = [Q(j == cell) for j in range(len(knots)-1)]
    before = None
    for order in range(1, degree+1):
        before = level
        level = []
        for j in range(len(knots)-order-1):
            left = (x-knots[j])*before[j]/(knots[j+order]-knots[j]) if knots[j+order] != knots[j] else Q(0)
            right = (knots[j+order+1]-x)*before[j+1]/(knots[j+order+1]-knots[j+1]) if knots[j+order+1] != knots[j+1] else Q(0)
            level.append(left+right)
    if not derivative: return tuple(level)
    return tuple((degree*before[j]/(knots[j+degree]-knots[j]) if knots[j+degree] != knots[j] else Q(0))
                 - (degree*before[j+1]/(knots[j+degree+1]-knots[j+1]) if knots[j+degree+1] != knots[j+1] else Q(0))
                 for j in range(len(level)))


@lru_cache(maxsize=20000)
def hat_axis(knots, point, derivative=False, side=0):
    knots = tuple(map(Q, knots)); x = Q(point)
    require(knots[0] <= x <= knots[-1], 'Hat coordinate domain')
    if x == knots[0]: cell = 0
    elif x == knots[-1]: cell = len(knots)-2
    elif side < 0: cell = next(j for j in range(len(knots)-1) if knots[j] < x <= knots[j+1])
    else: cell = next(j for j in range(len(knots)-1) if knots[j] <= x < knots[j+1])
    width = knots[cell+1]-knots[cell]; values = [Q(0)]*len(knots)
    if derivative: values[cell], values[cell+1] = -1/width, 1/width
    else: values[cell], values[cell+1] = (knots[cell+1]-x)/width, (x-knots[cell])/width
    return tuple(values)


def exact_row(desc, point, derivative=False, side=0):
    x, y, v = tuple(map(Q, point)); require(all(0 <= z <= 1 for z in (x,y,v)), 'Feature domain [0,1]^3')
    kind = desc['type']; answer = {}
    if kind == 'monomial':
        for j, (p,q,r) in enumerate(desc['exponents']):
            z = x**p*y**q*(r*v**(r-1) if derivative else v**r)
            if z: answer[j] = z
    elif kind == 'anchored_relu':
        for j, base in enumerate((Q(1), x, y)):
            z = base if derivative else base*v
            if z: answer[j] = z
        for j, unit in enumerate(desc['units'], start=3):
            wx,wy,wv = map(Q,unit['direction']); cx,cy = map(Q,unit['state_center']); scale = Q(unit['scale'])
            base = scale*(wx*(x-cx)+wy*(y-cy)-Q(unit['threshold'])); z = base+scale*wv*v
            value = scale*wv*Q(z>0 or (z==0 and side>=0)) if derivative else max(z,Q(0))-max(base,Q(0))
            if value: answer[j] = value
    elif kind in ('tensor_bspline','tensor_hat'):
        axes=[]
        for axis,z in enumerate((x,y,v)):
            k=tuple(desc['knots'][axis]); der = derivative and axis==2
            axes.append(spline_axis(k,3,z,der) if kind=='tensor_bspline' else hat_axis(k,z,der,side if axis==2 else 0))
        for j,(a,b,c) in enumerate(desc['columns']):
            z=axes[0][a]*axes[1][b]*axes[2][c]
            if z: answer[j]=z
    else: raise ValueError('Unknown declared basis')
    if derivative:
        capacity=Q(1,8)+(x+y)/16
        answer={j:z/capacity for j,z in answer.items()}
    count('exact_feature_rows');count('nonzero_feature_entries',len(answer))
    return answer


def exact_design(desc, labels):
    budget=desc['budget']; expected_states=[[i/(budget-1),j/(budget-1)] for i in range(budget) for j in range(budget)]
    probes=sorted({v+h for v in (0.,.25,.5,.75,1.) for h in (-2**-12,0.,2**-12) if 0<=v+h<=1})
    require(labels['state_grid']==expected_states and labels['normalized_action_probes']==probes, 'Unchanged complete acquisition grid')
    require(len(labels['values'])==13*budget**2 and len(labels['marginals'])==5*budget**2, 'Complete label census')
    vr=[]; targets=[]
    for k,row in enumerate(labels['values']):
        expect=expected_states[k//13]+[probes[k%13]]
        require(row['u']==expect,'Value design ordering')
        lo,hi=Q(row['continuation_difference_lower']),Q(row['continuation_difference_upper'])
        require(lo<=hi,'Value target interval order')
        vr.append(exact_row(desc,row['u']));targets.append((lo+hi)/2)
    dr=[];lo=[];hi=[];metadata=[]
    for k,row in enumerate(labels['marginals']):
        expect=expected_states[k//5]+[[0.,.25,.5,.75,1.][k%5]]
        require(row['u']==expect,'Marginal design ordering')
        v=Q(row['u'][2]); sides=[1] if v==0 else [-1] if v==1 else [-1,1] if desc['type'] in ('anchored_relu','tensor_hat') else [0]
        for side in sides:
            a,b=Q(row['continuation_marginal_lower']),Q(row['continuation_marginal_upper']);require(a<=b,'Marginal interval order')
            dr.append(exact_row(desc,row['u'],True,side));lo.append(a);hi.append(b)
            metadata.append({'label_index':k,'u':row['u'],'side':side,'lower':row['continuation_marginal_lower'],'upper':row['continuation_marginal_upper']})
    return vr,targets,dr,lo,hi,metadata


def matrix_discrepancy(rows, saved, n):
    require(len(rows)==len(saved),'Saved design row count'); worst=Q(0)
    for row,old in zip(rows,saved):
        require(len(old)==n,'Saved design width')
        for j,z in enumerate(old):
            if z or j in row: worst=max(worst,abs(row.get(j,Q(0))-Q(z)))
    return worst


def dense(rows,n,np):
    a=np.zeros((len(rows),n))
    for i,row in enumerate(rows):
        for j,z in row.items():a[i,j]=float(z)
    return a


def dot(row,theta):
    return sum((z*theta[j] for j,z in row.items()),Q(0))


def box_min(g,lower,upper):
    return sum((z*(lo if z>=0 else hi) for z,lo,hi in zip(g,lower,upper)),Q(0))


def value_certificate(rows,target,theta,lower,upper):
    n=len(theta);obj=Q(0);g=[Q(0)]*n
    for row,y in zip(rows,target):
        r=dot(row,theta)-y;obj+=r*r
        for j,z in row.items():g[j]+=2*r*z
    lower_bound=max(Q(0),obj+box_min(g,lower,upper)-sum((g[j]*theta[j] for j in range(n)),Q(0)))
    require(0<=lower_bound<=obj,'Exact squared-loss support certificate')
    return {'sum_squared_loss':obj,'mean_squared_loss':obj/len(rows),'optimum_lower':lower_bound,
            'optimality_gap_upper':obj-lower_bound,'box_gradient':g,
            'method':'Exact convex tangent minimized over the declared box; no optimizer success assertion is used.'}


def marginal_certificate(rows,lo,hi,theta,lower,upper,multipliers):
    upper_bound=max(max(dot(r,theta)-a,b-dot(r,theta)) for r,a,b in zip(rows,lo,hi))
    require(len(multipliers)==2*len(rows),'All marginal dual coordinates')
    w=[max(Q(0),-Q(float(z))) for z in multipliers];mass=sum(w,Q(0))
    w=[z/mass for z in w] if mass else [Q(1,len(w))]*len(w)
    require(sum(w,Q(0))==1 and all(z>=0 for z in w),'Exact normalized nonnegative dual')
    g=[Q(0)]*len(theta);constant=Q(0);m=len(rows)
    for i,(r,a,b) in enumerate(zip(rows,lo,hi)):
        constant+=-w[i]*a+w[m+i]*b
        for j,z in r.items():g[j]+=(w[i]-w[m+i])*z
    lower_bound=max(Q(0),constant+box_min(g,lower,upper))
    require(0<=lower_bound<=upper_bound,'Exact robust-marginal weak duality')
    return {'robust_node_residual_upper':upper_bound,'optimum_lower':lower_bound,
            'optimality_gap_upper':upper_bound-lower_bound,'normalized_dual_weights':w,
            'dual_box_gradient':g,'zero_mass_uniform_rule_used':mass==0,
            'method':'Exact simplex normalization and box minimum; finite design and fixed coefficients only.'}


def rounded(raw,lower,upper):
    integers=[min(int(hi*SCALE),max(int(lo*SCALE),round(Q(float(z))*SCALE))) for z,lo,hi in zip(raw,lower,upper)]
    return [Q(z,SCALE) for z in integers],integers


def serialization_check(model,fit,lower,upper):
    n=len(lower);raw=fit['raw_solver']['x'][:n];rounded_theta,integers=rounded(raw,lower,upper)
    actual=[Q(int(z),int(model['theta_denominator'])) for z in model['theta_numerators']]
    require(model['theta_denominator']==SCALE,'30-bit denominator')
    require(actual==rounded_theta and integers==model['theta_numerators'],'Independent ties-even rounding and clipping')
    require(actual==list(map(Q,model['theta'])),'Stored binary64 and rational identity')
    require(model['theta_hex']==[float(z).hex() for z in actual],'Stored hexadecimal identity')
    require(all(lo<=z<=hi for z,lo,hi in zip(actual,lower,upper)),'Exact stored coefficient feasibility')
    return actual


def audit_one(model,fit,old_design,labels,solver_cache,np,scipy,output_folder):
    desc=model['basis'];family=desc['arm'];budget=desc['budget'];loss=model['loss'];n=desc['feature_count']
    lower,upper=validate_basis(desc,family,budget)
    vr,target,dr,dlo,dhi,metadata=exact_design(desc,labels)
    require(metadata==old_design['derivative_rows'],'Independent one-sided derivative row construction')
    require([r['u'] for r in labels['values']]==[r['u'] for r in old_design['value_rows']],'Independent value row construction')
    discrepancies={'value':matrix_discrepancy(vr,old_design['value_matrix'],n),'derivative':matrix_discrepancy(dr,old_design['derivative_matrix'],n)}
    stored=serialization_check(model,fit,lower,upper)
    require(model['fit_global_certificate_claim'] is False,'No inherited whole-domain fit certificate')
    arrays=dense(vr,n,np),np.array([float(z) for z in target]),dense(dr,n,np),np.array([float(z) for z in dlo]),np.array([float(z) for z in dhi])
    value_a,y,deriv_a,lo,hi=arrays;start=time.perf_counter()
    key=(budget,model['index'],loss)
    if family=='hinge':
        require(key in solver_cache,'Matching paid ReLU audit precedes hinge copy')
        raw,raw_record=solver_cache[key];raw=list(raw);raw_record=dict(raw_record,solver_invoked=False,matched_relu_audit_readout_copied=True)
        require(model['exact_feature_and_readout_identity_with_relu'] is True,'Inherited hinge copy identity marker')
    elif loss=='value':
        from scipy.optimize import lsq_linear
        res=lsq_linear(value_a,y,bounds=(np.array(list(map(float,lower))),np.array(list(map(float,upper)))),
                       method='bvls',tol=1e-12,max_iter=1000,verbose=0)
        raw=list(res.x)
        raw_record={'solver':'SciPy lsq_linear BVLS active-set','shared_library_with_production':True,
                    'different_algorithm_from_historical_TRF':True,'solver_invoked':True,
                    'success':bool(res.success),'status':int(res.status),'message':str(res.message),
                    'x':raw,'iterations':int(res.nit),'reported_half_sum_squares':float(res.cost),'reported_optimality':float(res.optimality)}
        count('new_value_solver_invocations')
    else:
        from scipy.optimize import linprog
        shift=np.array(list(map(float,lower)));span=np.array([float(b-a) for a,b in zip(lower,upper)])
        aa=np.vstack((np.column_stack((deriv_a,-np.ones(len(dr)))),np.column_stack((-deriv_a,-np.ones(len(dr))))))
        bb=np.concatenate((lo-deriv_a@shift,-hi+deriv_a@shift))
        res=linprog(np.r_[np.zeros(n),1.],A_ub=aa,b_ub=bb,bounds=[(0,float(w)) for w in span]+[(0,None)],
                    method='highs-ds',options={'presolve':True,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
        raw=None if res.x is None else list(res.x[:n]+shift)
        raw_record={'solver':'SciPy linprog shared HiGHS dual simplex','shared_library_with_production':True,
                    'independent_LP_solver_implementation':False,'solver_invoked':True,
                    'formulation':'z=theta-lower; 0<=z<=upper-lower, robust rows with shifted RHS',
                    'success':bool(res.success),'status':int(res.status),'message':str(res.message),
                    'x':raw,'shifted_solution':None if res.x is None else res.x.tolist(),'iterations':int(res.nit),
                    'reported_objective':None if res.fun is None else float(res.fun),
                    'inequality_marginals':None if res.ineqlin.marginals is None else res.ineqlin.marginals.tolist()}
        count('new_marginal_solver_invocations')
    solve_seconds=time.perf_counter()-start
    write(output_folder/'RAW_SOLVER126.json',dict(raw_record,solver_seconds=solve_seconds))
    require(raw_record['success'] and raw is not None and np.all(np.isfinite(raw)),'Independent solver failed; preserve attempt')
    if family=='relu':solver_cache[key]=(list(raw),raw_record)
    new,integers=rounded(raw,lower,upper)
    stored_value=value_certificate(vr,target,stored,lower,upper);new_value=value_certificate(vr,target,new,lower,upper)
    result={'arm':family,'loss':loss,'budget':budget,'risk_index':model['index'],'alpha':labels['alpha'],'feature_count':n,
            'value_rows':len(vr),'marginal_rows':len(dr),'raw_solver':raw_record,'solver_seconds':solve_seconds,
            'historical_design_exact_discrepancies':discrepancies,'historical_rounding_serialization_verified':True,
            'prespecified_feature_generation_verified':True,'data_driven_feature_selection_performed':False,
            'stored_value_certificate':stored_value,'independent_value_certificate':new_value,
            'coefficient_exact_match_to_historical':new==stored,'coefficient_match_required':False,
            'independent_theta_numerators':integers,'independent_theta_denominator':SCALE,
            'finite_design_only':True,'global_domain_validation_executed':False,
            'economic_queries':0,'deployed_actor_replaced':False,'external_authorship_independence_claimed':False}
    if loss=='marginal':
        result['stored_marginal_certificate']=marginal_certificate(dr,dlo,dhi,stored,lower,upper,fit['raw_solver']['inequality_marginals'])
        result['independent_marginal_certificate']=marginal_certificate(dr,dlo,dhi,new,lower,upper,raw_record['inequality_marginals'])
        a=result['stored_marginal_certificate'];b=result['independent_marginal_certificate']
        result['signed_independent_minus_stored_objective_interval']=[b['optimum_lower']-a['robust_node_residual_upper'],b['robust_node_residual_upper']-a['optimum_lower']]
        result['actual_rounded_objective_difference']=b['robust_node_residual_upper']-a['robust_node_residual_upper']
    else:
        result['signed_independent_minus_stored_objective_interval']=[new_value['optimum_lower']-stored_value['sum_squared_loss'],new_value['sum_squared_loss']-stored_value['optimum_lower']]
        result['actual_rounded_objective_difference']=new_value['sum_squared_loss']-stored_value['sum_squared_loss']
    independent_model={'kind':'r126-audit-only-r121-readout','basis':desc,'loss':loss,'theta_numerators':integers,
                       'theta_denominator':SCALE,'theta':[float(z) for z in new],'theta_hex':[float(z).hex() for z in new],
                       'anchor':labels['anchor'],'deployment_authorized':False,'finite_design_audit_only':True}
    require([Q(z,SCALE) for z in independent_model['theta_numerators']]==list(map(Q,independent_model['theta'])),'Independent serialized exact coefficients')
    return result,independent_model


def self_test():
    desc={'type':'anchored_relu',**expected_basis('relu',5)[0]}
    hinge={'type':'anchored_relu',**expected_basis('hinge',5)[0]}
    for point in [(Q(0),Q(0),Q(0)),(Q(1,2),Q(1,2),Q(1,8)),(Q(1),Q(1),Q(1))]:
        for side in (-1,1):require(exact_row(desc,point,True,side)==exact_row(hinge,point,True,side),'Synthetic feature equivalence')
        require(exact_row(desc,[point[0],point[1],Q(0)])=={},'Synthetic exact anchor')
    for k in [(0,0,0,0,1,1,1,1),(0,0,0,0,Q(1,2),1,1,1,1)]:
        for x in [Q(0),Q(1,4),Q(1,2),Q(1)]:
            require(sum(spline_axis(k,3,x))==1,'Synthetic spline unity')
            require(sum(spline_axis(k,3,x,True))==0,'Synthetic spline derivative unity')
    require(rounded([2**-31,3*2**-31],[Q(-128)]*2,[Q(128)]*2)[1]==[0,2],'Synthetic ties-even')
    certificate=value_certificate([{0:Q(1)}],[Q(2)],[Q(1)],[Q(0)],[Q(1)])
    require(certificate['optimum_lower']==certificate['sum_squared_loss']==1,'Synthetic constrained value optimum')
    cert=marginal_certificate([{0:Q(1)}],[Q(0)],[Q(2)],[Q(1)],[Q(0)],[Q(2)],[-.5,-.5])
    require(cert['optimum_lower']==cert['robust_node_residual_upper']==1,'Synthetic exact LP dual')
    return {'status':'passed','original_economic_calls':0,'historical_fits_executed':0,'counts':COUNTS}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-commit');parser.add_argument('--output',type=Path);parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps(serial(self_test()),sort_keys=True));return 0
    if args.output is None or args.source_commit is None:parser.error('--source-commit and exclusive --output are required')
    args.output.mkdir(parents=True,exist_ok=False);started=time.perf_counter();wall=datetime.now(timezone.utc).isoformat();records=[];failures=[];solver_cache={}
    try:
        gate=source_gate(args.source_commit);write(args.output/'SOURCE_READBACK126.json',gate)
        import numpy as np
        import scipy
        write(args.output/'ENVIRONMENT126.json',{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,
              'threads':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},'argv':sys.argv})
        for budget in (5,9):
            acq=INPUTS/f'results121/acquisition{budget}-attempt01'
            for index in (0,1):
                labels_path=acq/f'labels-{index}.json';labels=read(labels_path)
                for family in FAMILIES:
                    for loss in LOSSES:
                        name=f'{budget}-{index}-{family}-{loss}';folder=acq/'models'/f'{index}-{family}-{loss}';clock=time.perf_counter()
                        try:
                            model,fit,design=(read(folder/f) for f in ('model.json','fit.json','design.json.gz'))
                            require(model['label_sha256']==sha(labels_path),'Actual original actor-label identity')
                            model_output=args.output/'models'/name
                            model_output.mkdir(parents=True,exist_ok=False)
                            write(model_output/'INPUT_IDENTITIES126.json',{'model':sha(folder/'model.json'),'labels':sha(labels_path),'fit':sha(folder/'fit.json'),'design':sha(folder/'design.json.gz')})
                            result,independent_model=audit_one(model,fit,design,labels,solver_cache,np,scipy,model_output)
                            result.update(model_sha256=sha(folder/'model.json'),labels_sha256=sha(labels_path),fit_sha256=sha(folder/'fit.json'),
                                          design_sha256=sha(folder/'design.json.gz'),historical_source_commit=model['source_commit'],elapsed_seconds=time.perf_counter()-clock)
                            write(args.output/'models'/name/'independent_model.json',independent_model)
                            readback=read(args.output/'models'/name/'independent_model.json')
                            require(readback==serial(independent_model),'JSON serialization independent readback')
                            write(args.output/'models'/name/'CERTIFICATE126.json',result);append(args.output/'records126.jsonl',result);records.append(result)
                            print('AUDITED',name,round(result['elapsed_seconds'],3),flush=True)
                        except BaseException:
                            failure={'model':name,'exception':traceback.format_exc(),'elapsed_seconds':time.perf_counter()-clock,'attempt_retained':True}
                            append(args.output/'FAILED126.jsonl',failure);failures.append(failure);print('FAILED',name,flush=True)
        write(args.output/'EXECUTION126.json',{'status':'executed' if len(records)==56 and not failures else 'executed_with_failures',
              'source_commit':args.source_commit,'started_utc':wall,'finished_utc':datetime.now(timezone.utc).isoformat(),'total_seconds':time.perf_counter()-started,
              'successful_model_audits':len(records),'expected_model_audits':56,'failed_model_audits':len(failures),'counts':COUNTS,
              'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'economic_queries':0,'deployed_actors_replaced':0,
              'scope':'Independent feature/design/refit/rounding/serialization implementation with shared NumPy/SciPy and shared HiGHS LP library. Exact finite-design certificates; no new whole-domain or policy-population claims.',
              'failed_models':[x['model'] for x in failures]})
        return 0 if len(records)==56 and not failures else 2
    except BaseException:
        append(args.output/'FAILED126.jsonl',{'exception':traceback.format_exc(),'phase':'initialization_or_outer_execution','elapsed_seconds':time.perf_counter()-started})
        raise


if __name__=='__main__':
    raise SystemExit(main())
