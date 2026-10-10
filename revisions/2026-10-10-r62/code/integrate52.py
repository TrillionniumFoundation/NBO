"""One-time additive manuscript integration, before science and publication.

All four resulting ordinary manuscript sources are committed before the
new numerical run. The offline builder never needs this staging operation.
"""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1]
NEW_CODE={'contrast52.py','tests52.py','study52.py','audit52.py','build52.py','integrate52.py','publish52.py'}
def main():
    P=R/'preserved/R51'
    if P.exists():raise FileExistsError('The predecessor has already been preserved')
    P.mkdir()
    for n in ('ECTA.tex','supp.tex','complete.tex','complete-supp.tex','response.tex','README.md'):
        shutil.copy2(R/n,P/n)
    shutil.copy2(R/'response.md',P/'response.md')
    shutil.copy2(R/'response52.md',R/'response.md')
    retained={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and p.relative_to(R).parts[0] in ('code','inputs','evidence','preserved','results') and '__pycache__' not in p.parts and not(p.parent==R/'code' and p.name in NEW_CODE)}
    (R/'audit/INHERITANCE52.json').write_text(json.dumps({'predecessor_commit':'62ffa8d0753c82a1363831f49a297c815d89204f','retained_sha256':retained},indent=2,sort_keys=True)+'\n')
    abstract='''This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. A constructive continuation retains feasible action witnesses, with policy-identical native and affine--ReLU realizations. Signed own-policy evaluation bands give an acquisition-aware improvement gate. We strengthen its finite-sweep accuracy account by certifying the action contrasts of continuation errors rather than their global width. Coupled Bellman residuals supply constructive certificates; verified action-null components, including a nonconstant one-unit ReLU in the original investment model, need not consume the improvement budget. Under exact contrast, search and comparison conditions, optimality follows within the finite horizon without intermediate cost increases. The investment study separates construction, certification, actual costs and verification work, applying the same terminal improvement to witness and FVI incumbents. An exhaustive observation-cell ablation tests robustness to action-null errors without creating new cost observations. The inherited direct comparisons generally favor FVI despite own-incumbent gains. Complete development editions preserve the original theory, applications and adverse evidence.'''
    intro='''The relevant continuation error can be smaller than its global range. We show that a coupled-residual certificate controls the error in feasible action comparisons, and use it in a stronger finite-sweep bound for the same Bellman optimum. A verified nonconstant action-null component need not consume any improvement budget. The original investment dynamics admit an explicit one-unit ReLU example. An exhaustive observation-cell diagnostic holds the returned economic policies fixed while varying this nuisance; it tests certificate robustness, not another expected-cost ranking.\n\n'''
    for n in ('ECTA','complete'):
        p=R/(n+'.tex');text=p.read_text()
        text=text.replace(r'\input{sections/finite_sweeps51}',r'\input{sections/finite_sweeps51}'+'\n'+r'\input{sections/action_contrast52}')
        text=text.replace(r'\input{sections/study51}',r'\input{sections/study51}'+'\n'+r'\input{sections/study52}')
        text=text.replace('active R51 exposition','active R52 exposition').replace('current R51 argument','current R52 argument').replace('Current R51 development','Current R52 development')
        if n=='ECTA':
            text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+abstract+'\n'+m[2],text,flags=re.S)
            text=text.replace(r'\input{sections/core49}',intro+r'\input{sections/core49}',1)
            text=text.replace('Neural Bellman Operators therefore provide','The action-contrast result further separates continuation representation from decision-relevant error. Its coupled-residual certificate and action-null correction preserve the same safety and optimality targets. The exhaustive cell study checks an exact robustness property on the original economy; its identical returned policies do not supply additional independent cost observations.\n\nNeural Bellman Operators therefore provide')
        p.write_text(text)
    for n in ('supp','complete-supp'):
        p=R/(n+'.tex');text=p.read_text()
        text=text.replace(r'\input{sections/finite_sweeps_proofs51}',r'\input{sections/finite_sweeps_proofs51}'+'\n'+r'\input{sections/contrast_proofs52}')
        text=text.replace(r'\bibliographystyle',r'\section{Exhaustive robustness-service accounting}\label{supp:work52}'+'\n'+r'\input{tables/work52}'+'\n'+r'\bibliographystyle',1)
        text=text.replace('and the R51 revision','and the R52 revision').replace('current R51 argument','current R52 argument').replace('Current R51 development','Current R52 development')
        p.write_text(text)
    shutil.copy2(R/'README52.md',R/'README.md')
if __name__=='__main__':main()
