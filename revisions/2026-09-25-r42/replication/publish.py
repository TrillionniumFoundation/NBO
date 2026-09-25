#!/usr/bin/env python3
"""Build publication identity and verify additive preservation before commit."""
import gzip,hashlib,json,os,platform,subprocess,sys,zipfile
from fractions import Fraction as F
from pathlib import Path
import fitz
import numpy,scipy
from verify_structured import verify,mutations
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[1]
BASE_SHA='70aa68e2ecac000e16fb3a6b2c2f5ee275b6b64f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for p in sorted((BASE/'proofs').glob('*.json.gz')):
    with gzip.open(p,'rt') as f:o=json.load(f)
    if o.get('schema')!='NBO-R42-exogenous-exact-v1':raise RuntimeError('Unexpected proof schema')
    r=verify(o);r['file']=str(p.relative_to(ROOT));r['sha256']=sha(p);checks.append(r)
with gzip.open(BASE/'proofs/case00.json.gz','rt') as f:mut=mutations(json.load(f))
(BASE/'results/publication_rechecks.json').write_text(json.dumps(dict(passed=True,proofs=checks,mutations=mut),indent=2)+'\n')
suite=json.loads((BASE/'results/structured_suite.json').read_text())
assert len(suite['outcomes'])==12 and all(r['status']=='certified' and F(r['gap'])<F(9,10**8) for r in suite['outcomes'])
assert len(json.loads((BASE/'results/repair_tests.json').read_text())['cases'])==48
# Assemble a distinct historical annex; preserve the original source PDFs.
hist=fitz.open()
for name in ['ECTA_R40.pdf','SUPP_R40.pdf']:
    with fitz.open(ROOT/name) as d:hist.insert_pdf(d)
hist.save(ROOT/'HISTORY_R42.pdf');hist.close()
pages={}
for prefix in ['ECTA','SUPP','RESPONSE','COMPUTATION']:
    with fitz.open(ROOT/f'{prefix}_R42.pdf') as d:
        pages[prefix]=len(d)
        assert all(len(p.get_text().strip())>10 for p in d)
    log=(ROOT/f'{prefix}_R42.log').read_text(errors='replace')
    assert 'There were undefined references' not in log and 'undefined citations' not in log
    assert 'Overfull \\hbox' not in log, prefix+' has an overfull box'
# Compare baseline tracked content against the actual working tree.
preservation={'baseline':BASE_SHA,'passed':None,'scope':'Not a Git checkout; local PDF/source build only'}
if (ROOT/'.git').exists():
    raw=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE_SHA],cwd=ROOT,text=True)
    inherited=set(raw.splitlines());bad=[]
    changes=subprocess.check_output(['git','diff','--name-status',BASE_SHA,'--'],cwd=ROOT,text=True)
    for line in changes.splitlines():
        code,path=line.split('\t',1)
        if path in inherited and path!='REVISION_INDEX.md':bad.append(line)
    assert not bad, 'Inherited files changed: '+repr(bad)
    archive=BASE/'history/REVISION_INDEX_before_R42.md'
    assert archive.read_bytes()==subprocess.check_output(['git','show',BASE_SHA+':REVISION_INDEX.md'],cwd=ROOT)
    preservation=dict(baseline=BASE_SHA,passed=True,inherited_paths=len(inherited),except_archived_index='REVISION_INDEX.md',changes_to_inherited_scientific_files=bad)
(BASE/'results/preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
env=dict(python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,platform=platform.platform(),threads={k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']})
(BASE/'results/environment.json').write_text(json.dumps(env,indent=2)+'\n')
index='''# R42 review object\n\nCurrent manuscript: `ECTA_R42.pdf`. Technical supplement: `SUPP_R42.pdf`. Point-by-point response: `RESPONSE_R42.pdf`. Computation and verification: `COMPUTATION_R42.pdf`. Historical preservation volume: `HISTORY_R42.pdf`.\n\nBranch: `revision/econometrica-r42-atomic-structure-2026-09-25`. Base: R41 `70aa68e2ecac000e16fb3a6b2c2f5ee275b6b64f`. Addressed report: `reviews/2026-09-25-econometrica-r40/referee_report.md`.\n\nR42 adds the finite-horizon undiscounted slack ladder, an exact zero-tolerance characterization, exact unrestricted-policy atomic aggregation under exogenous dynamics, 12 independently checked larger structural LP closures, and an executed nonzero TV-reset budget. The supplement also proves a discounted infinite-horizon tail enclosure with an explicit exact-terminal trust boundary.\n\nThe structural models do not include the original action-dependent maintenance kernels. All 30 positive-cost primary randomized intervals remain open; the original nonlinear tighter-tolerance rows remain lower-only. The existing successful R41 finest-object audit is incorporated, not relabeled as a new local rerun. No empirical calibration is claimed.\n\nEvery earlier scientific file is retained. The previous current index is archived in `revisions/2026-09-25-r42/history/REVISION_INDEX_before_R42.md`. The original article and technical supplement are combined without page edits in the separate historical volume.\n\nSee `revisions/2026-09-25-r42/README.md`, `PUBLICATION_MANIFEST.json`, and the result/proof/source directories for reproduction, exact endpoints, execution classification, coverage, and preservation checks.\n'''
(ROOT/'REVISION_INDEX.md').write_text(index)
(ROOT/'R42_REVIEW.md').write_text(index)
coverage={
 'F1':'New exact atomic class and executed density transfer; original controlled atoms not covered',
 'F2':'Closed structured long-horizon cases; generic exponential burden retained',
 'F3':'Full same-object LP comparator plus unchanged prior McCormick comparison',
 'F4':'Exact medians and savings; original 30 positive gaps not closed',
 'F5':'Exact structural theorem, not a generic box-convergence claim',
 'F6':'Finest independent R41 audit incorporated; old tight-tolerance uppers not supplied',
 'F7':'12 predeclared structural cases, up to 64 states and 64 dates, 3/5 actions',
 'F8':'Witness condition extended; difficult operating-oracle experiment not supplied',
 'F9':'Nonzero full density budget, including failed sufficient tightening',
 'F10':'Stronger theory and designed service economics; no empirical calibration',
 'F11':'All new finite certificates independently checked; mathematical trust boundaries explicit',
 'F12':'Explicit compatible occupancy formulation and exact structural reduction',
 'F13':'Retained component; new equal-budget local-work ablation not executed',
 'F14':'beta=1 and zero-tolerance extensions; analytic discounted tail bridge; no average-cost claim'}
(BASE/'results/review_coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
manifest=dict(schema='NBO-R42-publication-v1',base_commit=BASE_SHA,protocol_commit='a6c6440b67210a4e6d1d75b372b5c4e59c6691a0',pages=pages,structured_cases=12,repair_tests=48,independent_proof_objects=len(checks),max_structured_gap=str(max(F(r['gap']) for r in suite['outcomes'])),preservation=preservation,inherited_finest_run=36066906929,artifacts={})
files=[p for p in BASE.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='PUBLICATION_MANIFEST.json' and 'transport' not in p.parts]
files += [ROOT/f'{prefix}_R42.{ext}' for prefix in ['ECTA','SUPP','RESPONSE','COMPUTATION'] for ext in ['tex','pdf']]+[ROOT/'HISTORY_R42.pdf',ROOT/'R42_REVIEW.md',ROOT/'REVISION_INDEX.md']
for p in sorted(files):manifest['artifacts'][str(p.relative_to(ROOT))]=dict(bytes=p.stat().st_size,sha256=sha(p))
(BASE/'PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'NBO_R42_review_package.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files+[BASE/'PUBLICATION_MANIFEST.json']:
        z.write(p,p.relative_to(ROOT))
    for name in ['econsocart.cls','econsocart.cfg','ecta-fullname.bst']:
        z.write(ROOT/name,name)
    # All R40 source dependencies and retained data used to assemble R42.
    for p in (ROOT/'revisions/2026-09-25-r40').rglob('*'):
        if p.is_file() and p.suffix not in ['.b64'] and '__pycache__' not in str(p):z.write(p,p.relative_to(ROOT))
    for name in ['ECTA_R40.pdf','SUPP_R40.pdf']:z.write(ROOT/name,name)
print(json.dumps({k:v for k,v in manifest.items() if k!='artifacts'},indent=2))
