"""All 66 declared normalized comparative-statics scenarios, not a population sample."""
from pathlib import Path
from fractions import Fraction as F
import copy,json,time,resource,hashlib
import kernel as k
from primary import save,digest,ROOT
BASE={'beta':F(19,20),'weight_slope':F(1),'density':'uniform','maintenance_cost':F(3,20),'defer_persistence':F(3,4)}
SPECS=[('baseline',{})]+[(name,{key:value}) for name,key,value in (
 ('discount_090','beta',F(9,10)),('discount_099','beta',F(99,100)),
 ('flat_revision_weight','weight_slope',F(0)),('steep_revision_weight','weight_slope',F(2)),
 ('high_condition_density','density','2x'),('low_condition_density','density','2(1-x)'),
 ('maintenance_010','maintenance_cost',F(1,10)),('maintenance_020','maintenance_cost',F(1,5)),
 ('defer_persistence_065','defer_persistence',F(13,20)),('defer_persistence_085','defer_persistence',F(17,20)))]
def set_model(spec):
    k.BETA=spec['beta'];k.COSTS=(F(0),spec['maintenance_cost'],F(9,20))
    k.MAPS=(((spec['defer_persistence'],F(0)),(spec['defer_persistence'],F(1,20))),
      ((F(17,20),F(1,10)),(F(17,20),F(7,50))),((F(1,10),F(4,5)),(F(1,10),F(17,20))))
    slope=spec['weight_slope']
    def intervention(raw,action):
        return k.PW(raw.xs[:],[(F(0),F(0)) if b==action else (slope,F(1)) for a,b in raw.ab],
             [F(0) if a==action else 1+slope*x for x,a in zip(raw.xs,raw.ys)]).norm()
    k.intervention=intervention

def rule(T,name):
    result=[]
    for t in range(T):
        if name=='condition':cuts=[F(0),F(3,10),F(3,5),F(1)];actions=[2,1,0]
        elif name=='preventive':cuts=[F(0),F(3,20),F(3,4),F(1)];actions=[2,1,0]
        elif name=='calendar' and t%4==0:cuts=[F(0),F(1,5),F(1)];actions=[2,1]
        else:cuts=[F(0),F(1)];actions=[0]
        result.append(k.PW(cuts,[(F(0),F(a)) for a in actions],list(map(F,actions+[actions[-1]]))))
    return result

def weighted(f,density):
    m,b={'uniform':(F(0),F(1)),'2x':(F(2),F(0)),'2(1-x)':(F(-2),F(2))}[density]
    return sum((a*m*(r**3-l**3)/3+(a*b+c*m)*(r*r-l*l)/2+c*b*(r-l) for (a,c),l,r in zip(f.ab,f.xs,f.xs[1:])),F(0))
def run():
    start=time.perf_counter();rows=[];work=[];T=8
    for name,changes in SPECS:
        spec={**BASE,**changes};set_model(spec);V,_,stat=k.exact_dp(T)
        for eps in (F(1,20),F(1,5)):
            U,qs,wlog=k.witnesses(T,eps);allowed=k.admissible(U,qs,F(wlog['eta']))
            work.append({'specification':name,'epsilon':str(eps),'operating_reference_seconds':stat['seconds'],'witness_seconds':wlog['seconds']})
            for rawname in ('condition','preventive','calendar'):
                tic=time.perf_counter();raw=rule(T,rawname);policy,C=k.repair(raw,allowed);point,P=k.repair(raw,allowed,False)
                J=k.evaluate(policy);PJ=k.evaluate(point)
                gap=max(k.linear_comb([v,j],[F(1),F(-1)]).extent()[1] for v,j in zip(V,J))
                pgap=max(k.linear_comb([v,j],[F(1),F(-1)]).extent()[1] for v,j in zip(V,PJ))
                saving=k.linear_comb([P[0],C[0]],[F(1),F(-1)])
                assert gap<=eps and pgap<=eps and saving.extent()[0]>=0
                dcost=weighted(C[0],spec['density']);pcost=weighted(P[0],spec['density'])
                record={'specification':name,'primitive_changes':{kk:str(vv) for kk,vv in spec.items()},'installed_rule':rawname,'T':T,'epsilon':str(eps),
                  'dynamic_cost':str(dcost),'pointwise_cost':str(pcost),'occupancy_saving':str(pcost-dcost),'strict_saving':pcost>dcost,
                  'dynamic_regret':str(gap),'pointwise_regret':str(pgap),'all_restart_feasible':True,'same_action_class':True,
                  'dynamic_policy_sha256':digest([p.dump() for p in policy]),'pointwise_policy_sha256':digest([p.dump() for p in point]),
                  'seconds':time.perf_counter()-tic,'max_cost_pieces':max(len(c.ab) for c in C+P),'max_bits':max(c.bits() for c in C+P)}
                proof={'metadata':record,'model':k.model(),'revision_weight':'1+'+str(spec['weight_slope'])+'*x','raw':[p.dump() for p in raw],
                  'allowed':[[p.dump() for p in row] for row in allowed],'dynamic_policy':[p.dump() for p in policy],
                  'pointwise_policy':[p.dump() for p in point],'dynamic_cost':[p.dump() for p in C],'pointwise_cost':[p.dump() for p in P],
                  'V':[p.dump() for p in V],'J':[p.dump() for p in J],'pointwise_J':[p.dump() for p in PJ]}
                filename=name+'_'+rawname+'_'+str(eps).replace('/','_')+'.json.gz'
                record['proof_sha256']=save(ROOT/'results/sensitivity'/filename,proof);record['proof_file']='sensitivity/'+filename;rows.append(record)
                print(name,str(eps),rawname,'saving',float(pcost-dcost),flush=True)
    assert len(rows)==66
    save(ROOT/'results/sensitivity.json',{'cases':66,'outcomes':rows,'work':work,'strict_savings':sum(x['strict_saving'] for x in rows),
       'failed_certificates':0,'seconds':time.perf_counter()-start,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       'interpretation':'Designed one-at-a-time normalized economic scenarios; neither a dollar calibration nor a random population sample. All outcomes, including zeros, retained.'})
if __name__=='__main__':run()
