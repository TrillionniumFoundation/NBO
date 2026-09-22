"""Create a PDF/source/evidence review package, without compiler or font files.
Numerical re-execution uses the full pinned GitHub checkout, as R17 inputs are
intentionally not duplicated into this compact publication package.
"""
from pathlib import Path
import re,zipfile
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'NBO_R18_review_package.zip'
files={ROOT/n for n in ['R18_REVIEW.md','ECTA_R18.tex','ECTA_R18.pdf','SUPP_R18.tex','SUPP_R18.pdf','RESPONSE_R18.tex','RESPONSE_R18.pdf','econsocart.cls']}
files|={p for p in (ROOT/'revisions/2026-09-23-r18').rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'bootstrap' not in p.parts and p.suffix not in {'.pyc','.so'}}
# Include every repository TeX input needed by these manuscript wrappers.
todo=[p for p in files if p.suffix=='.tex'];visited=set()
while todo:
    p=todo.pop()
    if p in visited:continue
    visited.add(p)
    for name in re.findall(r'\\input\{([^}]+)\}',p.read_text()):
        q=ROOT/(name if name.endswith('.tex') else name+'.tex')
        if not q.is_file():raise FileNotFoundError(q)
        files.add(q);todo.append(q)
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(files):z.write(p,str(p.relative_to(ROOT)))
print(f'{DEST.name}: {len(files)} files, {DEST.stat().st_size} bytes')
