"""Exact deterministic outer bounds and separately feasible upper policies.
The installed policies are frozen R34 inputs. No historical run claim is reused.
Run from repository root: python revisions/2026-09-24-r38/replication/primary.py
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import gzip,json,hashlib,time,platform,resource,sys
import kernel as k
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'2026-09-24-r34'
OUT=ROOT/'results'
ZERO,ONE=F(0),F(1)

def encoded(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
def digest(d):return hashlib.sha256(encoded(d)).hexdigest()
def save(path,d):
    path.parent.mkdir(parents=True,exist_ok=True)
    b=encoded(d)
    if path.suffix=='.gz':
        with path.open('wb') as fp:
            with gzip.GzipFile(fileobj=fp,mode='wb',mtime=0) as gz:gz.write(b)
    else:path.write_bytes(json.dumps(d,sort_keys=True,indent=2).encode()+b'\n')
    return hashlib.sha256(b).hexdigest()
def load(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def dumps(fs):return [f.dump() for f in fs]
def bounds(V,J):return max(k.linear_comb([v,j],[ONE,-ONE]).extent()[1] for v,j in zip(V,J))
def outer(L,U,raw,eps):
    allowed=[[k.threshold(k.linear_comb([L[t],q],[ONE,-ONE]),eps) for q in k.q_functions(U[t+1])] for t in range(len(raw))]
    policy,B=k.repair(raw,allowed)
    return B,policy

def upper(V,raw,eps,penalty):
    T=len(raw);J=[None]*(T+1);C=[None]*(T+1);policy=[None]*T
    J[T]=k.affine(F(1,2));C[T]=k.affine()
    for t in reversed(range(T)):
        qj=k.q_functions(J[t+1]);qc=[k.linear_comb([q,k.intervention(raw[t],a)],[ONE,ONE]) for a,q in enumerate(k.q_functions(C[t+1],False))]
        allowed=[k.threshold(k.linear_comb([V[t],q],[ONE,-ONE]),eps) for q in qj]
        obj=[k.linear_comb([c,j],[ONE,-penalty]) for c,j in zip(qc,qj)]
        try:_,policy[t]=k.envelope(obj,False,allowed)
        except ValueError as e:return None,{'status':'empty_feasible_action_set','date':t,'reason':str(e)}
        J[t]=k.select(qj,policy[t]);C[t]=k.select(qc,policy[t])
    return (policy,J,C),{'status':'feasible','regret':str(bounds(V,J)),'cost':str(C[0].integral())}

def run():
    OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter();values={};operating=[]
    for T in (4,8,12):
        V,p,stat=k.exact_dp(T);values[T]=(V,p)
        operating.append({'T':T,**stat,'process_highwater_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    old_restart=load(OLD/'results/restart_closure.json')['outcomes']
    old_map={(int(o['T']),o['proposal'],o['epsilon']):o for o in old_restart}
    results=[];failures=[]
    paths=sorted((OLD/'results/certificates').glob('*_primal_dual.json.gz'))
    for path in paths:
        tic=time.perf_counter();base=load(path);T=base['T'];eps=F(base['epsilon']);raw=list(map(k.PW.load,base['raw']));V,pstar=values[T]
        B,bpolicy=outer(V,V,raw,eps);lower_seconds=time.perf_counter()-tic
        tic=time.perf_counter();U=list(map(k.PW.load,base['U']));b=ZERO;L=[None]*(T+1);L[T]=U[T]
        for t in reversed(range(T)):
            b=F(base['defects'][t])+k.BETA*b;L[t]=k.linear_comb([U[t]],[ONE],b=-b)
        Bsafe,psafe=outer(L,U,raw,eps);safe_seconds=time.perf_counter()-tic
        tic=time.perf_counter();cand=[];attempts=[]
        for name,policy in [('inherited_R34',list(map(k.PW.load,base['policy']))),('necessary_selector',bpolicy),('operating_optimal',pstar)]:
            J=k.evaluate(policy);C=k.evaluate(policy,raw);reg=bounds(V,J)
            attempts.append({'candidate':name,'regret':str(reg),'cost':str(C[0].integral()),'status':'feasible' if reg<=eps else 'infeasible'})
            if reg<=eps:cand.append((C[0].integral(),name,policy,J,C))
        for pen in (ZERO,ONE,F(4),F(16)):
            triple,stat=upper(V,raw,eps,pen);attempts.append({'candidate':'backward_penalty_'+str(pen),**stat})
            if triple is not None:
                pol,J,C=triple;cand.append((C[0].integral(),'backward_penalty_'+str(pen),pol,J,C))
        cost,name,policy,J,C=min(cand,key=lambda z:(z[0],z[1]));upper_seconds=time.perf_counter()-tic
        lower=B[0].integral();safelower=Bsafe[0].integral()
        assert ZERO<=safelower<=lower<=cost
        rawJ=k.evaluate(raw);preserve=min(k.linear_comb([j,r],[ONE,-ONE]).extent()[0] for j,r in zip(J,rawJ))
        difference=[k.linear_comb([c,b],[ONE,-ONE]) for c,b in zip(C,B)]
        pointwise=all(d.extent()==(ZERO,ZERO) for d in difference)
        old=old_map[(T,base['proposal'],base['epsilon'])]
        obj={'schema':'NBO-R38-primary-v1','model':k.model(),'T':T,'epsilon':str(eps),'proposal':base['proposal'],
          'policy_class':'deterministic_Markov','constraint':'all_state_all_restart','objective':'uniform_initial_integrated_discounted_revision_cost',
          'base_file':str(path.relative_to(ROOT.parents[1])),'base_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'raw':dumps(raw),'raw_sha256':digest(base['raw']),'V':dumps(V),'operating_policy':dumps(pstar),
          'lower':dumps(B),'lower_policy':dumps(bpolicy),'lower_sha256':digest(dumps(B)),
          'U':dumps(U),'L':dumps(L),'defects':base['defects'],'gamma':base['gamma'],
          'safe_lower':dumps(Bsafe),'safe_lower_policy':dumps(psafe),
          'policy':dumps(policy),'policy_sha256':digest(dumps(policy)),'J':dumps(J),'C':dumps(C),
          'lower_integral':str(lower),'upper_integral':str(cost),'safe_lower_integral':str(safelower),
          'operating_regret':str(bounds(V,J)),'exact_integrated':lower==cost,'exact_pointwise':pointwise,'selected':name}
        filename=path.name.replace('_primal_dual','_deterministic');ph=save(OUT/'primary'/filename,obj)
        row={key:obj[key] for key in ('T','epsilon','proposal','policy_class','objective','lower_integral','upper_integral','safe_lower_integral','operating_regret','exact_integrated','exact_pointwise','selected','policy_sha256','raw_sha256','lower_sha256')}
        row.update({'proof_file':'primary/'+filename,'proof_sha256':ph,'gap':str(cost-lower),'witness_lower_improvement':str(lower-safelower),
          'inherited_randomized_lower':old['new_global_lower'],'inherited_upper':old['upper_cost'],'upper_improvement':str(F(old['upper_cost'])-cost),
          'preservation_margin':str(preserve),'preservation_certified':preserve>=0,'attempts':attempts,
          'necessary_lower_seconds':lower_seconds,'safe_lower_seconds':safe_seconds,'upper_portfolio_seconds':upper_seconds,
          'max_lower_pieces':max(len(x.ab) for x in B),'max_upper_cost_pieces':max(len(x.ab) for x in C),
          'max_bits':max(x.bits() for x in V+B+C+J),'process_highwater_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        results.append(row);print(T,base['proposal'],str(eps),'exact',lower==cost,'cost',float(cost),'gap',float(cost-lower),flush=True)
        save(OUT/'primary_progress.json',{'outcomes':results})
    assert len(results)==42
    summary={'schema':'NBO-R38-primary-ledger-v1','outcomes':results,'operating_solves':operating,'failures':failures,
      'cases':len(results),'exact_integrated':sum(r['exact_integrated'] for r in results),
      'positive_cost_exact':sum(r['exact_integrated'] and F(r['upper_integral'])>0 for r in results),
      'exact_pointwise':sum(r['exact_pointwise'] for r in results),'seconds':time.perf_counter()-start,
      'python':sys.version,'platform':platform.platform(),'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'accounting':'Exact V charged once per horizon. Frozen R34 proposals and prior bounds are inherited; no neural training is claimed. Candidate failures retained. Verifier separately timed.'}
    save(OUT/'primary.json',summary)
    print({k:v for k,v in summary.items() if k not in ('outcomes','operating_solves')},flush=True)
if __name__=='__main__':run()
