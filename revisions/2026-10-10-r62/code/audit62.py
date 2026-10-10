"""Offline R62 replay. No fitting, new paths, or replacement service clocks.

All recorded nodal decisions, feasibility, policy-error recursions and cost
interval arithmetic are checked. A deterministic node subset reintegrates
primitive query endpoints; full reference integration is not silently claimed.
"""
from pathlib import Path
from fractions import Fraction as F
import itertools,json,time
import numpy as np
import core62 as c
import science62 as s
R=c.R

def read(path):return json.loads(Path(path).read_text())
def same(a,b,why):c.need(np.array_equal(a,b),why)
def check_ci(new,old,why):
    for key in ('interval_exact','endpoint_sha256','sign','support_exact'):
        c.need(new[key]==old[key],why+' '+key)

def main():
    start=time.perf_counter();fz=s.verify();execution=read(R/'audit/EXECUTION62.json');c.need(execution['status']=='executed' and execution['source_freeze_sha256']==fz,'Incomplete science')
    source=read(R/'audit/PREPARATION62.json')
    for name,h in source['protected_sha256'].items():c.need(c.digest(R/name)==h,'Predecessor changed: '+name)
    tasks=[];nodal=0;inference=0;primitive_queries=0;witness_changes=0
    for d,m,T,ladder,A,q in c.TASKS:
        name=c.key(d,m,T);folder=R/'results62'/name;summary=read(folder/'summary.json')
        c.need(summary['source_freeze_sha256']==fz and summary['ladder']==list(ladder),'Task protocol identity')
        proposals={};part=c.n.Partition(d,32,551)
        for kind,seed in itertools.product(('relu','quadratic'),c.SEEDS):
            key=f'{kind}-{seed}';path=folder/'proposals'/(key+'.json');record=read(path)
            c.need(c.digest(path)==summary['proposal_record_sha256'][key],'Fitting record identity')
            c.need(record['partition']==part.payload() and record['seed']==seed,'Generator-independent partition/seed')
            actions=np.array(record['actions']);c.need(actions.shape==(T,32,m),'Coarse actor shape')
            proposals[key]=dict(partition=part,actions=actions)
        targets={'common':[]};last_policies={};rung_facts=[]
        for sub in ladder:
            dest=folder/f'n{sub}';ref=read(dest/'reference.json');c.need(c.digest(dest/'reference.npz')==ref['raw_sha256'],'Reference raw identity')
            const=c.constants(d,m,T,sub,A,q);c.need(c.const_payload(const)==ref['constants'],'Analytic constants')
            with np.load(dest/'reference.npz') as z:arr={k:z[k] for k in z.files}
            for t in range(T):
                expected=np.maximum(0.,(c.I.point(arr['lattice_min_lower'][t])-c.rat(const['action'][t])).lo)
                same(expected,arr['lower'][t],'Continuous-action lower allowance')
            c.need(np.all(arr['lower']<=arr['upper']),'Reference bracket order')
            same(arr['selected_upper'],arr['upper'],'Actual common selected Q upper')
            cert,_=c.certificate(arr['policy'],arr['selected_upper'],arr['lower'],d,m,T,sub,A,q)
            c.need(cert==ref['policy_certificate'],'Common whole-policy recursion')
            for first,last,points in c.grid(d,sub):
                cap=c.cap_points(points)
                c.need(np.all(arr['policy'][:,first:last]>=0) and np.all(arr['policy'][:,first:last].sum(axis=-1)<=cap),'Whole nodal common feasibility')
            # Reintegrate a fixed, outcome-independent set of complete nodal
            # common menus. Exact equality checks the same arithmetic algorithm.
            ids=sorted({0,ref['nodes']//3,ref['nodes']//2,ref['nodes']-1})
            pts=[]
            for ix in ids:
                z=ix;x=np.empty(d)
                for j in reversed(range(d)):x[j]=(z%(sub+1))/sub;z//=sub+1
                pts.append(x)
            pts=np.array(pts);cap=c.cap_points(pts)
            for t in range(T):
                nxt=None if t==T-1 else (c.Table(arr['lower'][t+1],d,sub),c.Table(arr['upper'][t+1],d,sub))
                lows=np.full(len(ids),np.inf);ups=lows.copy();selected=np.zeros((len(ids),m))
                for frac in c.fractions_menu(m,A):
                    aa=c.I.point(cap[:,None]*np.array(frac));v=c.qbound(c.I.point(pts),aa,t,T,q,m,const,nxt)
                    lows=np.minimum(lows,v.lo);take=v.hi<ups;ups[take]=v.hi[take];selected[take]=aa.lo[take];primitive_queries+=len(ids)
                same(lows,arr['lattice_min_lower'][t,ids],'Primitive lower-node reintegration')
                same(ups,arr['upper'][t,ids],'Primitive upper-node reintegration')
                same(selected,arr['policy'][t,ids],'Primitive common selection')
            targets['common'].append((sub,cert['maximum_date_gap_upper']));last_policies={'common':arr['policy']};row=dict(n=sub,common_gap=cert['maximum_date_gap_upper'],methods={})
            for key,proposal in proposals.items():
                record=read(dest/(key+'.json'));path=dest/(key+'.npz');c.need(c.digest(path)==record['raw_sha256'],'Fitted-policy array identity')
                with np.load(path) as z:pa={k:z[k] for k in z.files}
                for t in range(T):
                    for first,last,points in c.grid(d,sub):same(c.transferred_actions(proposal,points,t),pa['pure'][t,first:last],'Every actual fitted nodal transfer')
                    take=pa['pure_upper'][t]<arr['upper'][t]
                    same(np.where(take[:,None],pa['pure'][t],arr['policy'][t]),pa['guarded'][t],'Every guarded nodal action')
                    same(np.minimum(arr['upper'][t],pa['pure_upper'][t]),pa['guarded_upper'][t],'Every guarded Q upper')
                    c.need(int(take.sum())==record['counts'][t]['additional_witness_nodes'],'Witness contribution count')
                    witness_changes+=int(take.sum());nodal+=2*ref['nodes']
                    nxt=None if t==T-1 else (c.Table(arr['lower'][t+1],d,sub),c.Table(arr['upper'][t+1],d,sub))
                    v=c.qbound(c.I.point(pts),c.I.point(pa['pure'][t,ids]),t,T,q,m,const,nxt)
                    same(v.hi,pa['pure_upper'][t,ids],'Primitive fitted-node Q reintegration');primitive_queries+=len(ids)
                for variant in ('pure','guarded'):
                    ci,_=c.certificate(pa[variant],pa[variant+'_upper'],arr['lower'],d,m,T,sub,A,q)
                    c.need(ci==record[variant+'_certificate'],'Fitted actual-policy recursion')
                    k=key+'-'+variant;targets.setdefault(k,[]).append((sub,ci['maximum_date_gap_upper']));last_policies[k]=pa[variant]
                    row['methods'][k]=ci['maximum_date_gap_upper']
            nodal+=T*ref['nodes'];rung_facts.append(row)
        last_policies['zero']=np.zeros_like(last_policies['common'])
        for key,pol in last_policies.items():
            with np.load(folder/'returned'/(key+'.npz')) as z:same(pol,z['policy'],'Returned actor is actual final-rung actor')
        for key,rows in targets.items():
            for tol,old in zip(c.TOLS,summary['targets'][key]):
                hit=next((sub for sub,bound in rows if F(bound)<=tol),None)
                c.need(old['tolerance']==str(tol) and old['first_n']==hit and old['status']==('attained' if hit else 'budget_exhausted'),'Original-optimum first crossing')
        costpath=folder/'costs.json';cost=read(costpath);clock=read(folder/'clock.json')
        c.need(c.digest(costpath)==summary['costs_sha256']==clock['costs_sha256'],'Cost summary identity')
        c.need(c.digest(folder/'path-endpoints.npz')==cost['raw_sha256'],'Cost endpoints identity')
        c.need(cost['paths']==s.PATHS and cost['family_maximum']==s.FAMILY,'Inference family contract')
        with np.load(folder/'path-endpoints.npz') as z:
            lo=z['lower'];hi=z['upper'];c.need(lo.shape==hi.shape==(len(cost['unique_policy_keys']),s.PATHS),'Path endpoint shape')
            c.need(np.all(lo<=hi) and np.isfinite(lo).all() and np.isfinite(hi).all(),'Finite ordered path endpoints')
            H=c.support(T);index={key:cost['unique_policy_keys'].index(cost['aliases'][key]) for key in cost['policy_keys']}
            for key,old in cost['absolute'].items():
                c.need(s.array_hash(last_policies[key])==cost['policy_sha256'][key],'Actual inference-policy identity')
                i=index[key];check_ci(s.endpoint_record(lo[i],hi[i],F(0),H),old,'Marginal interval');inference+=1
            for key,old in cost['contrasts'].items():
                i=index[old['left']];j=index[old['right']]
                if i==j:c.need(old['interval_exact']==['0','0'] and old['identity'],'Policy identity interval')
                else:
                    val=c.I(lo[i],hi[i])-c.I(lo[j],hi[j]);check_ci(s.endpoint_record(val.lo,val.hi,-H,H),old,'Paired policy-cost interval')
                inference+=1
        work=summary['full_catalogue_release_work_seconds'];final=rung_facts[-1]
        signs={}
        for kind in ('relu','quadratic'):
            for variant in ('pure','guarded'):
                vals=[cost['contrasts'][f'{kind}-{seed}-{variant}-minus-common'] for seed in c.SEEDS]
                signs[kind+'-'+variant]={z:sum(v['sign']==z for v in vals) for z in ('negative','positive','zero','unresolved')}
        tasks.append(dict(task=name,d=d,m=m,T=T,rungs=rung_facts,targets=summary['targets'],full_catalogue_release_work_seconds=work,costs=cost,cost_classifications=signs,reference_cumulative_seconds=summary['reference'][-1]['cumulative_reference_seconds'],peak_process_rss_kib=summary['peak_rss_kib']))
    result=dict(status='passed',source_freeze_sha256=fz,baseline_commit=source['baseline_commit'],controlling_review_commit=source['review_commit'],protected_predecessor_files=len(source['protected_sha256']),tasks=tasks,checked_nodal_action_records=nodal,reintegrated_primitive_point_action_queries=primitive_queries,checked_interval_records=inference,additional_witness_node_cases=witness_changes,fitting_services=execution['primitive_fitted_services'],new_production_path_rows=execution['independent_path_rows_under_declared_model'],audit_new_fits=0,audit_new_paths=0,elapsed_replay_seconds=time.perf_counter()-start,scope='Exhaustive stored node-action transfer, guarded selection, feasibility, certificate recursion and interval-statistic replay. Four fixed vertices per rung reintegrate all common menus and every fitted proposal. No claim of independent full-domain integration or independent proof of the regularity theorem.')
    c.save(R/'audit/SCIENCE_REPLAY62.json',result)
    print(json.dumps({k:result[k] for k in ('status','checked_nodal_action_records','reintegrated_primitive_point_action_queries','checked_interval_records','additional_witness_node_cases','fitting_services','new_production_path_rows','elapsed_replay_seconds')},indent=2),flush=True)
if __name__=='__main__':main()
