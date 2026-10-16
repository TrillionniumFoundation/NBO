"""Post-evaluation re-accounting; no fit, actor, sample or decision is changed."""
import hashlib,json,pathlib
import numpy as np
from interval94 import I,up
from investment94 import BETA,TERMINAL_TOL
R=pathlib.Path(__file__).resolve().parents[1]
c=json.loads((R/'results94/CALIBRATION94.json').read_text());out={'scope':'Post-evaluation deterministic certificate re-accounting of every existing fitted-arm row. Not a prospectively registered ablation or a new economic sample.','new_fit_attempts':0,'new_independent_observations':0,'rows':[]}
text=r'''\begin{table}[htbp]
\caption{Three valid certificate accounts for the same frozen fitted policies}\label{tab:accounts95}
\centering\small
\begin{tabular}{@{}llrrrr@{}}\toprule
$\alpha$ & Continuation & Supremum norm & Signed scalar & Joint support & Qualified\\\midrule
'''
for idx,lev in c['levels'].items():
 for arm in ('quadratic','relu','spline'):
  p=R/f'results94/evaluation-local95/alpha-{idx}-{arm}.csv';a=np.genfromtxt(p,delimiter=',',names=True)
  b=lev['constructions'][arm]['uniform_residual'];rad=max(abs(b['lower']),abs(b['upper']))
  norm=(I(a['own_Q_gap_upper'])+BETA*(I(rad)*2+TERMINAL_TOL)).hi
  signed=(I(a['own_Q_gap_upper'])+BETA*(I(b['upper'])-I(b['lower'])+TERMINAL_TOL)).hi
  joint=a['original_optimum_loss_upper']
  row={'alpha':lev['alpha'],'arm':arm,'rows':len(a),'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'supnorm_max':float(max(norm)),'signed_max':float(max(signed)),'joint_max':float(max(joint)),'supnorm_pass':int(sum(norm<=1/16)),'signed_pass':int(sum(signed<=1/16)),'joint_pass':int(sum(joint<=1/16)),'uniform_residual_construction_work':lev['constructions'][arm]['residual_work']}
  out['rows'].append(row)
  from decimal import Decimal,ROUND_CEILING
  fmt=lambda x:format(Decimal.from_float(x).quantize(Decimal('.000001'),rounding=ROUND_CEILING),'f')
  text+=' & '.join([str(lev['alpha']),{'relu':'ReLU','quadratic':'Quadratic','spline':'Spline'}[arm],fmt(row['supnorm_max']),fmt(row['signed_max']),fmt(row['joint_max']),str(row['joint_pass'])+'/2,048'])+r'\\'+'\n'
text+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{.98\linewidth}\footnotesize
Entries are maximum original-optimum policy-loss bounds across the same 2,048 rows. Supremum-norm and signed-scalar bounds use the same frozen whole-square residual cover. Joint support uses the paid original-value witness. No row satisfies $1/16$ with either scalar account; every row does with the joint certificate. This is post-evaluation deterministic re-accounting, not a prospective runtime ablation or an optimality claim for any certificate-construction algorithm.
\end{minipage}\end{table}
'''
(R/'tables/accounts95.tex').write_text(text);(R/'audit/local95/ACCOUNTS95.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
