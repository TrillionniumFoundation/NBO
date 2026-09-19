"""R19 scientific generation. Never rewrites canonical inputs or historical results.

The producer proposes witnesses. verify.py independently checks them without
importing this module, Engine, or the proposal evaluation routine.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, resource, sys, time
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'replication/r19/output'
sys.path.insert(0,str(ROOT/'replication/r13'))
from canonical import load
from engine import Engine, SIGNS, EPS
from certified_arithmetic import derive, positive_witness
import proposal_benchmark as pb


def put(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')


def ratio(q): return str(q.numerator)+'/'+str(q.denominator)


def analytic():
    # Positive rational series; the checker uses a different truncation and
    # independently checks the analytic inequalities rather than these decimals.
    m=40
    lo=2*sum((Q(1,3)**(2*j+1)/Q(2*j+1) for j in range(m)),Q(0))
    hi=lo+2*Q(1,3)**(2*m+1)/(Q(2*m+1)*(1-Q(1,9)))
    c0=Q(1,2); ca=(lo/2,hi/2); fa=Q(9,25); f0=Q(51,100); eta=Q(1,10**6)
    pa=(1-ca[1]-fa*fa/50,1-ca[0]-fa*fa/50)
    p0=1-c0-f0*f0/50
    robust=1-eta/(fa-ca[1])-ca[1]-fa*fa/50-eta
    obj=dict(schema='nbo-r19-analytic-v1',log2=[ratio(lo),ratio(hi)],
      threshold_adjustment=[ratio(x) for x in ca],threshold_no_adjustment=ratio(c0),
      fee_adjustment=ratio(fa),fee_no_adjustment=ratio(f0),eta=ratio(eta),
      surplus_adjustment=[ratio(x) for x in pa],surplus_no_adjustment=ratio(p0),
      robust_adjustment_lower=ratio(robust),robust_decision_margin_lower=ratio(robust-p0),
      residuals={'adjustment':'identically zero','no_adjustment':'identically zero'},
      scope='Analytic Brownian quadratic benchmark only; not a transfer of the CRRA arrays.')
    put(OUT/'continuous_benchmark.json',obj)
    # Exact economic information fixtures, including the adversarial-noise boundary.
    fixtures=[]
    for k in (2,3,5):
      weights=[Q(i+1,k) for i in range(k)]; rho=min(weights); c=rho/3; h=Q(2,5)
      axis=[]
      for i in range(k):
        for a in (-3,-1,0,1,3):
          t=[Q(0)]*k;t[i]=Q(a)
          v1=max(t);v0=max(Q(0),v1);axis.append([i,a,ratio(v1),ratio(v0)])
      fixtures.append(dict(k=k,weights=[ratio(x) for x in weights],safe=ratio(c),
        axis_queries=axis,joint_query=[ratio(-h*x) for x in weights],
        joint_values=[ratio(-h*rho),'0/1'],minimax_regret=ratio(c*(rho-c)/rho),
        noise_boundary=ratio(h*rho/2)))
    put(OUT/'theorem_fixtures.json',dict(schema='nbo-r19-theorems-v1',information=fixtures,
      global_loss_examples={'two_local_losses':'2/100','global_budget':'1/100',
        'rare_probability':'1/100','rare_local_loss':'1/1','rare_total_loss':'1/100'}))


def feasible_first(eng,q,adj,sign):
    ids=np.flatnonzero(eng.first_mask(adj,sign,.8,.5));i=int(ids[np.argmax(q[ids])])
    if sign=='positive':return positive_witness(eng.fm,q,i,.8,adj,1e-10)
    return dict(indices=[i],weights=[1.],action=eng.fm.actions[i].tolist(),value=float(q[i]),
      positivity_margin=0.,closure_value=float(q[i]),closure_gap=0.,attained=True)


def graph_zero(eng,v,lam,d,F,adj,sign):
    # A 4*EPS supergraph includes every exactly optimal action. The arithmetic
    # ceiling EPS is independently DERIVED before this routine is used.
    fq=(1-lam)*eng.fq(0,v[1],d)+lam*eng.fq(1,v[1],d)
    fm=eng.first_mask(adj,sign,.8,.5)
    first=np.flatnonzero(fm & (fq>=fq[fm].max()-4*EPS))
    reached=np.zeros(eng.S,bool)
    for k,weight in ((0,1-lam),(1,lam)):
      if weight:
        z=eng.fm.rows[k][first];reached[z.indices[z.data>0]]=True
    counts=[];nm=len(eng.b.e[0].menu)
    for n in range(1,eng.N):
      q=(1-lam)*eng.q(0,n,v[n+1],d,F)+lam*eng.q(1,n,v[n+1],d,F)
      allow=eng.mask(n,adj,1) & (q>=v[n,:,None]-4*EPS)
      counts.append(int(reached.sum()))
      if np.any(reached & allow[:,eng.stop]):return False,counts
      nxt=np.zeros(eng.S,bool)
      for k,weight in ((0,1-lam),(1,lam)):
        if not weight:continue
        for z,offset in ((eng.b.e[k].common,0),(eng.b.e[k].extra[n],nm)):
          ss,aa=np.where(reached[:,None] & allow[:,offset:offset+z.na])
          rows=ss*z.na+aa
          if len(rows):
            mat=z.matrix[rows];nxt[mat.indices[mat.data>0]]=True
      reached=nxt
    return True,counts


def enforcement(eng):
    lam=.125;d=.42425;rows=[];archive={}
    for adj in (True,False):
      vi,pi,fi=eng.solve(lam,d,0.,adj,8)
      eligible=np.flatnonzero(~eng.b.e[0].boundary)
      uniform=max(0.,max(float(np.max(eng.b.terminal[eligible]-vi[n,eligible])) for n in range(1,8)))
      key=str(int(adj));archive[key+'.infinite.values']=vi;archive[key+'.infinite.policy']=pi
      for sign in SIGNS:
        low=0.;high=1.;vl,pl,fl=eng.solve(lam,d,low,adj,1)
        ql=(1-lam)*eng.fq(0,vl[1],d)+lam*eng.fq(1,vl[1],d)
        wl=feasible_first(eng,ql,adj,sign)
        if wl['value']-fi[sign][0]<=2*EPS:raise ValueError('initial lower fee is not a strict witness')
        vh,ph,fh=eng.solve(lam,d,high,adj,1)
        ok,counts=graph_zero(eng,vh,lam,d,high,adj,sign)
        if not ok:raise ValueError('fee ceiling lacks a zero-surrender graph certificate')
        iterations=0
        while high-low>1/4096 and iterations<20:
          mid=(low+high)/2;vm,pm,fm=eng.solve(lam,d,mid,adj,1)
          qm=(1-lam)*eng.fq(0,vm[1],d)+lam*eng.fq(1,vm[1],d)
          wm=feasible_first(eng,qm,adj,sign)
          if wm['value']-fi[sign][0]>2*EPS:
            low=mid;vl,pl,fl,wl=vm,pm,fm,wm
          else:
            good,cc=graph_zero(eng,vm,lam,d,mid,adj,sign)
            if good:high=mid;vh,ph,fh,counts=vm,pm,fm,cc
            else:break
          iterations+=1
        tag=key+'.'+sign
        archive[tag+'.lower.policy']=pl
        archive[tag+'.upper.values']=vh
        archive[tag+'.upper.policy']=ph
        qinf=(1-lam)*eng.fq(0,vi[1],d)+lam*eng.fq(1,vi[1],d)
        wi=feasible_first(eng,qinf,adj,sign)
        vc,pc,fc=eng.solve(lam,d,.765,adj,1)
        qc=(1-lam)*eng.fq(0,vc[1],d)+lam*eng.fq(1,vc[1],d)
        wc=feasible_first(eng,qc,adj,sign);zc,cnt=graph_zero(eng,vc,lam,d,.765,adj,sign)
        archive[tag+'.common.values']=vc;archive[tag+'.common.policy']=pc
        rows.append(dict(id=tag,adjustment=adj,sign=sign,initial_fee_bracket=[low,high],
          uniform_fee_bracket=[max(0.,uniform-EPS),uniform+EPS],
          no_surrender_value_bracket=[wi['value']-EPS,fi[sign][0]+EPS],
          lower_witness=wl,no_surrender_witness=wi,
          lower_strict_gain=wl['value']-fi[sign][0]-2*EPS,
          upper_graph_zero=True,upper_reached_counts=counts,iterations=iterations,
          common_fee=.765,common_fee_graph_zero=zc,common_fee_witness=wc,
          common_fee_option_bracket=[max(0.,wc['value']-fi[sign][0]-2*EPS),
            max(0.,fc[sign][0]-wi['value']+2*EPS)]))
        print('ENFORCEMENT',tag,low,high,'uniform',uniform,flush=True)
    np.savez_compressed(OUT/'enforcement_witness.npz',**archive)
    put(OUT/'enforcement.json',dict(schema='nbo-r19-enforcement-v1',law=lam,benefit=d,
      arithmetic_allowance=EPS,rows=rows,scope='Frozen array target, eight dates. Upper endpoints use an all-optimal-action supergraph with structural zero reachable surrender. Lower endpoints use feasible strict payoff improvements. Positive closure bounds are not asserted to attain their supremum.'))


def proposals(eng):
    archive={};rows=[];fits=[];laws=(0.,.125,1.);seeds=(1901,1902,1903)
    for adj in (True,False):
      eng.cache.clear();t=time.perf_counter()
      anchors=[eng.solve(lam,.42425,.85,adj,1)[1].copy() for lam in (.12,.13)]
      teacher=time.perf_counter()-t
      X=np.concatenate([pb.features(eng,lam) for lam in (.12,.13)])
      targets=np.concatenate([p[1:].ravel() for p in anchors]);classes,y=np.unique(targets,return_inverse=True)
      phi=pb.polynomial(X);t=time.perf_counter()
      beta=np.linalg.solve(phi.T@phi+1e-5*np.eye(phi.shape[1]),phi.T@np.eye(len(classes))[y])
      poly_seconds=time.perf_counter()-t;models={}
      for seed in seeds:
        t=time.perf_counter();w,loss=pb.train(X,y,len(classes),45,seed);seconds=time.perf_counter()-t
        models[seed]=(w,seconds)
        for i,a in enumerate(w):archive[f'{int(adj)}.seed{seed}.weight{i}']=a
        fits.append(dict(adjustment=adj,seed=seed,training_seconds=seconds,
          teacher_seconds=teacher,rows=len(X),classes=len(classes),epochs=45,
          initial_loss=loss[0],final_loss=loss[-1],parameter_bytes=sum(a.nbytes for a in w)+classes.nbytes))
      archive[f'{int(adj)}.classes']=classes;archive[f'{int(adj)}.polynomial']=beta
      for i,p in enumerate(anchors):archive[f'{int(adj)}.anchor{i}']=p
      for lam in laws:
        eng.cache.clear();t=time.perf_counter();vr,pr,fr=eng.solve(lam,.42425,.85,adj,1);reference=time.perf_counter()-t
        archive[f'{int(adj)}.{lam}.reference']=vr
        for method,seed in [('nearest',None),('polynomial',None),('bank',None)]+[('neural',s) for s in seeds]:
          t=time.perf_counter()
          if method=='nearest':pols=[anchors[int(lam>.125)]];training=0.;params=sum(a.nbytes for a in anchors)
          elif method=='polynomial':pols=[pb.feasible(eng,pb.polynomial(pb.features(eng,lam))@beta,classes,adj)];training=poly_seconds;params=beta.nbytes+classes.nbytes
          elif method=='bank':pols=anchors;training=0.;params=sum(a.nbytes for a in anchors)
          else:
            w,training=models[seed];pols=[pb.feasible(eng,pb.scores(pb.features(eng,lam),w),classes,adj)];params=sum(a.nbytes for a in w)+classes.nbytes
          proposal=time.perf_counter()-t;t=time.perf_counter()
          vals=[pb.value(eng,p,lam,adj) for p in pols];evaluation=time.perf_counter()-t
          witnesses={};tag=f'{int(adj)}.{lam}.{method}.{seed}'
          for sign in SIGNS:
            ii=max(range(len(vals)),key=lambda i:vals[i][sign]['value'])
            witnesses[sign]=vals[ii][sign];archive[tag+'.policy.'+sign]=pols[ii]
          rows.append(dict(id=tag,adjustment=adj,law=lam,method=method,seed=seed,
            proposal_seconds=proposal,evaluation_seconds=evaluation,
            reference_seconds=reference,teacher_seconds=teacher,training_seconds=training,
            online_with_reference_seconds=proposal+evaluation+reference,
            parameter_bytes=params,lower_witnesses=witnesses,
            reference_values={s:fr[s][0] for s in SIGNS},
            gaps={s:max(0.,fr[s][0]-witnesses[s]['value'])+2*EPS for s in SIGNS}))
          print('PROPOSAL',tag,rows[-1]['gaps'],flush=True)
    np.savez_compressed(OUT/'proposal_witness.npz',**archive)
    put(OUT/'proposals.json',dict(schema='nbo-r19-proposals-v1',seeds=list(seeds),fits=fits,rows=rows,
      state_count=eng.S,state_dimension=2,horizon=8,common_actions=len(eng.b.e[0].menu),
      training_laws=[.12,.13],test_laws=list(laws),
      scope='Repeated-seed fixed-target implementation study, not a state-dimension scaling frontier. Same exact first-date optimization and exact-DP upper reference for all methods. Bank evaluation charges every teacher policy. Offline costs are shown separately; checker cost is reported in validation.json.'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--analytic-only',action='store_true');args=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter();analytic()
    if not args.analytic_only:
      b,j=load(ROOT/'replication/r13/canonical');eng=Engine(b,j)
      put(OUT/'arithmetic.json',derive(b,j));enforcement(eng);proposals(eng)
    put(OUT/'generation.json',dict(source_commit=os.environ.get('R19_SOURCE_COMMIT','unrecorded'),
      python=sys.version,platform=platform.platform(),numpy=np.__version__,
      threads={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},
      elapsed_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      canonical_manifest_sha256=hashlib.sha256((ROOT/'replication/r13/canonical/manifest.json').read_bytes()).hexdigest()))
if __name__=='__main__':main()
