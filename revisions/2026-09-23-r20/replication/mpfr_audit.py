"""Independent arithmetic recheck of every final confirmatory expert."""
from pathlib import Path
import hashlib,json,os,time
os.environ['BACKEND']='mpfr'
from certify_stochastic import certify,ROOT
R=ROOT/'revisions/2026-09-23-r20'

def run():
 start=time.perf_counter();records=[]
 for seed in range(20100,20105):
  for vertex in range(4):
   actor=R/f'results/neural/seed{seed}/vertex{vertex}/actor_1000.json'
   data=json.loads(actor.read_text());c=certify(data)
   original=json.loads(actor.with_name('certificate_1000.json').read_text())
   for key in ['value_interval','price_interval','reserve_interval','initial_portfolio_interval']:
    a,b=original[key],c[key];assert max(a[0],b[0])<=min(a[1],b[1]),(key,a,b)
   c.update({'seed':seed,'vertex':vertex,'actor_sha256':hashlib.sha256(actor.read_bytes()).hexdigest(),'actor_path':str(actor.relative_to(ROOT)),
      'arithmetic_intersection':'all four reported intervals overlap; numerical comparison is not an independent mathematical proof'})
   out=R/f'results/mpfr/seed{seed}_vertex{vertex}.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(c,indent=2)+'\n')
   records.append(c);(R/'results/mpfr/records.json').write_text(json.dumps(records,indent=2)+'\n')
   print('MPFR',seed,vertex,c['regret_upper'],flush=True)
 (R/'results/mpfr/resources.json').write_text(json.dumps({'wall_seconds':time.perf_counter()-start,'checks':len(records)},indent=2)+'\n')
if __name__=='__main__':run()
