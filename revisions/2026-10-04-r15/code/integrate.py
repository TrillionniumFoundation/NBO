"""Build one current article from the reviewed, immutable mathematical record.

Default: write reading-copy roots to R15/preview, never to repository roots.
Publication: --write-roots requires all new scientific sections to exist.
Every label in the reviewed source closure receives a current or exact-archive
destination.  Historical sources are read from Git, not silently edited.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
M = R / 'manuscript'
COMMIT = 'f5021cefa71492babfcbfa580e0c984f59a9de26'
PREFIX = M.relative_to(ROOT).as_posix()
LABEL = re.compile(r'\\label\{([^}]+)\}')
INPUT = re.compile(r'\\input\{([^}]+)\}')
REF = re.compile(r'\\(?:eqref|ref|pageref)\{([^}]+)\}')
NEW_SCIENCE = ('manuscript/new_theory.tex', 'manuscript/new_proofs.tex',
               'manuscript/experiment_design.tex', 'manuscript/primary_interpretation.tex',
               'manuscript/paired_interpretation.tex',
               'manuscript/paired_transfer.tex',
               'results/experiment/report/method_evidence.tex',
               'results/publication_tables/table_method_summary.tex',
               'results/publication_tables/table_method_comparisons.tex',
               'results/publication_tables/table_method_seed_endpoints.tex',
               'results/mechanism/report/mechanism_evidence.tex',
               'results/mechanism/report/table_mechanism_evaluation.tex',
               'results/mechanism/report/table_mechanism_welfare.tex',
               'results/mechanism/report/table_mechanism_full.tex',
               'results/mechanism/report/table_mechanism_work.tex',
               'results/paired_transfer/paired_transfer_main.tex',
               'results/paired_transfer/paired_transfer_supplement.tex',
               'results/economic_bounds/economic_bounds.tex',
               'results/scalar_report/scalar_evidence.tex',
               'results/scalar_report/scalar_complete_tables.tex')
_CACHE = {}


def old(path):
    if path not in _CACHE:
        try:
            data = subprocess.check_output(
                ['git', 'show', f'{COMMIT}:{path}'], cwd=ROOT, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # A shallow finalizer checkout need not contain the old Git object.
            # Archived roots and unchanged historical files are acceptable only
            # after exact SHA verification against the pinned source inventory.
            candidate = (R / ('archive/r14-' + path)
                         if path in ('ECTA.tex', 'supp.tex') else ROOT / path)
            data = candidate.read_bytes()
        expected = json.loads((R / 'SOURCE_INVENTORY.json').read_text())['source_files'][path]['sha256']
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError('Reviewed source identity changed: ' + path)
        _CACHE[path] = data.decode()
    return _CACHE[path]


def piece(path, start=None, stop=None):
    text = old(path)
    left = text.index(start) if start else 0
    right = text.index(stop, left) if stop else len(text)
    first = text[:left].count('\n') + 1
    return f'% Reviewed source: {path}, line {first}, commit {COMMIT}\n' + text[left:right]


def expand(text):
    def read(match):
        name = match.group(1)
        if not name.endswith('.tex'):
            name += '.tex'
        return '\n' + expand(piece(name)) + '\n'
    return INPUT.sub(read, text)


def present(text):
    """Editorial changes only: current headings, leading zeros, dated names.

    Revision identifiers inside labels and immutable paths are left untouched.
    This is not a rewrite of any economic assumption or numerical value.
    """
    for name, replacement in {
        'R6': 'initial evaluation study', 'R7': 'finite-policy study',
        'R8': 'continuous-action study', 'R9': 'signed-envelope study',
        'R10': 'absolute-bound study', 'R11': 'policy-specific study',
        'R12': 'population study', 'R14': 'comparison study',
    }.items():
        text = re.sub(r'\b' + name + r'\b', replacement, text)
    text = re.sub(r'(?<![\d\w])\.(\d)', r'0.\1', text)
    text = text.replace(r'\paragraph{', r'\paragraph*{')
    text = text.replace('in this revision', 'in this paper')
    text = text.replace('used in the reviewed draft', 'under joint differentiation')
    text = text.replace('the revised critic objective', 'the block-specific critic objective')
    text = text.replace('The inherited ', 'The ')
    text = text.replace('are now included in the supplement.',
                        r'are retained in the complete numerical archive indexed in Appendix~\ref{app:r15index}.')
    return text


def generated(name, text):
    text = present(expand(text))
    if name.startswith('appendix_'):
        # One subject per appendix; inherited section titles become subtopics.
        first = re.search(r'\\section\{[^}]+\}', text)
        if first:
            before, after = text[:first.end()], text[first.end():]
            text = before + section_to_subsection(after)
    # The leading zero required by the journal makes this inherited display
    # slightly wider.  Split its diffusion term without changing the equation.
    text = text.replace(r'\right]dt' + '\n       +0.15\\,dW_i+0.10\\,dW_0,',
                        r'\right]dt\nonumber\\' + '\n       &\\quad+0.15\\,dW_i+0.10\\,dW_0,')
    (M / name).write_text('% Generated by code/integrate.py; edit extraction rules there.\n'
                         + text.strip() + '\n')


def inp(name):
    return '\\input{' + PREFIX + '/' + name + '}\n'


def result_input(path):
    return '\\input{' + (R / path).relative_to(ROOT).as_posix() + '}\n'


def section_to_subsection(text):
    return text.replace(r'\subsection{', r'\subsubsection{').replace(r'\section{', r'\subsection{')


def materialize():
    a = old('ECTA.tex')
    s = old('supp.tex')
    generated('model.tex', piece('ECTA.tex', r'\section{The Controlled Economy}',
                                r'\section{Neural Bellman Operators}'))
    lit = piece('ECTA.tex', r'\subsection{Relation to the literature}',
                'The inherited continuous-capital result')
    lit += r'''The article proceeds from the economic problem to its evaluation and
improvement map. Section~\ref{sec:theory} states the general verification
results. Sections~\ref{sec:r10continuous}--\ref{sec:r15mechanism} specialize
the welfare account to the capital economy. Section~\ref{sec:economic-scope}
states the other economic applications. The computational study distinguishes
the existing comparison from the current experiment. The supplement collects
the complete models, derivations, proofs, and supporting diagnostics by subject.
'''
    generated('literature.tex', lit)
    method = piece('ECTA.tex', r'\section{Neural Bellman Operators}',
                   'The distinction changes the population problem.')
    method += r'''The distinction is substantive: joint differentiation can move
the critic away from the policy-evaluation root. Appendix~\ref{app:r15evaluation}
gives a counterexample, the recursive lifetime policy derivative, and the
conditioning requirements. The local Hamiltonian objective is not identified
with a lifetime policy gradient under arbitrary state sampling.
The evaluated reference policy may remain fixed while a separate candidate
actor is improved at successive work levels. Updating that reference defines
a new evaluation target and is recorded explicitly.

\subsection{Rollout and costate evaluation}\label{sec:r11learning}
'''
    learning = piece('revisions/2026-10-04-r11/manuscript/learning.tex',
                     'For a frozen policy', r'\subsection{Comparison and selection}')
    learning = learning.replace('Five critic steps and five actor steps are performed for each fresh rollout batch. ',
                                'The number of critic and actor steps per rollout batch is a declared design parameter. ')
    learning = learning.replace('The critic has the same two hidden tanh layers and hard terminal component as the R10 implementation.',
                                'The rollout implementation uses two hidden tanh layers and a hard terminal component.')
    method += learning
    method += piece('revisions/2026-09-29-r6/manuscript/operator.tex')
    generated('method.tex', method)
    general = piece('ECTA.tex', r'\section{Verification, Approximation, and Viscosity Selection}',
                    r'\subsection{Why an integrated differential residual')
    general += r'''Appendix~\ref{app:r15evaluation} gives the differential-residual
counterexample, independent domain and action coverage, the complete-action
envelope, and the guarded finite-model evaluation map. Appendix~\ref{app:proofs}
proves the results, including finite-horizon error accumulation.
'''
    generated('general_theory.tex', general)
    capital_source = 'revisions/2026-10-04-r10/manuscript/continuous.tex'
    specific_source = 'revisions/2026-10-04-r11/manuscript/policy_specific.tex'
    anchor_start = r'Let $\beta\geq\kappa\|B\|_2$'
    actor_start = r'\subsection{The deployed neural map and its numerical guard}'
    cost_start = r'\subsection{Computable scope and cost}'
    transfer_start = r'\subsection{A network-independent diffusion-transfer bound}'
    certificate_start = r'\subsection{A post-training certificate}'
    sample_start = 'For $n$ fresh independent paths'
    capital = piece(capital_source, stop=anchor_start)
    capital += r'''
For the analytical comparison, keep $m_0$ interior and assume
$\rho>0$, $\zeta,\chi,\kappa\geq0$,
and let $\beta\geq\kappa\|B\|_2$ and $s_0\geq\|\Pi y\|_d$.
Choose $\epsilon\geq0$ so that
$[m_0(t)-\epsilon,m_0(t)+\epsilon]\subset[\underline m,M]$
at every date.
With $V^*(y)=\sup_m J_y(m)$ over the full adapted admissible class,
the schedule gap obeys
$0\leq V^*(y)-J_y(m_0)\leq G_d$. The exact scalar integral defining $G_d$
is \eqref{eq:r10anchorbound}; Appendix~\ref{app:r15capitalaccounts}
gives its curvature and dispersion constants, Theorem~\ref{thm:r10tube},
and the complete proof. This analytical bound supplies a common economic
reference. The policy-specific endpoint below measures what the fitted actor
adds to that reference.

'''
    capital += piece(capital_source, actor_start, cost_start)
    capital += section_to_subsection(piece(specific_source, stop=transfer_start))
    capital += r'''
\subsubsection{Transferring the computed payoff to the economy}
The statistic $X_{\phi,h}$ is evaluated for the held controller in
\eqref{eq:r11implementation}, using the same actions when comparing its
internal state with its economic diffusion. Proposition~\ref{prop:r11transfer}
in Appendix~\ref{app:r15capitalaccounts} bounds
$|\Delta_\phi-\E X_{\phi,h}|$ by the saved allowance
$E_{\phi,h}^{\rm all}$. The exact-arithmetic diffusion allowance is
$E_\epsilon(h)+E_0(h)$, with $E_\epsilon$ defined in
\eqref{eq:r11bias}. The appendix gives the additional clipped-innovation,
forward-arithmetic, and enclosed-integration terms. The $O(h)$ diffusion
bound uses bounded actions, the global drift and derivative bounds of the
specified hyperbolic-tangent production function, and additive diffusion;
it requires no derivative bound for the trained network.

\subsubsection{A post-training certificate}
Use the deterministic clipping threshold $b_\phi$ and expectation-tail
allowance $\tau_\phi$ constructed in
Appendix~\ref{app:r15capitaltail}. They account for the unbounded Gaussian
terminal-dispersion term and are not estimated from the final sample range.
Let $X^c_{\phi,h}$ be $X_{\phi,h}$ clipped to
$[-b_\phi,b_\phi]$, so that
$|\E X_{\phi,h}-\E X^c_{\phi,h}|\leq\tau_\phi$.

'''
    capital += section_to_subsection(piece(specific_source, sample_start))
    capital = capital.replace(
        r'\begin{theorem}[Policy-specific continuous-time certificate]',
        r'\Needspace{8\baselineskip}' + '\n'
        + r'\begin{theorem}[Policy-specific continuous-time certificate]')
    capital = capital.replace(
        r'through \eqref{eq:r11gain}--\eqref{eq:r11bias}',
        r'through \eqref{eq:r11gain} and the transfer bound \eqref{eq:r11bias}')
    generated('capital.tex', capital)
    mechanism = piece('revisions/2026-10-04-r14/manuscript/theory.tex',
                       stop=r'\section{Observation and the Economic Implementation}')
    mechanism = mechanism.replace('The new experiment therefore includes',
                                   'The existing comparison therefore includes')
    mechanism = mechanism.replace(r'\input{revisions/2026-10-04-r14/manuscript/mechanism_welfare.tex}',
        r'''The continuous-time performance-difference account in
Proposition~\ref{prop:r14economiccostate} integrates evaluation and action errors
under the candidate's occupation law. Its full statement, proof, and alternative
residual-to-costate conditions are in the supplement. Training-design prediction
errors alone do not meet that account. The current finite-step mechanism below
instead states its continuation target exactly and carries its welfare comparison
to the continuous economy through the separate payoff-transfer bound.''')
    generated('mechanism.tex', mechanism)
    generated('fees.tex', piece('revisions/2026-10-04-r14/manuscript/theory.tex',
                                r'\subsection{When is state-dependent management worth its fee?}'))
    generated('economic_scope.tex', piece('revisions/2026-10-04-r14/manuscript/economic_scope.tex'))

    # Supplement: all substantive application definitions and mathematical
    # arguments remain current; duplicated iteration genealogies do not.
    ev = r'\section{Policy Evaluation, Approximation, and Complete Action Coverage}\label{app:r15evaluation}' + '\n'
    ev += piece('ECTA.tex', 'The distinction changes the population problem.', r'\begin{algorithm}')
    ev += piece('ECTA.tex', r'\subsection{Conditioning and stopping}',
                r'\input{revisions/2026-09-29-r6/manuscript/operator.tex}')
    ev += piece('supp.tex', r'\section{Policy Evaluation and the Recursive Policy Gradient}',
                r'\section{Benchmark Derivations}')
    ev += piece('ECTA.tex', r'\subsection{Why an integrated differential residual',
                r'\input{revisions/2026-09-29-r6/manuscript/bridge.tex}')
    ev += piece('revisions/2026-09-29-r6/manuscript/bridge.tex')
    ev += piece('revisions/2026-10-03-r8/manuscript/method.tex')
    # Guard and signed-cover statements are already in the applications block.
    generated('appendix_evaluation.tex', ev)
    proofs = piece('revisions/2026-10-04-r11/manuscript/retained_proofs.tex',
                   r'\section{Proofs}', r'\input{revisions/2026-10-03-r9/manuscript/proofs.tex}')
    proofs += piece('revisions/2026-10-03-r9/manuscript/proofs.tex')
    proofs += piece('revisions/2026-10-04-r14/manuscript/proofs_r12.tex',
                    stop=r'\subsection{Reproducibility and cost accounting}')
    proofs += piece('revisions/2026-10-04-r14/manuscript/mechanism_welfare.tex')
    generated('appendix_proofs.tex', proofs)
    capital_accounts = r'''\section{Capital Error Bounds and Numerical Accounts}
\label{app:r15capitalaccounts}
This appendix supplies the complete supporting constants and proofs for the
capital model and policy-specific theorem in the main article. The economic
state, objective, action box, benchmark schedule, and implemented controller
are those in \eqref{eq:r10state}--\eqref{eq:r10anchor} and
\eqref{eq:r11implementation}. The analytical anchor, diffusion transfer,
and clipping account concern different error terms; none is a training
convergence assertion.

\section{The analytical anchor and tube bound}
'''
    capital_accounts += piece(capital_source, anchor_start, actor_start)
    capital_accounts += piece(capital_source, cost_start)
    capital_accounts += piece('revisions/2026-10-04-r10/manuscript/proofs.tex')
    capital_accounts += piece(specific_source, transfer_start, certificate_start).replace(
        transfer_start, r'\section{A network-independent diffusion-transfer bound}', 1)
    capital_accounts += r'''\section{The deterministic clipping and tail account}
\label{app:r15capitaltail}
'''
    capital_accounts += piece(specific_source, certificate_start, sample_start).replace(
        certificate_start, '', 1)
    capital_accounts += piece('revisions/2026-10-04-r11/manuscript/proofs.tex')
    capital_accounts = capital_accounts.replace(
        'It is provided in the appendix.',
        r'The complete proof appears in Section~\ref{app:r10proof}.')
    capital_accounts = capital_accounts.replace(
        'The proof is in the supplement.',
        r'The complete proof appears in Section~\ref{app:r11proofs}.')
    generated('appendix_capital_accounts.tex', capital_accounts)
    applications = r'\section{Complete Economic Applications}\label{app:r15applications}' + '\n'
    applications += piece('revisions/2026-10-04-r11/manuscript/retained_applications.tex')
    applications += piece('supp.tex', r'\section{Benchmark Derivations}',
                          r'\section{Stochastic Hessian Objectives and Complexity}')
    applications += piece('revisions/2026-10-04-r11/manuscript/r8_supplement_layout.tex',
                          stop=r'\section{Historical Numerical Record and Source Preservation}')
    # Principal tables and every substantive model/proof remain above.  The
    # eight all-configuration tables repeat the principal results with all raw
    # rows. They remain in the exact source archive rather than being reprinted.
    applications += r'''\subsection{Complete configuration records}
The principal application comparisons above retain the whole-domain failure,
fresh-grid comparison, policy correction costs, and consumption compensation.
The complete configuration tables additionally report every boundary-region
summary, action-saturation rate, training seed, correction record, and capital
payoff pair. They remain in the exact numerical archive identified in
Appendix~\ref{app:r15index}; the editorial map records the original table
labels and source lines. A policy refitted on a nested grid remains a different
object from a frozen policy evaluated off grid. None of those negative results
is replaced by the successful comparison at the center of a state domain.
'''
    generated('appendix_applications.tex', applications)
    implementation = piece('supp.tex', r'\section{Stochastic Hessian Objectives and Complexity}',
                            r'\section{Reproduction and Further Comparisons}')
    implementation += piece('revisions/2026-09-29-r6/manuscript/supplement_details.tex',
                            stop=r'\section{Design, Budgets, and Reproducibility}')
    generated('appendix_implementation.tex', implementation)
    obs = r'\section{Observation and Implementation}\label{app:r15observationtheory}' + '\n'
    obs += piece('revisions/2026-10-04-r14/manuscript/theory.tex',
                 r'\section{Observation and the Economic Implementation}',
                 r'\subsection{When is state-dependent management worth its fee?}')
    obs += piece('revisions/2026-10-04-r14/manuscript/proofs_new.tex')
    generated('appendix_observation.tex', obs)
    diagnostics = r'\section{Independent Numerical Diagnostics}\label{app:r15diagnostics}' + '\n'
    diagnostics += piece('revisions/2026-09-29-r6/manuscript/consumption.tex')
    diagnostics += piece('revisions/2026-10-04-r14/manuscript/reference_supplement.tex')
    diagnostics += piece('revisions/2026-10-04-r14/manuscript/sensing_supplement.tex')
    generated('appendix_diagnostics.tex', diagnostics)
    generated('archive_index.tex', r'''\section{Source and Evidence Index}\label{app:r15index}
The current article has one evaluation--improvement algorithm and one set of
theorem statements. Complete application models and their proofs remain in this
supplement. The preceding reading copy and complete numerical record are
preserved at repository commit
\texttt{f5021cef\allowbreak a71492ba\allowbreak bfcbfa58\allowbreak 0e0c984f\allowbreak 59a9de26}.
The exact main and supplementary roots have Git blob identities, respectively,
\begin{quote}\small\ttfamily
c13f5e95\allowbreak 1b47577f\allowbreak 0cd4bcbb\allowbreak b8b3d003\allowbreak e92e6a33e\\
9ae1d87d\allowbreak dc6da2e0\allowbreak cd047552\allowbreak 2c269da8\allowbreak ee55a1be.
\end{quote}

The revision's source inventory records every source file and its digest in
that reading copy. Its editorial map assigns every preceding equation,
result, section, and table label to the current main text, current supplement,
or the exact archived record. The latter holds complete seed-level tables,
checkpoint histories, earlier fitting protocols, and the successive revision
narratives. Their raw arrays, unsuccessful runs, and compiled records remain
available at their original repository paths. The existing unfavorable direct
and costate comparisons are summarized in the main article; reorganizing their
source does not alter those results or convert an inconclusive interval into
equivalence.
''')
    evidence = r'''% Generated entry point; component files retain their authorship.
\section{Evaluation and Economic Performance}\label{sec:r15evidence}
The continuation-learning comparison and the finite-observation exercise
address separate questions in the capital economy. The former assesses
continuation evaluation and feasible improvement under its stated volatility
parameters and complete method distribution. The latter evaluates the original
saved policies with a protected parent at their original volatility parameters.
Their controller identities, information sets, and probability accounts remain
distinct.
'''
    for name in ['experiment_design.tex', 'baseline_design.tex', 'method_inference.tex']:
        if (M / name).exists(): evidence += inp(name)
    method_report = R / 'results/experiment/report/method_evidence.tex'
    publication = R / 'results/publication_tables'
    main_publication = ['table_method_summary.tex', 'table_method_comparisons.tex']
    redirects = {}
    if method_report.exists() and all((publication / name).exists() for name in main_publication):
        # The report's prose is reproduced mechanically, with exactly two input
        # paths changed. Numerical tables have a single current source, and no
        # number or result sentence is reinterpreted by this editorial layer.
        original = method_report.read_text()
        rendered = original
        for name in main_publication:
            prior = (method_report.parent / name).relative_to(ROOT).as_posix()
            current = (publication / name).relative_to(ROOT).as_posix()
            prior_input, current_input = '\\input{' + prior + '}', '\\input{' + current + '}'
            if rendered.count(prior_input) != 1:
                raise RuntimeError('Expected exactly one publication-table input: ' + prior)
            rendered = rendered.replace(prior_input, current_input)
            redirects[prior] = current
        (M / 'method_evidence.tex').write_text('% Generated from the immutable method report; only the two table input paths differ.\n' + rendered)
        evidence += inp('method_evidence.tex')
        if (M / 'primary_interpretation.tex').exists():
            evidence += inp('primary_interpretation.tex')
    paired_main = R / 'results/paired_transfer/paired_transfer_main.tex'
    paired_supplement = R / 'results/paired_transfer/paired_transfer_supplement.tex'
    paired_ready = (paired_main.exists() and paired_supplement.exists()
                    and (M / 'paired_transfer.tex').exists())
    if paired_ready:
        paired = r'''% Generated entry point after complete-data paired-transfer reporting.
\subsection{Direct comparisons with a shared diffusion-transfer account}
\label{sec:r15pairedcomparison}
The direct statistic already compares policies on common innovations. The
deterministic transfer can use that same coupling. Proposition~\ref{prop:r15pairedtransfer}
in the supplement bounds the error of the payoff difference for two held
policies directly, retaining the original decision grid and realized actions.
The fitted policies, simulated observations, stopping decisions, clipping,
tail account, and simultaneous confidence family remain unchanged.

The following table reports the original and refined endpoints together.
The refinement concerns a proved deterministic allowance; it is not an
additional simulation experiment or a retrospectively changed stopping rule.
Comparisons involving a schedule fallback retain their stated fallback account.
'''
        paired += r'\begingroup\setlength{\tabcolsep}{3pt}' + '\n'
        paired += result_input('results/paired_transfer/paired_transfer_main.tex')
        paired += '\\endgroup\n'
        if (M / 'paired_interpretation.tex').exists():
            paired += inp('paired_interpretation.tex')
        (M / 'paired_comparison.tex').write_text(paired)
        evidence += inp('paired_comparison.tex')
    if (R / 'results/economic_bounds/economic_bounds.tex').exists():
        evidence += result_input('results/economic_bounds/economic_bounds.tex')
    mechanism_dir = R / 'results/mechanism/report'
    mechanism_main = ['mechanism_evidence.tex', 'table_mechanism_evaluation.tex', 'table_mechanism_welfare.tex']
    if all((mechanism_dir / name).exists() for name in mechanism_main):
        wrapper = '% Generated include-only wrapper; all values and narrative remain in the original report.\n'
        wrapper += ''.join(result_input('results/mechanism/report/' + name) for name in mechanism_main)
        (M / 'mechanism_evidence.tex').write_text(wrapper)
        evidence += inp('mechanism_evidence.tex')
    if (R / 'results/scalar_report/scalar_evidence.tex').exists():
        evidence += result_input('results/scalar_report/scalar_evidence.tex')
    if (M / 'observation_evidence.tex').exists(): evidence += inp('observation_evidence.tex')
    (M / 'new_evidence.tex').write_text(evidence)
    report_dir = R / 'results/experiment/report'
    report_tables = [publication / 'table_method_seed_endpoints.tex',
                     report_dir / 'table_method_checkpoint_progress.tex']
    if all(path.exists() for path in report_tables):
        complete = r'\section{Complete Computational Outcomes}\label{app:r15experiment}' + '\n'
        complete += 'The following tables retain every declared stream and saved checkpoint.\n'
        complete += ''.join('\\input{' + path.relative_to(ROOT).as_posix() + '}\n' for path in report_tables)
        (M / 'experiment_supplement.tex').write_text(complete)
        redirects[(report_dir / 'table_method_seed_endpoints.tex').relative_to(ROOT).as_posix()] = report_tables[0].relative_to(ROOT).as_posix()
    mechanism_full = ['table_mechanism_full.tex', 'table_mechanism_work.tex']
    if all((mechanism_dir / name).exists() for name in mechanism_full):
        complete = r'\section{Complete Mechanism Assessment}\label{app:r15mechanismrecord}' + '\n'
        complete += 'The following records retain every candidate and the work used in its independent mechanism assessment.\n'
        complete += ''.join(result_input('results/mechanism/report/' + name) for name in mechanism_full)
        (M / 'mechanism_supplement.tex').write_text(complete)
    if (R / 'results/scalar_report/scalar_complete_tables.tex').exists():
        (M / 'scalar_supplement.tex').write_text('% Generated include-only wrapper.\n'
            + result_input('results/scalar_report/scalar_complete_tables.tex'))
    if paired_ready:
        (M / 'paired_comparison_supplement.tex').write_text(
            '% Generated include-only wrapper; original and refined endpoint records are both retained.\n'
            + r'\begingroup\setlength{\tabcolsep}{2pt}' + '\n'
            + result_input('results/paired_transfer/paired_transfer_supplement.tex')
            + '\\endgroup\n')
    (R / 'PRESENTATION_INPUTS.json').write_text(json.dumps(dict(
        status='Only complete report groups are included; no placeholder outcomes are generated.',
        method_narrative_sha256=(hashlib.sha256(method_report.read_bytes()).hexdigest() if method_report.exists() else None),
        table_input_redirects=redirects,
        paired_transfer_included=paired_ready,
        pending_required_files=[name for name in NEW_SCIENCE if not (R / name).is_file()]), indent=2) + '\n')


def current_closure(text, rootname, locations=None):
    locations = {} if locations is None else locations
    for label in LABEL.findall(text):
        locations.setdefault(label, []).append(rootname)
    for match in INPUT.finditer(text):
        path = ROOT / match.group(1)
        if not path.suffix:
            path = path.with_suffix('.tex')
        if not path.exists():
            raise FileNotFoundError(path)
        current_closure(path.read_text(), path.relative_to(ROOT).as_posix(), locations)
    return locations


def flattened(text):
    return INPUT.sub(lambda m: flattened((ROOT / m.group(1)).read_text()), text)


def verify_mathematical_preservation(inventory, current):
    pattern = re.compile(r'\\begin\{(theorem|proposition|lemma|corollary|assumption|proof)\}(.*?)\\end\{\1\}', re.S)
    def canonical(text):
        return re.sub(r'\s+', ' ', re.sub(r'%[^\n]*', '', present(text))).strip()
    current_matches = list(pattern.finditer(current))
    current_bodies = {canonical(match.group(0)) for match in current_matches}
    records = []
    for path in inventory['source_files']:
        text = old(path)
        for match in pattern.finditer(text):
            body = canonical(match.group(0))
            records.append(dict(path=path, source_line=text[:match.start()].count('\n') + 1,
                                type=match.group(1), labels=LABEL.findall(match.group(0)),
                                statement_sha256=hashlib.sha256(body.encode()).hexdigest(),
                                current_statement_equal_after_editorial_normalization=body in current_bodies))
    reviewed_labels = {label for record in records for label in record['labels']}
    current_new_statements = [dict(type=match.group(1), labels=LABEL.findall(match.group(0)),
                                  statement_sha256=hashlib.sha256(canonical(match.group(0)).encode()).hexdigest())
                              for match in current_matches
                              if match.group(1) != 'proof'
                              and set(LABEL.findall(match.group(0))) - reviewed_labels]
    report = dict(reviewed_commit=COMMIT,
                  normalization='Whitespace/comments, documented revision-name typography substitutions, leading decimal zeros only; no mathematical changes.',
                  reviewed_statements=sum(x['type'] != 'proof' for x in records),
                  reviewed_proof_environments=sum(x['type'] == 'proof' for x in records),
                  preserved=sum(x['current_statement_equal_after_editorial_normalization'] for x in records),
                  current_environment_counts=dict(Counter(match.group(1) for match in current_matches)),
                  current_new_statements=current_new_statements,
                  records=records)
    (R / 'MATHEMATICAL_PRESERVATION.json').write_text(json.dumps(report, indent=2) + '\n')
    if not all(x['current_statement_equal_after_editorial_normalization'] for x in records):
        raise RuntimeError('A reviewed mathematical statement or proof environment is not preserved in the current text')


def integrate(write_roots=False):
    materialize()
    pending = [name for name in NEW_SCIENCE if not (R / name).is_file()]
    if write_roots and pending:
        raise RuntimeError('Publication roots require completed scientific sections: ' + ', '.join(pending))
    preview = R / 'preview'
    preview.mkdir(exist_ok=True)
    build = (R / ('build' if write_roots else 'previewbuild')).relative_to(ROOT).as_posix()
    a = old('ECTA.tex').split(r'\end{frontmatter}')[0] + '\\end{frontmatter}\n'
    if (M / 'abstract.tex').exists():
        abstract = (M / 'abstract.tex').read_text()
        abstract_body = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', abstract, re.S).group(1)
        if len(abstract_body.split()) > 150:
            raise RuntimeError('Econometrica abstract exceeds 150 words')
        a = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',
                   lambda _: abstract.strip(), a, flags=re.S)
    s = old('supp.tex').split(r'\end{frontmatter}')[0] + '\\end{frontmatter}\n'
    lemma_declaration = r'\newtheorem{lemma}[theorem]{Lemma}'
    corollary_declaration = r'\newtheorem{corollary}[theorem]{Corollary}'
    a = a.replace(lemma_declaration, lemma_declaration + '\n' + corollary_declaration)
    s = s.replace(lemma_declaration, lemma_declaration + '\n' + corollary_declaration)
    # Results are sequential in each document.  Mark the supplementary sequence
    # explicitly so a relocated theorem cannot share a displayed identifier
    # with a different theorem in the main article.
    s = s.replace(r'\newtheorem{theorem}{Theorem}',
                  r'\newtheorem{theorem}{Theorem}' + '\n'
                  + r'\renewcommand{\thetheorem}{S.\arabic{theorem}}' + '\n'
                  + r'\renewcommand{\theequation}{S.\arabic{equation}}')
    a = a.replace(r'\usepackage{microtype}',
                  r'\usepackage{microtype}' + '\n' + r'\usepackage{needspace}')
    s = s.replace(r'\usepackage{microtype}',
                  r'\usepackage{microtype}' + '\n' + r'\usepackage{needspace}')
    # float (loaded by algorithm) must precede hyperref.  Loading it afterward
    # makes both the float box and caption install an identical PDF destination.
    # Keep xr-hyper before hyperref; do not alter the publisher's class/config.
    hyperlink = r'\RequirePackage[colorlinks,citecolor=blue,linkcolor=blue,urlcolor=blue]{hyperref}'
    a = a.replace(hyperlink + '\n', '').replace(r'\startlocaldefs', hyperlink + '\n' + r'\startlocaldefs')
    s = s.replace(hyperlink + '\n', '').replace(r'\startlocaldefs', hyperlink + '\n' + r'\startlocaldefs')
    a = a.replace('revisions/2026-10-04-r14/build/supp_refs', build + '/supp_refs')
    s = s.replace('revisions/2026-10-04-r14/build/ECTA_refs', build + '/ECTA_refs')
    main_names = ['introduction.tex', 'literature.tex', 'model.tex', 'method.tex',
                  'algorithm.tex', 'general_theory.tex', 'capital.tex', 'mechanism.tex']
    if (M / 'new_theory.tex').exists(): main_names.append('new_theory.tex')
    main_names += ['implementation_summary.tex', 'fees.tex', 'economic_scope.tex', 'evidence_baseline.tex']
    if (M / 'new_evidence.tex').exists(): main_names.append('new_evidence.tex')
    main_names.append('conclusion.tex')
    a += ''.join(inp(name) for name in main_names)
    supplement_names = ['appendix_evaluation.tex', 'appendix_proofs.tex',
                        'appendix_capital_accounts.tex']
    if (M / 'new_proofs.tex').exists(): supplement_names.append('new_proofs.tex')
    paired_ready = all((R / path).exists() for path in [
        'manuscript/paired_transfer.tex', 'results/paired_transfer/paired_transfer_main.tex',
        'results/paired_transfer/paired_transfer_supplement.tex'])
    if (M / 'paired_transfer.tex').exists(): supplement_names.append('paired_transfer.tex')
    if (M / 'method_inference_proof.tex').exists(): supplement_names.append('method_inference_proof.tex')
    supplement_names += ['appendix_applications.tex', 'appendix_implementation.tex',
                         'appendix_observation.tex', 'appendix_diagnostics.tex']
    for name in ['new_evidence_supplement.tex', 'experiment_supplement.tex', 'mechanism_supplement.tex',
                 'scalar_algebraic_enclosure.tex', 'scalar_supplement.tex',
                 'observation_supplement.tex', 'protected_observation.tex']:
        if (M / name).exists(): supplement_names.append(name)
    if paired_ready: supplement_names.append('paired_comparison_supplement.tex')
    supplement_names.append('archive_index.tex')
    s += r'''\section*{Guide to the Supplement}
The supplement collects general approximation arguments, capital-model proofs,
the complete original economic applications, implementation details, and
independent diagnostics. It uses the main article's notation and cross-references.
Supplementary results and equations use separate continuous sequences
S.1, S.2, and so forth. Tables retain their appendix-letter prefixes.
The final source index identifies the exact preceding numerical record.
\begin{appendix}
'''
    s += ''.join(inp(name) for name in supplement_names)
    tail = '\\bibliographystyle{ecta-fullname}\n\\bibliography{revision_reference}\n\\end{document}\n'
    a += tail
    s += '\\end{appendix}\n' + tail
    locations = current_closure(a, 'ECTA.tex')
    current_closure(s, 'supp.tex', locations)
    duplicates = {k: v for k, v in locations.items() if len(v) > 1}
    if duplicates:
        raise RuntimeError('Duplicate current labels: ' + json.dumps(duplicates))
    alltext = flattened(a) + '\n' + flattened(s)
    refs = set(REF.findall(alltext))
    missing_refs = sorted(refs - locations.keys())
    inv = json.loads((R / 'SOURCE_INVENTORY.json').read_text())
    verify_mathematical_preservation(inv, alltext)
    mapping = []
    for path, record in inv['source_files'].items():
        source_text = old(path)
        for match in LABEL.finditer(source_text):
            label = match.group(1)
            current = label in locations
            mapping.append(dict(label=label, source_path=path,
                                source_line=source_text[:match.start()].count('\n') + 1,
                                source_git_blob=record['git_blob'], source_sha256=record['sha256'],
                                destination='current' if current else 'exact_archive',
                                current_files=locations.get(label, []),
                                archive_commit=COMMIT, archive_path=path,
                                reason=('Substantive statement or current supporting evidence retained.' if current
                                        else 'Complete preceding experiment or iteration narrative remains in the immutable reviewed record.')))
    # Mathematical labels may not disappear under an editorial reorganization.
    missing_math = [x['label'] for x in mapping if x['destination'] == 'exact_archive'
                    and x['label'].startswith(('eq:', 'thm:', 'prop:', 'lem:', 'ass:'))]
    report = dict(reviewed_commit=COMMIT, root_write_authorized_by_cli=write_roots,
                  pending_scientific_sections=pending,
                  current_main_files=main_names, current_supplement_files=supplement_names,
                  current_labels=len(locations), reviewed_labels=len(mapping),
                  preserved_current_labels=sum(x['destination'] == 'current' for x in mapping),
                  exact_archive_labels=sum(x['destination'] == 'exact_archive' for x in mapping),
                  mathematical_labels_missing_from_current=missing_math,
                  unresolved_current_references=missing_refs,
                  algorithm_count=len(re.findall(r'\\begin\{algorithm\}', alltext)),
                  archived_roots={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (R / 'archive').glob('*') if p.is_file()},
                  labels=mapping)
    (R / 'EDITORIAL_MAP.json').write_text(json.dumps(report, indent=2) + '\n')
    if missing_math:
        raise RuntimeError('Substantive mathematical labels must remain current: ' + ', '.join(missing_math))
    if write_roots and missing_refs:
        raise RuntimeError('Unresolved publication references: ' + ', '.join(missing_refs))
    if report['algorithm_count'] != 1:
        raise RuntimeError('Current article must have exactly one algorithm')
    (preview / 'ECTA.tex').write_text(a)
    (preview / 'supp.tex').write_text(s)
    response = a.split(r'\begin{document}')[0]
    response = re.sub(r'\\externaldocument\{[^}]+\}(?:\[[^]]*\])?', '', response)
    response += '\\externaldocument{' + build + '/ECTA_refs}[ECTA.pdf]\n'
    response += '\\externaldocument{' + build + '/supp_refs}[supp.pdf]\n'
    response += '\\begin{document}\n' + inp('response_body.tex') + '\\end{document}\n'
    if (M / 'response_body.tex').exists():
        (preview / 'response.tex').write_text(response)
        (R / 'response.tex').write_text(response)
    if write_roots:
        (ROOT / 'ECTA.tex').write_text(a)
        (ROOT / 'supp.tex').write_text(s)
    print(json.dumps({k: v for k, v in report.items() if k != 'labels'}, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-roots', action='store_true', help='explicitly materialize publication roots')
    integrate(**vars(parser.parse_args()))
