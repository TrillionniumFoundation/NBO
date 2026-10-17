"""Print all declared horizons; outward rational rounding, no selected omissions."""
from pathlib import Path
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parents[1]
def up(v,places=6):
    v=F(v);s=10**places;n=-((-v.numerator*s)//v.denominator)
    sign='-' if n<0 else '';n=abs(n);return sign+str(n//s)+'.'+str(n%s).zfill(places)
def main():
    data=json.loads((R/'results92/SUMMARY92.json').read_text());audit=json.loads((R/'audit/reproduction92/INDEPENDENT92.json').read_text())
    if audit['status']!='passed':raise AssertionError('Independent record required before tables')
    rows=[]
    for T in (2,3,4,8,16,32,64):
        cases=[x for x in data['cases'] if x['T']==T]
        if len(cases)!=12:raise AssertionError('Complete horizon block')
        bs=[x['bounds'][-1] for x in cases]
        before=sum(x['pieces_before'] for x in bs);after=sum(x['pieces_after'] for x in bs)
        rows.append(f"{T} & {len(cases)} & {up(max(F(x['scalar_bound']) for x in bs))} & {up(max(F(x['max_state_bound']) for x in bs))} & {before-after} & {max(x['rational_bits_max_retained'] for x in cases)}"+r' \\')
    text=r'''\begin{table}[htbp]
\centering
\caption{Centered-risk diagnostics at residual radius $1/8$}\label{tab:centered92}
{\small\setlength{\tabcolsep}{4pt}
\begin{tabular}{rrrrrr}
\hline
Horizon & Cases & Scalar bound & State bound & Cuts & Bits \\
\hline
'''+ '\n'.join(rows)+r'''
\hline
\end{tabular}}
\par\smallskip
{\footnotesize Each horizon contains all three risk levels and four shared parameters. Bounds are maxima over that block, rounded upwards; cuts count strictly excluded risk pieces for the displayed radius. Bits is the maximum numerator or denominator bit length in the retained exact records. The complete catalogue includes all three radii, including zero. These are deterministic diagnostics, not economic observations or measured speedups.}
\end{table}
'''
    (R/'tables').mkdir(exist_ok=True);(R/'tables/centered92.tex').write_text(text)
    (R/'audit/reproduction92/TABLES92.json').write_text(json.dumps({'status':'passed','horizon_rows':7,'case_count':data['case_count'],'interval_configurations':data['interval_configurations'],'independent_inequalities':audit['exact_certificate_inequalities'],'complete_policies_enumerated':audit['complete_policies_enumerated']},indent=2)+'\n')
if __name__=='__main__':main()
