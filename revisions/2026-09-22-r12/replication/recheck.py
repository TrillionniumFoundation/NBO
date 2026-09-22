"""Clean-checkout replay of frozen policies and duals; preserve every planned cell."""
import argparse,contextlib,hashlib,json,os,pathlib,shutil,sys,time,traceback
import price_envelope as e
sys.path[:0]=[str(e.ROOT/'revisions/2026-09-22-r10/replication'),str(e.ROOT/'revisions/2026-09-22-r9/replication')]
import original_policy_certificate as policy
import flexible_dual as dual

def case(node):
 k=node['k'];out=e.REV/f'ci_results/k{k:g}';out.mkdir(parents=True,exist_ok=True)
 source=os.environ.get('R12_SOURCE_COMMIT','local-clean-recheck');start=time.perf_counter()
 status={'price':k,'status':'started','source_commit':source}
 e.dump(out/'status.json',status)
 try:
  src=e.ROOT/node['actor_path'];fit=src.parent/f'dual_pilot_k{k:g}.json'
  status['input_hashes']={str(p.relative_to(e.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,fit]}
  shutil.copy2(src,out/src.name);shutil.copy2(fit,out/fit.name)
  policy.OUT=out;dual.OUT=out
  with (out/'execution.log').open('w') as log,contextlib.redirect_stdout(log):
   lo=policy.run(f'k{k:g}',resolutions=(1024,));hi=dual.run(k,resolutions=((16,256),))
  L=lo['records'][-1]['policy_value_interval'][0];U=hi['records'][-1]['optimal_value_upper'];B=lo['adjustment_budget_interval']
  assert max(abs(L-node['L']),abs(U-node['U']),*(abs(x-y) for x,y in zip(B,node['B'])))<1e-13
  assert U-L<.01
  status.update(status='success',L=L,U=U,B=B,actor_path=node['actor_path'])
 except Exception as err:status.update(status='failed',exception=str(err));(out/'exception.txt').write_text(traceback.format_exc())
 finally:status['seconds']=time.perf_counter()-start;e.dump(out/'status.json',status)
 return status

def run_group(group):
 nodes=e.load_nodes();plan=[n for i,n in enumerate(nodes) if i%6==group]
 # Every planned status exists before any expensive calculation.
 for n in plan:e.dump(e.REV/f"ci_results/k{n['k']:g}/status.json",{'price':n['k'],'status':'not_executed','source_commit':os.environ.get('R12_SOURCE_COMMIT')})
 results=[case(n) for n in plan]
 e.dump(e.REV/f'ci_results/group-{group}.json',{'status':'PASS' if all(r['status']=='success' for r in results) else 'FAIL','planned_prices':[n['k'] for n in plan],'results':results})
 return all(r['status']=='success' for r in results)

def collect():
 nodes=e.load_nodes();out=[];complete=[]
 for node in nodes:
  p=e.REV/f"ci_results/k{node['k']:g}/status.json"
  r=json.loads(p.read_text()) if p.is_file() else {'price':node['k'],'status':'missing'}
  out.append(r)
  if r['status']=='success':complete.append(dict(node,L=r['L'],U=r['U'],B=r['B']))
 result={'status':'FAIL','source_commit':os.environ.get('R12_SOURCE_COMMIT'),'planned_prices':[n['k'] for n in nodes],'cells':out}
 if len(complete)==len(nodes):
  env=e.certify(complete);e.dump(e.REV/'ci_results/independent_envelope.json',env)
  if env['status']=='PASS':result.update(status='PASS',uniform_regret_upper=env['uniform_regret_upper'])
 e.dump(e.REV/'ci_results/status.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cells'},indent=2));return result['status']=='PASS'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--group',type=int,choices=range(6));p.add_argument('--collect',action='store_true');a=p.parse_args()
 if a.collect:ok=collect()
 else:ok=run_group(a.group)
 sys.exit(0 if ok else 1)
