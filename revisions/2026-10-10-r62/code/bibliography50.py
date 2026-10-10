"""Deterministic author-year bibliography from retained, audited ECTA entries.

The full BibTeX source is preserved. This fallback removes a build-time
BibTeX executable dependency; it does not infer metadata from citations.
"""
from pathlib import Path
import re,json,sys
R=Path(__file__).resolve().parents[1]
def render(name):
    entries=json.loads((R/'publication/bibliography-entries.json').read_text())
    aux=(R/'build'/f'{name}.aux').read_text();keys={v for m in re.findall(r'\\citation\{([^}]+)\}',aux) for v in m.split(',')}
    if '*' in keys:keys=set(entries)
    missing=keys-set(entries)
    if missing:raise ValueError('Unmaterialized reference metadata: '+str(missing))
    ordered=sorted(keys,key=lambda k:re.search(r'\\textsc\{([^}]+)',entries[k])[1].lower())
    text=r'\begin{thebibliography}{'+str(len(keys))+'}\n'+r'\newcommand{\enquote}[1]{``#1\x27\x27}'.replace(r'\x27',"'")+'\n'+r'\expandafter\ifx\csname natexlab\endcsname\relax\def\natexlab#1{#1}\fi'+'\n\n'
    text+='\n\n'.join(entries[k] for k in ordered)+'\n\n\\end{thebibliography}\n'
    (R/'build'/f'{name}.bbl').write_text(text)
    return ordered
if __name__=='__main__':print(render(sys.argv[1]))
