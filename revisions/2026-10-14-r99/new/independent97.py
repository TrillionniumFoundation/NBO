"""Independent proposal replay and exact-rational audit; no production kernels.

NumPy is used for a separately derived proposal implementation. Certificates
are checked by the retained Fraction primitive evaluator, not by this proposal.
"""
from __future__ import annotations
import csv, hashlib, json, math, pathlib, sys, time, struct
from fractions import Fraction as Q
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'code'))
from independent94 import economic_S, next_state, terminal_bounds
from independent96 import endpoints, original_lower, tail
B=np.array([.5,.25]); SIG=np.array([1.,-1.]); RAD=1/32; BETA=15/16


def primitive(y, terminal=False):
    diff=y[...,0]-y[...,1]; short=np.maximum(.5-y.sum(axis=-1),0)
    val=(2 if terminal else 1)*np.sum((y-.625)**2,axis=-1)+diff*diff/4+2*short*short
    grad=(4 if terminal else 2)*(y-.625)+np.stack((diff/2,-diff/2),axis=-1)-4*short[...,None]
    return val,grad


def transition(x,a,z=0.):
    return 1/16+x/2+x[...,::-1]/8+x*(1-x[...,::-1])/16+a[...,None]*B+np.asarray(z)[...,None]*SIG


def last_value_gradient(x,a,alpha, state_gradient=False):
    # Interpolate the primitive polynomial at -R,0,R, rather than using the
    # production risk coefficient formula. Its shortfall term is constant in z.
    y=transition(x,a); v0,g0=primitive(y,True); vm,gm=primitive(y-RAD*SIG,True); vp,gp=primitive(y+RAD*SIG,True)
    linear=(vp-vm)/(2*RAD); quadratic=(vp+vm-2*v0)/(2*RAD**2)
    if np.any(quadratic<=0): raise ArithmeticError('Primitive shock convexity lost')
    removed=2*RAD*alpha; l=np.maximum(-RAD,np.minimum(RAD-removed,-linear/(2*quadratic)-removed/2)); u=l+removed
    mass=2*RAD*(1-alpha)
    m1=(l*l-u*u)/(2*mass); m2=(l**3+2*RAD**3-u**3)/(3*mass)
    base,gx=primitive(x); tailgrad=g0+(gp-gm)/(2*RAD)*m1[...,None]
    value=base+a*a+4*a**4+BETA*(v0+linear*m1+quadratic*m2)
    ga=2*a+16*a**3+BETA*np.sum(tailgrad*B,axis=-1)
    if not state_gradient:return value,ga
    diag=.5+(1-x[...,::-1])/16; cross=.125-x[...,::-1]/16
    grad=gx+BETA*(tailgrad*diag+tailgrad[...,::-1]*cross)
    cap=.125+x.sum(axis=-1)/16; lam=np.where(cap-a<2**-30,np.maximum(-ga,0),0)
    return value,grad-lam[...,None]/16


def conventional_value(x,alpha):
    cap=.125+x.sum(axis=-1)/16; lo=np.zeros_like(cap);hi=cap.copy()
    _,gl=last_value_gradient(x,lo,alpha);_,gh=last_value_gradient(x,hi,alpha)
    for _ in range(18):
        a=(lo+hi)/2;_,ga=last_value_gradient(x,a,alpha);lo=np.where(ga<0,a,lo);hi=np.where(ga>=0,a,hi)
    a=np.where(gl>=0,0,np.where(gh<=0,cap,(lo+hi)/2));a=np.floor(a*2**38)/2**38
    return last_value_gradient(x,a,alpha,True)


def decode(path):
    raw=pathlib.Path(path).read_bytes()
    if raw.startswith(b'online-original'):return None
    a=np.frombuffer(raw,dtype='<f8');k=len(a)//4-1
    if len(a)!=4+4*k:raise ValueError('Invalid model')
    return int(a[0]),a[1:1+2*k].reshape(k,2),a[1+2*k:1+3*k],a[1+3*k:]


def fitted_value(y,model):
    kind,W,b,c=model;z=np.einsum('...d,kd->...k',y,W)+b
    phi=z*z if kind==0 else np.maximum(z,0)
    value=c[0]+np.sum(y*c[1:3],axis=-1)+np.sum(phi*c[3:],axis=-1)
    slope=2*z if kind==0 else (z>0).astype(float)
    grad=c[1:3]+np.einsum('...k,k,kd->...d',slope,c[3:],W)
    return value,grad


def proposal(x,alpha,model):
    x=np.asarray(x);cap=.125+x.sum(axis=-1)/16;lo=np.zeros(len(x));hi=cap.copy()
    shock=-RAD+(np.arange(128)+.5)*(2*RAD/128)
    def gradient(a):
        y=transition(x[:,None,:],a[:,None],shock[None,:])
        val,gr=conventional_value(y,alpha) if model is None else fitted_value(y,model)
        k=int(128*(1-alpha));idx=np.argsort(val,axis=-1,kind='stable')[:,-k:]
        slopes=np.sum(gr*B,axis=-1);riskgrad=np.take_along_axis(slopes,idx,axis=1).mean(axis=1)
        return 2*a+16*a**3+BETA*riskgrad
    gl=gradient(lo);gh=gradient(hi)
    for _ in range(16):
        a=(lo+hi)/2;g=gradient(a);lo=np.where(g<0,a,lo);hi=np.where(g>=0,a,hi)
    a=np.where(gl>=0,0,np.where(gh<=0,cap,(lo+hi)/2))
    return np.floor(a*2**30)/2**30


def read(path):
    with pathlib.Path(path).open() as f:return list(csv.DictReader(f))


def selected(rows):
    ids={0,len(rows)-1}
    # Deterministic extrema cover boundaries, poor first proposals and widths.
    for key in ('x0','x1','proposed_loss','width'):
        vals=[float(r[key]) for r in rows];ids.update((int(np.argmin(vals)),int(np.argmax(vals))))
    rejected=[i for i,r in enumerate(rows) if r['rejected']=='True']
    if rejected:ids.add(rejected[0]);ids.add(rejected[-1])
    return sorted(ids)


def run():
    start=time.perf_counter();dest=R/'audit97/INDEPENDENT97.json'
    result={'status':'started','source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
            'scope':'Separately derived binary64 proposals; exact-rational statistics; stratified rational endpoints. Not independent authorship or a proof-assistant verification.',
            'proposal_replay':[],'rational_endpoints':[],'exact_statistics':[],'discrepancies':[]}
    def save():
        result['seconds']=time.perf_counter()-start;dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    save();old=R/'results96/evaluation-primary';reference=json.loads((old/'RESULTS96.json').read_text())
    names=('online-risk-dp','quadratic','relu','spline')
    for index,alpha in enumerate((.5,.75)):
        data={arm:read(old/f'alpha-{index}-{arm}.csv') for arm in names}
        for lefti,left in enumerate(names):
            for right in names[lefti+1:]:
                lows=[];highs=[]
                for a,b in zip(data[left],data[right]):
                    if any(a[k]!=b[k] for k in ('row','x0','x1')):raise AssertionError('Unpaired source catalogue')
                    lows.append(max(-Q(1,256),Q(float(a['lower']))-Q(float(b['upper']))))
                    highs.append(min(Q(1,256),Q(float(a['upper']))-Q(float(b['lower']))))
                lo=sum(lows)/4096-Q(1,4096);hi=sum(highs)/4096+Q(1,4096)
                pub=reference['levels'][str(index)]['pairs'][left+' minus '+right]['interval']
                if not Q(pub[0])<=lo<=hi<=Q(pub[1]):raise AssertionError('Exact statistical containment failed')
                result['exact_statistics'].append({'risk_index':index,'left':left,'right':right,'lower':str(lo),'upper':str(hi),'contained':True})
        for arm,rows in data.items():
            obj=None if arm==names[0] else decode(R/f'results96/alpha-{index}/{arm}.bin')
            # Replay every original first proposal, including the conventional solver.
            ids=list(range(len(rows)))
            maximum=0.;mismatch=[]
            for offset in range(0,len(ids),64):
                batch=ids[offset:offset+64];x=np.array([[float(rows[j]['x0']),float(rows[j]['x1'])] for j in batch])
                got=proposal(x,alpha,obj);wanted=np.array([float(rows[j]['proposed']) for j in batch]);err=np.abs(got-wanted)
                maximum=max(maximum,float(err.max()))
                for j,g,w,e in zip(batch,got,wanted,err):
                    if e>2**-29:mismatch.append({'row':j,'independent':float(g),'production':float(w),'absolute_difference':float(e)})
            result['proposal_replay'].append({'risk_index':index,'arm':arm,'rows':len(ids),'selected_rows':'all',
                'maximum_absolute_difference':maximum,'tolerance':2**-29,'discrepancies':mismatch})
            result['discrepancies'].extend(mismatch);save()
        # Three difficult rows per stored arm plus conventional extrema, not a random sample.
        jobs=[]
        for arm,rows in data.items():
            pool=selected(rows);chosen=pool[:2]+[max(range(len(rows)),key=lambda j:float(rows[j]['proposed_loss']))]
            jobs.extend((arm,j,rows[j]) for j in sorted(set(chosen)))
        for arm,j,row in jobs:
            x=[Q(float(row['x0'])),Q(float(row['x1']))];a=Q(float(row['actions']));aa=Q(alpha)
            lo,hi=endpoints(x,a,aa,bins=256);lower=original_lower(x,a,aa)
            contained=Q(float(row['lower']))<=lo<=hi<=Q(float(row['upper']))
            admitted=hi-lower<=Q(1,256)
            result['rational_endpoints'].append({'risk_index':index,'arm':arm,'row':j,'lower':str(lo),'upper':str(hi),
                'optimum_lower':str(lower),'contained':contained,'admitted':admitted})
            if not contained or not admitted:result['discrepancies'].append({'kind':'endpoint','risk_index':index,'arm':arm,'row':j})
            save()
    result['old_rows_statistically_recomputed']=32768
    result['status']='passed' if not result['discrepancies'] else 'discrepancies-retained';save()
    if result['discrepancies']:raise AssertionError('Independent audit discrepancies preserved in '+str(dest))
    return result
if __name__=='__main__':run()
