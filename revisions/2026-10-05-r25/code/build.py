"""Native R25 econsocart build, peer-reference convergence and source-bound release.

No journal class or font file is altered. A document with no citations does
not trigger BibTeX. The inherited failure remains recorded in the release audit.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import zipfile
ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
B = R / 'build'
DOCS = ('ECTA', 'supp', 'applications', 'evidence', 'response')

def command(args, log):
    with (B / log).open('w') as out:
        p = subprocess.run(args, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, timeout=300)
    if p.returncode:
        raise RuntimeError(' '.join(map(str, args)) + '\n' + (B / log).read_text(errors='replace')[-18000:])

def build():
    B.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        for ext in ('aux', 'bbl', 'blg', 'log', 'out', 'toc', 'pdf', 'fls'):
            (B / f'{name}.{ext}').unlink(missing_ok=True)
        (B / f'{name}_refs.aux').unlink(missing_ok=True)
    bibliography = []
    for cycle in range(1, 6):
        for name in DOCS:
            command(['pdflatex', '-no-shell-escape', '-recorder', '-file-line-error', '-interaction=nonstopmode', '-halt-on-error', '-output-directory=' + str(B.relative_to(ROOT)), str((R / f'{name}.tex').relative_to(ROOT))], f'{name}.pass{cycle}.stdout')
            aux = (B / f'{name}.aux').read_text(errors='replace')
            (B / f'{name}_refs.aux').write_text('\n'.join((s for s in aux.splitlines() if s.startswith('\\newlabel{'))) + '\n')
            if cycle == 1:
                cited = bool(re.search('\\\\citation\\{', aux))
                has_bib = bool(re.search('\\\\bibdata\\{', aux))
                bibliography.append({'document': name, 'citations_present': cited, 'bibliography_present': has_bib, 'bibtex_run': cited and has_bib})
                if cited and has_bib:
                    command(['bibtex', str((B / name).relative_to(ROOT))], f'{name}.bibtex.stdout')
    records = []
    for name in DOCS:
        log = (B / f'{name}.log').read_text(errors='replace')
        pdf = B / f'{name}.pdf'
        info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
        command(['pdftotext', '-layout', str(pdf), str(B / f'{name}.txt')], f'{name}.text.stdout')
        records.append({'document': name, 'source': str((R / f'{name}.tex').relative_to(ROOT)), 'pages': int(re.search('^Pages:\\s+(\\d+)', info, re.M)[1]), 'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'undefined': bool(re.search('(?:Reference|Citation).* undefined|There were undefined', log)), 'multiply_defined': bool(re.search('multiply[ -]defined', log, re.I)), 'duplicate_destination': 'destination with the same identifier' in log, 'missing_character': 'Missing character:' in log, 'overfull_hbox': [float(x) for x in re.findall('Overfull \\\\hbox \\(([-0-9.]+)pt too wide\\)', log)], 'overfull_vbox': [float(x) for x in re.findall('Overfull \\\\vbox \\(([-0-9.]+)pt too high\\)', log)]})
    report = {'class_name': 'econsocart', 'options': 'ecta,nameyear,draft', 'cycles': 5, 'documents': records, 'bibliography': bibliography, 'visual_inspection': 'Selected page images are rendered separately; log checks do not themselves constitute visual inspection.'}
    (R / 'results/COMPILATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)
    for rec in records:
        assert not any((rec[k] for k in ('undefined', 'multiply_defined', 'duplicate_destination', 'missing_character'))), rec
        assert not any((v > 1 for v in rec['overfull_hbox'] + rec['overfull_vbox'])), rec


def tests():
    import sys
    suites=[]
    for name,folder in [('R25','2026-10-05-r25'),('R24','2026-10-05-r24'),('R23','2026-10-05-r23'),('R21','2026-10-05-r21'),('R19','2026-10-05-r19-integrated')]:
        path=ROOT/'revisions'/folder/'code'
        run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(path),'-p','test*.py','-v'],cwd=ROOT,capture_output=True,text=True)
        text=run.stdout+run.stderr
        (R/'results'/('TESTS_'+name+'.log')).write_text(text)
        found=re.search(r'Ran (\d+) tests?',text)
        skipped=re.search(r'OK \(skipped=(\d+)\)',text)
        rec={'suite':name,'tests':int(found[1]) if found else 0,'skipped':int(skipped[1]) if skipped else 0,'returncode':run.returncode}
        suites.append(rec)
        (R/'results/TESTS_ALL.json').write_text(json.dumps(suites,indent=2)+'\n')
        print('TEST_SUITE',rec,flush=True)
        assert run.returncode==0 and found,text[-10000:]
        if os.environ.get('GITHUB_ACTIONS')=='true':assert not rec['skipped'],rec
    return suites


def release():
    build()
    compilation=json.loads((R/'results/COMPILATION.json').read_text())
    preservation=json.loads((R/'PRESERVATION.json').read_text())
    construction=json.loads((R/'results/CONSTRUCTION_AUDIT.json').read_text())
    replay=json.loads((R/'results/inherited_r23/REPLAY.json').read_text())
    refinement=json.loads((R/'results/inherited_r24/REFINEMENT.json').read_text())
    tested=json.loads((R/'results/TESTS_ALL.json').read_text())
    previews=R/'results/previews';previews.mkdir(exist_ok=True)
    desired={'ECTA':{'prop:r25isotropic','thm:r25finitepolicy','tab:r25construction','prop:r24learning'},'supp':{'sec:r25proofs','sec:r25record'},'applications':set(),'evidence':set(),'response':set()}
    rendered=[]
    for name,labels in desired.items():
        pages={1}
        for line in (B/(name+'_refs.aux')).read_text().splitlines():
            m=re.match(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{(\d+)\}',line)
            if m and m[1] in labels:pages.add(int(m[2]))
        for page in sorted(pages):
            dest=previews/f'{name}-p{page}'
            subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r','110','-singlefile','-png',str(B/(name+'.pdf')),str(dest)],check=True)
            rendered.append({'document':name,'page':page,'path':str(dest.with_suffix('.png').relative_to(ROOT))})
    (R/'results/RENDERED_PAGES.json').write_text(json.dumps(rendered,indent=2)+'\n')
    audit={'publication_source_commit':os.environ.get('GITHUB_SHA','local source-bound validation'),
           'experiment_source_commit':'9bf608d5154dfb61ff0ab209c2b66d1f8dbcc148',
           'review_commit':'281e57b18a2d88de68d2219da1a7194e90570d13',
           'inheritance_commit':'00f834b2d0ad259a0ffc70868dce416d183002ba',
           'native_documents':compilation['documents'],'tests':tested,
           'new_services':construction['services'],'new_certified':construction['certified'],
           'new_training_dates':construction['training_dates'],'new_targets_met':construction['training_targets_met'],
           'initial_dates_outside_old_basin':construction['initial_dates_outside_old_local_basin'],
           'new_maximum_policy_bound':construction['maximum_policy_bound'],
           'inherited_candidates_replayed':replay['candidate_hashes_verified'],
           'inherited_failed_checks_retained':refinement['original_failed_checks'],
           'symmetric_refinement_replayed':refinement['candidate_hashes_verified'],
           'refinement_resolved_checks':refinement['newly_resolved_original_failures'],
           'preservation':preservation,
           'history':{'r24_failed_run':37323807665,'failure':'Native layout: 3.72244pt and 3.35576pt horizontal overflows. Corrected with displayed mathematics in R25-owned copies; no old source or overflow limit changed.'},
           'scope':'Constructive finite trained-factor policy theorem and complete frozen execution. The structural comparator remains cheaper. No calibration, general neural superiority or continuous-time transfer inferred.',
           'visual_check':'Selected rendered pages are supplied for manual inspection; successful log checks alone are not visual approval.'}
    (R/'RELEASE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    inputs=set()
    ignored={'.aux','.out','.log','.fls','.toc','.pfb','.pfm','.ttf','.otf','.tfm','.afm','.pk'}
    for name in DOCS:
        for line in (B/(name+'.fls')).read_text(errors='replace').splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=(p if p.is_absolute() else ROOT/p).resolve()
            if p.is_relative_to(ROOT) and p.is_file() and p.suffix not in ignored:inputs.add(p)
        inputs.update([B/(name+'.pdf'),B/(name+'.log')])
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in str(p) or '/build/' in str(p) or '/previews/' in str(p):continue
        if p.name in ('BUILD_RUN.log','PUBLICATION_FILES_SHA256.json') or '/delivery/' in str(p):continue
        if p.suffix in ('.json','.jsonl','.tex','.bib','.md','.py','.txt','.log','.npz'):inputs.add(p)
    for p in ROOT.glob('*.bib'):inputs.add(p)
    for p in ROOT.glob('*.bst'):inputs.add(p)
    for p in list(inputs):
        if p.suffix=='.tex':
            for group in re.findall(r'\\bibliography\{([^}]+)\}',p.read_text()):
                for name in group.split(','):
                    q=ROOT/(name.strip()+'.bib')
                    if q.exists():inputs.add(q)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)}
    (R/'PUBLICATION_FILES_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    out=Path('/tmp/NBO_R25_publication.zip')
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(inputs):z.write(p,str(p.relative_to(ROOT)))
        z.write(R/'PUBLICATION_FILES_SHA256.json',str((R/'PUBLICATION_FILES_SHA256.json').relative_to(ROOT)))
    print('PUBLICATION_ARCHIVE',out,out.stat().st_size,hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
    print('RELEASE_AUDIT',json.dumps({k:v for k,v in audit.items() if k!='preservation'},indent=2),flush=True)


if __name__=='__main__':
    tests()
    release()
