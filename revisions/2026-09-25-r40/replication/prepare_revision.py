"""Materialize the complete R40 manuscript without altering inherited source.
Inputs are the frozen R38/R39 scientific objects; all output is R40-scoped
except the explicitly versioned root entry points and current review index.
"""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,shutil,sys,importlib.util,re,subprocess,platform
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
R39=ROOT.parent/'2026-09-25-r39';R38=ROOT.parent/'2026-09-24-r38'
BASE='bf5d42b08debd4c26341ab1b1231a6a6242df4f9'
BRANCH='revision/econometrica-r40-referee-complete-2026-09-25'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def save(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def diagnostic():
    v=module('r40_independent_parser',R38/'replication/verify_primary.py')
    original=read(R38/'results/primary.json')['outcomes'];rows=[];loci=[]
    for row in sorted(original,key=lambda z:(z['T'],z['proposal'],F(z['epsilon']))):
        source=R38/'results'/row['proof_file'];assert hashlib.sha256(gzip.decompress(source.read_bytes())).hexdigest()==row['proof_sha256']
        d=read(source);u,lo=F(row['upper_integral']),F(row['lower_integral']);assert u>=lo>=0
        necessary=next(a for a in row['attempts'] if a['candidate']=='necessary_selector');reg=F(necessary['regret'])
        rows.append(dict(T=row['T'],proposal=row['proposal'],epsilon=row['epsilon'],gap=str(u-lo),gap_over_upper=str((u-lo)/u) if u else None,
          necessary_selector_regret=str(reg),necessary_selector_excess=str(max(F(0),reg-F(row['epsilon']))),proof_file=row['proof_file'],proof_sha256=sha(source)))
        if row['exact_integrated'] and not row['exact_pointwise']:
            diff=[]
            for t,(c,b) in enumerate(zip(map(v.parse,d['C']),map(v.parse,d['lower']))):
                xs=sorted(set(c[0])|set(b[0]));intervals=[];points=[]
                for l,r in zip(xs,xs[1:]):
                    h=v.subtract(v.line(c,(l+r)/2),v.line(b,(l+r)/2));assert min(v.at(h,l),v.at(h,r))>=0
                    if h!=(v.Z,v.Z):intervals.append(dict(left=str(l),right=str(r),slope=str(h[0]),intercept=str(h[1])))
                for x in xs:
                    y=v.value(c,x)-v.value(b,x);assert y>=0
                    if y:points.append(dict(x=str(x),difference=str(y)))
                if intervals or points:diff.append(dict(date=t,open_intervals=intervals,isolated_points=points))
            assert diff and all(z['date']>0 for z in diff)
            loci.append(dict(T=row['T'],proposal=row['proposal'],epsilon=row['epsilon'],initial_functionwise_equal=True,full_restart_disagreement=diff))
    result=dict(deterministic_outcomes=rows,integrated_not_functionwise=loci,local_lp_inherited=read(R38/'results/local_lp.json'),scope='R40 reconstruction from retained exact objects; no old result or candidate is removed.')
    save(ROOT/'results/diagnostics.json',result);return result

def weighted(v,f,scope):
    z=F(0)
    for (a,b),l,r in zip(f[1],f[0],f[0][1:]):
        a,b,l,r=map(lambda x:F(str(x)),(a,b,l,r));normal=a*(r*r-l*l)/2+b*(r-l);high=2*a*(r**3-l**3)/3+b*(r*r-l*l)
        z+=normal if scope=='uniform' else high if scope=='high_condition' else 2*normal-high
    return z

def audit_summaries():
    v=module('r40_parser_audit',R38/'replication/verify_primary.py')
    old=read(R38/'results/primary.json')['outcomes'];index={(x['T'],x['proposal'],x['epsilon']):x for x in old}
    primary=read(R39/'results/primary_combined.json')['outcomes'];lotteries=read(R39/'results/randomized_primary.json')['outcomes'];lm={(x['T'],x['proposal'],x['epsilon']):x for x in lotteries}
    reports=read(R39/'results/verify_continuum.json')['outcomes'];vm={x['file']:x for x in reports}
    margins=[];provenance=[]
    for row in primary:
        key=(row['T'],row['proposal'],row['epsilon']);legacy=index[key];base=read(R38/'results'/legacy['proof_file']);lr=lm[key]
        pp=R39/'results'/lr['proof_file'];rp=R39/'results'/row['proof_file'];assert sha(pp)==lr['proof_sha256'] and sha(rp)==row['proof_sha256']
        vr=vm['results/'+lr['proof_file']];assert vr['passed'] and vr['sha256']==sha(pp) and vr['restart_sha256']==sha(rp)
        pd,rd=read(pp),read(rp);assert pd['V']==base['V'] and pd['raw']==base['raw']
        for scope,z in row['initial_bounds'].items():
            oldz=lr['initial_bounds'][scope];lower=max(F(oldz['lower']),F(rd['initial_lower'][scope]));upper=min(F(z['lottery_cost_upper']),F(z['inherited_deterministic_upper']))
            assert lower==F(z['lower']) and upper==F(z['upper']) and lower<=upper
            detlower=weighted(v,v.parse(base['lower'][0]),scope);detupper=weighted(v,v.parse(base['C'][0]),scope)
            assert detlower==F(z['deterministic_lower']) and detupper==F(z['inherited_deterministic_upper'])
            assert z['strict_randomized_improvement']==(F(z['lottery_cost_upper'])<detlower)
            assert F(z['gap'])==upper-lower and F(z['relative_gap'])==((upper-lower)/upper if upper else 0)
            hsum=sum(F(19,20)**s for s in range(row['T']));margin=max(F(0),detlower-F(z['lottery_cost_upper']))
            margins.append(dict(T=row['T'],proposal=row['proposal'],epsilon=row['epsilon'],initial_law=scope,deterministic_lower=str(detlower),lottery_upper=z['lottery_cost_upper'],separation_margin=str(margin),discounted_periods=str(hsum),per_date_overhead_threshold=str(margin/hsum),strict_ranking_requires='overhead strictly below the positive threshold'))
            provenance.append(dict(T=row['T'],proposal=row['proposal'],epsilon=row['epsilon'],initial_law=scope,
                active_lower_source='new_connected_local' if F(rd['initial_lower'][scope])>=F(oldz['lower']) else 'retained_randomized_bound_component',
                newly_checked_local_lower=rd['initial_lower'][scope],retained_randomized_lower=oldz['lower'],published_lower=z['lower'],
                lottery_sha256=sha(pp),restart_sha256=sha(rp),deterministic_proof_sha256=legacy['proof_sha256']))
    finite=read(R39/'results/finite.json')['outcomes'];checks={r['file']:r for r in read(R39/'results/verify_finite.json')['outcomes']}
    for row in finite:
        p=R39/'results'/row['proof_file'];d=read(p);ch=checks['results/'+row['proof_file']]
        assert ch['passed'] and ch['sha256']==sha(p)
        for key in ('lower','upper','gap','closed','evaluations'):assert row[key]==d[key],(row['proof_file'],key)
    nonlinear=read(R39/'results/nonlinear_support.json')['outcomes'];tight=read(R39/'results/nonlinear_tight_tolerance.json')['outcomes']
    for row in nonlinear+tight:assert sha(R39/'results'/row['proof_file'])==row['proof_sha256']
    protocol=read(R39/'protocol/holdout.json')
    for name,digest in protocol['algorithm_sha256'].items():assert sha(R39/'replication'/name)==digest
    assert len(primary)==42 and len(finite)==16 and len(margins)==126 and len(nonlinear)==20 and len(tight)==4
    save(ROOT/'results/economic_margins.json',dict(outcomes=margins,scope='Derived from exact frozen primary endpoints; no empirical calibration and no claim of a new holdout.'))
    result=dict(passed=True,frozen_source_commit=BASE,primary_rows=42,finite_rows=16,nonlinear_rows=20,tight_tolerance_lower_only_rows=4,
       strict_uniform=sum(z['initial_law']=='uniform' and F(z['separation_margin'])>0 for z in margins),endpoint_provenance=provenance,
       historical_verifier_reports={n:sha(R39/'results'/n) for n in ('verify_finite.json','verify_continuum.json','verify_nonlinear.json')},
       limitations=['Hash linkage confirms object identity, not an independent rederivation of every historical bound.',
        'R34 randomized and R38 deterministic components retain their documented proof provenance.',
        'R40 fresh replay coverage is in replay_*.json and must not be assigned to unlisted objects.'])
    save(ROOT/'results/publication_audit.json',result);return result

def prepare():
    if not __debug__ or sys.flags.optimize:raise RuntimeError('assertions required')
    ROOT.joinpath('paper/generated').mkdir(parents=True,exist_ok=True)
    for p in (R39/'paper').glob('*.tex'):
        text=p.read_text().replace('revisions/2026-09-25-r39/paper','revisions/2026-09-25-r40/paper')
        if p.name=='preamble.tex':text=text.replace('Revision R39','Revision R40')
        (ROOT/'paper'/p.name).write_text(text)
    for name in ('primary_combined.json','finite.json','nonlinear_support.json','nonlinear_tight_tolerance.json'):
        shutil.copyfile(R39/'results'/name,ROOT/'results'/name)
    diag=diagnostic();audit=audit_summaries()
    tables=module('r40_tables',R39/'replication/make_tables.py');tables.ROOT=ROOT;tables.OUT=ROOT/'paper/generated';tables.run()
    # A new, additive section does not replace any existing theorem or proof.
    p=ROOT/'paper/main_part2.tex';s=p.read_text();needle='\\subsection{A complete finite-state construction}'
    s=s.replace(needle,'\\input{revisions/2026-09-25-r40/paper/witness_theorem}\n\n'+needle);p.write_text(s)
    p=ROOT/'paper/main_part1.tex';s=p.read_text().replace('It yields convergent global policy search','A witness-driven form avoids an exact operating solve. It yields convergent global policy search')
    needle='A second result transfers finite-state certificates'
    s=s.replace(needle,'The witness-driven extension separates operating approximation error from policy-search error in one computable global bound. It supplies a positive-margin check and a constructive policy without passing the exact optimum to the repair routine. A further perturbation result converts model error into operating and cost allowances; strict randomized separations also yield break-even administration charges. These statements extend the numerical method rather than changing its economic objective.\n\n'+needle)
    p.write_text(s)
    p=ROOT/'paper/main_part3.tex';s=p.read_text()
    old=r'''\begin{equation}\label{eq:localLP}
 B_t(x)=\max\left\{F_t(x),\min_{p\in\Delta(A):\ \sum_ap_aT_t^aU_{t+1}(x)\geq L_t(x)-\varepsilon}
 \sum_ap_a\{k_t(x,a)+\beta P_t^aB_{t+1}(x)\}\right\},\quad B_T=0.
\end{equation}'''
    new=r'''\[
 \mathcal D_t(x)=\left\{p\in\Delta(A):\sum_ap_aT_t^aU_{t+1}(x)\geq L_t(x)-\varepsilon\right\}.
\]
\begin{equation}\label{eq:localLP}
 B_t(x)=\max\left\{F_t(x),\min_{p\in\mathcal D_t(x)}
 \sum_ap_a\{k_t(x,a)+\beta P_t^aB_{t+1}(x)\}\right\},\quad B_T=0.
\end{equation}'''
    assert old in s;s=s.replace(old,new);p.write_text(s)
    p=ROOT/'paper/main_part4.tex';s=p.read_text();s=s.replace('\\section{Conclusion}', '\\input{revisions/2026-09-25-r40/paper/economic_margin}\n\n\\section{Conclusion}')
    s=s.replace('Full independent scalar arithmetic covers the entire $(T,N)=(8,64)$ and $(32,64)$ objects, including candidate upper evaluation. Other rows use directed construction arithmetic and read-only structural checks; their independent label is not inherited from adjacent rows.', 'Inherited full independent scalar checks cover $(T,N)=(8,64)$ and $(32,64)$. R40 additionally replays the complete $(32,128)$ object, including the candidate upper cost and all-restart operating bound. The $(32,256)$ result retains directed construction and structural checks, not the independent label of adjacent rows.')
    s=s.replace('At the independently checked $T=32,N=64$ resolution, both endpoints and the all-restart operating inequality are rebuilt with a separate arithmetic implementation.', 'Both endpoints and the all-restart operating inequality are independently rebuilt at $T=32,N=64$, and the R40 audit extends this to the complete $T=32,N=128$ object.')
    p.write_text(s)
    # Correct the inherited label specifically, without rewriting historical runs.
    f=ROOT/'paper/generated/nonlinear_selected.tex';lines=f.read_text().splitlines();lines=[line.replace('not independent','full R40') if line.startswith('32 & 128 &') else line for line in lines];f.write_text('\n'.join(lines)+'\n')
    margins=read(ROOT/'results/economic_margins.json')['outcomes'];rows=[]
    for r in margins:
        if r['initial_law']=='uniform' and (r['proposal']=='defer' or (r['proposal']=='neural31001' and r['epsilon']=='1/100')):
            rows.append(tables.line([r['T'],tables.text(r['proposal']),tables.fmt(r['epsilon'],2),tables.fmt(r['deterministic_lower'],5,'lower'),tables.fmt(r['lottery_upper'],5,'upper'),tables.fmt(r['per_date_overhead_threshold'],6,'lower')]))
    (ROOT/'paper/generated/overhead_selected.tex').write_text(''.join(rows))
    props=read(ROOT/'results/property_tests.json')
    p=ROOT/'paper/supplement.tex';s=p.read_text().replace('p{.35\\textwidth}', 'p{.33\\textwidth}').replace('Selector deficit & Excess over $\\varepsilon$', 'Deficit & Excess').replace('independent scalar checks for two complete objects','independent scalar checks for two inherited objects and a new complete $(32,128)$ replay')
    s=s.replace('Finite complete search &', 'Witness-driven repair & Checked $L\\leq V\\leq U$, $U_T=g$, and positive residual margin $(1-\\beta)\\varepsilon-d$ & Analytic bracket plus 48 exact multi-action test cases. A failed margin check is not economic infeasibility. \\\\Model perturbation & Uniform error bounds over all common policies and every alternative model; $\\varepsilon>2a$ & One tightened policy is portable across models. Error radii are assumptions, not estimated confidence sets here. \\\\Administration charge & Same operating model and initial law, feasible lottery upper, valid deterministic lower, bounded nonnegative overhead & All 126 exact known-model margins retained. Strict superiority requires overhead strictly below its threshold. \\\\Finite complete search &')
    add='''\\section{Additional witness, robustness, and arithmetic audits}
The main article proves a witness-driven feasibility repair and a lattice error budget that requires checked operating witnesses rather than an exact operating optimum. Its repair slack is $(1-\\beta)\\varepsilon-d>0$, where $d$ bounds the upper witness's Bellman residual. Approximation of the operating value and approximation of the policy remain separately visible. The new fixed-space perturbation proposition preserves one policy across every model in its uncertainty set. Break-even administration charges are derived for all 126 primary initial-law configurations, including zero margins.

The new rational repair constructor does not compute or accept the exact optimum. In 48 designed test models, a separate exact operating oracle constructs TEST witnesses; it is not input to the constructor. Signed stage and terminal rewards, two or three actions, two or three states, and horizons 2 through 5 are covered. SymPy matrix evaluation checks every operating and cost value against the Fraction constructor. All 48 deliberately nonpositive witness-slack cases are rejected as uncertified, not declared infeasible. These tests supplement the analytic theorem.

The seeded piecewise-affine audit checks 200 discontinuous pairs, including separately represented knot values, with '''+str(props['piecewise_affine']['comparisons'])+''' independent value comparisons and 400 malformed-partition rejections. An additional 120 local programs are checked by an independently assembled SymPy active-basis calculation; '''+str(props['local_lp']['coincident_operating_values'])+''' contain coincident operating values and '''+str(props['local_lp']['active_pure_boundaries'])+''' have a pure action exactly on the operating boundary. These are measured degeneracy counts for the new audit, not retrospectively invented counts for the historical adaptive solver.

R40 replays all 16 finite proof trees, three declared full primary lottery/local objects, and the complete nonlinear $(T,N)=(32,128)$ object using the frozen independent verifiers. The latter extends prior scalar verification to a finer mesh. The full inherited 42-primary-object verifier coverage is retained by exact hash linkage; the three new primary replays are not represented as 42 fresh executions. None of these tests is a statistical false-acceptance guarantee.

'''
    s=s.replace('\\subsection{Preserved scientific content}',add+'\\subsection{Preserved scientific content}')
    s=s.replace('Other nonlinear meshes have directed construction and structural checks, not the same independent status.', 'Other nonlinear meshes, except the new R40 $(32,128)$ replay, have directed construction and structural checks, not the same independent status.')
    p.write_text(s)
    p=ROOT/'paper/response.tex';s=p.read_text().replace('R39 Response','R40 Response').replace('to the R39 revision','to the R40 revision')
    add='''\\section{R40 completion and additional substantive revisions}
This version preserves the complete R38 review object and the intervening R39 scientific execution at commit \\path{bf5d42b08debd4c26341ab1b1231a6a6242df4f9}. R39 contained new source and checked computations but lacked its final diagnostics and compiled publication. R40 supplies those missing objects, audits their correspondence, and adds the results below. The inherited timed experiments are not presented as newly collected holdout evidence.

\\paragraph{Operating approximation: F1, F5, and F7.} The witness-driven repair theorem in the main article gives a globally feasible common policy using $U$ instead of an exact $V$. Its displayed lattice bracket accounts jointly for witness width, Bellman residual, and policy resolution. The sufficient positive-slack test is computable; a failed test is not a conclusion of economic infeasibility. This addition addresses the operating-oracle objection directly, while preserving every earlier convergence theorem and proof.

\\paragraph{Economic content: F9 and additional comments 5, 18, 19, and 25.} A new model-perturbation proposition translates verified parameter uncertainty into operating-tolerance and implementation-cost adjustments for every alternative model, including one policy feasible throughout the uncertainty set. A further cost comparison derives the administration overhead that a certified lottery can absorb while remaining cheaper than every deterministic feasible policy. All 126 initial-law margins, including zeros, are calculated from exact retained endpoints. They are normalized-model economic margins, not empirical estimates or assumed confidence regions.

\\paragraph{Independent verification: F4 and F11.} R40 independently replays the entire nonlinear $T=32,N=128$ object rather than transferring an independent label from the coarser $N=64$ objects. It also replays all 16 finite proof trees and three explicitly selected continuous-state objects. The complete inherited 42-object primary verification remains hash-linked and separately labeled. The new witness, discontinuity, and local-degeneracy tests are recorded with their actual counts and rejection outcomes.

\\paragraph{Complete publication.} Four compiled documents, complete source, generated diagnostics, figures, response mapping, and preservation manifest are supplied on a new branch. The nonlinear $N=256$ row remains a directed-construction result, not a newly independent scalar replay. Material long-horizon gaps, the tight nonlinear lower-only rows, and the unsolved stopped-control numerical allowance remain visible. No numerical claim is upgraded merely because the publication now compiles.

'''
    s=s.replace('\\section{Overview of the revision}',add+'\\section{Overview of the revision}');s=s.replace('The finer meshes are not assigned the same independent label.', 'The complete $(32,128)$ object additionally receives a fresh R40 independent replay; the finest $N=256$ row is not assigned that label.');p.write_text(s)
    # Supplied separately: an accurate replacement computation report for R40.
    shutil.copyfile(ROOT/'paper/computation_r40.tex',ROOT/'paper/computation.tex')
    for prefix,name in [('ECTA','main'),('SUPP','supplement'),('RESPONSE','response'),('COMPUTATION','computation')]:
        (REPO/f'{prefix}_R40.tex').write_text('\\input{revisions/2026-09-25-r40/paper/'+name+'}\n')
    # Historical review navigation is retained exactly before replacing the pointer.
    h=ROOT/'history/REVISION_INDEX_before_R40.md';h.parent.mkdir(parents=True,exist_ok=True)
    if not h.exists() and (REPO/'REVISION_INDEX.md').exists():shutil.copyfile(REPO/'REVISION_INDEX.md',h)
    review='''# R40 review object\n\nThe current object is `ECTA_R40.pdf`, with `SUPP_R40.pdf`, `RESPONSE_R40.pdf`, and `COMPUTATION_R40.pdf`.\n\nAddressed report: `reviews/2026-09-25-econometrica-r38/referee_report.md`, review commit `acbede22e517a245fcc5244de7171c1ae218ea73`.\n\nFrozen scientific base: R39 `bf5d42b08debd4c26341ab1b1231a6a6242df4f9`. R40 adds witness-driven global repair, portable model-error intervals, break-even randomization overhead, exact property tests, finer nonlinear independent replay, complete diagnostics, and compiled publication. Inherited experiments are explicitly not a new holdout.\n\nAll prior tracked files are retained unchanged except this current index; the previous index is preserved in `revisions/2026-09-25-r40/history/REVISION_INDEX_before_R40.md`. The full R38 main and technical supplement are also appended verbatim to the new supplement. `HISTORY_R38.pdf` remains unchanged.\n\nSee `revisions/2026-09-25-r40/results/publication_audit.json`, `replay_*.json`, and `PUBLICATION_MANIFEST.json` for object identity, fresh replay coverage, and preservation checks. These distinguish independent arithmetic from hash identity and structural validation.\n\nRemaining numerical widths are retained: 30 positive-cost primary randomized intervals are not exact; the fine nonlinear bound is not near-exact; tight-tolerance nonlinear rows are lower-only; the separate stopped-control target is not certified at 0.01.\n'''
    (REPO/'R40_REVIEW.md').write_text(review);(REPO/'REVISION_INDEX.md').write_text(review)
    # Source/response preservation and 14+25 mapping, not a blanket accept verdict.
    response=(ROOT/'paper/response.tex').read_text();assert len(re.findall(r'\\subsection\{R38-F\d+:',response))==14
    assert len(re.findall(r'\\subsection\{\d+\.',response))==25
    save(ROOT/'results/review_coverage.json',dict(major_comments=[f'R38-F{i}' for i in range(1,15)],additional_comments=list(range(1,26)),response='RESPONSE_R40.pdf',status='Every comment receives a direct response; remaining numerical and application limitations are retained, not claimed resolved by citation or compilation.'))
    print('Prepared complete R40 source; strict uniform margins:',audit['strict_uniform'])


def manifest():
    for mode in ('finite','continuum','nonlinear'):
        d=read(ROOT/'results'/f'replay_{mode}.json');assert d['passed']
        assert d['verifier_sha256']==sha(R39/'replication'/f'verify_{mode}.py')
        for row in d['outcomes']:
            if mode=='nonlinear':assert sha(R39/'results'/row['proof_file'])==row['proof_sha256']
            else:
                obj=R39/row['file'];assert sha(obj)==row['sha256']
                if mode=='continuum':assert sha(R39/'results/restart'/obj.name.replace('random_','restart_'))==row['restart_sha256']
    assert len(read(ROOT/'results/replay_finite.json')['outcomes'])==16
    n=read(ROOT/'results/replay_nonlinear.json')['outcomes'][0];assert (n['T'],n['mesh'])==(32,128)
    assert read(ROOT/'results/publication_audit.json')['passed']
    for name in ('ECTA','SUPP','RESPONSE','COMPUTATION'):
        p=REPO/f'{name}_R40.pdf';assert p.exists() and p.stat().st_size>1000
        log=REPO/f'{name}_R40.log'
        if log.exists():
            s=log.read_text(errors='replace')
            assert 'Undefined control sequence' not in s and 'undefined references' not in s
    # Git identifies every inherited tracked path, not just convenient manuscripts.
    preservation=[]
    if (REPO/'.git').exists():
        raw=subprocess.check_output(['git','ls-tree','-r','-z',BASE],cwd=REPO)
        for entry in raw.split(b'\0'):
            if not entry:continue
            meta,path=entry.split(b'\t',1);mode,typ,blob=meta.decode().split();path=path.decode()
            if typ!='blob':continue
            target=ROOT/'history/REVISION_INDEX_before_R40.md' if path=='REVISION_INDEX.md' else REPO/path
            assert target.exists(),('lost inherited file',path)
            identity=subprocess.check_output(['git','hash-object',str(target)],cwd=REPO,text=True).strip()
            assert identity==blob,('changed inherited file',path)
            preservation.append(dict(path=path,blob_sha=blob,retained_at=str(target.relative_to(REPO))))
    docs={f'{name}_R40.pdf':sha(REPO/f'{name}_R40.pdf') for name in ('ECTA','SUPP','RESPONSE','COMPUTATION')}
    records={str(p.relative_to(REPO)):sha(p) for folder in ('paper','replication','results') for p in (ROOT/folder).rglob('*') if p.is_file()}
    save(ROOT/'PUBLICATION_MANIFEST.json',dict(schema='NBO-R40-publication-v1',branch=BRANCH,frozen_base_commit=BASE,review_commit='acbede22e517a245fcc5244de7171c1ae218ea73',documents=docs,records=records,
       inherited_files_checked=len(preservation),preservation_scope='All frozen-base git blobs, with only the current index archived and redirected.',historical_documents={name:sha(REPO/name) for name in ('ECTA_R38.pdf','SUPP_R38.pdf','HISTORY_R38.pdf')},python=sys.version,platform=platform.platform()))
    save(ROOT/'results/preservation.json',dict(passed=True,inherited_files_checked=len(preservation),files=preservation))
    print('Publication gate passed:',len(preservation),'inherited files retained')

if __name__=='__main__':
    if '--manifest' in sys.argv:manifest()
    else:prepare()
