"""Native econsocart build, peer-reference convergence and source-bound release.

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
        raise RuntimeError(' '.join(map(str, args)) + '\n' +
                           (B / log).read_text(errors='replace')[-18000:])


def build():
    B.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        for ext in ('aux', 'bbl', 'blg', 'log', 'out', 'toc', 'pdf', 'fls'):
            (B / f'{name}.{ext}').unlink(missing_ok=True)
        (B / f'{name}_refs.aux').unlink(missing_ok=True)
    bibliography = []
    for cycle in range(1, 6):
        for name in DOCS:
            command(['pdflatex', '-no-shell-escape', '-recorder', '-file-line-error',
                     '-interaction=nonstopmode', '-halt-on-error',
                     '-output-directory=' + str(B.relative_to(ROOT)),
                     str((R / f'{name}.tex').relative_to(ROOT))],
                    f'{name}.pass{cycle}.stdout')
            aux = (B / f'{name}.aux').read_text(errors='replace')
            (B / f'{name}_refs.aux').write_text('\n'.join(
                s for s in aux.splitlines() if s.startswith(r'\newlabel{')) + '\n')
            if cycle == 1:
                cited = bool(re.search(r'\\citation\{', aux))
                has_bib = bool(re.search(r'\\bibdata\{', aux))
                bibliography.append({'document': name, 'citations_present': cited,
                                     'bibliography_present': has_bib,
                                     'bibtex_run': cited and has_bib})
                if cited and has_bib:
                    command(['bibtex', str((B / name).relative_to(ROOT))],
                            f'{name}.bibtex.stdout')
    records = []
    for name in DOCS:
        log = (B / f'{name}.log').read_text(errors='replace')
        pdf = B / f'{name}.pdf'
        info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
        command(['pdftotext', '-layout', str(pdf), str(B / f'{name}.txt')],
                f'{name}.text.stdout')
        records.append({
            'document': name, 'source': str((R / f'{name}.tex').relative_to(ROOT)),
            'pages': int(re.search(r'^Pages:\s+(\d+)', info, re.M)[1]),
            'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
            'undefined': bool(re.search(r'(?:Reference|Citation).* undefined|There were undefined', log)),
            'multiply_defined': bool(re.search(r'multiply[ -]defined', log, re.I)),
            'duplicate_destination': 'destination with the same identifier' in log,
            'missing_character': 'Missing character:' in log,
            'overfull_hbox': [float(x) for x in re.findall(r'Overfull \\hbox \(([-0-9.]+)pt too wide\)', log)],
            'overfull_vbox': [float(x) for x in re.findall(r'Overfull \\vbox \(([-0-9.]+)pt too high\)', log)]})
    report = {'class_name': 'econsocart', 'options': 'ecta,nameyear,draft',
              'cycles': 5, 'documents': records, 'bibliography': bibliography,
              'visual_inspection': 'Selected page images are rendered separately; '
                                   'log checks do not themselves constitute visual inspection.'}
    (R / 'results/COMPILATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)
    for rec in records:
        assert not any(rec[k] for k in ('undefined', 'multiply_defined',
                                       'duplicate_destination', 'missing_character')), rec
        assert not any(v > 1 for v in rec['overfull_hbox'] + rec['overfull_vbox']), rec
    previews = R / 'results/previews'
    previews.mkdir(exist_ok=True)
    wanted = {'ECTA': {'prop:r24learning', 'prop:r24energy', 'tab:r23frontier'},
              'supp': {'sec:r24record'}, 'applications': set(),
              'evidence': set(), 'response': set()}
    rendered = []
    for name, labels in wanted.items():
        pages = {1}
        for line in (B / f'{name}_refs.aux').read_text().splitlines():
            m = re.match(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{(\d+)\}', line)
            if m and m[1] in labels:
                pages.add(int(m[2]))
        for page in sorted(pages):
            dest = previews / f'{name}-p{page}'
            subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-r', '110',
                            '-singlefile', '-png', str(B / f'{name}.pdf'), str(dest)], check=True)
            rendered.append({'document': name, 'page': page,
                             'path': str(dest.with_suffix('.png').relative_to(ROOT))})
    (R / 'results/RENDERED_PAGES.json').write_text(json.dumps(rendered, indent=2) + '\n')
    tests = json.loads((R / 'results/TESTS_ALL.json').read_text())
    refinement = json.loads((R / 'results/REFINEMENT.json').read_text())
    preservation = json.loads((R / 'PRESERVATION.json').read_text())
    replay = json.loads((R / 'results/inherited_r23/REPLAY.json').read_text())
    release = {
        'source_commit': os.environ.get('GITHUB_SHA'),
        'review_commit': '281e57b18a2d88de68d2219da1a7194e90570d13',
        'integration_base': 'c327e0f4f1d5c8c6381dfe0f2b6001fbd7bb7f96',
        'native_documents': records, 'tests': tests,
        'original_candidates_replayed': replay['candidate_hashes_verified'],
        'original_stopping_decisions_replayed': replay['replayed_decisions_agree'],
        'refinement_candidates_replayed': refinement['candidate_hashes_verified'],
        'newly_resolved_original_failures': refinement['newly_resolved_original_failures'],
        'original_failed_checks_retained': refinement['original_failed_checks'],
        'missing_inherited_labels': preservation['missing_inherited_labels'],
        'modified_or_deleted_inherited_files': preservation['modified_or_deleted_inherited_tracked_files'],
        'history': [
            {'run': 37312535231, 'result': 'R23 publication stopped because inherited R19 tests needed torch; original failure retained.'},
            {'run': 37313934492, 'result': 'R23 tests passed; publication stopped at BibTeX for the citation-free evidence document. R24 fixes the build without changing the journal class or primary evidence.'}],
        'claims': 'New finite-step and residual-energy results; inherited fits and primary clocks are not replaced. No new neural cost-superiority trial is claimed.',
        'manifest_scope': 'The live BUILD_RUN.log stream is excluded; stable per-document logs, PDFs, source and evidence are retained separately.'}
    (R / 'RELEASE_AUDIT.json').write_text(json.dumps(release, indent=2) + '\n')
    inputs = set()
    ignored = {'.aux', '.out', '.log', '.fls', '.toc', '.pfb', '.pfm', '.ttf', '.otf', '.tfm', '.afm', '.pk'}
    for name in DOCS:
        for line in (B / f'{name}.fls').read_text(errors='replace').splitlines():
            if not line.startswith('INPUT '): continue
            p = Path(line[6:])
            p = (p if p.is_absolute() else ROOT / p).resolve()
            if p.is_relative_to(ROOT) and p.is_file() and p.suffix not in ignored:
                inputs.add(p)
        inputs.add(B / f'{name}.pdf')
        inputs.add(B / f'{name}.log')
    for sub in ('code', 'manuscript', 'archive'):
        for p in (R / sub).rglob('*'):
            if p.is_file() and '__pycache__' not in str(p): inputs.add(p)
    for p in (R / 'results').rglob('*'):
        if p.name == 'BUILD_RUN.log':
            continue  # tee is still appending the stdout of this process.
        if p.is_file() and p.suffix in ('.json', '.jsonl', '.tex', '.log', '.txt'):
            inputs.add(p)
    for p in R.iterdir():
        if p.is_file() and p.name != 'PUBLICATION_FILES_SHA256.json': inputs.add(p)
    for p in ROOT.glob('*.bib'): inputs.add(p)
    for p in ROOT.glob('*.bst'): inputs.add(p)
    for p in list(inputs):
        if p.suffix == '.tex':
            for group in re.findall(r'\\bibliography\{([^}]+)\}', p.read_text()):
                for name in group.split(','):
                    q = ROOT / (name.strip() + '.bib')
                    if q.exists(): inputs.add(q)
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(inputs)}
    (R / 'PUBLICATION_FILES_SHA256.json').write_text(json.dumps(manifest, indent=2) + '\n')
    archive = Path('/tmp/NBO_R24_publication.zip')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(inputs): z.write(p, str(p.relative_to(ROOT)))
        z.write(R / 'PUBLICATION_FILES_SHA256.json', str((R / 'PUBLICATION_FILES_SHA256.json').relative_to(ROOT)))
    print('PUBLICATION_ARCHIVE', archive, archive.stat().st_size,
          hashlib.sha256(archive.read_bytes()).hexdigest(), flush=True)
    print('RELEASE_AUDIT', json.dumps(release, indent=2), flush=True)
    return report


if __name__ == '__main__':
    build()
