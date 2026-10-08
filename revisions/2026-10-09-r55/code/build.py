"""Offline, non-retraining publication build for the R50 referee package.

Restores immutable historical inputs in a temporary directory, reconstructs
both R49 evidence blocks, runs exact tests and R50 record audits, regenerates
all tables and sources, and compiles all five current documents. No measured
service record or scientific source is changed. No network is accessed.
"""
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

R = Path(__file__).resolve().parents[1]
FONT_EXTENSIONS = {'.ttf', '.otf', '.woff', '.woff2', '.pfb', '.pfa', '.afm', '.tfm'}
EVIDENCE = {
    'R49-main.zip': 'd367b908c754dfa66efd5b6ed40fd6ce46a6e6606cde959811afb850b4b3c601',
    'R49-graded.zip': '280f32e6cc66344e31c5e04487cd813bdaf21908f6860d1449b2c297f4268517',
    'R48-publication.zip': 'b82272add8e7ea630ef1ab45455b079514fd848311e2d23db84d2b11ab9cd5df',
}
ENV = {**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
       'MKL_NUM_THREADS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
LOGS = R / 'audit' / 'build-logs'

def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def run(command: list[str], name: str, cwd: Path = R) -> str:
    logfile = LOGS / (name + '.log')
    with logfile.open('w') as out:
        proc = subprocess.run(command, cwd=cwd, env=ENV, stdout=out,
                              stderr=subprocess.STDOUT, check=False)
    text = logfile.read_text(errors='replace')
    if proc.returncode:
        raise RuntimeError(f'{name} failed (exit {proc.returncode}); {logfile}\n{text[-3000:]}')
    return text

def unpack(path: Path, destination: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            name = Path(item.filename)
            if name.is_absolute() or '..' in name.parts or name.suffix.lower() in FONT_EXTENSIONS:
                raise ValueError(f'Unsafe or prohibited archive member: {name}')
        archive.extractall(destination)

def tests(command: list[str], name: str, cwd: Path = R) -> dict:
    text = run(command, name, cwd)
    found = re.search(r'Ran (\d+) tests?', text)
    if not found or not re.search(r'^OK\s*$', text, re.M):
        raise RuntimeError(f'{name}: unittest success record missing')
    return {'tests': int(found[1]), 'successful': True,
            'log': str((LOGS / (name + '.log')).relative_to(R))}

def historical() -> dict:
    """Use committed ZIP bytes, not an expiring Actions download."""
    for name, expected in EVIDENCE.items():
        if digest(R / 'evidence' / name) != expected:
            raise ValueError(f'Evidence identity mismatch: {name}')
    with tempfile.TemporaryDirectory(prefix='nbo-r50-offline-') as temp:
        root = Path(temp)
        revisions = root / 'revisions'
        r48 = revisions / '2026-10-08-r48'
        r49 = revisions / '2026-10-08-r49'
        shutil.copytree(R / 'inputs' / 'revisions', revisions)
        unpack(R / 'evidence/R48-publication.zip', r48)
        unpack(R / 'evidence/R49-main.zip', r49)
        unpack(R / 'evidence/R49-graded.zip', r49)
        # The manuscript-source analyzers are retained as ordinary UTF-8 files.
        # They are not inferred from the result archives or modified here.
        for file in (R / 'inputs/revisions/2026-10-08-r49/code').glob('*.py'):
            shutil.copy2(file, r49 / 'code' / file.name)
        inherited = {
            'R49': tests([sys.executable, 'code/tests49.py'], 'inherited-r49-tests', r49),
            'graded_R49': tests([sys.executable, 'code/tests_graded49.py'], 'inherited-graded-tests', r49),
        }
        for name in ('analyze49', 'analyze_graded49', 'tables49'):
            run([sys.executable, f'code/{name}.py'], name, r49)
        corrections = []
        for path in (r49 / 'tables').glob('*.tex'):
            text = path.read_text()
            # The frozen historical table generator used a Python \v escape
            # in two epsilon headers. Correct only the derived current copy.
            fixed = text.replace('\x0barepsilon', r'\varepsilon')
            if fixed != text:
                corrections.append({'file': path.name, 'before': digest(path),
                                    'fix': 'vertical-tab + arepsilon -> LaTeX varepsilon'})
            (R / 'tables' / path.name).write_text(fixed)
        shutil.copy2(r49 / 'results-discussion49.tex', R / 'results-discussion49.tex')
        for path in (r48 / 'tables').glob('*.tex'):
            if not (R / 'tables' / path.name).exists():
                shutil.copy2(path, R / 'tables' / path.name)
        for path in (r48 / 'sections').glob('*.tex'):
            if not (R / 'sections' / path.name).exists():
                shutil.copy2(path, R / 'sections' / path.name)
        summaries = {}
        for name in ('PUBLICATION_SUMMARY', 'RESULT_AUDIT', 'GRADED_SUMMARY', 'COMBINED_EVIDENCE_SUMMARY'):
            summaries[name] = json.loads((r49 / 'audit' / (name + '.json')).read_text())
        # The separately deposited referee audit is preserved and independently rerun.
        verifier = R / 'inputs/reviews/R49/verify_r49_review.py'
        run([sys.executable, str(verifier), '--study-root', str(r49),
             '--graded-root', str(r49), '--study-zip', str(R / 'evidence/R49-main.zip'),
             '--graded-zip', str(R / 'evidence/R49-graded.zip'),
             '--output', str(R / 'audit/R49_REFEREE_REPLAY.json')], 'referee-r49-replay')
        write_json(R / 'audit/HISTORICAL_RECONSTRUCTION.json',
                   {'evidence_sha256': EVIDENCE, 'inherited_tests': inherited,
                    'derived_table_typography_corrections': corrections,
                    'summaries': summaries, 'network_used': False,
                    'historical_scientific_sources_modified': False})
        return inherited

def response() -> None:
    run(['pandoc', '-f', 'markdown', '-t', 'latex', '--wrap=auto', 'response.md',
         '-o', 'build/response-body.tex'], 'response-conversion')
    front = r'''\documentclass[ecta,nameyear,draft]{econsocart}
\input{preamble}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\begin{document}
\begin{frontmatter}
\title{Response to the Referee: Neural Bellman Operators}
\runtitle{Response to the Referee}
\begin{aug}
\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}
\address[id=add1]{Peking University}
\end{aug}
\begin{abstract}Revision R50, 8 October 2026. This response addresses the R50 threshold report and the controlling R49 substantive report. The same Neural Bellman Operators paper is revised, with all historical adverse evidence retained.\end{abstract}
\end{frontmatter}
'''
    body = (R / 'build/response-body.tex').read_text()
    body = re.sub(r'\\texttt\{([^{}]*)\}',
                  lambda m: r'\nolinkurl{' + m[1].replace(r'\_', '_') + '}', body)
    (R / 'response.tex').write_text(front + body + '\n\\end{document}\n')

def compile_document(name: str) -> dict:
    command = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
               '-output-directory=build', name + '.tex']
    run(command, name + '-pass0')
    if name != 'response':
        run([sys.executable, 'code/bibliography50.py', name], name + '-bibliography')
    for iteration in range(1, 4):
        run(command, f'{name}-pass{iteration}')
    log = (R / 'build' / (name + '.log')).read_text(errors='replace')
    bad_patterns = {
        'undefined_references': r"(?:Reference|Citation).*undefined|There were undefined references",
        'duplicate_labels': r'multiply defined|multiply-defined labels',
        'overfull_boxes': r'Overfull \\[hv]box',
        'missing_characters': r'Missing character:',
        'fatal_errors': r'^!|Fatal error',
    }
    bad = {key: re.findall(pattern, log, re.M) for key, pattern in bad_patterns.items()}
    if any(bad.values()):
        raise RuntimeError(f'Publication typography gate failed for {name}: {bad}')
    pdf = R / 'build' / (name + '.pdf')
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    return {'document': name, 'pages': int(re.search(r'^Pages:\s*(\d+)', info, re.M)[1]),
            'sha256': digest(pdf), **bad,
            'font_substitution_warnings': re.findall(r"Font shape `[^']+' undefined", log),
            'bibliography_engine': 'audited retained author-year entries; full BibTeX source preserved'}

def main() -> None:
    for executable in ('pdflatex', 'pandoc', 'pdfinfo'):
        if shutil.which(executable) is None:
            raise RuntimeError('Required publication executable missing: ' + executable)
    LOGS.mkdir(parents=True, exist_ok=True)
    (R / 'build').mkdir(exist_ok=True)
    (R / 'tables').mkdir(exist_ok=True)
    inherited = historical()
    newtests = {
        'constructive_and_improvement': tests([sys.executable, 'code/tests50.py'], 'new-exact-tests'),
        'publication_regressions': tests([sys.executable, 'code/publication_tests50.py'], 'new-publication-tests'),
    }
    run([sys.executable, 'code/audit50.py'], 'new-record-audit')
    run([sys.executable, 'code/tables50.py'], 'new-tables')
    run([sys.executable, 'code/assemble50.py'], 'assemble')
    response()
    compiled = [compile_document(name) for name in ('ECTA', 'supp', 'complete', 'complete-supp', 'response')]
    source = {}
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix.lower() in FONT_EXTENSIONS:
            continue
        relative = p.relative_to(R)
        if relative.parts[0] in ('build', 'audit'):
            continue
        source[str(relative)] = digest(p)
    write_json(R / 'audit/PUBLICATION_FILES_SHA256.json', source)
    report = {'status': 'local_build_passed',
              'referee_commit': '2822f50100c7a53ec5fe07d39e9b37d487ab0547',
              'substantive_review_commit': '4708450610c38e6b8963670cecadc887508c85c0',
              'baseline_manuscript_commit': '4ede6077aa3d78aa36ec9b9471e5338a636a49f4',
              'new_tests': newtests, 'inherited_tests': inherited,
              'total_tests': sum(v['tests'] for v in [*newtests.values(), *inherited.values()]),
              'records': json.loads((R / 'audit/RESULT_AUDIT.json').read_text()),
              'compilation': compiled, 'scientific_observations_overwritten': False,
              'network_used': False, 'remote_push_performed_by_this_builder': False,
              'publication_file_count': len(source),
              'statistical_scope': 'Conditional IID model stated in manuscript; fixed streams establish reproducibility, not mathematical independence.',
              'font_note': 'Bundled class requests a few unavailable Palatino shapes. TeX records substitutions; missing-glyph and overflow gates are separate and pass.'}
    write_json(R / 'audit/RELEASE_AUDIT.json', report)
    print(json.dumps({'total_tests': report['total_tests'], 'compilation': compiled}, indent=2))

if __name__ == '__main__':
    main()
