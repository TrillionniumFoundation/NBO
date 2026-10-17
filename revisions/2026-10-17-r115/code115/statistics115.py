"""Standard-library, exact-product inference and independent trace accounting.

No production acquisition, Bellman, selection or floating interval code is
imported. Products and gain arithmetic are rational; Decimal transcendental
bounds are rounded conservatively and checked at two working precisions.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import argparse, hashlib, json, math, time
TAU=F(1,256); D=2**40; STAKES=tuple(4**k for k in range(10)); THRESHOLD=16000
PREFIXES=(32,64,128,256,512,1024); TARGETS=(F(1,2**24),F(1,2**22),F(1,2**20),F(1,2**18))
ARMS=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
SERVICES=('compiled','compiled-safe','gain-16'); KEYS=('lower','upper','optimum_lower','loss','width')

def fr(x): return F(x) if isinstance(x,(F,str,int)) else F(float(x))
def read(p): return json.loads(Path(p).read_text())
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def require(ok,msg):
    if not ok: raise ArithmeticError(msg)

def certificate(r,prefix=''):
    lo,hi,opt,gap,width=[fr(r[prefix+k]) for k in KEYS]
    require(lo<=hi and opt<=hi,'certificate ordering')
    require(0<=hi-opt<=gap<=TAU,'original optimum qualification')
    require(0<=hi-lo<=width<=F(1,8192),'original policy width')
    return lo,hi,opt,gap,width

def gain_rows(data,completed):
    require(len(data['rows'])==len(completed['rows']),'matched sample')
    current={}; total={}; checks=0; changes={}
    for row,ctrl in zip(data['rows'],completed['rows']):
        certificate(row);certificate(ctrl);certificate(row,'baseline_');j=row['row'];checks+=15
        require((row['x0'],row['x1'])==(ctrl['x0'],ctrl['x1']),'state identity')
        require(row['completed_baseline_action']==ctrl['action'],'completed incumbent identity')
        for k in KEYS:require(row['baseline_'+k]==ctrl[k],'completed certificate identity');checks+=1
        current[j]={'action':fr(ctrl['action']),**{k:fr(ctrl[k]) for k in KEYS}}
        total[j]=F(0);changes[j]=0
    for t in data['trials']:
        j=t['row'];s=current[j];checks+=6
        require(fr(t['incumbent_action'])==s['action'],'trace action custody')
        require(fr(t['incumbent_lower'])==s['lower'] and fr(t['incumbent_upper'])==s['upper'],'trace interval custody')
        if t.get('skipped',False):
            require(data['service']=='gain-16' and s['loss']<=F(1,65536) and not t['accepted'],'stop authority')
            continue
        lo,hi,opt,gap,width=[fr(t['candidate_'+k]) for k in KEYS]
        require(lo<=hi and 0<=hi-opt<=gap and 0<=hi-lo<=width,'candidate interval arithmetic')
        gate=hi<s['lower'] and gap<=TAU and width<=F(1,8192) and fr(t['candidate_action'])!=s['action']
        require(gate==t['accepted'],'exact strict descent gate')
        if gate:
            total[j]+=s['lower']-hi;changes[j]+=1
            s.update(action=fr(t['candidate_action']),lower=lo,upper=hi,optimum_lower=opt,loss=gap,width=width)
    result=[]
    for row,ctrl in zip(data['rows'],completed['rows']):
        j=row['row'];s=current[j];checks+=10
        require(s['action']==fr(row['action']) and changes[j]==row['safe_changes'],'returned trace')
        for k in KEYS:require(s[k]==fr(row[k]),'returned certificate identity')
        cap=F(1,8)+(fr(row['x0'])+fr(row['x1']))/16
        require(0<=fr(row['action'])<=cap,'original action feasibility')
        require(fr(row['action_distance_upper'])**2>=fr(row['loss']),'outward action distance')
        same=row['action']==ctrl['action'];lo=total[j]
        marginal=F(0) if same else max(F(0),fr(ctrl['lower'])-fr(row['upper']))
        hi=F(0) if same else min(TAU,fr(ctrl['upper'])-fr(row['lower']))
        require(0<=lo<=marginal<=hi<=TAU,'nonnegative original-policy gain account')
        result.append({'row':j,'lower':str(lo),'marginal_lower':str(marginal),'upper':str(hi),
                       'same_action':same,'accepted_updates':changes[j]})
    return result,checks

def product_ge(p,c,k,n):
    """p=prod(1+c*y_i); compare p/(1+c*k/D)^n >= 16000."""
    return (p.numerator << (40*n)) >= THRESHOLD*p.denominator*pow(D+c*k,n)

def integer_hash(v):
    return hashlib.sha256(v.to_bytes(max(1,(v.bit_length()+7)//8),'big')).hexdigest()

def mean_bound(products,n):
    best=0;winner=None;checks=0
    for c,p in zip(STAKES,products):
        if p < THRESHOLD:continue
        lo,hi=0,D
        while lo<hi:
            mid=(lo+hi+1)//2;ok=product_ge(p,c,mid,n);checks+=1
            if ok:lo=mid
            else:hi=mid-1
        if lo>best:best,winner=lo,c
    if not best:return {'n':n,'normalized_dyadic_integer':0,'lower':'0','stake':None,'exact_checks':checks}
    p=products[STAKES.index(winner)]
    require(product_ge(p,winner,best,n),'published rational product witness');checks+=1
    require(best==D or all(not product_ge(p,c,best+1,n) for c,p in zip(STAKES,products)),'maximal dyadic endpoint');checks+=len(STAKES)
    return {'n':n,'normalized_dyadic_integer':best,'lower':str(TAU*F(best,D)),
        'stake':winner,'product_numerator_sha256':integer_hash(p.numerator),
        'product_denominator_sha256':integer_hash(p.denominator),'exact_checks':checks,
        'next_grid_endpoint_rejected':True,'threshold':THRESHOLD}

def infer(values):
    ys=[fr(v)/TAU for v in values];require(all(0<=y<=1 for y in ys),'bounded observations')
    products=[F(1) for c in STAKES];prefixes=[];first={str(t):None for t in TARGETS};checks=0
    bases={(c,t):1+c*t/TAU for c in STAKES for t in TARGETS}
    powers={(c,t):1 for c in STAKES for t in TARGETS}
    for n,y in enumerate(ys,1):
        for h,c in enumerate(STAKES):
            products[h]*=1+c*y
            for target in TARGETS:
                if first[str(target)] is not None:continue
                b=bases[c,target];powers[c,target]*=b.numerator
                p=products[h]
                ok=p.numerator*pow(b.denominator,n)>=THRESHOLD*p.denominator*powers[c,target];checks+=1
                if ok:first[str(target)]={'n':n,'stake':c,'target':str(target),'exact':True}
        if n in PREFIXES:prefixes.append(mean_bound(products,n))
    return {'prefixes':prefixes,'first_crossings':first,'exact_crossing_comparisons':checks,
            'full_sample_executed':True,'shadow_stopping_not_saved_execution':True}

def radius(logarg,denom):
    with localcontext() as c:
        c.prec=90;x=(Decimal(logarg).ln()/Decimal(denom)).sqrt()
        hi=F(x)+F(1,10**75)
    with localcontext() as c:
        c.prec=120;y=(Decimal(logarg).ln()/Decimal(denom)).sqrt()
        require(hi>F(y),'outward concentration radius')
    return hi

def audit_all(out):
    out=Path(out);start=time.perf_counter();checks=0;allrows=0;allslots=0;groups=[]
    for name in ['primary']+[f'timing/{i}' for i in range(7)]:
        m=read(out/name/'MANIFEST.json');loaded={}
        for e in m['records']:
            p=out/e['path'];require(digest(p)==e['sha256'],'measured record hash');checks+=1
            d=read(p);loaded[e['risk_index'],e['arm'],e['service']]=d
            allrows+=len(d['rows']);allslots+=len(d['trials'])
        for i in range(2):
            for arm in ARMS:
                ctrl=loaded[i,arm,'compiled']
                for s in ('compiled-safe','gain-16'):
                    d=loaded[i,arm,s];gain,k=gain_rows(d,ctrl);checks+=k
                    if name=='primary':
                        dest=out/'gains'/f'{i}-{arm}-{s}.json';dump(dest,{'rows':gain})
                        groups.append({'risk_index':i,'arm':arm,'service':s,'gain_path':str(dest.relative_to(out)),
                                       'gain_sha256':digest(dest)})
        for i in range(2):
            for s in SERVICES:
                a,b=loaded[i,'relu',s],loaded[i,'hinge',s]
                require(a['rows']==b['rows'] and a['trials']==b['trials'],'equivalent geometry control');checks+=1
    require(allrows==59904,'all 49152 primary and 10752 timing decisions retained')
    require(allslots==119808,'all attempted or skipped trial slots retained')
    dump(out/'AUDIT115.json',{'status':'passed','checks':checks,'decision_rows':allrows,'trial_slots':allslots,
                            'gain_groups':groups,'seconds':time.perf_counter()-start,'source_sha256':digest(__file__),
                            'scope':'exact stored trace arithmetic; not an independent full risk implementation'})
    return groups

def analysis(out):
    out=Path(out);start=time.perf_counter();groups=audit_all(out);results=[]
    hoeff=TAU*radius(1600,2048)
    for g in groups:
        values=read(out/g['gain_path'])['rows'];vals=[F(r['lower']) for r in values]
        info=infer(vals);mean=sum(vals,F(0))/1024
        marginal=sum(F(r['marginal_lower']) for r in values)/1024
        high=sum(F(r['upper']) for r in values)/1024
        g.update(info,mean_trace_lower=str(mean),mean_marginal_lower=str(marginal),mean_gain_upper=str(high),
                 hoeffding_fixed_n_lower=str(max(F(0),mean-hoeff)),
                 changed_states=sum(not r['same_action'] for r in values),
                 accepted_updates=sum(r['accepted_updates'] for r in values))
        results.append(g);print('INFERENCE',g['risk_index'],g['arm'],g['service'],g['prefixes'][-1]['lower'],flush=True)
    signed=[];rad=TAU*radius(3200,512)
    for i in range(2):
        control=read(out/'primary'/f'{i}-quadratic-compiled.json')['rows']
        for arm in ARMS:
            for s in ('compiled-safe','gain-16'):
                rr=read(out/'primary'/f'{i}-{arm}-{s}.json')['rows'];lo=F(0);hi=F(0);identical=True
                for a,b in zip(rr,control):
                    if a['action']==b['action']:continue
                    identical=False
                    l=max(-TAU,fr(a['lower'])-fr(b['upper']));u=min(TAU,fr(a['upper'])-fr(b['lower']))
                    require(l<=u,'signed original-policy comparison');lo+=l;hi+=u
                signed.append({'risk_index':i,'arm':arm,'service':s,'sample_lower':str(lo/1024),
                    'sample_upper':str(hi/1024),'population_lower':str(max(-TAU,lo/1024-rad)),
                    'population_upper':str(min(TAU,hi/1024+rad)),
                    'all_sample_actions_identical':identical,'radius_retained':True})
    dump(out/'STATISTICS115.json',{'safe':results,'signed_vs_quadratic':signed,'safe_delta':'1/50',
          'signed_delta':'1/50','joint_coverage_lower':'24/25','normalized_grid':'1/1099511627776',
          'safe_hoeffding_radius':str(hoeff),'signed_radius':str(rad),'seconds':time.perf_counter()-start,
          'source_sha256':digest(__file__),'inference_conditional_on_frozen_actors':True})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();analysis(a.output)
