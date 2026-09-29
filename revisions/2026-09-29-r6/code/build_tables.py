"""Generate manuscript tables from actual saved runs; no acceptance flags altered."""
from pathlib import Path
import json,numpy as np
P=Path(__file__).resolve().parents[1];R=P/'results';M=P/'manuscript'
def read(n):return json.loads((R/(n+'.json')).read_text())
def num(x):
 if x is None:return '--'
 if x==0:return '0'
 if abs(x)<.001 or abs(x)>=1000:
  a,e=f'{x:.2e}'.split('e');return '$'+a+r'\times10^{'+str(int(e))+'}$'
 return f'{x:.4f}'
def table(name,caption,label,headers,rows,note):
 text=r'\begin{table}[t]\centering'+'\n'+r'\caption{'+caption+r'}\label{'+label+'}\n'+r'\small\begin{tabular}{'+('l'+'r'*(len(headers)-1))+'}\n'+r'\toprule'+'\n'+' & '.join(headers)+r'\\\midrule'+'\n'
 text+='\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'+r'\bottomrule\end{tabular}'+'\n'+r'\par\smallskip\footnotesize '+note+'\n'+r'\end{table}'+'\n';(M/name).write_text(text)
def main():
 M.mkdir(exist_ok=True,parents=True)
 rows=[]
 for r in read('consumption_primary')['runs']:
  f=R/(r['model_id']+'_certificate.json');c=json.loads(f.read_text()) if f.exists() else {}
  rows.append([{'nbo':'NBO','direct':'Direct HJB','joint':'Joint loss'}[r['method']],r['seed'],num(r['value_error_max']),num(r['residual_max']),num(c.get('action_gap_upper')),num(c.get('policy_regret_upper'))])
 table('table_consumption.tex','Multilayer consumption: approximation and continuous-domain verification','tab:consumption-r6',['Method','Seed',r'$\|v-V_h^*\|_\infty$',r'Sampled $e$',r'Uniform $\eta$',r'Regret bound'],rows,r'The comparison grid has 2,560 intervals on $[.5,2.5]$. The last two columns cover the entire continuous interval and consumption set $[.02,.6]$. All six certificates have uniform evaluation error at most $.002$ and endpoint error below $10^{-12}$. Dashes indicate no accepted certificate, not zero error. Reference error and the sampled differential residual are not used as uniform bounds.')
 rows=[]
 for r in read('ndu_primary'):
  rows.append(['NBO' if r['method']=='nbo' else 'Direct Bellman',r['seed'],num(r['value_error_max']),num(r['policy_regret_max']),num(r['certificate']['policy_regret_upper']),num(r['heldout_value_error_rms'])])
 table('table_ndu.tex','Neural preference adjustment on the same finite economy','tab:ndu-r6',['Method','Seed',r'Value error',r'Policy regret',r'Bound $R_0$',r'Midpoint RMS'],rows,r'The first three error columns use every state and time of the $17\times25\times21$ grid with 175 actions; $R_0$ is the time-zero certificate, while the first two columns maximize their independently computed errors over all times. Midpoints compare the time-zero neural critic with the finite-reference interpolant. Continuous-action and controlled-diffusion discretization errors are not included. The accuracy targets were value error $.2$ and policy regret $.1$.')
 a=read('coupled_primary');rows=[]
 for d in [2,5,10,20]:
  for m in ['nbo_exact','direct']:
   z=[r for r in a if r['dimension']==d and r['method']==m]
   if len(z)!=3:raise ValueError('incomplete coupled suite')
   rows.append(['NBO' if m=='nbo_exact' else 'Direct HJB',d,num(max(r['diagnostics']['residual_rms'] for r in z)),num(max(r['diagnostics']['action_gap_max'] for r in z)),f"{sum(not r['diagnostic_pass'] for r in z)}/3",num(float(np.median([r['seconds'] for r in z])))])
 table('table_coupled.tex','Actual training in dense nonquadratic capital models','tab:coupled-r6',['Method','$d$',r'Worst RMS',r'Worst gap',r'Failures',r'Median seconds'],rows,r'Maxima are across three seeds, each evaluated at 512 independent points in $[0,1]\times[-.5,.5]^d$. The failure criterion is RMS residual above $.025$ or queried action gap above $.01$ after 600 updates. Both methods use the same critic architecture and global action routine. Times include training diagnostics, not the subsequent Monte Carlo evaluations. These are sampled diagnostics, not uniform economic bounds.')
 rows=[]
 for r in read('cournot_primary'):
  if r['tie_rule']!='low' or r['adjustment_cost'][1]!=1:continue
  rows.append([f"{r['grid']}$^2$",r['steps'],r['investment_actions'],int(r['market_size']),num(r['center_investment'][0]),num(r['center_value'][0]),num(max(r['exploitability_max']))])
 table('table_game.tex','Dynamic Cournot: independent fixed-rival best responses','tab:game-r6',['Grid','Steps','Actions','$M_2$',r'$I_1(0)$',r'$V_1(0)$',r'Max. gain'],rows,r'Center state is $(K_1,K_2)=(.775,.775)$. Horizon is three, capital lies in $[.05,1.5]^2$, and investment in $[0,.8]$. The final column maximizes independently computed dynamic unilateral gains over both firms and every finite-model state and time. Zero denotes the displayed floating-point precision; it is not a continuous-game error bound. Six principal cases additionally include a high-index equilibrium tie rule and asymmetric adjustment costs.')
 # Supplement: every primary training run, sensitivity run, and pilot summary.
 lines=[r'\section{Run-Level Numerical Accounts}',r'\subsection{Consumption fitting and verification}',r'\begin{longtable}{llrrrr}',r'\toprule Method & Seed & Width/depth & Fit seconds & Verify seconds & Pass\\\midrule\endhead']
 for r in read('consumption_primary')['runs']+read('consumption_sensitivity')['runs']:
  f=R/(r['model_id']+'_certificate.json');c=json.loads(f.read_text()) if f.exists() else {}
  lines.append(' & '.join([r['method'],str(r['seed']),f"{r['width']}/{r['depth']}",num(r['seconds']),num(c.get('seconds')),str(r['diagnostic_pass'])])+r'\\')
 lines+=[r'\bottomrule\end{longtable}',r'Pass in this table means the prespecified sampled diagnostic. Continuous certification is reported separately and only for the primary NBO and direct-HJB runs. Every closure count, pointwise derivative array, parameter, and iteration trace is in the corresponding raw result.',r'\subsection{Action bounds and numerical domains}',r'\begin{longtable}{llrrrr}',r'\toprule Actions & Grid/time & $k$ & Center value & Upper $m$ freq. & Upper $p$ freq.\\\midrule\endhead']
 for r in read('ndu_sensitivity'):
  label=r['actions'].replace('_',r'\_');grid=f"{r['state_grid'][0]}x{r['state_grid'][1]}/{r['steps']}"+('*' if r['wealth_interval'][0]<.49 else '')
  lines.append(' & '.join([label,grid,num(r['cost']),num(r['center_value']),num(r['action_upper_frequency'][0]),num(r['action_upper_frequency'][1])])+r'\\')
 lines+=[r'\bottomrule\end{longtable}',r'An asterisk marks wealth interval $[.25,4]$, rather than $[.5,2]$. Frequencies use all nonabsorbing state--time nodes. The raw record includes both bounds for each of the three controls. ``Expanded'' has 175 actions; ``refined'' has 1,053 actions in the same box; ``expanded\_domain'' changes the box itself.',r'\subsection{Dense neural runs, trace estimators, and coverage}',r'\begin{longtable}{llrrrrr}',r'\toprule Method & $d$/seed & Steps & RMS & Gap & Seconds & Pass\\\midrule\endhead']
 for name in ['coupled_primary','coupled_trace','coupled_coverage']:
  for r in read(name):
   label=r['method'].replace('nbo_','').replace('_',r'\_')+('*' if name=='coupled_coverage' else '')
   lines.append(' & '.join([label,f"{r['dimension']}/{r['seed']}",str(r['steps']),num(r['diagnostics']['residual_rms']),num(r['diagnostics']['action_gap_max']),num(r['seconds']),str(r['diagnostic_pass'])])+r'\\')
 lines+=[r'\bottomrule\end{longtable}',r'An asterisk marks the follow-up fitting domain $[-1.5,.5]^d$ and 1,000 updates. Product uses two independent two-probe banks; single squares a four-probe trace. Every row retains its own history and exact-trace diagnostic set. Runtime is not a hardware-independent complexity bound.',r'\subsection{Policy-payoff diagnostics}',r'\begin{longtable}{llrrrr}',r'\toprule Method & $d$/seed & Critic at zero & Euler mean & MC s.e. & Critic minus mean\\\midrule\endhead']
 for name in ['coupled_primary','coupled_coverage']:
  for r in read(name):
   if r['dimension'] not in [10,20]:continue
   sim=r['simulations'][1];label=r['method'].replace('nbo_','').replace('_',r'\_')+('*' if name=='coupled_coverage' else '')
   lines.append(' & '.join([label,f"{r['dimension']}/{r['seed']}",num(sim['initial_critic']),num(sim['mean']),num(sim['standard_error']),num(sim['initial_critic']-sim['mean'])])+r'\\')
 lines+=[r'\bottomrule\end{longtable}',r'These estimates use 2,048 paths and 80 Euler steps from zero log capital. Forty-step samples are also saved. Identical random seeds pair policy comparisons at the same step size; the forty- and eighty-step simulations are not a Brownian-coupled refinement estimator. The standard error measures sampling error only. The initial critic is not an external optimal-value reference.']
 text='\n'.join(lines)+'\n'
 text=text.replace(r'\begin{longtable}',r'\begingroup\footnotesize\setlength{\tabcolsep}{4pt}'+ '\n'+r'\begin{longtable}').replace(r'\end{longtable}',r'\end{longtable}\endgroup')
 (M/'tables_supplement.tex').write_text(text)
if __name__=='__main__':main()
