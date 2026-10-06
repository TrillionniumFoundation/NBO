"""Source-bound R32 publication and unchanged-protocol replay.

Run from a clean working directory, not a clone of the repository's binary
history. All scientific inputs are fetched by immutable commit and hashed.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import zipfile

REPO = 'TrillionniumFoundation/NBO'
BASE = '2bbd8900080a009e806f8d9d0f27fb9f0eefe9e1'
SCIENCE = '01d627862b2c6fbc00c49c0c61968fc8a76e3363'
SOURCE = os.environ['NBO_SOURCE_SHA']
ROOT = Path(os.environ['NBO_WORKSPACE']).resolve()
REL = 'revisions/2026-10-06-r32'
R = ROOT/REL
OLD = 'revisions/2026-10-05-r21'
RECORD = {}
INPUT = re.compile(r'(?m)^\s*\\(?:input|include)\s*\{([^}]+)\}')
LABEL = re.compile(r'\\label\s*\{([^}]+)\}')
DOCS = ['historical_article', 'historical_supplement', 'applications', 'supp', 'ECTA', 'response']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get(url, authenticated=False):
    headers = {'User-Agent': 'NBO-R32-reproduction'}
    if authenticated:
        headers['Authorization'] = 'Bearer '+os.environ['GITHUB_TOKEN']
        headers['Accept'] = 'application/vnd.github+json'
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as h:
                return h.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404 or attempt == 3:
                raise
        except (OSError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(1+attempt)
    raise RuntimeError('Unreachable fetch state')


def api(path):
    return json.loads(get('https://api.github.com/repos/'+REPO+'/'+path, True))


def need(name, ref=BASE):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Unsafe repository path: '+name)
    dest = ROOT/p
    if dest.exists():
        return dest
    data = get('https://raw.githubusercontent.com/'+REPO+'/'+ref+'/'+urllib.parse.quote(name, safe='/'))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    RECORD[name] = {'commit': ref, 'sha256': sha(data), 'bytes': len(data),
                    'git_blob_sha': hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
    return dest


def clean_tex(text):
    return re.sub(r'(?m)(?<!\\)%.*$', '', text)


def literal_path(name, suffix):
    if any(c in name for c in ('\\', '#', '{', '}')):
        raise ValueError('Nonliteral scientific include needs explicit routing: '+name)
    return name if Path(name).suffix else name+suffix


def closure(name, seen=None):
    seen = set() if seen is None else seen
    if name in seen:
        return seen
    seen.add(name)
    p = need(name)
    if p.suffix != '.tex':
        return seen
    text = clean_tex(p.read_text())
    for child in INPUT.findall(text):
        closure(literal_path(child.strip(), '.tex'), seen)
    for group in re.findall(r'\\bibliography\s*\{([^}]+)\}', text):
        for bib in group.split(','):
            need(literal_path(bib.strip(), '.bib'))
    for image in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\s*\{([^}]+)\}', text):
        if any(c in image for c in ('\\', '#', '{', '}')):
            continue
        names = [image] if Path(image).suffix else [image+x for x in ('.pdf', '.png', '.jpg')]
        for k, candidate in enumerate(names):
            try:
                need(candidate)
                break
            except urllib.error.HTTPError as exc:
                if exc.code != 404 or k == len(names)-1:
                    raise
    return seen


def write(name, text):
    p = R/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf8')
    return p


def save_record():
    write('audit/INPUT_FILES.json', json.dumps(RECORD, indent=2, sort_keys=True)+'\n')


def run(cmd, logname, env=None):
    path = R/'audit'/logname
    path.parent.mkdir(parents=True, exist_ok=True)
    print('EXECUTE', ' '.join(map(str, cmd)), flush=True)
    start = time.perf_counter()
    with path.open('w') as out:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT)
    text = path.read_text(errors='replace')
    print(text[-22000:], flush=True)
    result = {'command': list(map(str, cmd)), 'returncode': proc.returncode,
              'elapsed_seconds': time.perf_counter()-start, 'log': str(path.relative_to(ROOT))}
    m = re.search(r'Ran (\d+) tests? in', text)
    if m:
        result['tests'] = int(m.group(1))
    if proc.returncode:
        raise RuntimeError('Command failed; retained log: '+str(path))
    return result


def fetch_code_folder(revision):
    name = 'revisions/'+revision+'/code'
    entries = api('contents/'+name+'?ref='+BASE)
    for row in entries:
        if row['type'] == 'file' and row['name'].endswith('.py'):
            need(row['path'])


def prepare():
    ROOT.mkdir(parents=True, exist_ok=True)
    new_files = ['README.md', 'response.md', 'manuscript/curvature.tex',
                 'code/curvature_certificate.py', 'code/test_geometry.py',
                 'publication/assemble.py', 'publication/publish.py']
    for f in new_files:
        need(REL+'/'+f, SOURCE)
    for rev in ('2026-10-05-r23', '2026-10-05-r25', '2026-10-06-r27',
                '2026-10-06-r28', '2026-10-06-r29'):
        fetch_code_folder(rev)
    manifest_path = need('revisions/2026-10-06-r30/protocols/SOURCE_FREEZE.json')
    manifest = json.loads(manifest_path.read_text())
    for path, expected in manifest['files'].items():
        if sha(need(path).read_bytes()) != expected:
            raise RuntimeError('Frozen scientific input mismatch: '+path)
    checks = []
    checks.append(run([sys.executable, '-m', 'unittest', 'discover', '-s',
        'revisions/2026-10-06-r29/code', '-p', 'test_entropic_budget.py', '-v'], 'TESTS_INHERITED_R29.log'))
    checks.append(run([sys.executable, '-m', 'unittest', 'discover', '-s',
        REL+'/code', '-p', 'test_geometry.py', '-v'], 'TESTS_R32.log'))
    write('audit/TEST_RESULTS.json', json.dumps(checks, indent=2)+'\n')
    for name in ('econsocart.cls', 'econsocart.cfg', 'ecta-fullname.bst',
                 'revision_reference.bib', 'reference.bib', 'appendix_reference.bib'):
        need(name)
    old_closure = set()
    for name in ('ECTA.tex', 'supp.tex', 'applications.tex'):
        old_closure |= closure(OLD+'/'+name)
    extras = [
        'revisions/2026-10-05-r23/manuscript/full_policy.tex',
        'revisions/2026-10-05-r23/manuscript/full_policy_proofs.tex',
        'revisions/2026-10-05-r23/manuscript/full_policy_experiment.tex',
        'revisions/2026-10-06-r27/manuscript/entropic_main.tex',
        'revisions/2026-10-06-r27/manuscript/entropic_proofs.tex',
        'revisions/2026-10-06-r31/manuscript/constructive_risk.tex',
        'revisions/2026-10-06-r31/manuscript/constructive_proofs.tex',
        'revisions/2026-10-06-r31/manuscript/introduction.tex',
        'revisions/2026-10-06-r31/manuscript/conclusion.tex']
    for name in extras:
        closure(name)
    need('revisions/2026-10-06-r27/references.bib')
    need('revisions/2026-10-06-r31/results/EXECUTION_COMPLETE.json')
    blob = api('git/blobs/947147612cc22f5e10ff15faf347fcb3de222656')
    report = base64.b64decode(blob['content'])
    if hashlib.sha1(b'blob '+str(len(report)).encode()+b'\0'+report).hexdigest() != '947147612cc22f5e10ff15faf347fcb3de222656':
        raise RuntimeError('Referee identity mismatch')
    write('audit/referee_report_R21.md', report.decode())
    labels = sorted(set().union(*(set(LABEL.findall((ROOT/p).read_text())) for p in old_closure)))
    write('audit/HISTORICAL_PUBLICATION.json', json.dumps({'base': BASE,
          'components': sorted(old_closure), 'labels': labels}, indent=2)+'\n')
    save_record()


def tex_escape(s):
    table = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
             '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
             '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(table.get(c, c) for c in str(s))


def evidence(rows, summary):
    table = [r'\begin{table}[t]', r'\caption{Complete recursive-policy services: separately identified replay}',
             r'\label{tab:r32replay}', r'\centering\small', r'\begin{tabular}{rrlrrr}',
             r'\toprule', r'$d$ & $\theta/d$ & Generator & Certified & Seconds & Largest bound \\', r'\midrule']
    for d in (10, 50):
        for risk in (0., 2., 4.):
            for method in ('NBO-primitive-risk', 'structural'):
                group = [r for r in rows if r['dimension'] == d and r['risk_per_dimension'] == risk and r['method'] == method]
                good = [r for r in group if r['status'] == 'certified']
                bounds = [r['certificate']['policy_gap_upper'] for r in group if 'certificate' in r]
                bound = f'{max(bounds):.3g}' if bounds else '--'
                clock = statistics.mean(r['complete_service_seconds'] for r in group)
                label = 'NBO' if method == 'NBO-primitive-risk' else 'Structural'
                table.append(f'{d} & {risk:g} & {label} & {len(good)}/{len(group)} & {clock:.4f} & {bound} '+r'\\')
    table += [r'\bottomrule', r'\end{tabular}', r'\par\medskip\parbox{.95\linewidth}{\footnotesize Each row includes all three economic regimes and both registered seeds. Seconds are the mean realized complete service clock, not a population expectation. The largest bound includes the relative action-execution allowance. The target is $10^{-4}$. Failures are retained in the denominators.}', r'\end{table}']
    write('results/replay_table.tex', '\n'.join(table)+'\n')
    clocks = []
    for d in (10, 50):
        for regime in ('anchor', 'technology', 'valuation'):
            for risk in (0., 2., 4.):
                group = [r for r in rows if r['dimension'] == d and r['regime'] == regime and r['risk_per_dimension'] == risk]
                costs = {m: statistics.mean(r['complete_service_seconds'] for r in group if r['method'] == m)
                         for m in ('NBO-primitive-risk', 'structural')}
                clocks.append({'dimension': d, 'regime': regime, 'risk_per_dimension': risk,
                    'nbo_over_structural': costs['NBO-primitive-risk']/costs['structural'], **costs})
    write('results/COMPLETE_WORK_COMPARISON.json', json.dumps(clocks, indent=2)+'\n')
    wins = sum(r['nbo_over_structural'] < 1 for r in clocks)
    nbo = [r for r in rows if r['method'] == 'NBO-primitive-risk']
    update_count = sum(r.get('counters', {}).get('hidden_updates', 0) for r in nbo)
    certified = sum(r['status'] == 'certified' for r in rows)
    text = r'''\section{Recursive Policy Accuracy and Complete Work}\label{sec:r32evidence}
The recursive experiment uses the capital primitives above and the entropic
criterion, with $\theta/d\in\{0,2,4\}$. The two registered seeds are 29011 and
29029. Both candidate generators receive the same analytic Gaussian primitives.
The neural generator follows the primitive allocation, then fits its own
finalized future at each date. The structural generator uses the same primitives
without that factor training. The independent verifier receives only the
returned gains and model; it does not call an optimal-policy recursion.

The original 72-service catalogue, ordering, tolerances, initialization rule,
slack, caps, and failure rule are unchanged. Its scientific source predates
this revision. The present execution is a separately identified replay, not a
replacement for the original measured clocks and not an additional population
sample. The estimand is deterministic certification and realized complete work
on this declared catalogue. In particular, the two seeds do not support a
method-level reliability interval over an unspecified population of fits.

The acceptance test is a full-policy gap of at most $10^{-4}$, including the
relative action-execution allowance $10^{-12}$. Every real vector action and
every state are covered by the coefficient inequalities; future controls are
reoptimized in each regime. The initial comparison is uniform on
$\|x_0\|^2\leq d$. The directly specified model requires no class restriction
or discretization transfer, but its moment-domain and execution conditions
remain substantive premises.
'''
    text += f'\nThe replay returns {certified} certified services out of {len(rows)}. '
    text += f'The neural records contain {update_count} hidden-weight updates in total. '
    text += 'All unsuccessful thresholds and exceptions, when present, remain in the service record.\n'
    text += r'\input{revisions/2026-10-06-r32/results/replay_table.tex}'+'\n\n'
    text += f'Across the 18 dimension--regime--risk cells, mean neural service time is below structural time in {wins} cells. '
    text += r'''This is a descriptive comparison of these complete executions.
A successful neural policy certificate establishes accuracy of the returned
policy; it does not establish that the neural construction is necessary or
least costly. In particular, the structural solution remains available in this
quadratic economy. The theorem's finite training budget is a constructive
property, not a sampling or wall-clock advantage over an analytic comparator.

Initialization, primitive-envelope construction, factor updates and Gram
checks, actor solves, candidate serialization, durable writes, and final
verification are all charged to the service. The closing service-ledger write
and common execution overhead are separately recorded. The counters distinguish
actor solves, own-policy transforms, and hidden updates; both methods use
analytic Gaussian information and have zero simulation transitions. The
process memory high-water mark is not a method-specific memory comparison.

The exact-rational checks in Section~\ref{sec:r32geometry} are separate
small-matrix validation exercises. They test the singular saddle, target-error
allowance, Hessian identity, and recursive terminal boundary. Their outcomes
are not counted as additional economic services or used to change the frozen
stopping rule. The source manifest, all new raw service records, attempted
certificates, model and candidate arrays, test logs, and compilation logs are
part of the replication release.

The earlier finite-law services retain their different estimand. Their
check-and-refresh NBO rule costs more than fresh refitting in all eight
future-change cells, while cached simulation is the least-cost fully certified
procedure in those cells. These adverse outcomes are preserved in the
historical article and supplement. The new full-policy and training statements
address different mathematical obligations; they do not rewrite that frontier.
'''
    write('manuscript/evidence.tex', text)


def replace_external(text, doc):
    text = re.sub(r'(?m)^\\externaldocument[^\n]*\n', '', text)
    ext = ''.join('\\externaldocument{'+REL+'/build/'+doc+'_from_'+other+'}['+other+'.pdf]\n'
                  for other in DOCS if other != doc)
    return text.replace(r'\begin{document}', ext+r'\begin{document}', 1)


def front(title):
    return '\n'.join([r'\begin{document}', r'\begin{frontmatter}', '\\title{'+title+'}',
        r'\runtitle{Neural Bellman Operators}', r'\begin{aug}',
        r'\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}}',
        r'\address[id=add1]{Peking University}', r'\end{aug}', r'\end{frontmatter}', ''])


def inputs(paths):
    return ''.join('\\input{'+p+'}\n' for p in paths)


def make_publication():
    original = (ROOT/OLD/'ECTA.tex').read_text()
    old_supp = (ROOT/OLD/'supp.tex').read_text()
    original_app = (ROOT/OLD/'applications.tex').read_text()
    pre = original.split(r'\begin{document}')[0]
    pre = re.sub(r'(?m)^\\externaldocument[^\n]*\n', '', pre)
    pre += '\n'+r'\setlength{\emergencystretch}{2em}'+'\n'
    bibs = 'revision_reference,revisions/2026-10-05-r19-integrated/references,revisions/2026-10-05-r21/references,revisions/2026-10-06-r27/references'
    end = '\n\\bibliographystyle{ecta-fullname}\n\\bibliography{'+bibs+'}\n\\end{document}\n'
    abstract = '''This paper develops Neural Bellman Operators for policy evaluation and
feasible improvement in controlled economies. Centered continuation errors
connect evaluation to decisions, and full-action Bellman bounds connect
returned decisions to policy accuracy. For a trainable square continuation
in a recursive capital economy, economic primitives determine a finite
training schedule before policy targets are supplied. A gradient--curvature
bound gives a second route from updated hidden weights to continuation
accuracy, including explicitly bounded own-policy evaluation error. An
independent verifier assesses rounded vector policies under continuous
Gaussian shocks and recursive risk preferences. The numerical studies
separate policy accuracy, constructive neural training, and complete work;
strong conventional and structural comparators and all adverse outcomes
remain visible. The original controlled-diffusion model and its distinct
economic applications are retained with their own domain and comparison
conditions. A policy certificate is not equated with neural cost superiority.'''
    matter = original.split(r'\begin{document}', 1)[1].split(r'\end{frontmatter}', 1)[0]+r'\end{frontmatter}'+'\n'
    matter = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}', lambda m: '\\begin{abstract}\n'+abstract+'\n\\end{abstract}', matter, flags=re.S)
    construction = (ROOT/'revisions/2026-10-06-r31/manuscript/constructive_risk.tex').read_text()
    old = 'The terminal actor uses\n$Q_f$ directly.'
    new = 'The terminal actor uses the known transformed coefficient\n$\\Psi_\\theta(Q_f)$ without a factor fit; its formula is\n\\eqref{eq:r32terminal}.'
    if old not in construction:
        raise RuntimeError('Expected terminal editorial anchor missing')
    write('manuscript/constructive_risk.tex', construction.replace(old, new))
    main_paths = [
      'revisions/2026-10-06-r31/manuscript/introduction.tex',
      'revisions/2026-10-04-r16/manuscript/literature.tex',
      'revisions/2026-10-05-r19-integrated/manuscript/literature_addition.tex',
      'revisions/2026-10-04-r16/retained/manuscript/model.tex',
      'revisions/2026-10-04-r16/retained/manuscript/method.tex',
      'revisions/2026-10-04-r16/retained/manuscript/algorithm.tex',
      'revisions/2026-10-05-r19-integrated/manuscript/targets.tex',
      'revisions/2026-10-05-r19-integrated/manuscript/decision_main.tex',
      'revisions/2026-10-05-r21/manuscript/composition_main.tex',
      'revisions/2026-10-05-r23/manuscript/full_policy.tex',
      'revisions/2026-10-06-r27/manuscript/entropic_main.tex',
      REL+'/manuscript/constructive_risk.tex', REL+'/manuscript/curvature.tex',
      'revisions/2026-10-05-r23/manuscript/full_policy_experiment.tex',
      REL+'/manuscript/evidence.tex',
      'revisions/2026-10-04-r16/retained/manuscript/economic_scope.tex',
      'revisions/2026-10-06-r31/manuscript/conclusion.tex']
    main = pre+r'\begin{document}'+matter+inputs(main_paths)+end
    write('ECTA.tex', replace_external(main, 'ECTA'))
    supp_pre = pre.replace(r'\newtheorem{theorem}{Theorem}',
        r'\newtheorem{theorem}{Theorem}'+'\n'+r'\renewcommand{\thetheorem}{S.\arabic{theorem}}'+'\n'+
        r'\renewcommand{\theequation}{S.\arabic{equation}}'+'\n'+r'\renewcommand{\thesection}{S.\arabic{section}}')
    supp_paths = ['revisions/2026-10-05-r19-integrated/manuscript/decision_proofs.tex',
        'revisions/2026-10-05-r21/manuscript/composition_proofs.tex',
        'revisions/2026-10-05-r23/manuscript/full_policy_proofs.tex',
        'revisions/2026-10-06-r27/manuscript/entropic_proofs.tex',
        'revisions/2026-10-06-r31/manuscript/constructive_proofs.tex']
    write('supp.tex', replace_external(supp_pre+front('Technical Supplement to Neural Bellman Operators')+inputs(supp_paths)+end, 'supp'))
    write('historical_article.tex', replace_external(original, 'historical_article'))
    write('historical_supplement.tex', replace_external(old_supp, 'historical_supplement'))
    write('applications.tex', replace_external(original_app, 'applications'))
    blocks = []
    for block in (R/'response.md').read_text().split('\n\n'):
        block = block.strip().replace('`', '')
        if not block or block.startswith('# '):
            continue
        if block.startswith('### '):
            blocks.append('\\subsection*{'+tex_escape(block[4:])+'}')
        elif block.startswith('## '):
            blocks.append('\\section*{'+tex_escape(block[3:])+'}')
        else:
            blocks.append(tex_escape(block))
    write('response.tex', replace_external(pre+front('Response to the Referee on Neural Bellman Operators')+'\n\n'.join(blocks)+'\n\\end{document}\n', 'response'))
    paths = set()
    for doc in DOCS:
        paths |= closure(REL+'/'+doc+'.tex')
    old = json.loads((R/'audit/HISTORICAL_PUBLICATION.json').read_text())
    preserved = set().union(*(set(LABEL.findall((ROOT/p).read_text())) for p in paths))
    missing = sorted(set(old['labels'])-preserved)
    if missing:
        raise RuntimeError('Historical labels missing: '+repr(missing))
    write('audit/PRESERVATION.json', json.dumps({'base_commit': BASE,
        'original_publication_components': len(old['components']),
        'original_publication_labels': len(old['labels']), 'missing_labels': missing,
        'old_paths_modified': [], 'original_wrappers_preserved_at': OLD,
        'publication_changes': 'New wrappers and explicit terminal-transform clarification; no original source replacement'}, indent=2)+'\n')
    save_record()


def execute():
    if (R/'audit/INPUT_FILES.json').exists():
        RECORD.update(json.loads((R/'audit/INPUT_FILES.json').read_text()))
    env = os.environ.copy()
    env['NBO_SOURCE_COMMIT'] = SCIENCE
    result = run([sys.executable, 'revisions/2026-10-06-r30/code/execute.py'], 'REPLAY_R30.log', env)
    primary = ROOT/'revisions/2026-10-06-r30/results/primary'
    target = R/'results/replay'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(primary, target)
    summary = json.loads((target/'SUMMARY.json').read_text())
    rows = [json.loads(line) for line in (target/'services.jsonl').read_text().splitlines() if line.strip()]
    if len(rows) != 72 or len({r['key'] for r in rows}) != 72:
        raise RuntimeError('Complete unique catalogue not preserved')
    identity = {'base_commit': BASE, 'publication_source_commit': SOURCE,
        'scientific_source_commit': SCIENCE, 'run_id': os.environ.get('GITHUB_RUN_ID'),
        'actual_execution_location': 'GitHub Actions ubuntu-latest',
        'literal_harness_identity_note': 'The frozen harness literal local research container is retained. This wrapper identifies the actual runner.',
        'primary_outcomes_replaced': False, 'execution': result,
        'services': len(rows), 'certified': sum(r['status'] == 'certified' for r in rows),
        'failed': sum(r['status'] == 'failed' for r in rows),
        'uncertified': sum(r['status'] == 'uncertified' for r in rows)}
    write('audit/REPLAY_IDENTITY.json', json.dumps(identity, indent=2)+'\n')
    evidence(rows, summary)
    make_publication()


def doc_labels(doc):
    paths = closure(REL+'/'+doc+'.tex')
    return set().union(*(set(LABEL.findall((ROOT/p).read_text())) for p in paths))


def refresh_refs():
    build = R/'build'; build.mkdir(exist_ok=True)
    for doc in DOCS:
        used = doc_labels(doc)
        priority = ['ECTA', 'supp', 'applications', 'historical_article', 'historical_supplement', 'response']
        for other in priority:
            if other == doc:
                continue
            aux = build/(other+'.aux')
            lines = []
            if aux.exists():
                for line in aux.read_text(errors='replace').splitlines():
                    match = re.match(r'\\newlabel\{([^}]+)\}', line)
                    if match and match.group(1) not in used:
                        used.add(match.group(1)); lines.append(line)
            (build/(doc+'_from_'+other+'.aux')).write_text('\\relax\n'+'\n'.join(lines)+'\n')


def build():
    RECORD.update(json.loads((R/'audit/INPUT_FILES.json').read_text()))
    env = os.environ.copy()
    env['BIBINPUTS'] = str(ROOT)+':'+env.get('BIBINPUTS', '')
    env['BSTINPUTS'] = str(ROOT)+':'+env.get('BSTINPUTS', '')
    (R/'build').mkdir(exist_ok=True)
    for iteration in range(5):
        refresh_refs()
        for doc in DOCS:
            cmd = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
                   '-output-directory='+str(R/'build'), str(R/(doc+'.tex'))]
            run(cmd, 'TEX_'+doc+'_pass'+str(iteration)+'.log', env)
            if iteration == 0 and '\\bibdata' in (R/'build'/(doc+'.aux')).read_text():
                run(['bibtex', str(R/'build'/doc)], 'BIB_'+doc+'.log', env)
    reports = []
    for doc in DOCS:
        log = (R/'build'/(doc+'.log')).read_text(errors='replace')
        unresolved = [line for line in log.splitlines() if 'undefined' in line.lower() and
                      ('reference' in line.lower() or 'citation' in line.lower())]
        duplicates = 'There were multiply-defined labels' in log
        if unresolved or duplicates:
            raise RuntimeError('Unresolved publication references in '+doc+': '+repr(unresolved[:12]))
        page = re.search(r'Output written on .*?\((\d+) pages?', log, flags=re.S)
        reports.append({'document': doc, 'pages': int(page.group(1)) if page else None,
            'undefined_references': unresolved, 'multiply_defined_labels': duplicates,
            'overfull_hboxes': len(re.findall(r'Overfull \\hbox', log)),
            'overfull_vboxes': len(re.findall(r'Overfull \\vbox', log)),
            'pdf_sha256': sha((R/'build'/(doc+'.pdf')).read_bytes())})
    write('audit/COMPILATION.json', json.dumps(reports, indent=2)+'\n')
    tests = json.loads((R/'audit/TEST_RESULTS.json').read_text())
    replay = json.loads((R/'audit/REPLAY_IDENTITY.json').read_text())
    release = {'publication_source_commit': SOURCE, 'base_commit': BASE,
        'referee_blob': '947147612cc22f5e10ff15faf347fcb3de222656',
        'test_suites': tests, 'tests_passed': sum(t.get('tests', 0) for t in tests),
        'replay': replay, 'compilation': reports,
        'preservation': json.loads((R/'audit/PRESERVATION.json').read_text()),
        'validation_scope': 'Algebraic/unit checks, unchanged-protocol execution and native LaTeX compilation; not an editorial acceptance or a general neural work-advantage claim',
        'visual_inspection': 'Not performed by this automated workflow; page and overflow diagnostics are recorded'}
    write('audit/RELEASE_AUDIT.json', json.dumps(release, indent=2)+'\n')
    save_record()
    manifest = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in R.rglob('*')
                if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.aux', '.bbl', '.blg', '.out', '.toc')
                and p.name not in ('PUBLICATION_FILES_SHA256.json', 'REPLICATION.zip')}
    write('PUBLICATION_FILES_SHA256.json', json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    with zipfile.ZipFile(R/'REPLICATION.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name == 'REPLICATION.zip':
                continue
            if p.suffix in ('.aux', '.bbl', '.blg', '.out', '.toc'):
                continue
            if 'revisions/2026-10-06-r30/results/' in str(p.relative_to(ROOT)):
                continue  # retained once at the separately identified R32 replay path
            z.write(p, p.relative_to(ROOT))
    print(json.dumps(release, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('prepare', 'execute', 'build'))
    args = parser.parse_args()
    {'prepare': prepare, 'execute': execute, 'build': build}[args.mode]()
