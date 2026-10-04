"""Compare learned scalar costates with independent finite-grid policy values."""
import argparse
from common import *
def run(development=False):
    base=R/('development' if development else 'results')/'reference';meta=json.loads((base/'REFERENCE.json').read_text());rows=[]
    nbo=next(f for f in meta['fits'] if f['method']=='nbo');actor,critic,_=old.load(base/(nbo['id']+'.pt'))
    for row in meta['records']:
        with np.load(base/(row['id']+'.npz')) as z:
            y=z['state'];mask=(abs(y)<=1.);xx=torch.from_numpy(np.c_[np.zeros(mask.sum()),y[mask]])
            _,v,_,p=old.first_jet(critic,xx);target=z['nbo'][mask];costate=np.gradient(z['nbo'],y)[mask]
            diff=p.detach().numpy().ravel()-costate
            with torch.no_grad():m=actor(xx).numpy().ravel()
            optimal=np.interp(y[mask],y[1:-1],z['optimal_action_t0'])
            rows.append(dict(grid=row['id'],state_domain=[-1.,1.],value_rmse=float(np.sqrt(np.mean((v.detach().numpy().ravel()-target)**2))),costate_rmse=float(np.sqrt(np.mean(diff**2))),costate_max_error=float(abs(diff).max()),action_rmse_against_grid_optimum=float(np.sqrt(np.mean((m-optimal)**2))),reference_raw_sha256=row['raw_sha256'],critic_weights_sha256=nbo['weights_sha256']))
    result=dict(source_commit=source(),records=rows,scope='t=0, |log capital|<=1; independent finite-grid fixed-policy costate and optimal-action diagnostic. Discretization and boundary bias are not eliminated; not a uniform continuous-time critic certificate.')
    write(base/'CRITIC_REFERENCE.json',result);print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--development',action='store_true');a=p.parse_args();run(a.development)
