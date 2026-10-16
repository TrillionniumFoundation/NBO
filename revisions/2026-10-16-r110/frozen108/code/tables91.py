"""All deterministic R91 configurations, without rounding exact diagnostic values."""
from pathlib import Path
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parents[1]
def math(s):
    x=F(s)
    return '$'+(str(x.numerator) if x.denominator==1 else r'\frac{'+str(x.numerator)+'}{'+str(x.denominator)+'}')+'$'
def main():
    out=json.loads((R/'audit/RISK91.json').read_text())
    if out['status']!='passed' or len(out['records'])!=27 or out['complete_policies']!=1728:raise AssertionError('Incomplete exact catalogue')
    header=r'Case & $\alpha$ & $\beta$ & Policies & Max. loss & Max. bound & Min. slack \\'+'\n'
    text=r'{\small\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{longtable}{lrrrccc}'+'\n'+r'\caption{Every exact signed-risk qualification configuration}\label{tab:risk91}\\'+'\n'+r'\hline'+'\n'+header+r'\hline\endfirsthead'+'\n'+r'\hline'+'\n'+header+r'\hline\endhead'+'\n'
    for row in out['records']:
        if F(row['min_slack'])<0 or row['policies']!=64:raise AssertionError('Invalid exact test record')
        items=[str(row['case']+1),math(row['alpha']),math(row['discount']),'64']+[math(row[x]) for x in ('max_actual_loss','max_certificate','min_slack')]
        text+=' & '.join(items)+r' \\[2pt]'+'\n'
    text+=r'\hline\end{longtable}}'+'\n'+r'\noindent{\footnotesize All quantities are exact rational values. Case 2 uses deterministic numerical successors; Cases 1 and 3 move successor mass in opposite directions. These are diagnostic configurations, not independent economic samples.}'+'\n'
    (R/'tables').mkdir(exist_ok=True);(R/'tables/risk91.tex').write_text(text)
if __name__=='__main__':main()
