"""Post-execution descriptions; never inputs to a primary constructor."""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,re,csv
ROOT=Path(__file__).resolve().parent.parent;REPO=ROOT.parents[1];GEN=ROOT/'paper/generated'
def nums(v):
 if isinstance(v,dict):
  for x in v.values():yield from nums(x)
 elif isinstance(v,list):
  for x in v:yield from nums(x)
 elif isinstance(v,str) and re.fullmatch(r'-?\d+(?:/\d+)?',v):yield Q(v)
def bits(v):
 n=d=0
 for x in nums(v):n=max(n,x.numerator.bit_length());d=max(d,x.denominator.bit_length())
 return n,d
def rowfile(name,rows):(GEN/name).write_text('\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)+'\n')
def main():
 out=[];details=[]
 for path in sorted((ROOT/'results').glob('finite-*.json')):
  s=json.loads(path.read_text());e=json.loads(gzip.decompress((REPO/s['proof']).read_bytes()));w=e['witness'];xi=max(map(Q,w['widths']));guard=(1-Q(e['model']['beta']))*Q(e['model']['epsilon']);trace=e.get('trajectory',e.get('trace',[]));root=Q(e.get('root_lower',e['tree'][0]['lower']));L=Q(e['lower']);U=Q(e['upper']);U0=Q(e['initial_upper']);den=(L-root)+(U0-U);b=bits(e);z=e.get('prices',{});ampl=w['history'][-1]['price_budget'];leaves=sum(not t.get('children') for t in e['tree']);vars=max(t.get('variables',0) for t in e['tree']);rec={'case':s['case'],'method':s['method'],'budget':int(s['budget_seconds']),'initial_upper':str(U0),'root_lower':str(root),'final_upper':str(U),'final_lower':str(L),'lower_movement':str(L-root),'upper_movement':str(U0-U),'lower_movement_share':str((L-root)/den) if den else None,'witness_bits':w['bits'],'xi_over_slack':str(xi/guard),'price_error_budget':ampl,'oracle_seconds':w['seconds'],'attempted_masks':len(z.get('masks',[])),'mask_statuses':z.get('masks',[]),'max_numerator_bits':b[0],'max_denominator_bits':b[1],'root_variables':vars,'leaves':leaves,'proof_bytes':s['proof_bytes'],'verify_seconds':s['verify_seconds'],'local':e.get('local')};details.append(rec)
  out.append([s['case'],s['method'][0].upper(),int(s['budget_seconds']),f'{float(U0):.5f}',f'{float(root):.5f}',f'{float(U0-U):.2g}',f'{float(L-root):.2g}',w['bits'],f'{float(xi/guard):.1g}'])
 rowfile('finite_diagnostics.tex',out)
 rowfile('finite_resources.tex',[[d['case'],d['method'][0].upper(),d['budget'],d['root_variables'],d['leaves'],f"{d['proof_bytes']/1024:.1f}",f"{d['verify_seconds']:.3f}",d['max_numerator_bits'],d['max_denominator_bits']] for d in details])
 coupling=[]
 for path in sorted((ROOT/'proofs').glob('price-audit-*.json.gz')):
  e=json.loads(gzip.decompress(path.read_bytes()));r=e['model'];beta=Q(r['beta']);spreads=[];maxprice=Q(0)
  for c in e['certificates']:
   if c.get('certified'):
    z={tuple(i['label']):Q(i['value']) for i in c['occupation']};succ={}
    for t in range(r['T']-1):
     for i in range(r['n']):
      for j in range(r['n']):
       f=beta*sum(z.get(('y',t,i,a),Q(0))*Q(r['P'][t][i][a][j]) for a in range(r['m']))
       if f:succ.setdefault((t+1,j),[]).append(z.get(('alpha',t,i,j),Q(0))/f)
    spreads += [max(v)-min(v) for v in succ.values()]
   maxprice=max([maxprice]+list(nums(c.get('field',[]))))
  b=bits(e);coupling.append({'case':path.name[12:-8],'max_incoming_budget_spread':str(max(spreads,default=Q(0))),'max_price':str(maxprice),'max_numerator_bits':b[0],'max_denominator_bits':b[1]})
 rowfile('coupling.tex',[[d['case'],f"{float(Q(d['max_incoming_budget_spread'])):.3g}",f"{float(Q(d['max_price'])):.3g}",d['max_numerator_bits'],d['max_denominator_bits']] for d in coupling])
 (ROOT/'results/diagnostics.json').write_text(json.dumps({'finite':details,'price_occupation':coupling,'interpretation':'post-execution descriptive quantities; no causal or statistical fit'},indent=2)+'\n')
if __name__=='__main__':main()
