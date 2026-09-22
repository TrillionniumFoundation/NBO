"""Generate every new table from exact recorded enclosures."""
import json,time
from fractions import Fraction as F
import price_envelope as e

def dec(x,n=8,up=True):
 x=F(x)*10**n;a=-(-x.numerator//x.denominator) if up else x.numerator//x.denominator
 sign='-' if a<0 else '';a=abs(a);return f'{sign}{a//10**n}.{a%10**n:0{n}d}'
def main():
 nodes=e.load_nodes();env=e.certify(nodes);e.dump(e.REV/'results/envelope.json',env)
 groups=[[.5,2,8],[4],[1.25,3,6],[.875,1.625,2.5,3.5,5,7],[4.5,5.5,6.5,7.5],[4.25]]
 keep=set();frontier=[]
 for adds in groups:
  keep.update(adds);part=[n for n in nodes if n['k'] in keep];r=e.certify(part)
  frontier.append({'nodes':len(part),'added_prices':adds,'uniform_regret_upper':r['uniform_regret_upper'],
                   'exact_gap':r['uniform_regret_rational'],'status':r['status'],
                   'cumulative_successful_task_seconds':sum(n.get('seconds',0) for n in part)})
 e.dump(e.REV/'results/frontier.json',{'rows':frontier,'scope':'Incremental successful task-wall durations summed across potentially concurrent price cases, excluding inherited computation and interrupted attempts.'})
 table=[r'\begin{tabular}{rrrr}\toprule',r'Certified prices & Uniform regret upper & Task-seconds & Target met \\ \midrule']
 for r in frontier:
  table.append(f"{r['nodes']} & {dec(F(r['exact_gap']),9)} & {r['cumulative_successful_task_seconds']:.2f} & "+('Yes' if r['status']=='PASS' else 'No')+r' \\')
 table+=[r'\bottomrule\end{tabular}']
 e.REV.joinpath('paper/tables').mkdir(parents=True,exist_ok=True)
 e.REV.joinpath('paper/tables/frontier.tex').write_text('\n'.join(table)+'\n')
 full=[r'\begin{tabular}{rrrrr}\toprule',r'$k_j$ & Feasible value lower & Optimal value upper & $b_j^-$ & $b_j^+$ \\ \midrule']
 for n in nodes:
  full.append(f"{n['k']:g} & {dec(n['L'],8,False)} & {dec(n['U'])} & {dec(n['B'][0],8,False)} & {dec(n['B'][1])}"+r' \\')
 full+=[r'\bottomrule\end{tabular}'];e.REV.joinpath('paper/tables/nodes.tex').write_text('\n'.join(full)+'\n')
 q=[e.query(x,nodes) for x in ['0.6','1.1','2.3','4.1','4.75','6.25','7.7421534486409955','8']]
 e.dump(e.REV/'results/query_examples.json',{'status':'PASS','queries':q})
 print(json.dumps({'status':env['status'],'nodes':len(nodes),'uniform_regret_upper':env['uniform_regret_upper']}))
if __name__=='__main__':main()
