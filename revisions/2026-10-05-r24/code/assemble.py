"""Assemble R24 from the inherited R23 integration; never edit an old source.

The R23 assembler is run only to reproduce its uncommitted publication
wrappers. R24 owns its wrappers, manuscript copies and derived tables.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
OLD = ROOT / 'revisions/2026-10-05-r23'
REVIEW = '281e57b18a2d88de68d2219da1a7194e90570d13'
BASE = 'c327e0f4f1d5c8c6381dfe0f2b6001fbd7bb7f96'
PREFIX = 'revisions/2026-10-05-r24'
OLDPREFIX = 'revisions/2026-10-05-r23'
DOCS = ('ECTA', 'supp', 'applications', 'evidence', 'response')


def save(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf8')


def transform(text):
    text = text.replace(OLDPREFIX + '/manuscript/', PREFIX + '/manuscript/')
    text = text.replace(OLDPREFIX + '/results/generated/', PREFIX + '/results/inherited_r23/')
    return text.replace(OLDPREFIX + '/build/', PREFIX + '/build/')


def dependencies(path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return seen
    seen.add(path)
    for name in re.findall(r'\\(?:input|include)\{([^}]+)\}', path.read_text()):
        child = ROOT / name
        if not child.suffix:
            child = child.with_suffix('.tex')
        if child.exists():
            dependencies(child, seen)
        elif '#' not in name and '\\' not in name:
            raise FileNotFoundError(child)
    return seen


def labels(paths):
    return set().union(*(set(re.findall(r'\\label\{([^}]+)\}', p.read_text())) for p in paths))


def assemble():
    spec = importlib.util.spec_from_file_location('inherited_assembler', OLD / 'code/assemble_publication.py')
    inherited = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inherited)
    inherited.assemble()
    # The R23 integration is now available locally, with its original sources intact.
    copies = []
    for p in sorted((OLD / 'manuscript').glob('*.tex')):
        dest = R / 'manuscript' / p.name
        if p.name == 'response_body.tex':
            save(R / 'archive/r23_response_body.tex', p.read_text())
            continue
        save(dest, transform(p.read_text()))
        copies.append({'original': str(p.relative_to(ROOT)),
                       'original_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                       'copy': str(dest.relative_to(ROOT)),
                       'change': 'path rebinding; introduction and conclusion additionally extended'})
    for p in sorted((OLD / 'results/generated').glob('*')):
        if p.is_file():
            dest = R / 'results/inherited_r23' / p.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if p.suffix == '.tex':
                save(dest, transform(p.read_text()))
            else:
                shutil.copyfile(p, dest)
    # Avoid overloading the inherited value constant c_t in the new budget formula.
    learning = R / 'manuscript/learning_main.tex'
    save(learning, learning.read_text().replace('c_t', r'\chi_t'))
    intro = R / 'manuscript/introduction.tex'
    save(intro, intro.read_text() + r'''
\paragraph{The trained continuation and its economic target.}
A continuation trained against one policy is not automatically a continuation
for the policy returned after improvement. Section~\ref{sec:r24learning}
gives an explicit finite-step hidden-weight bound and charges this own-policy
target drift before translating fitting accuracy into lifetime policy loss.
Section~\ref{sec:r24geometry} retains action curvature in the same loss
certificate. The refinement is applied symmetrically to every stored candidate;
its separate post-execution record does not replace the original prospective
work frontier. The distinction between the learner, the returned policy, and
the verifier is therefore maintained throughout the empirical comparison.
''')
    conclusion = R / 'manuscript/conclusion.tex'
    save(conclusion, conclusion.read_text() + r'''
The finite-step result adds a constructive inner-loop account for a fully
trainable continuation factor under an explicit rank basin. Its policy
implication includes both numerical perturbations and the change between the
training target and the returned policy's actual future. The residual-energy
refinement improves the sufficient policy account without changing the
candidate or the economic comparison class. These results make the NBO
learning-to-decision argument more explicit; neither is a substitute for a
comparative total-work result. The complete adverse evidence and the
structure-exploiting baseline remain part of that comparison.
''')
    for name in DOCS:
        text = transform((OLD / (name + '.tex')).read_text())
        if name == 'ECTA':
            anchor = r'\input{' + PREFIX + '/manuscript/full_policy.tex}'
            assert anchor in text
            text = text.replace(anchor, anchor + '\n' +
                                r'\input{' + PREFIX + '/manuscript/learning_main.tex}\n' +
                                r'\input{' + PREFIX + '/manuscript/geometry_main.tex}\n', 1)
            abstract = r'''\begin{abstract}
This paper develops Neural Bellman Operators for policy evaluation and
feasible improvement in controlled economies. Centered continuation error
and transport bounds govern reuse of learned futures. An all-state policy
certificate is linked to finite hidden-weight training through an explicit
rank basin, a perturbation allowance, and the change between the training
target and the returned policy's own continuation. A residual-energy
refinement retains action curvature. A source-frozen capital study has
continuous Gaussian shocks, 24 reoptimized dates, and ten or fifty vector
controls. All 480 neural, conventional-quadratic, and structural services
meet the full-policy tolerance; all 608 unsuccessful intermediate checks
remain in the record. A separate symmetric replay examines the refined
certificate without replacing primary clocks. Neural and conventional
representations receive matched evaluation information, and the structural
baseline remains fully competitive. The original nonlinear capital studies,
recursive utility, endogenous preferences, temporal selves, and games retain
their complete accounts. Candidate accuracy, finite-step learning implications,
and comparative method work are distinguished.
\end{abstract}'''
            text = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}', lambda m: abstract, text, flags=re.S)
        if name == 'supp':
            text = text.replace(r'\bibliographystyle',
                                r'\clearpage' + '\n' + r'\input{' + PREFIX +
                                '/results/refinement_record.tex}\n' + r'\bibliographystyle', 1)
        # No citation belongs to the standalone evidence wrapper. Running BibTeX
        # on that empty citation set caused the inherited publication failure.
        if name == 'evidence':
            text = re.sub(r'\\bibliographystyle\{[^}]+\}\s*\\bibliography\{[^}]+\}', '', text)
        if name in ('ECTA', 'supp'):
            text = re.sub(r'\\bibliography\{([^}]+)\}',
                          lambda m: r'\bibliography{' + m[1] + ',' + PREFIX + '/references}', text)
        save(R / (name + '.tex'), text)
    olddeps = set()
    newdeps = set()
    for name in DOCS[:-1]:
        olddeps |= dependencies(OLD / (name + '.tex'))
    for name in DOCS:
        newdeps |= dependencies(R / (name + '.tex'))
    oldlabels, newlabels = labels(olddeps), labels(newdeps)
    missing = sorted(oldlabels - newlabels)
    assert not missing, ('missing inherited labels', missing)
    changed = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=MDT', BASE, '--'], cwd=ROOT, text=True).splitlines()
    assert not changed, ('changed inherited tracked files', changed)
    inherited_review = json.loads((OLD / 'PRESERVATION.json').read_text())
    audit = {'review_commit': REVIEW, 'integration_base_commit': BASE,
             'modified_or_deleted_inherited_tracked_files': changed,
             'reviewed_source_components': inherited_review['inherited_source_components'],
             'reviewed_labels': inherited_review['inherited_labels'],
             'r23_integration_components': len(olddeps),
             'r23_integration_labels': len(oldlabels), 'current_labels': len(newlabels),
             'missing_inherited_labels': missing, 'manuscript_copies': copies,
             'historical_results': 'All original primary ledgers and candidates remain at their inherited paths.'}
    save(R / 'PRESERVATION.json', json.dumps(audit, indent=2) + '\n')
    save(R / 'SOURCE_COMMIT.txt', os.environ.get('GITHUB_SHA', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()) + '\n')
    save(R / 'ANALYSIS_SCOPE.md', '''# Scope of the new analysis

The latest addressed report is the R21 report at review commit
281e57b18a2d88de68d2219da1a7194e90570d13. The inherited integration is
c327e0f4f1d5c8c6381dfe0f2b6001fbd7bb7f96.

The R23 primary fitting experiment is not rerun. Its 480 services, 1088
attempted checks, candidate files, timing records and 608 unsuccessful
checks remain unchanged. R24 replays all candidates with a deterministic
residual-energy refinement, symmetrically across every method and regime.
The finite-step theorem and high-precision tests are new. A final-factor
basin calculation tests possible further training against returned-policy
values; it does not relabel the historical R23 target or learning rate.

No population confidence interval, new prospective stopping clock, new
training-randomness distribution or neural cost-superiority result is
inferred. The analysis source is frozen by its committed implementation
and the hashes stored in results/ANALYSIS_SOURCE_SHA256.json.
''')
    save(R / 'README.md', '''# Neural Bellman Operators — R24

This is a continuation of the original paper responding to the R21 referee
report, with the inherited R23 full-policy integration and new learning and
residual-energy results. Earlier branches are not overwritten.

## Reading order

`build/ECTA.pdf` is the native Econometrica-class article. Its main argument
runs from the economic target to continuation control, the all-state policy
bound, finite-step trained-critic learning, and the complete policy study.
`build/response.pdf` answers B1–B9 and M1–M10 individually.
`build/supp.pdf` contains the complete technical supplement and the new
all-candidate refinement audit. `build/applications.pdf` retains all economic
applications. `build/evidence.pdf` retains the earlier nonlinear experiments
that were relocated, not deleted.

## New content and provenance

The new results are in `manuscript/learning_main.tex` and
`manuscript/geometry_main.tex`. `code/refinements.py` implements the verified
energy bound. `code/test_refinements.py` contains independent high-precision
and failure-path tests. `results/REFINEMENT.json` and its complete records
report the symmetric replay; `ANALYSIS_SCOPE.md` states exactly what it does
and does not establish. This is not a new fitting experiment or a replacement
for unfavorable original cost frontiers.

`PRESERVATION.json` checks inherited components and labels and confirms that
no inherited tracked file was modified or deleted. `PUBLICATION_FILES_SHA256.json`
binds the source, evidence summaries and PDFs. `results/TESTS_ALL.json` and
`results/COMPILATION.json` record actual validation outcomes. The original
R23 records remain at `../2026-10-05-r23/results/primary/`.

## Reproduction

Use the pinned numerical dependencies and native TeX packages in
`.github/workflows/nbo-r24-native-publication.yml`. Run the inherited R23
replay, `code/assemble.py`, and `code/build_native.py` from the repository
root. The new analysis can be repeated with `python code/analyze.py` after
adjusting that command to its repository-relative path. It does not modify
original primary records. All five publication wrappers are committed and
can also be compiled directly from the repository root with their peer
reference cycles.
''')
    save(ROOT / 'CURRENT_REVISION.md', '# Neural Bellman Operators — R24\n\nRead `revisions/2026-10-05-r24/README.md`. The native article is `revisions/2026-10-05-r24/ECTA.tex`; its PDF is `revisions/2026-10-05-r24/build/ECTA.pdf`. The response, complete technical supplement, applications and prior evidence are in the same revision.\n')
    print(json.dumps(audit, indent=2), flush=True)


if __name__ == '__main__':
    assemble()
