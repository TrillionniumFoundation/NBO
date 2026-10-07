"""R47 acquired-state deployment, identical-envelope control, exact frontiers."""
from __future__ import annotations
import hashlib,itertools,json,math,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import constrained as z
import direct as d
R=z.R;c=z.c;I=z.I
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def leaf_error(labels,L,dimension):
    """Two rounded operations after exact dyadic state-distance formation."""
    u=F(1,2**53);gamma=2*u/(1-2*u);Lf=F(float(L));conversion=abs(Lf-L)
    M=max(map(lambda v:abs(F(float(v))),labels))
    return dimension*conversion+gamma*(M+dimension*abs(Lf))

def deploy_one(payload,coordinate_radius,quantum):
    eta=F(coordinate_radius);quantum=F(quantum);r=2*eta
    measurements=np.array(list(itertools.product(np.arange(33)/32,repeat=2)))
    lower=np.maximum(0,measurements-float(eta));upper=np.minimum(1,measurements+float(eta))
    cap_lower=1/8+np.sum(lower,axis=1)/16 # all operations exact on these dyadic inputs
    reports=[];total=F(0);start=time.perf_counter()
    for t,raw in enumerate(payload['models'][:-1]):
        model=z.Model.load(raw);actions=np.asarray(payload['actors'][t]);row=payload['rows'][t]
        distance=np.sum(np.abs(measurements[:,None,:]-model.nodes[None,:,:]),axis=-1)
        scores=model.v[None,:]+float(model.L)*distance
        selected=np.argmin(scores,axis=1);stored=actions[selected]
        repaired=np.minimum(stored,cap_lower)
        if quantum:executed=np.floor(repaired/float(quantum))*float(quantum)
        else:executed=repaired.copy()
        assert np.all(executed>=0) and np.all(executed<=cap_lower)
        exact=model.cones(measurements)
        excess=exact.hi[np.arange(len(selected)),selected]-np.min(exact.lo,axis=1)
        nu=2*leaf_error(model.v,model.L,2)
        # Interval diagnostic may overestimate true excess by its own width.
        max_excess=F(float(np.max(excess)))
        diagnostic_radius=F(float(np.max(exact.hi-exact.lo)))
        assert max_excess<=nu+2*diagnostic_radius
        D=F(row['D']);extra=nu+2*model.L*r+D*(2*z.KA*r+quantum)
        total+=z.BETA**t*extra
        reports.append({'date':t,'measured_states':len(measurements),
            'active_robust_repairs':int(np.count_nonzero(repaired<stored)),
            'quantized_actions':int(np.count_nonzero(executed<repaired)),
            'maximum_repair_displacement':float(np.max(stored-executed)),
            'maximum_interval_index_excess':float(max_excess),'index_interval_width':float(diagnostic_radius),
            'uniform_index_allowance':str(nu),'additional_component':str(extra),
            'cone_comparisons':int(scores.size),'repair_minima':len(measurements),
            'feasible_for_entire_acquisition_box':True,
            'action_sha256':hashlib.sha256(executed.tobytes()).hexdigest()})
    return {'coordinate_radius':str(eta),'l1_radius_bound':str(r),'action_quantum':str(quantum),
            'extra_policy_bound':str(total),'total_policy_bound':str(F(payload['policy_bound_exact'])+total),
            'rows':reports,'seconds':time.perf_counter()-start,
            'scope':'all-state execution allowance proved for dyadic acquired inputs; grid records exercise the implementation, not a proof by sampling'}

def deployment_study(out):
    records=[]
    for T,p in itertools.product((2,3),(1,4)):
        for N in z.LADDER:
            path=R/'results/constrained'/f'feasible-cone-witness-T{T}-p{p}-r0'/f'checkpoint-N{N}.json'
            payload=json.loads(path.read_text())
            tests=[deploy_one(payload,eta,q) for eta in (F(0),F(1,4096),F(1,256)) for q in (F(0),F(1,4096))]
            records.append({'T':T,'price':p,'N':N,'checkpoint_sha256':H(path),'tests':tests})
    c.write_new(out/'acquisition.json',{'models':len(records),'deployment_cases':sum(len(r['tests']) for r in records),'records':records})

def semantic_control(out):
    records=[];points=np.arange(1025)/1024
    for T,p in itertools.product((2,4),(1,4)):
        for N in (16,32,64,128,256,512):
            path=d.BASE/'results/services'/f'cone-witness-T{T}-p{p}-r0'/f'checkpoint-N{N}.json'
            payload=json.loads(path.read_text());rows=[]
            for t,m in enumerate(payload['definition']['models']):
                definition=m['definition'];k=np.array(list(map(lambda s:float(F(s)),definition['grid'])))
                y=np.array(list(map(lambda s:float(F(s)),definition['labels'])));L=F(definition['L'])
                ci=y[None,:]+float(L)*np.abs(points[:,None]-k[None,:])
                native=np.min(ci,axis=1);circuit=ci.copy()
                start=time.perf_counter()
                while circuit.shape[1]>1:
                    n=circuit.shape[1]//2;a=circuit[:,:2*n:2];b=circuit[:,1:2*n:2]
                    values=a-np.maximum(a-b,0)
                    if circuit.shape[1]%2:values=np.concatenate((values,circuit[:,-1:]),axis=1)
                    circuit=values
                elapsed=time.perf_counter()-start
                u=F(1,2**53);err=leaf_error(y,L,1);native_err=err
                M=max(abs(F(float(v))) for v in y)+L
                depth=math.ceil(math.log2(len(k)))
                for _ in range(depth):err+=6*u*(M+err)
                discrepancy=F(float(np.max(np.abs(native-circuit[:,0]))))
                assert discrepancy<=native_err+err
                rows.append({'date':t,'cones':len(k),'grid_points':len(points),
                             'maximum_float_difference':float(discrepancy),
                             'proved_difference_allowance':str(native_err+err),
                             'relu_depth':depth,'relu_gate_evaluation_seconds_only':elapsed})
            records.append({'T':T,'price':p,'N':N,'policy_checkpoint_sha256':H(path),'rows':rows})
    c.write_new(out/'representation.json',{'records':records,
        'mathematical_equality':'same cones, same exact continuation, same compiled right-cell selector, same action witnesses and certificate',
        'training':'shared data, not two independent runs',
        'timing_scope':'gate microdiagnostic only; not a complete method-speed comparison',
        'neural_acceleration_established':False})

def frontier(out):
    cells=[]
    for T,p in itertools.product((2,4),(1,4)):
        rec=[]
        for method in ('cone-witness','spline-nearest'):
            path=d.BASE/'results/services'/f'{method}-T{T}-p{p}-r0/record.json'
            rec.append(json.loads(path.read_text()))
        cuts=sorted({F(0)}|{F(a['bound_exact']) for r in rec for a in r['attempts']})
        intervals=[]
        for left,right in zip(cuts,cuts[1:]):
            choices=[]
            for r in rec:
                selected=next((a for a in r['attempts'] if F(a['bound_exact'])<=left),None)
                choices.append(None if selected is None else {'N':selected['N'],'prefix_queries':selected['prefix_q_evaluations']})
            relation='both-unattained'
            if all(choices):
                w,s=[a['prefix_queries'] for a in choices]
                relation='witness-fewer' if w<s else ('spline-fewer' if s<w else 'same')
            elif choices[0]:relation='only-witness-attained'
            elif choices[1]:relation='only-spline-attained'
            intervals.append({'epsilon_left_closed':str(left),'epsilon_right_open':str(right),
                              'witness':choices[0],'spline':choices[1],'relation':relation})
        cells.append({'T':T,'price':p,'intervals':intervals,
                      'above_largest_breakpoint':'both first-rung query counts coincide'})
    c.write_new(out/'frontier.json',{'cells':cells,'design':'descriptive exact step functions of the frozen R46 curves; not new prospective targets'})

def main():
    out=R/'results/deployment'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);deployment_study(out);semantic_control(out);frontier(out)
if __name__=='__main__':main()
