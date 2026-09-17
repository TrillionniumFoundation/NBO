"""Fixed-calendar wealth-lottery perturbations and common-estimand menu audit."""
import argparse, time, hashlib
from model import *
from certificate import run as certify

def solve_grid(nx):
    start=time.perf_counter();mix=Model(Specification(nx=nx));rows=[]
    points=[(0.,.4),(0.,.45),(.25,.4),(.25,.45),(.125,.425)]
    for mesh in (True,False):
        for t,d in points:
            row=dict(nx=nx,menu='common_1565' if mesh else 'full_prolonged_1568',lambda_=t,d=d,classes={})
            for adj in (True,False):
                for sign,item in mix.class_pair(t,d,adj,mesh_only=mesh).items():
                    direct=mix.direct(item['policy'],t,d);err=float(abs(direct-item['value']).max());assert err<2e-11
                    row['classes'][('adj' if adj else 'fixed')+'_'+sign]=dict(value=float(direct[0,mix.center]),replay_error=err,policy_sha256=hashlib.sha256(item['policy'].tobytes()).hexdigest())
            c=row['classes'];row['delta_adjusted']=c['adj_positive']['value']-c['adj_nonpositive']['value'];row['delta_fixed']=c['fixed_positive']['value']-c['fixed_nonpositive']['value'];row['relative_option']=row['delta_adjusted']-row['delta_fixed']
            rows.append(row)
            save(f'spatial_partial_{nx}.json',dict(complete=False,rows=rows))
    # Bracket the local indifference crossing; no global monotonicity asserted.
    # Bisection leaves a trace of every evaluated value and a 4.88e-5 d bracket.
    frontiers=[]
    for t in (0.,.125,.25):
        for adj in (True,False):
            trace=[]
            def gap(d):
                pair=mix.class_pair(t,d,adj);v=pair['positive']['value'][0,mix.center]-pair['nonpositive']['value'][0,mix.center]
                trace.append([d,float(v)]);return v
            lo,hi=.2,.6;vl,vh=gap(lo),gap(hi)
            if vl*vh>=0:
                frontiers.append(dict(nx=nx,lambda_=t,adjustment=adj,bracket=None,trace=trace));continue
            for _ in range(13):
                mid=(lo+hi)/2;vm=gap(mid)
                if vm*vl>0:lo,vl=mid,vm
                else:hi,vh=mid,vm
            frontiers.append(dict(nx=nx,lambda_=t,adjustment=adj,bracket=[lo,hi],endpoint_values=[float(vl),float(vh)],trace=trace))
    # The old region remains in the record. This nested region is accompanied
    # by its full failure map rather than silently replacing the old claim.
    save(f'spatial_partial_{nx}.json',dict(complete=False,rows=rows,frontiers=frontiers))
    cert=certify(mix,region=(0.,.125,.4,.425),name=f'spatial_nested_certificate_{nx}.json')
    result=dict(nx=nx,rows=rows,frontiers=frontiers,elapsed_seconds=time.perf_counter()-start,
                common_action_count=1565,full_action_count=1568,calendar_intervals=8,
                certificate_file=f'spatial_nested_certificate_{nx}.json',target='declared finite lottery protocols, not a proved diffusion limit')
    save(f'spatial_{nx}.json',result);print('completed grid',nx,flush=True)
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--nx',type=int,required=True);args=ap.parse_args();solve_grid(args.nx)
