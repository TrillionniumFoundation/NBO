"""Materialize the R14 reading copy from byte-preserved reviewed roots."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
M = R / 'manuscript'
PREFIX = str(M.relative_to(ROOT))


def source(name):
    return (M / name).read_text()


def integrate():
    a = (R / 'archive/ECTA.base.tex').read_text()
    s = (R / 'archive/supp.base.tex').read_text()
    original_labels = set(re.findall(r'\\label\{([^}]+)\}', a))
    a = a.replace(r'\documentclass[ecta,draft]', r'\documentclass[ecta,nameyear,draft]')
    s = s.replace(r'\documentclass[ecta,draft]', r'\documentclass[ecta,nameyear,draft]')
    a = a.replace(r'\usepackage{xr}' + '\n', '').replace(r'\RequirePackage[colorlinks', r'\usepackage{xr-hyper}' + '\n' + r'\RequirePackage[colorlinks')
    s = s.replace(r'\usepackage{xr}' + '\n', '').replace(r'\RequirePackage[colorlinks', r'\usepackage{xr-hyper}' + '\n' + r'\RequirePackage[colorlinks')
    a = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',
               lambda _: source('abstract.tex').strip(), a, flags=re.S)
    start, end = a.index(r'\section{Introduction}'), a.index(r'\subsection{Relation to the literature}')
    a = a[:start] + source('introduction.tex') + '\n' + a[end:]
    roadmap_start = a.index('Section~\\ref{sec:model} specifies')
    roadmap_end = a.index(r'\section{The Controlled Economy}', roadmap_start)
    roadmap = r'''Section~\ref{sec:model} states the controlled economy, Section~\ref{sec:method} defines NBO, and Section~\ref{sec:theory} establishes the general verification accounts. Section~\ref{sec:economic-scope} states the economic applications and locates their complete derivations. The capital results and Section~\ref{sec:r11specific} supply the absolute and policy-specific benchmarks. Sections~\ref{sec:r12theory}--\ref{sec:r14work} connect costates to welfare, specify observation and implementation, and report the executed comparisons. The supplement contains complete proofs, every primary and fixed-work comparison, reference and sensing diagnostics, and the full prior application records.

'''
    a = a[:roadmap_start] + roadmap + a[roadmap_end:]
    insertion = r'\input{revisions/2026-10-04-r10/manuscript/continuous.tex}'
    a = a.replace(insertion, '\\input{' + PREFIX + '/economic_scope.tex}\n\n' + insertion, 1)
    moved = []
    for name in ['learning', 'study']:
        text = '\\input{revisions/2026-10-04-r11/manuscript/' + name + '.tex}'
        if a.count(text) != 1:
            raise ValueError('Unexpected historical input ' + name)
        moved.append(text)
        a = a.replace(text, '')
    cstart, cend = a.index(r'\section{Conclusion}'), a.index(r'\bibliographystyle')
    (R / 'archive/conclusion.base.tex').write_text(a[cstart:cend])
    new_sections = '\n'.join('\\input{' + PREFIX + '/' + name + '}' for name in [
        'theory.tex', 'study.tex', 'work_study.tex'])
    a = a[:cstart] + new_sections + '\n' + source('conclusion.tex') + a[cend:]
    a = a.replace('revisions/2026-10-04-r11/build/supp_refs',
                  'revisions/2026-10-04-r14/build/supp_refs')
    s = s.replace('revisions/2026-10-04-r11/build/ECTA_refs',
                  'revisions/2026-10-04-r14/build/ECTA_refs')
    a = a.replace(r'\externaldocument{revisions/2026-10-04-r14/build/supp_refs}', r'\externaldocument{revisions/2026-10-04-r14/build/supp_refs}[supp.pdf]')
    s = s.replace(r'\externaldocument{revisions/2026-10-04-r14/build/ECTA_refs}', r'\externaldocument{revisions/2026-10-04-r14/build/ECTA_refs}[ECTA.pdf]')
    addition = r'''\section{Guide to the Supplement}
The opening sections prove the costate, performance, and observation results used in the main article and report all primary and fixed-work outcomes. The retained sections give the complete application-specific arguments and earlier numerical evidence. A finite-game, finite-grid, or scalar-reference statement retains its stated domain; each continuous-time capital statement uses its own transfer account.
'''
    for name in ['proofs_r12.tex', 'proofs_new.tex', 'full_results.tex',
                 'extension_supplement.tex',
                 'reference_supplement.tex', 'sensing_supplement.tex']:
        addition += '\\input{' + PREFIX + '/' + name + '}\n'
    s = s.replace(r'\section{Organization of the Revised Supplement}',
                  addition + '\n' + r'\section{Earlier Verification and Application Results}', 1)
    tail = r'''
\section{Earlier Learning and Experimental Record}
The following learning specification and study are retained from the reviewed manuscript. Their fitted policies and numerical protocols are distinct from the complete population and direct-method study reported in the main article and at the beginning of this supplement.
'''
    tail += '\n'.join(moved) + '\n'
    s = s.replace(r'\bibliographystyle', tail + r'\bibliographystyle', 1)
    if not original_labels <= set(re.findall(r'\\label\{([^}]+)\}', a)):
        raise ValueError('A reviewed main-root label was lost')
    for name, text in [('ECTA.tex', a), ('supp.tex', s)]:
        (ROOT / name).write_text(text)
    response = a.split(r'\begin{document}')[0]
    response = re.sub(r'\\externaldocument\{[^}]+\}(?:\[[^\]]*\])?', '', response)
    response += r'\externaldocument{revisions/2026-10-04-r14/build/ECTA_refs}[ECTA.pdf]' + '\n'
    response += r'\externaldocument{revisions/2026-10-04-r14/build/supp_refs}[supp.pdf]' + '\n'
    response += '\\begin{document}\n\\input{' + PREFIX + '/response_body.tex}\n\\end{document}\n'
    (R / 'response.tex').write_text(response)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    mapping = {
        'base_commit': 'c8299feb2a3af0f147295d50036c8d8acca8f65c',
        'review_commit': '65110ed2991f4b955d2df37b2ab8635b12df5d1c',
        'title': 'Neural Bellman Operators',
        'archived_roots': {p.name: digest(p) for p in (R / 'archive').iterdir() if p.is_file()},
        'retained_main_root_labels': sorted(original_labels),
        'moved_intact_to_supplement': moved,
        'original_applications_visible_in_main': str((M / 'economic_scope.tex').relative_to(ROOT)),
        'historical_revision_files_edited': [],
        'new_manuscript_files': {p.name: digest(p) for p in M.glob('*.tex')},
    }
    (R / 'EDITORIAL_MAP.json').write_text(json.dumps(mapping, indent=2) + '\n')


if __name__ == '__main__':
    integrate()
