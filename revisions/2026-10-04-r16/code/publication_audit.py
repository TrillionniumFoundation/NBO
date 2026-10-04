#!/usr/bin/env python3
"""R16 D -> CI -> F publication audit, without training or confirmation draws.

The delivery-source commit D is an external argument. The final source closure
is derived only from materialized publication roots. A predecessor ledger and
payload manifest are hashed by the final audit, avoiding a self-referential F.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile

R = Path('revisions/2026-10-04-r16')
BASE = '1cb3cc9efe135966ec228dfaf51c6841a6dfc97c'
REVIEW = 'cb4595bbcc7147e47e44ba40cb2f5034510ae19f'
HISTORICAL_BLOBS = 12055
REVIEW_ROOT = Path('reviews/2026-10-04-econometrica-numerical-methods-r15')
REVIEW_NAMES = {'referee_report.md', 'review_manifest.json', 'verification_results.json', 'verify_r15_review.py'}
ROOT_ARCHIVE = {name: R / 'archive' / ('r15-' + name) for name in ('ECTA.tex', 'supp.tex', 'README.md')}
ROOTS = {'ECTA': Path('ECTA.tex'), 'supp': Path('supp.tex'),
         'applications': R / 'applications.tex', 'response': R / 'response.tex'}
WORKFLOW = Path('.github/workflows/nbo-r16-delivery.yml')
SOURCE_BRANCH = 'revision/econometrica-nbo-r16-delivery-source-2026-10-04'
TARGET_BRANCHES = (
    'revision/econometrica-nbo-r16-2026-10-04',
    'revision/nbo-paper-r16-2026-10-04',
    'revision/econometrica-nbo-r16-referee-ready-2026-10-04',
)
ROLES = {'replication', 'economic_robustness', 'signed_mechanism', 'continuation_menu'}
DERIVED_TOP = {'ARCHIVE_MANIFEST.json', 'EDITORIAL_MAP.json', 'MATHEMATICAL_PRESERVATION.json',
               'CURRENT_SOURCE_CLOSURE.json', 'SOURCE_LEDGER.json', 'EVIDENCE_MANIFEST.json',
               'FINAL_AUDIT.json', 'applications.tex', 'response.tex'}
DERIVED_RESULTS = {'COMPILATION.json', 'FINAL_LAYOUT_DIAGNOSTICS.json', 'MATERIALIZATION.json', 'current_source_closure.tsv'}
NONPUBLIC = {'preview', 'previewbuild', 'previewqa', '__pycache__', '.pytest_cache'}
INPUT = re.compile(r'\\(?:input|include)\{([^}]+)\}')
LABEL = re.compile(r'\\label\{([^}]+)\}')
REFERENCE = re.compile(r'\\(?:ref|eqref|autoref|pageref)\{([^}]+)\}')
MATHEMATICS = re.compile(r'\\begin\{(theorem|proposition|lemma|corollary|assumption|proof)\}(.*?)\\end\{\1\}', re.S)
HEADING = re.compile(r'\\(section|subsection|subsubsection|paragraph)\*?\{([^\n]*)\}')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                git_blob=hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest())


def safe_path(root, name):
    relative = PurePosixPath(str(name))
    require(not relative.is_absolute() and '..' not in relative.parts and str(relative) != '.',
            'unsafe relative manifest path: ' + str(name))
    answer = Path(root) / Path(*relative.parts)
    require(answer.resolve().is_relative_to(Path(root).resolve()), 'manifest path escapes repository')
    require(not answer.is_symlink(), 'symlink cannot stand for a publication source: ' + str(name))
    return answer


def replay_environment(cache=None):
    environment = os.environ.copy()
    environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0',
                       OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMBA_NUM_THREADS='1')
    if cache is not None:
        environment['NUMBA_CACHE_DIR'] = str(cache)
    return environment


class GitStore:
    """One streaming Git batch process; every source comparison is byte exact."""
    def __init__(self, repo):
        self.repo = Path(repo)
        self.trees = {}
        self.environment = dict(os.environ, GIT_NO_LAZY_FETCH='1')
        self.process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.environment)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, stderr=subprocess.PIPE, env=self.environment)

    def tree(self, commit):
        require(bool(re.fullmatch('[0-9a-f]{40}', commit or '')), 'full immutable commit SHA required')
        require(self.git('rev-parse', '--verify', commit + '^{commit}').decode().strip() == commit,
                'missing immutable commit: ' + commit)
        if commit not in self.trees:
            result = {}
            for entry in self.git('ls-tree', '-rz', '--full-tree', commit).split(b'\0'):
                if not entry:
                    continue
                metadata, name = entry.split(b'\t', 1)
                mode, kind, oid = metadata.split()
                require(kind == b'blob', 'submodules or non-blob leaves are not publication inputs')
                result[name.decode()] = dict(mode=mode.decode(), git_blob=oid.decode())
            self.trees[commit] = result
        return self.trees[commit]

    def _start(self, oid):
        self.process.stdin.write((oid + '\n').encode())
        self.process.stdin.flush()
        fields = self.process.stdout.readline().split()
        require(len(fields) == 3 and fields[0].decode() == oid and fields[1] == b'blob', 'invalid Git blob')
        return int(fields[2])

    def blob(self, oid):
        size = self._start(oid)
        data = self.process.stdout.read(size)
        require(len(data) == size and self.process.stdout.read(1) == b'\n', 'truncated Git blob')
        return data

    def compare(self, oid, path):
        path = Path(path)
        require(path.is_file() and not path.is_symlink(), 'missing/nonregular retained file: ' + str(path))
        size = self._start(oid)
        remaining = size
        digest = hashlib.sha256()
        equal = path.stat().st_size == size
        with path.open('rb') as handle:
            while remaining:
                block = self.process.stdout.read(min(remaining, 1024 * 1024))
                require(bool(block), 'truncated Git blob stream')
                digest.update(block)
                equal = handle.read(len(block)) == block and equal
                remaining -= len(block)
            equal = handle.read(1) == b'' and equal
        require(self.process.stdout.read(1) == b'\n', 'invalid Git blob terminator')
        require(equal, 'retained bytes differ from immutable Git blob: ' + str(path))
        return dict(git_blob=oid, sha256=digest.hexdigest(), bytes=size)

    def close(self):
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.process.stdout.close()
        self.process.stderr.close()


def check_history(repo, git, publication_source, commit=BASE, expected_count=HISTORICAL_BLOBS):
    """The complete tree proves preservation without fetching historical raw blobs.

    A Git blob identity includes its bytes and length. Every historical leaf must
    occur with the identical mode and object ID in D, at its original path or one
    of the three exact root archives. Materialized members get a further SHA256
    check. The final publisher repeats the tree comparison on F.
    """
    tree = git.tree(commit)
    destination_tree = git.tree(publication_source)
    require(len(tree) == expected_count, 'reviewed historical blob count changed')
    records = {}
    for name, facts in sorted(tree.items()):
        destination = ROOT_ARCHIVE.get(name, Path(name))
        require(facts['mode'] in ('100644', '100755'), 'unexpected historical Git mode')
        require(destination_tree.get(str(destination)) == facts,
                'historical Git leaf missing or altered in D: ' + name)
        record = dict(destination=str(destination), **facts, materialized=False)
        local = safe_path(repo, destination)
        if local.is_file():
            current = file_record(local)
            require(current['git_blob'] == facts['git_blob'], 'materialized historical bytes changed: ' + name)
            record.update(current, materialized=True)
        records[name] = record
    return dict(commit=commit, blobs=len(records), files=records,
                verification='Every Git leaf and mode in the complete D tree; additional SHA256 checks for materialized files. Historical raw blobs are not downloaded for publication.',
                root_archive_exceptions={name: str(path) for name, path in ROOT_ARCHIVE.items()})


def check_review(repo, git, publication_source):
    tree = git.tree(REVIEW)
    prefix = REVIEW_ROOT.as_posix() + '/'
    found = {name.removeprefix(prefix): facts for name, facts in tree.items() if name.startswith(prefix)}
    require(set(found) == REVIEW_NAMES, 'latest review must retain exactly its four recorded files')
    records = {}
    delivery = git.tree(publication_source)
    for name, facts in sorted(found.items()):
        path = str(REVIEW_ROOT / name)
        require(delivery.get(path) == facts, 'review source absent from D: ' + path)
        records[name] = git.compare(facts['git_blob'], safe_path(repo, path))
    return dict(review_commit=REVIEW, reviewed_publication_commit=BASE, files=records)


def strip_comments(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def canonical_math(text):
    text = strip_comments(text).replace(R.as_posix() + '/retained/', 'revisions/2026-10-04-r15/')
    return re.sub(r'\s+', ' ', text).strip()


def proof_sections(text):
    levels = {'section': 0, 'subsection': 1, 'subsubsection': 2, 'paragraph': 3}
    headings = list(HEADING.finditer(text))
    for index, match in enumerate(headings):
        if not re.search(r'\bproofs?\b', match.group(2), re.I):
            continue
        end = len(text)
        for later in headings[index + 1:]:
            if levels[later.group(1)] <= levels[match.group(1)]:
                end = later.start()
                break
        yield match, text[match.start():end]


def document_closure(repo, root, document, records, locations, ancestry=()):
    name = str(root)
    require(name not in ancestry, 'cyclic TeX input: ' + name)
    path = safe_path(repo, name)
    require(path.is_file(), 'missing current document source: ' + name)
    record = records.setdefault(name, dict(**file_record(path), documents=[]))
    if document not in record['documents']:
        record['documents'].append(document)
    text = strip_comments(path.read_text())
    for label in LABEL.findall(text):
        locations[label].append(dict(document=document, file=name))
    def expand(match):
        child = match.group(1)
        require('\\' not in child and '#' not in child, 'dynamic TeX input cannot enter audited source closure')
        if not Path(child).suffix:
            child += '.tex'
        return document_closure(repo, child, document, records, locations, ancestry + (name,))
    return INPUT.sub(expand, text)


def all_current_sources(repo):
    records, locations = {}, defaultdict(list)
    texts = {name: document_closure(repo, path, name, records, locations) for name, path in ROOTS.items()}
    for document, text in texts.items():
        declarations = [(r'\\documentclass(?:\[[^]]*\])?\{([^}]+)\}', '.cls'),
                        (r'\\bibliographystyle\{([^}]+)\}', '.bst'),
                        (r'\\bibliography\{([^}]+)\}', '.bib')]
        for pattern, suffix in declarations:
            for group in re.findall(pattern, text):
                for name in group.split(','):
                    path = safe_path(repo, name + suffix)
                    require(path.is_file(), 'journal/bibliography source must be local: ' + str(path))
                    record = records.setdefault(str(path.relative_to(repo)), dict(**file_record(path), documents=[]))
                    if document not in record['documents']:
                        record['documents'].append(document)
        # The publisher class loads this local configuration implicitly.
        cfg = Path(repo) / 'econsocart.cfg'
        require(cfg.is_file(), 'publisher class configuration is missing')
        record = records.setdefault('econsocart.cfg', dict(**file_record(cfg), documents=[]))
        if document not in record['documents']:
            record['documents'].append(document)
    return texts, records, locations


def check_editorial(repo, git, history):
    mapping = read(repo / R / 'EDITORIAL_MAP.json')
    require(mapping.get('root_write') is True and mapping.get('publication_ready') is True,
            'editorial map is a development preview')
    require(mapping['reviewed_commit'] == BASE and mapping['referee_commit'] == REVIEW, 'editorial source identity changed')
    texts, closure, locations = all_current_sources(repo)
    require(all(len(items) == 1 for items in locations.values()), 'duplicate current labels')
    scientific = '\n'.join(texts[name] for name in ('ECTA', 'supp', 'applications'))
    scientific_labels = {label for label, items in locations.items() if items[0]['document'] != 'response'}
    references = set(REFERENCE.findall('\n'.join(texts.values())))
    require(not (references - locations.keys()), 'unresolved current cross-document reference')
    require(len(re.findall(r'\\begin\{algorithm\}', scientific)) == 1, 'one current NBO algorithm required')
    inventory = read(repo / R / 'SOURCE_INVENTORY.json')
    require(inventory['reviewed_commit'] == BASE and len(inventory['files']) == 70, 'reviewed source closure changed')
    old_labels, environments, headings = [], [], []
    current_environments = {canonical_math(m.group(0)) for m in MATHEMATICS.finditer(scientific)}
    full_current = canonical_math(scientific)
    for item in inventory['files']:
        name = item['path']
        original = history['files'][name]
        require(item['git_blob'] == original['git_blob'], 'reviewed source inventory Git identity mismatch')
        data = git.blob(original['git_blob'])
        require(item['sha256'] == hashlib.sha256(data).hexdigest(), 'reviewed source inventory SHA256 mismatch')
        source = data.decode()
        old_labels.extend((name, label) for label in LABEL.findall(strip_comments(source)))
        for match in MATHEMATICS.finditer(source):
            body = canonical_math(match.group(0))
            require(body in current_environments, 'reviewed mathematical statement/proof missing: ' + name)
            environments.append(dict(source=name, kind=match.group(1), sha256=hashlib.sha256(body.encode()).hexdigest()))
        for match, block in proof_sections(source):
            body = canonical_math(block)
            require(body in full_current, 'complete heading-based proof missing: ' + name)
            headings.append(dict(source=name, heading=match.group(2), sha256=hashlib.sha256(body.encode()).hexdigest()))
    require(len(old_labels) == len({label for _, label in old_labels}) == 285, 'reviewed 285-label target changed')
    require(len(environments) == 33 and len(headings) == 18, 'reviewed statement/proof targets changed')
    require({label for _, label in old_labels} <= scientific_labels, 'a reviewed label exists only outside current scientific documents')
    require(sorted(old_labels) == sorted((x['source'], x['label']) for x in mapping['labels']), 'editorial map omits an old label')
    require(all(row['destination'] == 'current' for row in mapping['labels']), 'a reviewed label was relegated to archive')
    for row in mapping['labels']:
        require(row['current_locations'] == locations[row['label']], 'editorial map points to a different current location')
    supplied = read(repo / R / 'MATHEMATICAL_PRESERVATION.json')
    require(supplied['explicit_environment_count'] == 33 and supplied['heading_based_proof_count'] == 18,
            'supplied proof preservation counters differ')
    require(all(x['preserved_in_current_scientific_documents'] for x in supplied['environments'] + supplied['heading_based_proofs']),
            'supplied proof preservation reports missing content')
    require(mapping['preserved_current_labels'] == 285 and mapping['archived_only_reviewed_labels'] == 0,
            'current label preservation receipt differs')
    return dict(reviewed_source_files=70, reviewed_labels=285, current_scientific_labels=len(scientific_labels),
                explicit_mathematical_environments=33, heading_based_proofs=18,
                editorial_map_sha256=sha(repo / R / 'EDITORIAL_MAP.json'),
                mathematical_preservation_sha256=sha(repo / R / 'MATHEMATICAL_PRESERVATION.json'),
                environments=environments, heading_proofs=headings), texts, closure


def check_narrative(repo, texts):
    status = read(repo / R / 'PUBLICATION_STATUS.json')
    require(status.get('publication_ready') is True, 'publication status is not ready')
    require(not any(value is True for key, value in status.items() if 'pending' in key), 'a declared scientific narrative remains pending')
    response = texts['response']
    headings = re.findall(r'\\(?:sub)?section\*?\{([BM]\d+)(?=[:.\s])', response)
    expected = {f'B{i}' for i in range(1, 9)} | {f'M{i}' for i in range(1, 11)}
    require(len(headings) == 18 and set(headings) == expected, 'exactly one reply to B1-B8 and M1-M10 is required')
    forbidden = ['\\nboeditorialpending{', 'development draft.', 'to be completed',
                 'results are pending', 'scientific_evidence_pending', 'not yet available in this draft']
    for name, text in texts.items():
        normalized = ' '.join(text.lower().split())
        require(not any(marker in normalized for marker in forbidden), 'developer placeholder in current document: ' + name)
    abstracts = re.findall(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', texts['ECTA'], re.S)
    require(len(abstracts) == 1, 'one English abstract required')
    plain = re.sub(r'\\[A-Za-z]+\*?', ' ', abstracts[0])
    words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", plain)
    require(0 < len(words) <= 150, 'abstract exceeds 150 English words')
    require(r'\title{Neural Bellman Operators}' in texts['ECTA'], 'original article title changed')
    return dict(publication_status_sha256=sha(repo / R / 'PUBLICATION_STATUS.json'),
                response_headings=headings, abstract_words=len(words),
                scope='Completeness and accurate evidence scope, never a favorable-sign gate.')


def check_publication_inputs(repo, git, source, evidence_roots):
    records = {}
    for name, facts in git.tree(source).items():
        path = Path(name)
        is_revision = path.is_relative_to(R)
        if not is_revision and path not in (WORKFLOW, Path('README.md')):
            continue
        if is_revision:
            sub = path.relative_to(R)
            if set(sub.parts) & NONPUBLIC or sub.suffix == '.pyc' or sub.parts[0] in ('build', 'retained'):
                continue
            if len(sub.parts) == 1 and sub.name in DERIVED_TOP:
                continue
            if sub.parts[0] == 'results' and sub.name in DERIVED_RESULTS:
                continue
            if any(path.is_relative_to(Path(root)) for root in evidence_roots):
                continue
        records[name] = git.compare(facts['git_blob'], safe_path(repo, name))
    for required in (R / 'code/publication_audit.py', R / 'code/publication_families.py',
                     R / 'code/delivery.py', R / 'code/integrate.py', R / 'code/build.py',
                     R / 'PUBLICATION_SOURCES.json', WORKFLOW):
        require(str(required) in records, 'required frozen delivery input missing: ' + str(required))
    return records


def check_pdfs(repo):
    compilation = read(repo / R / 'results/COMPILATION.json')
    require(compilation['mode'] == 'publication' and compilation['output_count'] == 4, 'four publication PDFs required')
    supplied = {row['document']: row for row in compilation['documents']}
    require(set(supplied) == set(ROOTS), 'publication PDF identities differ')
    records = {}
    for name, row in supplied.items():
        pdf = repo / R / 'build' / (name + '.pdf')
        log = pdf.with_suffix('.log')
        require(pdf.is_file() and pdf.stat().st_size > 1000 and sha(pdf) == row['sha256'], 'PDF digest mismatch: ' + name)
        require(not any(row[key] for key in ('undefined', 'multiply_defined', 'duplicate_destinations', 'missing_characters', 'development_text_present')),
                'compilation record reports an unresolved diagnostic: ' + name)
        require(not row['overfull_hbox_points'], 'overfull horizontal box in publication: ' + name)
        require(not any(float(v) > 1 for v in row.get('overfull_vbox_points', [])), 'material vertical overflow in publication: ' + name)
        log_text = log.read_text(errors='replace')
        require(not re.search(r'(?:Reference|Citation) .*? undefined|There were undefined|Undefined control sequence|multiply[ -]defined|destination with the same identifier|Missing character:|Overfull \\hbox', log_text, re.I),
                'independent compiler-log gate failed: ' + name)
        info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
        pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
        require(pages == row['pages'] and pages > 0, 'PDF page count mismatch')
        extracted = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
        require('Development draft.' not in extracted and '\ufffd' not in extracted, 'placeholder or invalid glyph in rendered PDF')
        records[name] = dict(path=str(pdf.relative_to(repo)), pages=pages, sha256=sha(pdf),
                             log_sha256=sha(log), extracted_text_sha256=hashlib.sha256(extracted.encode()).hexdigest())
    return records


def check_editorial_replay(repo, closure, git, publication_source):
    """Reconstruct every publication root/map/retained component in a fresh tree."""
    generated = set(str(path) for path in ROOTS.values()) | {
        str(R / name) for name in ('ARCHIVE_MANIFEST.json', 'EDITORIAL_MAP.json', 'MATHEMATICAL_PRESERVATION.json')}
    generated.update(str(path.relative_to(repo)) for path in (repo / R / 'retained').rglob('*') if path.is_file())
    delivery_tree = git.tree(publication_source)
    retained_prefix = str(R / 'retained') + '/'
    require({name for name in delivery_tree if name.startswith(retained_prefix)} ==
            {name for name in generated if name.startswith(retained_prefix)},
            'D must contain the exact reviewed current retained component set')
    for name in sorted(generated):
        require(name in delivery_tree and delivery_tree[name]['mode'] == '100644' and
                delivery_tree[name]['git_blob'] == file_record(safe_path(repo, name))['git_blob'],
                'rebuilt editorial source differs from the reviewed source in D: ' + name)
    support = {str(R / 'code/integrate.py'), str(R / 'EDITORIAL_INPUTS.json'),
               str(R / 'PUBLICATION_STATUS.json'), str(R / 'SOURCE_INVENTORY.json'), str(R / 'manuscript/abstract.tex')}
    with tempfile.TemporaryDirectory(prefix='nbo-r16-editorial-replay-') as temporary:
        fresh = Path(temporary)
        subprocess.run(['git', 'init', '-q', str(fresh)], check=True, stdout=subprocess.DEVNULL)
        objects = subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-path', 'objects'], cwd=repo, text=True).strip()
        alternates = fresh / '.git/objects/info/alternates'
        alternates.write_text(objects + '\n')
        for name in (set(closure) | support) - generated:
            path = safe_path(repo, name)
            destination = safe_path(fresh, name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        # Its only Git operation is reading the already materialized 70-file R15
        # closure from the common object store. No raw evidence is copied.
        command = [sys.executable, str(fresh / R / 'code/integrate.py'), '--write-roots']
        result = subprocess.run(command, cwd=fresh, env=replay_environment(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        require(result.returncode == 0, 'independent editorial integration failed: ' + result.stdout[-5000:])
        reconstructed = {str(path.relative_to(fresh)) for path in (fresh / R / 'retained').rglob('*') if path.is_file()}
        require(reconstructed == {name for name in generated if Path(name).is_relative_to(R / 'retained')},
                'independent editorial replay changes retained component set')
        records = {}
        for name in sorted(generated):
            expected, actual = file_record(safe_path(repo, name)), file_record(safe_path(fresh, name))
            require(actual == expected, 'independent editorial integration differs: ' + name)
            records[name] = actual
    return dict(files=records, complete=True, same_publication_roots_and_maps=True,
                exact_reviewed_delivery_source=True, fresh_confirmation_draws=0,
                historical_raw_copied=False)


def payload_path(name):
    path = Path(name)
    if path in (Path('ECTA.tex'), Path('supp.tex'), Path('README.md')):
        return True
    if not path.is_relative_to(R):
        return False
    sub = path.relative_to(R)
    if set(sub.parts) & NONPUBLIC or sub.suffix == '.pyc':
        return False
    if len(sub.parts) == 1 and sub.name in ('EVIDENCE_MANIFEST.json', 'FINAL_AUDIT.json'):
        return False
    if sub.parts[0] == 'build' and path.suffix not in ('.pdf', '.txt', '.json', '.log'):
        return False
    return True


def publication_payload(repo, git, source, family_records):
    """Complete public R16 inventory, including preserved but sparse raw leaves."""
    source_tree = git.tree(source)
    evidence = {name: row for family in family_records.values() for name, row in family['evidence_files'].items()}
    payload = {}
    for name, facts in source_tree.items():
        if not payload_path(name):
            continue
        local = safe_path(repo, name)
        if local.is_file():
            payload[name] = dict(**file_record(local), mode=facts['mode'], storage='materialized')
        else:
            require(name in evidence, 'missing non-evidence publication input: ' + name)
            row = evidence[name]
            require(row['git_blob'] == facts['git_blob'], 'sparse evidence differs from D')
            payload[name] = {key: row[key] for key in ('sha256', 'bytes', 'git_blob', 'mode')}
            payload[name]['storage'] = 'preserved_git_leaf'
    for path in sorted((repo / R).rglob('*')):
        if path.is_file() and not path.is_symlink():
            name = str(path.relative_to(repo))
            if payload_path(name):
                payload[name] = dict(**file_record(path), mode=source_tree.get(name, {}).get('mode', '100644'), storage='materialized')
    for name in ('ECTA.tex', 'supp.tex', 'README.md'):
        payload[name] = dict(**file_record(repo / name), mode=source_tree.get(name, {}).get('mode', '100644'), storage='materialized')
    return payload


def emit_source_closure(repo, source, closure, input_records, family_records):
    """Called only after ready final roots and their PDF/source gates have passed."""
    owner = defaultdict(list)
    for name in input_records:
        owner[name].append(dict(role='delivery_source', commit=source))
    for role, report in family_records.items():
        for name in report['source_files']:
            owner[name].append(dict(role=role, commit=report['source_commit']))
        for name in report['evidence_files']:
            owner[name].append(dict(role=role + '_evidence', commit=report['evidence_commit']))
    rows = {}
    reviewed = {item['path']: item for item in read(repo / R / 'SOURCE_INVENTORY.json')['files']}
    for name, record in sorted(closure.items()):
        path = Path(name)
        derivation = 'frozen_source'
        if path in ROOTS.values() or path.is_relative_to(R / 'retained'):
            derivation = 'frozen_editorial_integrator'
            owner[name].append(dict(role='editorial_integrator', commit=source, source=str(R / 'code/integrate.py')))
        if path.is_relative_to(R / 'retained'):
            original = str(Path('revisions/2026-10-04-r15') / path.relative_to(R / 'retained'))
            require(original in reviewed, 'retained source lacks a reviewed ancestor')
            owner[name].append(dict(role='reviewed_scientific_source', commit=BASE, source=original,
                                    source_git_blob=reviewed[original]['git_blob'], source_sha256=reviewed[original]['sha256']))
        elif not path.is_relative_to(R) and path not in ROOTS.values():
            owner[name].append(dict(role='reviewed_support_source', commit=BASE, source=name, source_git_blob=record['git_blob']))
        require(owner[name] or derivation == 'frozen_editorial_integrator' or not path.is_relative_to(R),
                'current manuscript source has no immutable source owner: ' + name)
        rows[name] = dict(**record, immutable_owners=owner[name], derivation=derivation)
    output = dict(schema='nbo-r16-final-current-source-closure-v1', publication_source_commit=source,
                  final_roots={name: str(path) for name, path in ROOTS.items()}, files=rows,
                  timing='Generated from final publication roots after editorial, narrative, PDF and frozen-source gates; not from previews.',
                  self_reference='This record and its TSV are outside the TeX input closure they describe.')
    write(repo / R / 'CURRENT_SOURCE_CLOSURE.json', output)
    lines = ['documents\tpath\tbytes\tsha256\tgit_blob\tderivation\timmutable_commits']
    lines += ['\t'.join([','.join(x['documents']), name, str(x['bytes']), x['sha256'], x['git_blob'], x['derivation'],
                         ','.join(sorted({item['commit'] for item in x['immutable_owners']}))])
              for name, x in rows.items()]
    (repo / R / 'results/current_source_closure.tsv').write_text('\n'.join(lines) + '\n')
    return dict(files=len(rows), sha256=sha(repo / R / 'CURRENT_SOURCE_CLOSURE.json'),
                table_sha256=sha(repo / R / 'results/current_source_closure.tsv'))


def validate_configuration(cfg):
    require(cfg.get('schema') == 'nbo-r16-publication-sources-v1' and cfg.get('status') == 'complete',
            'publication source configuration is incomplete')
    require(cfg.get('historical_commit') == BASE and cfg.get('expected_historical_blobs') == HISTORICAL_BLOBS,
            'historical preservation target cannot change')
    require(cfg.get('review_commit') == REVIEW and cfg.get('expected_review_files') == 4, 'latest referee identity changed')
    require(cfg.get('source_branch') == SOURCE_BRANCH and tuple(cfg.get('target_branches', [])) == TARGET_BRANCHES,
            'publication branch contract changed')
    require(set(cfg.get('roles', {})) == ROLES, 'all four new scientific families are required')
    for role in cfg['roles'].values():
        for field in ('source_commit', 'evidence_commit'):
            require(bool(re.fullmatch('[0-9a-f]{40}', role.get(field) or '')), 'missing immutable scientific identity: ' + field)
    require(cfg.get('prior_attempt_history_complete') is True, 'preconfirmation source-attempt history has not been finalized')


def audit(repo, publication_source, sources, strict=False):
    repo = Path(repo).resolve()
    sources = Path(sources)
    if not sources.is_absolute():
        sources = repo / sources
    cfg = read(sources)
    validate_configuration(cfg)
    git = GitStore(repo)
    issues, checks = [], {}
    def run(name, function):
        try:
            checks[name] = function()
            return checks[name]
        except Exception as error:
            issues.append(dict(check=name, error_type=type(error).__name__, error=str(error)))
            if strict:
                raise
            return None
    try:
        require(git.git('rev-parse', 'HEAD').decode().strip() == publication_source, 'delivery checkout differs from D')
        run('publication_inputs', lambda: check_publication_inputs(repo, git, publication_source,
            [item['evidence_root'] for item in cfg['roles'].values()]))
        run('history', lambda: check_history(repo, git, publication_source))
        run('review', lambda: check_review(repo, git, publication_source))
        # Imported only after its D-bound bytes have been checked.
        from publication_families import check_family, check_confidence_families, check_prior_attempts, check_author_tables
        for name in sorted(ROLES):
            run(name, lambda name=name: check_family(repo, git, name, cfg['roles'][name], publication_source))
        run('confidence_families', lambda: check_confidence_families(repo, cfg['roles']))
        run('author_tables', lambda: check_author_tables(repo))
        run('prior_attempts', lambda: check_prior_attempts(repo, git, cfg.get('prior_attempts', [])))
        editorial = run('editorial', lambda: check_editorial(repo, git, checks['history'])) if 'history' in checks else None
        if editorial:
            checks['editorial'], texts, closure = editorial
            run('narrative', lambda: check_narrative(repo, texts))
            run('editorial_replay', lambda: check_editorial_replay(repo, closure, git, publication_source))
        run('pdfs', lambda: check_pdfs(repo))
        if editorial and 'pdfs' in checks:
            from layout_diagnostics import check_visual_review
            run('layout', lambda: check_visual_review(repo, closure, checks['pdfs']))
        require(not issues, 'publication audit has unresolved gates')
        family_records = {name: checks[name] for name in sorted(ROLES)}
        checks['current_source_closure'] = emit_source_closure(repo, publication_source, closure,
                                                               checks['publication_inputs'], family_records)
        ledger = dict(schema='nbo-r16-source-ledger-v1', complete=True, publication_source_commit=publication_source,
                      configuration_sha256=sha(sources), historical_commit=BASE, review_commit=REVIEW,
                      checks=checks, issues=[],
                      scientific_outcomes='No positive sign, superiority, equivalence or success rate is an audit pass condition.')
        ledger_path = repo / R / 'SOURCE_LEDGER.json'
        write(ledger_path, ledger)
        payload = publication_payload(repo, git, publication_source, family_records)
        manifest_path = repo / R / 'EVIDENCE_MANIFEST.json'
        write(manifest_path, dict(schema='nbo-r16-publication-payload-v1', publication_source_commit=publication_source,
            files=payload, scope='All public R16 source, complete new evidence Git leaves, predecessor ledgers and four PDFs. Raw files omitted by the bounded working-tree checkout remain in D and F with exact Git blob, SHA256 and length identities from their immutable E manifests. This inventory and FINAL_AUDIT are excluded to avoid circular hashes.'))
        final = dict(schema='nbo-r16-publication-audit-v1', complete=True, publication_source_commit=publication_source,
            source_ledger_sha256=sha(ledger_path), evidence_manifest_sha256=sha(manifest_path),
            configuration_sha256=sha(sources), payload_files=len(payload), historical_blobs_preserved=HISTORICAL_BLOBS,
            review_files_preserved=4, preserved_current_labels=285, explicit_mathematical_environments=33,
            heading_based_proofs=18, pdfs=checks['pdfs'], checks=sorted(checks), issues=[],
            delivery_identity=dict(source_branch=SOURCE_BRANCH, target_branches=list(TARGET_BRANCHES),
                                   workflow=str(WORKFLOW), workflow_sha256=sha(repo / WORKFLOW),
                                   github_run_id=os.environ.get('GITHUB_RUN_ID'), github_run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT')),
            self_reference='F is created after this receipt; D is supplied externally. The final receipt hashes already finalized predecessor files.')
        write(repo / R / 'FINAL_AUDIT.json', final)
        return final
    finally:
        git.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    parser.add_argument('--publication-source', required=True)
    parser.add_argument('--sources', default=str(R / 'PUBLICATION_SOURCES.json'))
    parser.add_argument('--strict', action='store_true')
    result = audit(**vars(parser.parse_args()))
    print(json.dumps(result, indent=2, allow_nan=False))
