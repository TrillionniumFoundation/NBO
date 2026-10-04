#!/usr/bin/env python3
"""Build four R16 reading roots with a complete, checked R15 preservation map.

The default writes preview roots only. Publication requires an explicit ready
manifest and --write-roots; the original R15 roots are checked before archiving.
Scientific modules are inputs, never rewritten by this editorial program.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
M = R / 'manuscript'
R15 = 'revisions/2026-10-04-r15/'
COMMIT = '1cb3cc9efe135966ec228dfaf51c6841a6dfc97c'
REVIEW = 'cb4595bbcc7147e47e44ba40cb2f5034510ae19f'
LABEL = re.compile(r'\\label\{([^}]+)\}')
INPUT = re.compile(r'\\(?:input|include)\{([^}]+)\}')
REF = re.compile(r'\\(?:ref|eqref|autoref|pageref)\{([^}]+)\}')
ENV = re.compile(r'\\begin\{(theorem|proposition|lemma|corollary|assumption|proof)\}(.*?)\\end\{\1\}', re.S)
HEADING = re.compile(r'\\(section|subsection|subsubsection|paragraph)\*?\{([^\n]*)\}')
ROOT_BLOBS = {'ECTA.tex': '32953ff2500f3af8a491cf1dd710276d2d77bdbf',
              'supp.tex': '50eac8d04b25b6521780d4e07b9617b377168e88'}
EDITORIAL_REPLACEMENTS = {'introduction.tex', 'literature.tex', 'conclusion.tex', 'archive_index.tex'}
PROSE_CORRECTIONS = (
    ('The capital economy studied below provides', 'The capital economy studied above provides'),
    ('Supplementary Sections~\\ref{sec:ndu}', 'Application Sections~\\ref{sec:ndu}'),
    ('Supplementary Section~\\ref{sec:recursive}', 'Application Section~\\ref{sec:recursive}'),
    ('Supplementary Section~\\ref{sec:temporal}', 'Application Section~\\ref{sec:temporal}'),
    ('Supplementary Sections~\\ref{sec:games}', 'Application Sections~\\ref{sec:games}'),
    ('the finite-policy study finite study trains', 'the finite-policy study trains'),
    ('Second, continuous-action study trains', 'Second, the continuous-action study trains'),
    ('does not. continuous-action study additionally', 'does not. The continuous-action study additionally'),
    ('\ncontinuous-action study adds', '\nThe continuous-action study adds'),
    ('\\caption{continuous-action study actor-free dynamic-game comparisons}',
     '\\caption{Continuous-action study: actor-free dynamic-game comparisons}'),
    ('response. finite-policy study and continuous-action study timings',
     'response. The finite-policy and continuous-action study timings'),
)
_SOURCE = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def git_source(path):
    if path not in _SOURCE:
        _SOURCE[path] = subprocess.check_output(['git', 'show', f'{COMMIT}:{path}'], cwd=ROOT)
    return _SOURCE[path]


def retained_path(path):
    if not path.startswith(R15):
        raise ValueError('Unexpected component outside reviewed R15: ' + path)
    return R / 'retained' / path.removeprefix(R15)


def normalize_source(text):
    """Ignore comments, paths, and the enumerated prose corrections, never mathematics."""
    for old, new in PROSE_CORRECTIONS:
        text = text.replace(old, new)
    return normalize_mathematics(text)


def normalize_mathematics(text):
    """The proof audit permits no prose replacements inside statements or proofs."""
    text = re.sub(r'%[^\n]*', '', text)
    text = text.replace(relative(R / 'retained') + '/', R15)
    return re.sub(r'\s+', ' ', text).strip()


def archive_roots(inventory):
    records = []
    (R / 'archive').mkdir(exist_ok=True)
    by_path = {x['path']: x for x in inventory['files']}
    for name in ['ECTA.tex', 'supp.tex', 'README.md']:
        data = git_source(name)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        expected = ROOT_BLOBS.get(name)
        if expected and blob != expected:
            raise RuntimeError('Reviewed root Git blob mismatch: ' + name)
        if name in by_path and digest(data) != by_path[name]['sha256']:
            raise RuntimeError('Reviewed root SHA256 mismatch: ' + name)
        dest = R / 'archive' / ('r15-' + name)
        if dest.exists() and dest.read_bytes() != data:
            raise RuntimeError('Refusing to replace a different archived root: ' + str(dest))
        dest.write_bytes(data)
        records.append(dict(source=name, destination=relative(dest), git_blob=blob,
                            sha256=digest(data), exact_bytes_verified=dest.read_bytes() == data))
    report = dict(reviewed_publication_commit=COMMIT, referee_commit=REVIEW, roots=records)
    (R / 'ARCHIVE_MANIFEST.json').write_text(json.dumps(report, indent=2) + '\n')
    return records


def materialize_retained(inventory):
    records = []
    for item in inventory['files']:
        path = item['path']
        data = git_source(path)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if digest(data) != item['sha256'] or blob != item['git_blob']:
            raise RuntimeError('Reviewed component identity mismatch: ' + path)
        if path in ROOT_BLOBS:
            continue
        dest = retained_path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        original = data.decode()
        rendered = INPUT.sub(lambda m: '\\input{' + relative(retained_path(m.group(1))) + '}', original)
        corrections = []
        for old, new in PROSE_CORRECTIONS:
            count = rendered.count(old)
            if count:
                corrections.append(dict(original=old, corrected=new, occurrences=count))
                rendered = rendered.replace(old, new)
        dest.write_text('% R15 component; only input paths and enumerated location/grammar prose are edited.\n'
                        + '% Source: ' + path + '; commit ' + COMMIT + '.\n' + rendered)
        records.append(dict(source=path, destination=relative(dest), source_sha256=item['sha256'],
                            current_sha256=digest(dest.read_bytes()),
                            prose_corrections=corrections,
                            equal_after_documented_editorial_normalization=
                            normalize_source(original) == normalize_source(dest.read_text())))
    if not all(x['equal_after_documented_editorial_normalization'] for x in records):
        raise RuntimeError('A retained source component changed beyond its input path')
    return records


def inp(path):
    return '\\input{' + relative(path) + '}\n'


def inherited(name):
    return R / 'retained/manuscript' / name


def flatten(text, document, locations, used, ancestry=()):
    for label in LABEL.findall(text):
        locations[label].append(dict(document=document, file=ancestry[-1] if ancestry else document))
    def replace(match):
        path = ROOT / match.group(1)
        if not path.suffix:
            path = path.with_suffix('.tex')
        key = relative(path)
        if key in ancestry:
            raise RuntimeError('Cyclic TeX input: ' + key)
        if not path.is_file():
            raise FileNotFoundError(path)
        used[document].append(key)
        return flatten(path.read_text(), document, locations, used, ancestry + (key,))
    return INPUT.sub(replace, text)


def proof_headings(text):
    """Capture whole proof sections, including proofs not in proof environments."""
    levels = {'section': 0, 'subsection': 1, 'subsubsection': 2, 'paragraph': 3}
    headings = list(HEADING.finditer(text))
    for i, match in enumerate(headings):
        if not re.search(r'\bproofs?\b', match.group(2), re.I):
            continue
        end = len(text)
        for other in headings[i + 1:]:
            if levels[other.group(1)] <= levels[match.group(1)]:
                end = other.start()
                break
        yield match, text[match.start():end]


def verify_preservation(inventory, flattened, locations, used, retained_records):
    corpus = normalize_mathematics('\n'.join(flattened.values()))
    current_env = {normalize_mathematics(m.group(0)) for m in ENV.finditer('\n'.join(flattened.values()))}
    environment_records, heading_records = [], []
    for item in inventory['files']:
        path = item['path']
        if path in ROOT_BLOBS:
            continue
        source = git_source(path).decode()
        for match in ENV.finditer(source):
            body = normalize_mathematics(match.group(0))
            environment_records.append(dict(source=path, line=source[:match.start()].count('\n') + 1,
                kind=match.group(1), labels=LABEL.findall(match.group(0)), sha256=digest(body.encode()),
                preserved_in_current_scientific_documents=body in current_env))
        for match, block in proof_headings(source):
            body = normalize_mathematics(block)
            heading_records.append(dict(source=path, line=source[:match.start()].count('\n') + 1,
                heading=match.group(2), sha256=digest(body.encode()),
                preserved_in_current_scientific_documents=body in corpus))
    all_used = set(sum(used.values(), []))
    block_records = []
    for record in retained_records:
        name = Path(record['source']).name
        if name in EDITORIAL_REPLACEMENTS:
            continue
        block_records.append(dict(**record, present_in_current_scientific_documents=record['destination'] in all_used))
    report = dict(reviewed_commit=COMMIT,
        proof_normalization='Whitespace, comments and input paths only; no prose or mathematical changes inside statements and proof blocks.',
        component_normalization='Whitespace, comments, input paths, and enumerated location/grammar prose only. No mathematical changes.',
        explicit_environment_count=len(environment_records),
        explicit_environment_counts=dict(Counter(x['kind'] for x in environment_records)),
        heading_based_proof_count=len(heading_records),
        complete_retained_component_count=len(block_records),
        environments=environment_records, heading_based_proofs=heading_records,
        complete_retained_components=block_records)
    (R / 'MATHEMATICAL_PRESERVATION.json').write_text(json.dumps(report, indent=2) + '\n')
    failures = [x for x in environment_records + heading_records
                if not x['preserved_in_current_scientific_documents']]
    missing_blocks = [x for x in block_records if not x['present_in_current_scientific_documents']]
    if failures or missing_blocks:
        raise RuntimeError('Incomplete current preservation: ' + json.dumps(dict(proofs=failures, components=missing_blocks)))
    mapping = []
    for item in inventory['labels']:
        label = item['label']
        if label not in locations:
            raise RuntimeError('A reviewed label is absent from all current documents: ' + label)
        mapping.append(dict(label=label, source=item['path'], source_line=item['line'],
                            current_locations=locations[label], destination='current'))
    return report, mapping


def preamble(kind, build):
    text = git_source('ECTA.tex').decode().split(r'\begin{document}')[0]
    text = re.sub(r'\\externaldocument\{[^}]+\}(?:\[[^]]*\])?', '', text)
    if kind in ('supp', 'applications'):
        prefix = 'S' if kind == 'supp' else 'A'
        text = text.replace(r'\newtheorem{theorem}{Theorem}', r'\newtheorem{theorem}{Theorem}' + '\n'
            + '\\renewcommand{\\thetheorem}{' + prefix + '.\\arabic{theorem}}\n'
            + '\\renewcommand{\\theequation}{' + prefix + '.\\arabic{equation}}\n'
            + '\\renewcommand{\\thetable}{' + prefix + '.\\arabic{table}}\n'
            + '\\renewcommand{\\thesection}{' + prefix + '.\\arabic{section}}\n')
    if build.endswith('/previewbuild'):
        text += '\\newcommand{\\NBOEditorialPending}[1]{\\begin{quote}\\textbf{Development draft.} #1\\end{quote}}\n'
    # A longtable needs its caption, header and several body rows on its first
    # page. This wrapper leaves every inherited table/source byte unchanged.
    text += '\\let\\NBOLongtable\\longtable\n'
    if kind == 'supp':
        # The two fixed R15 tables S.25/S.28 otherwise start at the very foot
        # of a page and repeat the continuation header before their caption.
        # Move only those starts; the retained table files remain unchanged.
        text += ('\\def\\longtable{\\ifnum\\value{table}=24\\relax\\clearpage\\fi'
                 '\\ifnum\\value{table}=27\\relax\\clearpage\\fi'
                 '\\Needspace{7\\baselineskip}\\NBOLongtable}\n')
    else:
        text += '\\def\\longtable{\\Needspace{7\\baselineskip}\\NBOLongtable}\n'
    if kind == 'applications':
        # Keep the two lines of the retained HJB display A.11 together.
        # This environment-local penalty leaves all formula bytes untouched.
        text += ('\\AddToHook{env/align/begin}{\\ifnum\\value{equation}=10\\relax'
                 '\\interdisplaylinepenalty=10000\\relax\\fi}\n')
    for other in ['ECTA', 'supp', 'applications']:
        if other != kind:
            text += '\\externaldocument{' + build + '/' + other + '_refs}[' + other + '.pdf]\n'
    return text + '\\begin{document}\n'


def frontmatter(kind):
    if kind == 'ECTA':
        original = git_source('ECTA.tex').decode()
        text = original.split(r'\begin{frontmatter}', 1)[1].split(r'\end{frontmatter}', 1)[0]
        abstract = (M / 'abstract.tex').read_text()
        body = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', abstract, re.S).group(1)
        if len(body.split()) > 150:
            raise RuntimeError('The main abstract exceeds 150 words')
        text = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}', lambda _: abstract.strip(), text, flags=re.S)
        return '\\begin{frontmatter}' + text + '\\end{frontmatter}\n'
    titles = {'supp': 'Technical Supplement to Neural Bellman Operators',
              'applications': 'Economic Applications of Neural Bellman Operators',
              'response': 'Response to the Referee on Neural Bellman Operators'}
    return ('\\begin{frontmatter}\n\\title{' + titles[kind] + '}\n\\runtitle{Neural Bellman Operators}\n'
            + '\\begin{aug}\n\\author[id=au1,addressref={add1}]{\\fnms{Qian}~\\snm{QI}}\n'
            + '\\address[id=add1]{Peking University}\n\\end{aug}\n\\end{frontmatter}\n')


def integrate(write_roots=False):
    inventory = json.loads((R / 'SOURCE_INVENTORY.json').read_text())
    if inventory['reviewed_commit'] != COMMIT or len(inventory['labels']) != 285:
        raise RuntimeError('Unexpected reviewed source inventory')
    archives = archive_roots(inventory)
    retained = materialize_retained(inventory)
    status_file = R / 'PUBLICATION_STATUS.json'
    status = json.loads(status_file.read_text()) if status_file.exists() else {'publication_ready': False}
    if write_roots and status.get('publication_ready') is not True:
        raise RuntimeError('Publication roots require a reviewed PUBLICATION_STATUS.json with publication_ready=true')
    build = relative(R / ('build' if write_roots else 'previewbuild'))
    config = json.loads((R / 'EDITORIAL_INPUTS.json').read_text())
    def group(name):
        paths = [ROOT / p for p in config.get(name, [])]
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(path)
        return paths
    main = [M / 'introduction.tex', M / 'literature.tex', inherited('model.tex'),
            inherited('method.tex'), inherited('algorithm.tex'), M / 'theory_guide.tex',
            inherited('capital.tex'), inherited('new_theory.tex')]
    main += group('new_theory_main') + [M / 'new_theory_summary.tex', M / 'computational_design.tex'] + group('new_results_main')
    main += [M / 'historical_evidence_summary.tex', inherited('implementation_summary.tex'),
             inherited('fees.tex'), inherited('economic_scope.tex'), M / 'conclusion.tex']
    supp = [M / 'supplement_guide.tex', inherited('general_theory.tex'), inherited('mechanism.tex'),
            inherited('appendix_evaluation.tex'), inherited('appendix_proofs.tex'),
            inherited('appendix_capital_accounts.tex'), inherited('new_proofs.tex'),
            inherited('paired_transfer.tex'), inherited('method_inference_proof.tex')]
    supp += group('new_theory_supplement') + [inherited('appendix_implementation.tex'),
            inherited('appendix_observation.tex'), inherited('appendix_diagnostics.tex'),
            M / 'previous_evidence_guide.tex', inherited('evidence_baseline.tex'), inherited('new_evidence.tex'),
            inherited('experiment_supplement.tex'), inherited('mechanism_supplement.tex'),
            inherited('scalar_algebraic_enclosure.tex'), inherited('scalar_supplement.tex'),
            inherited('observation_supplement.tex'), inherited('paired_comparison_supplement.tex')]
    supp += group('new_results_supplement') + [M / 'source_index.tex']
    applications = [M / 'applications_guide.tex', inherited('appendix_applications.tex')]
    scientific = {'ECTA': main, 'supp': supp, 'applications': applications}
    roots = {}
    tail = '\\bibliographystyle{ecta-fullname}\n\\bibliography{revision_reference}\n\\end{document}\n'
    for kind, paths in scientific.items():
        roots[kind] = preamble(kind, build) + frontmatter(kind) + ''.join(inp(p) for p in paths) + tail
    roots['response'] = preamble('response', build) + frontmatter('response') + inp(M / 'response_body.tex') + '\\end{document}\n'
    locations, used = defaultdict(list), defaultdict(list)
    flattened = {kind: flatten(text, kind, locations, used) for kind, text in roots.items() if kind != 'response'}
    duplicates = {k: v for k, v in locations.items() if len(v) != 1}
    if duplicates:
        raise RuntimeError('Duplicate labels in current documents: ' + json.dumps(duplicates))
    math, mapping = verify_preservation(inventory, flattened, locations, used, retained)
    corpus = '\n'.join(flattened.values())
    response_locations, response_used = defaultdict(list), defaultdict(list)
    response_text = flatten(roots['response'], 'response', response_locations, response_used)
    refs = set(REF.findall(corpus + response_text))
    missing_refs = sorted(refs - locations.keys() - response_locations.keys())
    if missing_refs:
        raise RuntimeError('Unresolved cross-document references: ' + ', '.join(missing_refs))
    algorithm_count = len(re.findall(r'\\begin\{algorithm\}', corpus))
    if algorithm_count != 1:
        raise RuntimeError('Exactly one current NBO algorithm is required')
    pending = any('\\NBOEditorialPending{' in text for text in flattened.values()) or '\\NBOEditorialPending{' in response_text
    if write_roots and pending:
        raise RuntimeError('Development placeholders cannot enter publication roots')
    report = dict(reviewed_commit=COMMIT, referee_commit=REVIEW, root_write=write_roots,
        publication_ready=status.get('publication_ready', False), development_placeholders=pending,
        reviewed_source_files=len(inventory['files']), reviewed_labels=len(mapping),
        preserved_current_labels=len(mapping), total_current_labels=len(locations),
        archived_only_reviewed_labels=0, unresolved_current_references=missing_refs,
        algorithm_count=algorithm_count, current_document_files=dict(used), labels=mapping,
        archived_roots=archives, explicit_mathematical_environments=math['explicit_environment_count'],
        heading_based_proofs=math['heading_based_proof_count'])
    (R / 'EDITORIAL_MAP.json').write_text(json.dumps(report, indent=2) + '\n')
    (R / 'preview').mkdir(exist_ok=True)
    for kind, text in roots.items():
        (R / 'preview' / (kind + '.tex')).write_text(text)
        if write_roots:
            dest = ROOT / (kind + '.tex') if kind in ('ECTA', 'supp') else R / (kind + '.tex')
            dest.write_text(text)
    print(json.dumps({k: v for k, v in report.items() if k not in ('labels', 'current_document_files', 'archived_roots')}, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-roots', action='store_true')
    integrate(**vars(parser.parse_args()))
