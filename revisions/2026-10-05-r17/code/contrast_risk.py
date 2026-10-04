"""Frozen R17 action-contrast risk audit of the complete R16 critic population.

The estimand is conditional risk of deployed binary64 predictions, not generic
training risk or the payoff of a different actor. No confirmation payoff is
read by preparation. Every saved critic and query is retained. Antithetic signs
are one observation; new Raw-prediction and audit domains are disjoint.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, platform, sys, time
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]
OLD=ROOT/'revisions/2026-10-04-r16'
sys.path.insert(0,str(OLD/'code'))
from menu_economy import load_economy, fixed_queries, canonical_hash, array_hash, write_json
from menu_methods import ScalarContinuation
import menu_verify as mv
from menu_verify import I, pc, statistics
BASE='0b15260752b8e988236f82cc0ee7752b44f326f1'

def seed_for(seed,cal,d,domain):
    text=f'NBO-R17-contrast-v1/{seed}/{cal}/{d}/{domain}'
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'big')%(2**63-1)

def protocols():
    return (json.loads((OLD/'protocols/menu_protocol.json').read_text()),
            json.loads((R/'protocols/contrast_risk.json').read_text()))

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def exact_contrast(a,b,z):
    """Risk-difference observation; inputs may also be exact Fractions."""
    return (a-b)*(a+b-2*z)

def two_action_regret(current,continuation,prediction):
    true=current+continuation
    return max(0.,true)-(true if current+prediction>=0 else 0.)

def geometry(e,q,a):
    ref=np.full_like(a,e.schedule[0]); states=q['states']
    if a.shape!=states.shape or not np.isfinite(a).all(): raise ValueError('invalid actions')
    if np.any(a<q['lower']) or np.any(a>q['upper']): raise ValueError('infeasible actions')
    constants=mv.model_constants(e)
    pa,pb=mv.post_interval(e,states,a),mv.post_interval(e,states,ref)
    xa,xb=pc.midpoint(pa),pc.midpoint(pb)
    center=pc.midpoint(mv.quadratic_value_interval(e,pa)-mv.quadratic_value_interval(e,pb))
    same=np.all(a==ref,axis=1); center[same]=0.
    rg=mv.conditional_range(e,a,ref,pa,pb,I(center),constants,8.)
    na=mv.numerical_account(e,pa,xa,constants,10.)
    nb=mv.numerical_account(e,pb,xb,constants,10.)
    # Complete evaluation, antithetic averaging, differences, and centering.
    numerical=(I(na['arithmetic_upper'])+I(nb['arithmetic_upper'])+
        I(pc.gamma(16))*(I(na['payoff_magnitude_upper'])+I(nb['payoff_magnitude_upper'])+I(abs(center))))
    clipping=I(na['gaussian_clipping_bias_upper'])+I(nb['gaussian_clipping_bias_upper'])
    bias=(numerical+clipping).hi.copy(); bias[same]=0.
    return dict(center=center.tolist(),bounds=rg['bounds'],tails=rg['tails'],
        evaluation_bias_upper=bias.tolist(),range_account=rg,
        numerical_left=na,numerical_right=nb,spectral=constants['spectral']),xa,xb

def draw_contrasts(e,xa,xb,seed,pairs,batch=1024):
    q,d=xa.shape; out=np.empty((q,pairs)); digest=hashlib.sha256()
    rng=np.random.Generator(np.random.PCG64(seed))
    for first in range(0,q*pairs,batch):
        last=min(first+batch,q*pairs); ids=np.arange(first,last)//pairs
        z=rng.standard_normal((last-first,e.steps,d+1))
        digest.update(z.astype('<f8',copy=False).tobytes());z=np.clip(z,-10.,10.)
        left=(mv._future_value(e,xa[ids],z,1.)+mv._future_value(e,xa[ids],z,-1.))/2
        right=(mv._future_value(e,xb[ids],z,1.)+mv._future_value(e,xb[ids],z,-1.))/2
        out.reshape(-1)[first:last]=left-right
    return out,digest.hexdigest()

def prepare_one(cal,d,seed,out,old,p):
    start=time.perf_counter(); e=load_economy(old,cal,d);q=fixed_queries(old,d)
    fit=OLD/f'results/continuation_menu/trials/{cal}_d{d}_s{seed}/fits/nbo_scalar'
    receipt=json.loads((fit/'FIT_WORK.json').read_text())
    if receipt['failed_fit'] or receipt['final_confirmation_read']: raise ValueError('invalid inherited fit')
    identity={}
    for name in ['model_stage3.pt','actions_stage3.npz']:
        item=receipt['payload_inventory'][name];path=fit/name
        if path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']: raise ValueError('inherited payload changed')
        identity[name]=item
    checkpoint=torch.load(fit/'model_stage3.pt',map_location='cpu',weights_only=True)
    if (checkpoint['method']!='nbo_scalar' or checkpoint['stage']!=3 or
        checkpoint['seed']!=seed or checkpoint['continuation_sha256']!=e.continuation_sha256):
        raise ValueError('checkpoint identity mismatch')
    model=ScalarContinuation(e,int(old['training']['field_width']));model.load_state_dict(checkpoint['model']);model.eval()
    with np.load(fit/'actions_stage3.npz',allow_pickle=False) as f:
        a=f['actions'].copy()
        if not np.array_equal(f['states'],q['states']): raise ValueError('query mismatch')
    g,xa,xb=geometry(e,q,a)
    with torch.no_grad():
        nbo=(model(torch.from_numpy(xa))-model(torch.from_numpy(xb))).numpy().reshape(-1)
    if not np.isfinite(nbo).all(): raise ValueError('nonfinite predictor')
    raw_seed=seed_for(seed,cal,d,'cached-raw-before-audit')
    raw,noise_hash=draw_contrasts(e,xa,xb,raw_seed,max(p['raw_paths'])//2)
    data={'actions':a,'left_post':xa,'right_post':xb,'nbo_prediction':nbo}
    for paths in p['raw_paths']: data[f'raw_{paths}']=raw[:,:paths//2].mean(axis=1)
    data['raw_pair_contrasts']=raw
    dest=out/f's{seed}';dest.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(dest/'PREDICTIONS.npz',**data)
    with (dest/'PREDICTIONS.npz').open('rb') as f: os.fsync(f.fileno())
    record=dict(calibration=cal,dimension=d,seed=seed,query_count=len(a),geometry=g,
        baseline=BASE,protocol_sha256=canonical_hash(p),old_protocol_sha256=canonical_hash(old),
        continuation_sha256=e.continuation_sha256,query_catalog_sha256=q['catalog_sha256'],
        inherited_payload=identity,predictions_sha256=sha(dest/'PREDICTIONS.npz'),
        raw_noise_seed=raw_seed,raw_noise_sha256=noise_hash,raw_pairs=max(p['raw_paths'])//2,
        audit_noise_seed=seed_for(seed,cal,d,'independent-risk-audit'),
        audit_draws_consumed=0,preparation_seconds=time.perf_counter()-start,
        target='uniform action-contrast risk of frozen finite predictions on NBO/reference pairs',
        inference_scope='conditional on inherited fits, selected actions, and the entire new Raw cache')
    write_json(dest/'PRE_AUDIT.json',record)
    return record

def risk_account(record,pred,paths):
    g=record['geometry'];n=pred['nbo_prediction'];r=pred[f'raw_{paths}'];center=I(g['center'])
    difference=I(n)-I(r); coefficient=-2*difference
    executed=-2*(n-r); error=(coefficient-I(executed)).absmax()
    b=I(g['bounds']); cabs=I(coefficient.absmax())
    known=difference*(I(n)+I(r)-2*center)
    bounds=(I(abs(executed))*b*(1+I(pc.gamma(2)))+I(4*np.nextafter(0.,1.))).hi
    bias=(cabs*I(g['evaluation_bias_upper'])+I(error)*b+
        I(pc.gamma(2))*I(abs(executed))*b+I(4*np.nextafter(0.,1.))).hi
    tail=(cabs*I(g['tails'])).hi
    identical=(n==r); bounds[identical]=0.;bias[identical]=0.;tail[identical]=0.
    lo,hi=known.lo.copy(),known.hi.copy();lo[identical]=0.;hi[identical]=0.
    return dict(coefficient=executed,known_lower=lo,known_upper=hi,bounds=bounds,bias=bias,tail=tail)

def prepare_cell(cal,d,out):
    old,p=protocols(); allowed=[x['id'] for x in old['calibrations']]
    if cal not in allowed or d not in old['dimensions']: raise ValueError('unregistered cell')
    out.mkdir(parents=True,exist_ok=True);records=[]
    for s in old['training_streams']['seeds']:
        records.append(prepare_one(cal,d,int(s),out,old,p))
    diagnostics=[]
    # Range-only precision guarantee is computed and durably written BEFORE
    # the first audit draw. It does not assume the realized variance is small.
    alpha=statistics.ConfidenceBudget(p['alpha'],p['event_count']).event_alpha
    total=len(records)*records[0]['query_count']*p['audit_pairs']
    for paths in p['raw_paths']:
        accounts=[]
        for r in records:
            with np.load(out/f's{r["seed"]}'/'PREDICTIONS.npz',allow_pickle=False) as pred:
                accounts.append(risk_account(r,pred,paths))
        bound=max(float(x['bounds'].max()) for x in accounts)
        # Display only: this pre-draw planning radius is NOT used to certify.
        radius=2*bound*math.sqrt(math.log(2/alpha)/(2*total))
        diagnostics.append(dict(raw_paths=paths,observations=total,range_upper=bound,
            range_only_halfwidth=radius,planning_units='squared utility',
            risk_resolution_target=p['risk_margin'],
            allowance_upper=statistics._mean_upper([statistics._mean_upper(x['bias']+x['tail']) for x in accounts]),
            interpretation='approximate pre-draw Hoeffding planning radius; not a confidence endpoint'))
    write_json(out/'PRE_AUDIT_CELL.json',dict(records=len(records),audit_draws_consumed=0,
        protocol_sha256=canonical_hash(p),planning=diagnostics,created_unix_ns=time.time_ns()))
    return records

def run_cell(cal,d,out):
    started=time.perf_counter();old,p=protocols();records=prepare_cell(cal,d,out)
    preparation=time.perf_counter()-started; e=load_economy(old,cal,d)
    for r in records:
        dest=out/f's{r["seed"]}'
        with np.load(dest/'PREDICTIONS.npz',allow_pickle=False) as pred:
            xa=pred['left_post'].copy();xb=pred['right_post'].copy()
        value,noise_hash=draw_contrasts(e,xa,xb,r['audit_noise_seed'],p['audit_pairs'])
        residual=value-np.asarray(r['geometry']['center'])[:,None]
        np.savez_compressed(dest/'AUDIT.npz',residual=residual)
        with (dest/'AUDIT.npz').open('rb') as f: os.fsync(f.fileno())
        write_json(dest/'AUDIT.json',dict(seed=r['seed'],noise_seed=r['audit_noise_seed'],
            noise_sha256=noise_hash,raw_sha256=sha(dest/'AUDIT.npz'),
            observations=int(residual.size),complete=True,predictions_sha256=r['predictions_sha256'],
            pre_audit_receipt_sha256=sha(dest/'PRE_AUDIT.json'),
            parent_pre_audit_cell_sha256=sha(out/'PRE_AUDIT_CELL.json')))
    write_json(out/'CELL_COMPLETE.json',dict(calibration=cal,dimension=d,seeds=[r['seed'] for r in records],
        source_commit=os.getenv('FROZEN_SOURCE_SHA',os.getenv('GITHUB_SHA','local')),protocol_sha256=canonical_hash(p),
        complete=True,preparation_seconds=preparation,total_seconds=time.perf_counter()-started,
        audit_pairs=len(records)*records[0]['query_count']*p['audit_pairs'],
        audit_continuation_paths=4*len(records)*records[0]['query_count']*p['audit_pairs'],
        python=platform.python_version(),numpy=np.__version__,torch=torch.__version__))

def report(root,out):
    old,p=protocols();seeds=list(old['training_streams']['seeds']); rows=[]
    alpha=statistics.ConfidenceBudget(p['alpha'],p['event_count']).event_alpha
    for cal in [x['id'] for x in old['calibrations']]:
        for d in old['dimensions']:
            cell=root/f'{cal}_d{d}';done=json.loads((cell/'CELL_COMPLETE.json').read_text())
            if not done['complete'] or done['seeds']!=seeds or done['protocol_sha256']!=canonical_hash(p):
                raise ValueError('missing or changed cell')
            for paths in p['raw_paths']:
                values={};bounds={};biases={};tails={};noise={};known=[];nclip=0
                for seed in seeds:
                    dest=cell/f's{seed}';r=json.loads((dest/'PRE_AUDIT.json').read_text())
                    audit=json.loads((dest/'AUDIT.json').read_text())
                    if r['protocol_sha256']!=canonical_hash(p) or r['audit_draws_consumed']!=0: raise ValueError('changed preparation')
                    if (r['seed']!=seed or r['calibration']!=cal or r['dimension']!=d or
                        r['audit_noise_seed']!=seed_for(seed,cal,d,'independent-risk-audit') or
                        audit['noise_seed']!=r['audit_noise_seed'] or audit['seed']!=seed or not audit['complete']):
                        raise ValueError('mixed audit identity')
                    for filename,key,receipt in [('PREDICTIONS.npz','predictions_sha256',r),('AUDIT.npz','raw_sha256',audit),
                          ('PRE_AUDIT.json','pre_audit_receipt_sha256',audit)]:
                        if sha(dest/filename)!=receipt[key]:raise ValueError('evidence changed')
                    if sha(cell/'PRE_AUDIT_CELL.json')!=audit['parent_pre_audit_cell_sha256']:raise ValueError('planning changed')
                    with np.load(dest/'PREDICTIONS.npz',allow_pickle=False) as pred:
                        acc=risk_account(r,pred,paths)
                    with np.load(dest/'AUDIT.npz',allow_pickle=False) as ar: residual=ar['residual'].copy()
                    if residual.shape!=(r['query_count'],p['audit_pairs']) or not np.isfinite(residual).all():raise ValueError('partial bank')
                    b=np.asarray(r['geometry']['bounds'])[:,None];clipped=np.clip(residual,-b,b)
                    nclip+=int(np.count_nonzero(residual!=clipped))
                    values[seed]=(acc['coefficient'][:,None]*clipped).reshape(-1)
                    bounds[seed]=float(acc['bounds'].max());biases[seed]=statistics._mean_upper(acc['bias'])
                    tails[seed]=statistics._mean_upper(acc['tail']);noise[seed]=str(audit['noise_seed'])
                    known.append(I(acc['known_lower'],acc['known_upper']))
                result=statistics.finite_stream_mean(values,declared_seeds=seeds,noise_keys=noise,
                    bounds=bounds,biases=biases,clipping_tails=tails,event_alpha=alpha,
                    confirmation_independent_of_selection=True)
                k=pc.mean_i(I(np.concatenate([x.lo for x in known]),np.concatenate([x.hi for x in known])))
                lo=float((k+I(result['lower'])).lo);hi=float((k+I(result['upper'])).hi)
                rows.append(dict(calibration=cal,dimension=d,raw_paths=paths,lower=lo,upper=hi,
                    estimate=float(pc.midpoint(k))+result['raw_mean'],known_lower=float(k.lo),known_upper=float(k.hi),
                    nbo_risk_lower=hi<0,raw_risk_lower=lo>0,
                    material_nbo_risk_reduction=hi < -p['risk_margin'],clipped_residuals=nclip,
                    interval=result,cell_total_seconds=done['total_seconds']))
    if len(rows)!=p['event_count']:raise ValueError('incomplete family')
    write_json(out,dict(schema='nbo-r17-contrast-risk-report-v1',baseline=BASE,
        protocol_sha256=canonical_hash(p),complete=True,event_count=len(rows),alpha=p['alpha'],
        scope=p['target'],joint_with_r16_failure_probability_upper=.06,rows=rows))
    print(json.dumps([{k:r[k] for k in ('calibration','dimension','raw_paths','lower','upper')} for r in rows],indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='cmd',required=True)
    worker=sub.add_parser('cell');worker.add_argument('--cal',required=True);worker.add_argument('--dimension',type=int,required=True);worker.add_argument('--out',type=Path,required=True)
    rep=sub.add_parser('report');rep.add_argument('--root',type=Path,required=True);rep.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.cmd=='cell':run_cell(args.cal,args.dimension,args.out)
    else:report(args.root,args.out)
