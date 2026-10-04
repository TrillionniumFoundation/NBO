#!/usr/bin/env python3
"""Compile the four current R16 documents and audit the final logs and PDFs.

Default: preview roots and previewbuild directory. --publication uses the
publication roots after integrate.py --write-roots has passed its ready gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]


def call(args, log, build_dir):
    with (build_dir / log).open('w') as handle:
        run = subprocess.run(args, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, timeout=300)
    if run.returncode:
        print((build_dir / log).read_text(errors='replace')[-12000:])
        raise RuntimeError('Compilation command failed: ' + ' '.join(map(str, args)))


def build(publication=False):
    if publication:
        state = json.loads((R / 'PUBLICATION_STATUS.json').read_text())
        if state.get('publication_ready') is not True:
            raise RuntimeError('Publication is not ready')
        # Reproduce the author-added shared-work table before compiling D's
        # reviewed bytes. The default table utility checks; it never rewrites.
        import sys
        subprocess.run([sys.executable, str(R / 'code/editorial_tables.py'), '--repo', str(ROOT)],
                       cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(R / 'code/editorial_hjb_diagnostics.py'), '--repo', str(ROOT)],
                       cwd=ROOT, check=True)
    target = R / ('build' if publication else 'previewbuild')
    target.mkdir(exist_ok=True)
    source = {
        name: ((ROOT / (name + '.tex') if name in ('ECTA', 'supp') else R / (name + '.tex'))
               if publication else R / 'preview' / (name + '.tex'))
        for name in ('ECTA', 'supp', 'applications', 'response')}
    for name, path in source.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        for suffix in ('.pdf', '.aux', '.bbl', '.blg', '.log', '.out', '.toc'):
            candidate = target / (name + suffix)
            if candidate.exists():
                candidate.unlink()
        refs = target / (name + '_refs.aux')
        if refs.exists():
            refs.unlink()
    for cycle in range(1, 5):
        for name, path in source.items():
            call(['pdflatex', '-no-shell-escape', '-file-line-error', '-interaction=nonstopmode',
                  '-halt-on-error', '-output-directory=' + str(target.relative_to(ROOT)),
                  str(path.relative_to(ROOT))], f'{name}.pass{cycle}.stdout', target)
            aux = (target / (name + '.aux')).read_text(errors='replace')
            # Export local labels only, preventing recursive xr-hyper imports.
            labels = [line for line in aux.splitlines() if line.startswith('\\newlabel{')]
            (target / (name + '_refs.aux')).write_text('\n'.join(labels) + '\n')
            if cycle == 1 and name != 'response':
                call(['bibtex', str((target / name).relative_to(ROOT))], f'{name}.bibtex.stdout', target)
    records = []
    for name, path in source.items():
        pdf = target / (name + '.pdf')
        log = (target / (name + '.log')).read_text(errors='replace')
        call(['pdftotext', '-layout', str(pdf), str(target / (name + '.txt'))], name + '.pdftotext.stdout', target)
        text = (target / (name + '.txt')).read_text(errors='replace')
        pdf_info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
        pages_match = re.search(r'^Pages:\s+(\d+)\s*$', pdf_info, re.M)
        records.append(dict(document=name, source=str(path.relative_to(ROOT)),
            pdf=str(pdf.relative_to(ROOT)), pages=int(pages_match.group(1)) if pages_match else None,
            sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
            undefined=bool(re.search(r'(?:Reference|Citation) .*? undefined|There were undefined', log)),
            multiply_defined=bool(re.search(r'multiply[ -]defined', log, re.I)),
            duplicate_destinations=bool(re.search(r'destination with the same identifier', log)),
            missing_characters=bool(re.search(r'Missing character:', log)),
            overfull_hbox_points=[float(x) for x in re.findall(r'Overfull \\hbox \(([-0-9.]+)pt too wide\)', log)],
            overfull_vbox_points=[float(x) for x in re.findall(r'Overfull \\vbox \(([-0-9.]+)pt too high\)', log)],
            development_text_present='Development draft.' in text))
    versions = {tool: subprocess.check_output([tool, '-v' if tool == 'pdfinfo' else '--version'],
                stderr=subprocess.STDOUT, text=True).splitlines()[0] for tool in ('pdflatex', 'bibtex', 'pdfinfo')}
    report = dict(mode='publication' if publication else 'preview', compilation_cycles=4, tool_versions=versions,
                  output_count=len(records), documents=records,
                  visual_inspection='Required separately after the final content build.')
    result = R / 'results'
    result.mkdir(exist_ok=True)
    (result / ('COMPILATION.json' if publication else 'PREVIEW_COMPILATION.json')).write_text(json.dumps(report, indent=2) + '\n')
    failures = [x for x in records if any(x[key] for key in
                ('undefined', 'multiply_defined', 'duplicate_destinations', 'missing_characters'))]
    if publication:
        failures += [x for x in records if x['development_text_present']]
        failures += [x for x in records if any(pt > 1 for pt in x['overfull_hbox_points'])]
    print(json.dumps(report, indent=2))
    if failures:
        raise RuntimeError('Final compilation diagnostics require correction')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication', action='store_true')
    build(**vars(parser.parse_args()))
