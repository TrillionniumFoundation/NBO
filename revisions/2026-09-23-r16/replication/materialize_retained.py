"""Materialize retained manuscript components from the immutable review input."""
from pathlib import Path
import subprocess,re
P=Path(__file__).resolve().parent.parent;ROOT=P.parents[1];D=P/'paper';BASE='bb09ac177fc766aea8aba26cb6a40b8aff68528c'
def old(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True)
def main():
    s=old('revisions/2026-09-22-r14/paper/main.tex')
    a=s.index(r'\section{The stopped preference');b=s.index(r'\section{A sharp economic');c=s.index(r'\section{Executed neural');d=s.index(r'\section{Conclusion}')
    (D/'retained_foundations.tex').write_text('% Preserved from R14 main: economy, verification, coefficient transport.\n'+s[a:b])
    (D/'retained_dual_state.tex').write_text('% Preserved from R14 main: dual and joint state-price construction.\n'+s[b:c])
    hist=re.sub(r'\\section\{([^}]+)\}',lambda m:r'\section{Retained R14: '+m.group(1)[0].lower()+m.group(1)[1:]+'}',s[c:d])
    hist=hist.replace('The fresh neural experiment uses','The retained R14 neural experiment uses',1)
    pre=r'\paragraph{Historical evidence retained.} The following original-economy experiments, bounds, comparisons, and welfare-resolution calculations are the R14 research record. Their sources and results are unchanged. They are not additional R16 training runs or endpoints of the fresh R16 library.'
    (D/'retained_experiments.tex').write_text(pre+'\n'+hist)
    (P/'archive').mkdir(exist_ok=True)
    (P/'archive/REVISION_INDEX_R14.md').write_text(old('REVISION_INDEX.md'))
if __name__=='__main__':main()
