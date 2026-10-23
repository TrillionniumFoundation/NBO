"""Source-only line breaking of verified R91 expressions; no gate is weakened."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1]
CHANGES={
 'sections/proofs86.tex':[(r'''\[
 \sup_{c\in\mathcal D}\{\lambda c\cdot(x-y)+p\cdot(w_x-w_y)+f\cdot(x-y)\}
 =\lambda h_{\mathcal D}(x-y)+p\cdot(w_x-w_y)+f\cdot(x-y).
\]''',r'''\begin{multline*}
 \sup_{c\in\mathcal D}\{\lambda c\cdot(x-y)+p\cdot(w_x-w_y)+f\cdot(x-y)\}\\
 =\lambda h_{\mathcal D}(x-y)+p\cdot(w_x-w_y)+f\cdot(x-y).
\end{multline*}''')],
 'sections/evidence86.tex':[(r'''\[
 \operatorname{width}=\operatorname{endpoint\ enclosure}
 +\operatorname{sampling\ variance\ allowance}
 +\operatorname{finite\ support\ allowance}.
\]''',r'''\begin{align*}
 \operatorname{width}&=\operatorname{endpoint\ enclosure}\\
 &\quad+\operatorname{sampling\ variance\ allowance}\\
 &\quad+\operatorname{finite\ support\ allowance}.
\end{align*}''')],
 'sections/risk91.tex':[(r'{\cal S}',r'\mathcal S'),
 ('Put $\\widehat T_{t,\\theta}(x)=\\inf_a\\widehat Q_{t,\\theta}(x,a)$ and assume uniform, verified bounds',r'''Put $\widehat T_{t,\theta}(x)=\inf_a\widehat Q_{t,\theta}(x,a)$ and define the signed discrepancy
\[
 D_{t,\theta}(x,a)=Q_t(f_{t+1,\theta};x,a)-\widehat Q_{t,\theta}(x,a).
\]
Assume uniform, verified bounds'''),
 (r''' b^-_{t,\theta}&\le Q_t(f_{t+1,\theta};x,a)-\widehat Q_{t,\theta}(x,a)
                              &&(a\in A_t(x)),\notag\\
 Q_t(f_{t+1,\theta};x,\pi_{t,\theta}(x))
       -\widehat Q_{t,\theta}(x,\pi_{t,\theta}(x))&\le b^{\pi,+}_{t,\theta}.''',r''' b^-_{t,\theta}&\le D_{t,\theta}(x,a)\quad(a\in A_t(x)),\notag\\
 D_{t,\theta}(x,\pi_{t,\theta}(x))&\le b^{\pi,+}_{t,\theta}.'''),
 (r'''+\gamma_{t,\theta}+b^{\pi,+}_{t,\theta}-b^-_{t,\theta}\bigr\}
       +B_T(d^+_\theta-d^-_\theta).''',r'''+\gamma_{t,\theta}+b^{\pi,+}_{t,\theta}-b^-_{t,\theta}\bigr\}\notag\\
 &\quad+B_T(d^+_\theta-d^-_\theta).''')]
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    records=[]
    for name,changes in CHANGES.items():
        p=R/name;old=p.read_text();text=old;before=sha(p)
        for a,b in changes:
            if a in text:text=text.replace(a,b)
            elif b not in text:raise AssertionError('Unrecognized expression '+name)
        if text!=old:
            backup=R/'preserved/R91-pre-layout'/name;backup.parent.mkdir(parents=True,exist_ok=True)
            if not backup.exists():shutil.copy2(p,backup)
            p.write_text(text)
        records.append({'path':name,'before_sha256':before,'after_sha256':sha(p)})
    p=R/'audit/LAYOUT91.json';p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():p.write_text(json.dumps({'status':'source_edits_applied','files':records,'scope':'Exact expressions retained; actual compiler and visual checks remain separate.'},indent=2)+'\n')
if __name__=='__main__':main()
