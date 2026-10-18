"""Frozen, fully retained continuous-risk investment experiment.

prepare writes a calibration/actor freeze; evaluate refuses changed source or
models. No evaluation row is opened during preparation or fitting. Repeat
runs are replication of the same stream, not additional economic observations.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,os,pathlib,platform,resource,subprocess,time
import numpy as np
from interval94 import I,up,down
from investment94 import BETA,RADIUS,TERMINAL_TOL,COUNTS,count,terminal_certificate,transition,discrete_avar_interval
from representations94 import fit,Fit
from continuum94 import certify_actor,policy_cost,uniform_residual,strict_tail_cuts,shock_mesh,query
ROOT=pathlib.Path(__file__).resolve().parents[1]
ARMS=('online-risk-dp','quadratic','relu','spline')
LEVELS=(.5,.75)
MARGIN=1/16
SUPPORT_RADIUS=5/64+BETA*(45/32+TERMINAL_TOL)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n');temp.replace(path)
def source_files():
    names=('interval94.py','investment94.py','terminal_controller94.py','representations94.py','continuum94.py','independent94.py','tests94.py','study94.py')
    return {'code/'+name:sha(ROOT/'code'/name) for name in names}|{name:sha(ROOT/name) for name in ('PROTOCOL94.md','AMENDMENT94.md')}
def git_sha():
    try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
    except subprocess.CalledProcessError:return os.environ.get('NBO_SOURCE_COMMIT','local-uncommitted')
def rows(stream,index,n,d=2):
    domain=[2026101394,stream,index]+([d] if stream==4 else [])
    gen=np.random.Generator(np.random.PCG64(np.random.SeedSequence(domain)))
    return gen.integers(0,2**20,size=(n,d),dtype=np.int64)/2**20

def measured(fn,*args,**kwargs):
    before=COUNTS.copy();start=time.perf_counter();out=fn(*args,**kwargs)
    return out,{'seconds':time.perf_counter()-start,'counts':{k:v-before.get(k,0) for k,v in COUNTS.items() if v!=before.get(k,0)}}
def mean_interval(lo,hi):
    b=I(lo,hi).sum()/len(lo);return [float(b.lo),float(b.hi)]
def quantiles(values):
    a=np.asarray(values,dtype=float);return {str(p):float(np.quantile(a,p)) for p in (0,.25,.5,.75,.9,.99,1)}

def evaluate_arm(x,alpha,model,path):
    aa=[];ll=[];uu=[];gg=[];og=[];all_attempts=[];parts=[]
    for start in range(0,len(x),64):
        b=x[start:start+64]
        (a,r,attempts),work=measured(certify_actor,b,alpha,model)
        costs,cwork=measured(policy_cost,I(b),I(a),alpha,128)
        original=r;original_attempts=[];owork=[]
        for bins in ((128,) if model is None else (128,256,512,1024,2048,4096)):
            if model is not None:
                original,ow=measured(query,I(b),I(a),alpha,None,bins);owork.append(ow)
            loss=up(costs.hi-original['lower'])
            original_attempts.append({'bins':bins,'maximum_loss_upper':float(np.max(loss)),'failed':int(np.sum(loss>1/16))})
            if np.all(loss<=1/16):break
        if np.any(loss<0):raise AssertionError('An original-optimum lower bound exceeds the feasible policy upper value')
        aa.extend(a.tolist());ll.extend(costs.lo.tolist());uu.extend(costs.hi.tolist());gg.extend(r['gap'].tolist());og.extend(loss.tolist())
        all_attempts.append(dict(first_row=start,rows=len(b),attempts=attempts,original_optimum_attempts=original_attempts));parts.append({'proposal_and_all_action_certificate':work,'original_complete_policy_evaluation':cwork,'additional_original_optimum_work':owork,'original_lower_witness_reused':model is None})
    lo=np.array(ll);hi=np.array(uu);actions=np.array(aa);gaps=np.array(gg);original_gaps=np.array(og)
    if np.any(~np.isfinite(lo)) or np.any(lo>hi):raise ArithmeticError('Invalid cost enclosure; no row can be removed')
    path.parent.mkdir(parents=True,exist_ok=True);s=time.perf_counter()
    with path.open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['row','x0','x1','action','own_Q_gap_upper','original_optimum_loss_upper','cost_lower','cost_upper'])
        writer.writerows((i,x[i,0],x[i,1],actions[i],gaps[i],original_gaps[i],lo[i],hi[i]) for i in range(len(x)))
    output_seconds=time.perf_counter()-s
    stats={'rows':len(x),'own_Q_target':1/64,'failed_Q_targets':int(np.sum(gaps>1/64)),'original_optimum_target':1/16,'failed_original_optimum_targets':int(np.sum(original_gaps>1/16)),'original_optimum_loss_distribution':quantiles(original_gaps),'gap_distribution':quantiles(gaps),'mean_cost_interval':mean_interval(lo,hi),'cost_width_distribution':quantiles(hi-lo),'raw_sha256':sha(path),'batches':all_attempts,'work_by_batch':parts,'output_seconds':output_seconds}
    return {'actions':actions,'lower':lo,'upper':hi,'stats':stats}

def prepare(out):
    if (out/'CALIBRATION94.json').exists():raise FileExistsError('Do not overwrite a completed calibration freeze')
    beginning=time.perf_counter();frozen={'schema':'NBO-R94-calibration-v1','source_commit':git_sha(),'source_files':source_files(),'evaluation_rows_opened':0,'levels':{},'stream_definition':'PCG64(SeedSequence([2026101394, stream, risk_index]))'}
    for idx,alpha in enumerate(LEVELS):
        folder=out/f'alpha-{idx}';folder.mkdir(parents=True,exist_ok=True)
        x=rows(1,idx,1024)
        labels,lwork=measured(terminal_certificate,I(x),alpha)
        with (folder/'training.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['x0','x1','label_lower','label_upper'])
            w.writerows(zip(x[:,0],x[:,1],labels['lower'],labels['upper']))
        y=labels['lower']+(labels['upper']-labels['lower'])/2
        models={};constructions={}
        for arm in ARMS[1:]:
            obj,fwork=measured(fit,arm,x,y)
            residual,rwork=measured(uniform_residual,obj,alpha,32)
            s=time.perf_counter();dump(folder/f'{arm}.json',obj.to_dict());obj=Fit.from_dict(json.loads((folder/f'{arm}.json').read_text()));loadwrite=time.perf_counter()-s
            models[arm]=obj
            constructions[arm]={'fit':fwork,'uniform_residual':residual,'residual_work':rwork,'serialization_and_reload_seconds':loadwrite,'model_sha256':sha(folder/f'{arm}.json'),'policy_identity':obj.identity(),'fit_record':obj.record}
        cal=rows(2,idx,128);calibrations={}
        for arm in ARMS:
            obj=evaluate_arm(cal,alpha,models.get(arm),folder/f'calibration-{arm}.csv')
            calibrations[arm]=obj['stats']
        selector=min(ARMS,key=lambda a:(sum(calibrations[a]['mean_cost_interval'])/2,a))
        frozen['levels'][str(idx)]={'alpha':alpha,'label_work':lwork,'training_sha256':sha(folder/'training.csv'),'constructions':constructions,'calibration':calibrations,'selected_arm':selector}
        dump(out/'PREPARATION_PROGRESS94.json',frozen)
    supplementary=[]
    for idx,alpha in enumerate(LEVELS):
        for d in (4,8):
            rec,work=measured(terminal_certificate,I(rows(4,idx,16,d)),alpha)
            supplementary.append({'alpha':alpha,'dimension':d,'states':16,'maximum_terminal_gap':float(np.max(rec['gap'])),'work':work,'primary_observations':0})
    frozen['supplementary']=supplementary;frozen['preparation_seconds']=time.perf_counter()-beginning;frozen['counts']=COUNTS.copy();frozen['machine']={'architecture':platform.machine(),'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__}
    dump(out/'CALIBRATION94.json',frozen)
    return frozen

def paired_interval(left,right):
    d=I(left['lower'],left['upper'])-I(right['lower'],right['upper']);n=len(d.lo)
    support=SUPPORT_RADIUS
    # Intersect with a proved support, never with an observed min or max.
    dlo=np.maximum(d.lo,-support);dhi=np.minimum(d.hi,support)
    if np.any(dlo>dhi):raise ArithmeticError('Original-law paired support contradicted')
    mid=dlo+(dhi-dlo)/2;center=float(np.mean(mid))
    radius=I(np.maximum(np.abs(dlo-center),np.abs(dhi-center)))
    # Subtraction used for radius also needs outward rounding.
    radius=I(up(np.maximum(np.abs((I(dlo)-center).lo),np.abs((I(dhi)-center).hi))))
    variance=float((radius.square().sum()/(n-1)).hi)
    first=I(variance)*14/n
    sampling=float((I(up(np.sqrt(first.hi)))+I(2*support)*49/(3*(n-1))).hi)
    mean=I(dlo,dhi).sum()/n
    lower=float(down(mean.lo-sampling));upper=float(up(mean.hi+sampling))
    ho=float((I(support)*2*I(up(np.sqrt(7/(2*n))))).hi)
    return {'rows':n,'difference_mean_numerical_interval':[float(mean.lo),float(mean.hi)],'paired_support':[-support,support],'sample_variance_upper':variance,'log_allowance':7,'family_comparisons':12,'family_confidence':.95,'sampling_radius_empirical_bernstein':sampling,'interval':[lower,upper],'hoeffding_interval':[float(down(mean.lo-ho)),float(up(mean.hi+ho))],'left_superior':upper<0,'right_superior':lower>0,'left_noninferior':upper<MARGIN,'right_noninferior':lower>-MARGIN,'equivalent_within_margin':lower>-MARGIN and upper<MARGIN,'margin':MARGIN}

def screening_benchmark(x,a,alpha):
    start=time.perf_counter();mids,_=shock_mesh(128)
    rec=terminal_certificate(transition(I(x),I(a),I(mids)),alpha)
    pad=I(15)*RADIUS/128;l=(I(rec['lower'])-pad).lo;u=(I(rec['upper'])+pad+TERMINAL_TOL).hi
    construction=time.perf_counter()-start
    s=time.perf_counter();cut=strict_tail_cuts(l,u,alpha);proof=time.perf_counter()-s
    k=int(128*(1-alpha));repeats=32
    full_times=[];pruned_times=[]
    for _ in range(3):
        s=time.perf_counter()
        for __ in range(repeats):full=np.sort(u,axis=-1)[:,-k:]
        full_times.append((time.perf_counter()-s)/repeats)
        s=time.perf_counter()
        for __ in range(repeats):reduced=np.array([np.sort(row[~cuts])[-k:] for row,cuts in zip(u,cut)])
        pruned_times.append((time.perf_counter()-s)/repeats)
        if not np.array_equal(full,reduced):raise AssertionError('Pruning changes the full upper-tail calculation')
    retained=np.sum(~cut,axis=-1)
    return {'rows':len(x),'bins_per_row':128,'candidate_bins':int(u.size),'excluded_bins':int(cut.sum()),'retained_bins':int((~cut).sum()),'retained_distribution':quantiles(retained),'no_cut_rows':int(np.sum(retained==128)),'unpruned_bound_construction_seconds':construction,'strict_cut_proof_seconds':proof,'full_sort_seconds':full_times,'pruned_sort_seconds':pruned_times,'mean_full_bound_and_sort_seconds':construction+float(np.mean(full_times)),'mean_pruned_bound_proof_sort_seconds':construction+proof+float(np.mean(pruned_times)),'sort_repeats_per_timing':32,'timing_replicates':3,'identical_tail_values':True,'new_economic_observations':0,'scope':'Paid original-value bounds then strict whole-bin pruning; extra diagnostic, not a whole-service speedup claim'}

def evaluate(out,tag):
    start=time.perf_counter();freeze=out/'CALIBRATION94.json';frozen=json.loads(freeze.read_text())
    if frozen['source_files']!=source_files():raise RuntimeError('Frozen numerical source changed before evaluation')
    dest=out/f'evaluation-{tag}'
    if (dest/'RESULTS94.json').exists():raise FileExistsError('Retain completed evaluation; use a new explicit replication tag')
    report={'schema':'NBO-R94-evaluation-v1','source_commit':git_sha(),'source_files':source_files(),'calibration_sha256':sha(freeze),'tag':tag,'levels':{},'independent_initial_state_observations':4096,'new_fit_attempts_in_prepare':6,'new_fit_attempts_in_evaluation':0,'machine':{'architecture':platform.machine(),'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__},'scope':'Original two-date scalar-control nested-AVaR investment; initial distribution is declared 20-bit dyadic uniform law'}
    for idx,alpha in enumerate(LEVELS):
        folder=out/f'alpha-{idx}';models={}
        for arm in ARMS[1:]:
            expected=frozen['levels'][str(idx)]['constructions'][arm]['model_sha256']
            if sha(folder/f'{arm}.json')!=expected:raise RuntimeError('Frozen model changed')
            models[arm]=Fit.from_dict(json.loads((folder/f'{arm}.json').read_text()))
        x=rows(3,idx,2048);observations={};arms={}
        for arm in ARMS:
            data,work=measured(evaluate_arm,x,alpha,models.get(arm),dest/f'alpha-{idx}-{arm}.csv')
            observations[arm]=data;arms[arm]={'data':data['stats'],'complete_evaluation_work':work}
            dump(dest/'PROGRESS94.json',{'alpha':alpha,'completed_arms':arms,'calibration_sha256':sha(freeze)})
        pairs={a+' minus '+b:paired_interval(observations[a],observations[b]) for a,b in itertools.combinations(ARMS,2)}
        screens={}
        # Every arm is included; fixed first 32 rows are diagnostics, not a
        # selected economic subgroup or additional primary observations.
        for arm in ARMS:
            screens[arm]=screening_benchmark(x[:32],observations[arm]['actions'][:32],alpha)
        report['levels'][str(idx)]={'alpha':alpha,'selected_arm':frozen['levels'][str(idx)]['selected_arm'],'arms':arms,'pairwise':pairs,'screening':screens}
        dump(dest/'PROGRESS94.json',report)
    report['total_evaluation_seconds']=time.perf_counter()-start;report['counts']=COUNTS.copy();report['maximum_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report['all_first_date_certificates_pass']=all(a['data']['failed_Q_targets']==0 and a['data']['failed_original_optimum_targets']==0 for lev in report['levels'].values() for a in lev['arms'].values())
    dump(dest/'RESULTS94.json',report)
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('prepare','evaluate'));p.add_argument('--output',type=pathlib.Path,default=ROOT/'results94');p.add_argument('--tag',default='primary')
    a=p.parse_args();start=time.perf_counter();result=prepare(a.output) if a.mode=='prepare' else evaluate(a.output,a.tag)
    print(json.dumps({'mode':a.mode,'seconds':time.perf_counter()-start,'machine':platform.machine(),'output':str(a.output),'success':True}))
if __name__=='__main__':main()
