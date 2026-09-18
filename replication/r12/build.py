"""Build and preflight all manuscripts, then prepare a preservation receipt."""
from __future__ import annotations
import hashlib,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];os.chdir(ROOT)
REV=Path('revisions/2026-09-18-r12-procurement-witness');REV.mkdir(exist_ok=True)
def command(*args):return subprocess.check_output(args,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
subprocess.run(['python','replication/r12/render_tables.py'],check=True)
for name in ('ECTA_R12','COMPENDIUM_R12','SUPP_R12'):
    with (REV/(name+'_build.log')).open('w') as log:
        subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error',name+'.tex'],stdout=log,stderr=subprocess.STDOUT,check=True)
    txt=Path(name+'.log').read_text(errors='replace')
    for bad in ('undefined references','undefined citations','There were multiply defined','Overfull \\hbox','!  ==> Fatal'):
        if bad in txt:raise RuntimeError(name+': '+bad)
    if name!='SUPP_R12':
        aux=Path(name+'.aux').read_text()
        Path(name+'_xrefs.aux').write_text('\n'.join(line for line in aux.splitlines() if line.startswith('\\newlabel'))+'\n')
    shutil.copy2(name+'.pdf',REV/(name+'.pdf'))
    shutil.copy2(name+'.log',REV/(name+'.log'))
import fitz
pdfs={}
for name in ('ECTA_R12','COMPENDIUM_R12','SUPP_R12'):
    p=REV/(name+'.pdf');doc=fitz.open(p)
    if any('??' in page.get_text() for page in doc):raise RuntimeError('unresolved PDF text '+name)
    pdfs[name]=dict(pages=len(doc),sha256=sha(p))
    for i in sorted({0,len(doc)-1,*([5,7,9] if name=='ECTA_R12' else [])}):
        if i<len(doc):doc[i].get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(REV/(name+f'_page_{i+1}.png'))
source=os.getenv('R12_SOURCE_SHA',os.getenv('GITHUB_SHA','local-development'))
identity=json.loads(Path('replication/r12/output/expected.json').read_text())
validation=json.loads(Path('replication/r12/output/independent_validation.json').read_text())
generation=json.loads(Path('replication/r12/output/execution.json').read_text())
receipt=dict(scientific_source_commit=generation['source_commit'],verification_source_commit=source,review_parent='442b009379402df7da354eacb4ff8f82d44cdce7',canonical_manifest_sha256=identity['canonical_manifest_sha256'],witness_manifest_sha256=sha('replication/r12/output/expected.json'),validation_sha256=sha('replication/r12/output/independent_validation.json'),pdfs=pdfs,workflow_run=os.getenv('GITHUB_RUN_ID'),validation_scope=validation['scope'])
if Path('.git').exists():
    base=receipt['review_parent'];paths=command('git','ls-tree','-r','--name-only',base).splitlines();preserved=0
    for path in paths:
        if path=='REVISION_INDEX.md':continue
        original=subprocess.check_output(['git','show',base+':'+path])
        if not Path(path).is_file() or Path(path).read_bytes()!=original:raise RuntimeError('historical file altered: '+path)
        preserved+=1
    receipt['historical_paths_preserved']=preserved
    receipt['scientific_source_files']={str(p):sha(p) for p in sorted(Path('replication/r12').glob('*.py'))}
(REV/'execution_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(REV/'README.md').write_text('# R12 — Neural Bellman Operators\n\nRead `ECTA_R12.pdf` first, `SUPP_R12.pdf` for complete proofs, and `COMPENDIUM_R12.pdf` for the full preserved theoretical and computational development. See `response_to_referee.md` and `preservation_map.md`.\n\nSource, canonical target, witness and verification identities are recorded separately in `execution_receipt.json`. The final deposit commit contains this directory; the scientific run is attributed to its recorded source commit, not retroactively to that deposit.\n\nReproduction: `python replication/r12/verify.py` from the repository root reads committed canonical inputs and validates the mathematical witnesses.\n')
if Path('.git').exists():
    index=Path('REVISION_INDEX.md');old=index.read_text();entry='## R12 — Procurement, service, and witness reconstruction (2026-09-18)'
    if entry not in old:
        index.write_text(old+'\n\n'+entry+'\n\nAuthoritative main: `ECTA_R12.tex`; complete proofs: `SUPP_R12.tex`; preserved full development: `COMPENDIUM_R12.tex`. PDFs, response and receipts: `revisions/2026-09-18-r12-procurement-witness/`. Reproduction: `replication/r12/README.md`. Scientific-source identity is in the execution receipt; the final deposit is the branch head containing these outputs. This is a substantive revision, not an alias of a review branch.\n')
print(json.dumps(receipt,indent=2))
