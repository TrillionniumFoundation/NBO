"""R108 independent arithmetic audit and prespecified kernel diagnostics.

Finite arithmetic checks support implementation evidence; they do not replace
continuum proofs. No primary fitting, service or selection routine is imported
by audit_records. Kernel diagnostics call the retained independent rational
primitive implementation, which does not import production interval code.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,math,sys,time
ROOT=Path(__file__).resolve().parents[1]


def check(condition,message):
    if not condition:raise ArithmeticError(message)


def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n')


def fr(v):return F(float(v))


def kernel_diagnostic(output):
    import numpy as np
    sys.path.insert(0,str(ROOT/'code'));sys.path.insert(0,str(ROOT/'code108'))
    import independent94 as exact
    import kernel108 as k
    from interval94 import I
    rows=[];start=time.perf_counter();checks=0
    for d in (2,4,8):
        x=np.array([[((17*i+11*j+3)%64)/64 for j in range(d)] for i in range(64)])
        for alpha in (.5,.75):
            before=k.econ.COUNTS.copy();t=time.perf_counter();prod=k.compiled_certificate(I(x),alpha);seconds=time.perf_counter()-t
            for i,row in enumerate(x):
                xx=list(map(fr,row));aa=fr(prod['action'][i]);a=F(alpha)
                poly=exact.polynomial_from_primitives(xx,aa);check(poly[2]==5,'Shock coefficient');checks+=1
                risk,left,right,eta=exact.tail_threshold(poly,a)
                value,g=exact.objective_gradient(xx,aa,a);cap=F(1,8)+sum(xx)/F(8*d)
                delta=max(-aa,min(cap-aa,-g/2));exact_gap=-g*delta-delta*delta
                check(F(0)<=aa<=cap,'Feasible compiled action');checks+=1
                check(F(0)<=exact_gap<=F(1,2**20),'Independent exact original-regret bound');checks+=1
                check(fr(prod['lower'][i])<=value<=fr(prod['upper'][i]),'Feasible value enclosure');checks+=1
                # Independent derivative coefficients are assembled in rational
                # arithmetic from original coordinates, not production coefficients.
                b=[F(1,2) if j%2==0 else F(1,4) for j in range(d)]
                r=exact.next_state(xx,F(0),F(0));s=[1 if j%2==0 else -1 for j in range(d)]
                c0=F(8,d)*sum(b[j]*(r[j]-F(5,8)) for j in range(d))
                c0+=F(1,2*d)*sum((b[j]-b[(j+1)%d])*(r[j]-r[(j+1)%d]) for j in range(d))
                d0=F(10,d)*sum(s[j]*r[j] for j in range(d));h0=F(1,2)-F(2,d)*sum(r)
                for u in (F(0),aa,cap):
                    m=max(-a/32,min(a/32,a*(d0+F(5,4)*u)/(10*(1-a))))
                    formula=16*u**3+2*u+F(15,16)*(c0+F(41,32)*u-3*max(F(0),h0-F(3,4)*u)+F(5,4)*m)
                    check(formula==exact.objective_gradient(xx,u,a)[1],'Exact cubic derivative identity');checks+=1
                low,high,aroot=exact.terminal_bounds(xx,a,steps=32)
                check(low<=value and fr(prod['lower'][i])<=high,'Independent root bracket');checks+=1
                rows.append({'d':d,'index':i,'alpha':alpha,'state':[str(v) for v in xx],'action':str(aa),
                  'exact_feasible_value':str(value),'exact_derivative':str(g),'exact_regret_upper':str(exact_gap),
                  'independent_optimum_lower':str(low),'independent_optimum_upper':str(high),
                  'production_lower':float(prod['lower'][i]),'production_upper':float(prod['upper'][i]),
                  'tail_interval':[str(left),str(right)],'batch_compiled_seconds':seconds})
    save(output,{'status':'passed','checks':checks,'states_risks':len(rows),'rows':rows,'seconds':time.perf_counter()-start,
                 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 'scope':'384 deterministic kernel contexts, exact rational primitive integration and 32-step independent bisection; not a learned high-dimensional or population tournament.'})


def audit_records(out):
    out=Path(out);count=0;records=[];nrows=0;ntrials=0
    manifests=['CATALOGUE.json']+[f'timing/PROCESS-{r}.json' for r in range(7)]
    for name in manifests:
        manifest=json.loads((out/name).read_text())
        entries=manifest['catalogue'] if name=='CATALOGUE.json' else manifest['records']
        for entry in entries:
            p=out/entry['path'];check(hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],'Output content hash');count+=1
            data=json.loads(p.read_text());nrows+=len(data['rows']);ntrials+=len(data['trials'])
            for row in data['rows']:
                lo,hi,opt=map(fr,(row['lower'],row['upper'],row['optimum_lower']))
                check(lo<=hi and opt<=hi,'Interval ordering');count+=1
                check(fr(row['loss'])>=hi-opt and fr(row['loss'])<=F(1,256),'Original loss bound');count+=1
                check(fr(row['width'])>=hi-lo and fr(row['width'])<=F(1,8192),'Policy-width target');count+=1
                cap=F(1,8)+(fr(row['x0'])+fr(row['x1']))/16
                check(0<=fr(row['action'])<=cap,'Original feasible action');count+=1
                check(fr(row['action_distance_upper'])**2>=fr(row['loss']),'Outward action-distance bound');count+=1
            states={row['row']:{'action':fr(row['completed_baseline_action']),'lo':fr(row['baseline_lower']),
                               'hi':fr(row['baseline_upper']),'changes':0} for row in data['rows']}
            for trial in data['trials']:
                state=states[trial['row']]
                check(state['action']==fr(trial['incumbent_action']) and state['lo']==fr(trial['incumbent_lower']) and state['hi']==fr(trial['incumbent_upper']),'Sequential incumbent identity');count+=1
                qualifies=(fr(trial['candidate_loss'])<=F(1,256) and fr(trial['candidate_width'])<=F(1,8192))
                gate=fr(trial['candidate_upper'])<state['lo'] and qualifies and fr(trial['candidate_action'])!=state['action']
                check(gate==trial['accepted'],'Strict unchanged completed-policy gate');count+=1
                if gate:state.update(action=fr(trial['candidate_action']),lo=fr(trial['candidate_lower']),hi=fr(trial['candidate_upper']),changes=state['changes']+1)
            if data['trials']:
                for row in data['rows']:
                    state=states[row['row']]
                    check(state['action']==fr(row['action']) and state['changes']==row['safe_changes'],'Final trace identity');count+=1
            records.append({'path':entry['path'],'rows':len(data['rows']),'trials':len(data['trials'])})
    # The safe baselines must equal their separately executed completed controls.
    for i in range(2):
        for arm in ('online','quadratic','relu','hinge','spline','poly2','poly3','grid'):
            for backend in ('legacy','compiled'):
                a=json.loads((out/'catalogue'/f'{i}-{arm}-{backend}.json').read_text())
                b=json.loads((out/'catalogue'/f'{i}-{arm}-{backend}-safe.json').read_text())
                for x,y in zip(a['rows'],b['rows']):
                    check(fr(x['action'])==fr(y['completed_baseline_action']),'Paired completed baseline action');count+=1
                    for key in ('lower','upper','optimum_lower','loss','width'):
                        check(fr(x[key])==fr(y['baseline_'+key]),'Paired completed baseline interval');count+=1
    check(nrows==18432,'All primary and seven timing decisions retained')
    check(ntrials==27648,'All prespecified guard trials retained')
    save(out/'AUDIT108.json',{'status':'passed','rational_record_checks':count,'decision_rows':nrows,'trial_rows':ntrials,
                           'files':records,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                           'scope':'Independent standard-library exact arithmetic reconstruction of all stored bounds and gates; not independent floating risk-oracle execution or formal theorem certification.'})

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('kernel','records'));p.add_argument('--output',type=Path,default=ROOT/'results108')
    a=p.parse_args()
    if a.mode=='kernel':kernel_diagnostic(a.output/'KERNEL_AUDIT108.json')
    else:audit_records(a.output)
