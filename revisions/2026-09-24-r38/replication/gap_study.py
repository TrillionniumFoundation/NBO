"""Controlled, policy-class-labelled gap diagnostics; never add across classes."""
from fractions import Fraction as F
import time
import kernel as k
from primary import ROOT,load,save,dumps,digest
OLD=tuple(map(F,(0,1,4,16,64,256,1024,4096)))
NEW=tuple(sorted(set(OLD)|set(map(F,('1/2','2','8','32','128','512','2048')))))
Z,O=F(0),F(1)
def support(raw,lam):
    T=len(raw);W=[None]*(T+1);pol=[None]*T;W[T]=k.affine(lam/2)
    for t in reversed(range(T)):
        qs=[k.linear_comb([q,k.intervention(raw[t],a)],[O,-O],a=lam,b=-lam*k.COSTS[a]) for a,q in enumerate(k.q_functions(W[t+1],False))]
        W[t],pol[t]=k.envelope(qs)
        for q in qs:assert k.linear_comb([W[t],q],[O,-O]).extent()[0]>=0
        assert k.linear_comb([W[t],k.select(qs,pol[t])],[O,-O]).extent()==(Z,Z)
    return W,pol

def floor(L,supports,eps,prices):
    B=[]
    for t in range(len(L)-1):
        fs=[k.affine()]+[k.linear_comb([L[t],supports[lam][0][t]],[lam,-O],b=-lam*eps) for lam in prices]
        value,_=k.envelope(fs);B.append(value)
    return B+[k.affine()]
def run():
    start=time.perf_counter();cache={};rows=[];work=[];primary=load(ROOT/'results/primary.json')
    for row in primary['outcomes']:
        d=load(ROOT/'results'/row['proof_file']);key=(d['T'],d['proposal']);raw=list(map(k.PW.load,d['raw']))
        if key not in cache:
            tic=time.perf_counter();ss={lam:support(raw,lam) for lam in NEW};cache[key]=ss
            obj={'T':key[0],'proposal':key[1],'raw':d['raw'],'supports':[{'multiplier':str(lam),'W':dumps(ss[lam][0]),'policy':dumps(ss[lam][1])} for lam in NEW]}
            filename=f'support_H{key[0]}_{key[1]}.json.gz';h=save(ROOT/'results/supports'/filename,obj)
            work.append({'T':key[0],'proposal':key[1],'support_solves':len(NEW),'seconds':time.perf_counter()-tic,'proof_file':'supports/'+filename,'proof_sha256':h})
        ss=cache[key];V=list(map(k.PW.load,d['V']));L=list(map(k.PW.load,d['L']));eps=F(d['epsilon'])
        BL=floor(L,ss,eps,OLD);BV=floor(V,ss,eps,OLD);BR=floor(V,ss,eps,NEW)
        for lo,hi in ((BL,BV),(BV,BR)):
            assert all(k.linear_comb([b,a],[O,-O]).extent()[0]>=0 for a,b in zip(lo,hi))
        x,y,z=(b[0].integral() for b in (BL,BV,BR))
        regret=F(next(a['regret'] for a in row['attempts'] if a['candidate']=='necessary_selector'))
        r={'T':key[0],'proposal':key[1],'epsilon':str(eps),'support_policy_class':'randomized_history_conditioned',
          'support_old_constructed_witness':str(x),'support_old_exact_value':str(y),'support_refined_exact_value':str(z),
          'support_floor_witness_improvement':str(y-x),'global_price_refinement_improvement':str(z-y),
          'deterministic_safe_lower':row['safe_lower_integral'],'deterministic_exact_value_lower':row['lower_integral'],
          'deterministic_witness_improvement':row['witness_lower_improvement'],'upper_search_improvement':row['upper_improvement'],
          'necessary_selector_operating_violation':str(max(Z,regret-eps)),'remaining_deterministic_interval':row['gap'],
          'inherited_randomized_restart_lower':row['inherited_randomized_lower'],'upper_cost':row['upper_integral']}
        name=f'diagnostic_H{key[0]}_{key[1]}_eps{str(eps).replace("/","_")}.json.gz'
        r['proof_file']='gap_functions/'+name;r['proof_sha256']=save(ROOT/'results/gap_functions'/name,{'metadata':r,'B_L_old':dumps(BL),'B_V_old':dumps(BV),'B_V_refined':dumps(BR)})
        rows.append(r);print(key,eps,'price_gain',float(z-y),'witness_gain',float(y-x),flush=True)
    save(ROOT/'results/gap_study.json',{'outcomes':rows,'support_work':work,'old_prices':list(map(str,OLD)),'refined_prices':list(map(str,NEW)),
       'seconds':time.perf_counter()-start,'scope':'Three global support floors are compared under identical raw inputs and separately labelled randomized/history policy scope. Deterministic outer-class diagnostics are another ladder, not additive terms of a randomized gap. Local LP error is measured separately with zero support floor.'})
if __name__=='__main__':run()
