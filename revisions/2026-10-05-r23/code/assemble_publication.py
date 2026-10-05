"""Assemble native revision wrappers; never mutate an inherited source file."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]
OLD=ROOT/'revisions/2026-10-05-r21'
BASE='281e57b18a2d88de68d2219da1a7194e90570d13'
PREFIX='revisions/2026-10-05-r23'
DOCS=('ECTA','supp','applications','evidence','response')


def save(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf8')


def links(text,name):
    text=re.sub(r'^\\externaldocument[^\n]*\n','',text,flags=re.M)
    refs=''.join('\\externaldocument{'+PREFIX+'/build/'+n+'_refs}['+n+'.pdf]\n' for n in DOCS if n!=name and n!='response')
    return text.replace('\\begin{document}',refs+'\\begin{document}',1)


def wrapper(preamble,title,body,bib=True,prefix=None):
    if prefix:
        defs='\n'.join('\\renewcommand{\\the'+v+'}{'+prefix+r'.\arabic{'+v+'}}' for v in ('theorem','equation','table','section'))+'\n'
        preamble=preamble.replace('\\endlocaldefs',defs+'\\endlocaldefs')
    front='\\begin{document}\n\\begin{frontmatter}\n\\title{'+title+'}\n\\runtitle{Neural Bellman Operators}\n\\begin{aug}\n\\author[id=au1,addressref={add1}]{\\fnms{Qian}~\\snm{QI}}\n\\address[id=add1]{Peking University}\n\\end{aug}\n\\end{frontmatter}\n'
    tail='\n\\bibliographystyle{ecta-fullname}\n\\bibliography{revision_reference,revisions/2026-10-05-r19-integrated/references,revisions/2026-10-05-r21/references}\n' if bib else '\n'
    return preamble+front+body+tail+'\\end{document}\n'


def dependencies(path,seen=None):
    seen=set() if seen is None else seen
    path=path.resolve()
    if path in seen:return seen
    seen.add(path);text=path.read_text()
    for p in re.findall(r'\\(?:input|include)\{([^}]+)\}',text):
        child=ROOT/p
        if not child.suffix:child=child.with_suffix('.tex')
        if child.exists():dependencies(child,seen)
        elif '#' not in p and '\\' not in p:raise FileNotFoundError(child)
    return seen


def outward_decimal(x,upper=False):
    f=Fraction(float(x))*1000000
    n=-((-f.numerator)//f.denominator) if upper else f.numerator//f.denominator
    sign='-' if n<0 else '';n=abs(n)
    return f'{sign}{n//1000000}.{n%1000000:06d}'


def assemble():
    report=json.loads((R/'results/generated/REPLAY.json').read_text())
    stats=json.loads((R/'results/primary/SUMMARY.json').read_text())
    services=[json.loads(x) for x in (R/'results/primary/services.jsonl').read_text().splitlines()]
    measured=sum(x['complete_service_seconds'] for x in services)
    overhead=stats['runtime_seconds_before_final_summary']-measured
    report['primary_loop_seconds']=stats['runtime_seconds_before_final_summary']
    report['sum_measured_service_seconds']=measured
    report['unallocated_loop_seconds']=overhead
    report['cost_note']='Final service-ledger writes and loop overhead are outside individual service clocks but inside the complete loop clock. Shared interpreter/environment startup is not measured by these clocks; publication replay is separate.'
    save(R/'results/generated/REPLAY.json',json.dumps(report,indent=2)+'\n')
    interpretation='\\paragraph{Interpretation of the cost comparison.}\n'
    for d in (10,50):
        c={x['method']:x for x in report['stream_totals'] if x['dimension']==d}
        w=c['NBO-warm']['mean_three_regime_seconds'];cold=c['NBO-cold']['mean_three_regime_seconds'];dp=c['Riccati']['mean_three_regime_seconds']
        interpretation+=f'At $d={d}$, the realized warm-to-cold NBO stream-cost ratio is ${w/cold:.3f}$ and the warm-NBO-to-Riccati ratio is ${w/dp:.3f}$. '
    interpretation+='These are descriptive ratios for the complete frozen streams, not population superiority tests. The conventional quadratic and Riccati candidates also meet the policy target. The comparison therefore supplies accurate trained neural policies and an explicit refresh comparison, not a theorem of neural cost dominance.\n\n'
    interpretation+=f'The complete execution loop takes {report["primary_loop_seconds"]:.3f} seconds, of which {measured:.3f} seconds are assigned to measured services and {overhead:.3f} seconds remain as service-ledger and loop overhead. The recorded process-wide memory high-water mark is {stats["process_high_water_rss_kib"]} KiB. It is not a per-method peak.\n\n'
    interpretation+=f'The separate trained-factor calculation verifies the rank premise for {report["factor_rank_verified"]} of {report["factor_diagnostics"]} final neural candidates; {report["factor_threshold_passes"]} also meet the original threshold through that alternative bound. Every unresolved auxiliary bound is retained. This post-execution analysis does not alter the original successful stopping decisions.\n'
    save(R/'results/generated/interpretation.tex',interpretation)
    # Print all economic intervals with exact rational outward decimal conversion.
    for short in (False,True):
        rows=[x for x in report['response_bands'] if not short or x['method'] in ('NBO-cold','Riccati')]
        label='tab:r23economicmain' if short else 'tab:r23responses'
        title='Investment responses: neural and structural policies' if short else 'Mean investment responses with reoptimized futures'
        lines=[r'\begin{longtable}{rllrrl}',r'\caption{'+title+r'}\label{'+label+r'}\\',r'\toprule $d$ & Procedure & Future & Lower & Upper & Sign\\\midrule\endfirsthead',r'\toprule $d$ & Procedure & Future & Lower & Upper & Sign\\\midrule\endhead']
        for b in rows:lines.append(f"{b['dimension']} & {b['method']} & {b['regime']} & {outward_decimal(b['lower'])} & {outward_decimal(b['upper'],True)} & {b['sign']}"+r'\\')
        lines.extend([r'\bottomrule\end{longtable}',r'\noindent\footnotesize Each interval is the hull over all registered seeds of paired optimum-response enclosures. Decimal endpoints are converted outward using exact rational arithmetic. These are model enclosures, not population confidence intervals.\normalsize'])
        save(R/'results/generated'/('economic_main.tex' if short else 'responses.tex'),'\n'.join(lines)+'\n')
    oldmain=(OLD/'ECTA.tex').read_text()
    main=oldmain
    for name in ('introduction','conclusion'):
        old='revisions/2026-10-05-r21/manuscript/'+name+'.tex'
        assert old in main;main=main.replace(old,PREFIX+'/manuscript/'+name+'.tex')
    targets=ROOT/'revisions/2026-10-05-r19-integrated/manuscript/targets.tex'
    text=targets.read_text().replace('our new primary target','the earlier scalar-service target').replace('New primary accuracy certificate and realized stopping target.','Earlier scalar-service certificate and stopping target.')
    row='Full dynamic policy loss & All adapted finite-cost policies and real vector actions & New all-state certificate in the declared discrete-time capital economy.\\\\\n'
    assert 'Diffusion control regret &' in text
    text=text.replace('Diffusion control regret &',row+'Diffusion control regret &',1)
    text+='\nThe new full-policy experiment in Section~\\ref{sec:r23experiment} uses a different target from the earlier scalar-service study: a uniform initial-domain lifetime loss against all adapted policies. Its additive cost convention is the negative of the reward convention above. The two experiments retain separate models, chronologies and error accounts.\n'
    save(R/'manuscript/targets.tex',text)
    main=main.replace(str(targets.relative_to(ROOT)),PREFIX+'/manuscript/targets.tex')
    cp=(OLD/'manuscript/composition_main.tex').read_text()
    cp+='\nSection~\\ref{sec:r23policy} supplies an all-state coercive alternative and executes its full-policy instantiation in a discrete-time capital economy. The finite catalogue evidence retained below is not used as a substitute for these global premises.\n'
    save(R/'manuscript/composition_main.tex',cp)
    main=main.replace('revisions/2026-10-05-r21/manuscript/composition_main.tex',PREFIX+'/manuscript/composition_main.tex')
    anchor='\\input{'+PREFIX+'/manuscript/composition_main.tex}'
    main=main.replace(anchor,anchor+'\n\\input{'+PREFIX+'/manuscript/full_policy.tex}')
    prior=['revisions/2026-10-05-r18/manuscript/current_results.tex','revisions/2026-10-05-r19-integrated/manuscript/prospective_main.tex','revisions/2026-10-05-r21/manuscript/future_main.tex']
    for p in prior:
        s='\\input{'+p+'}\n';assert s in main;main=main.replace(s,'')
    h='\\input{revisions/2026-10-04-r16/manuscript/historical_evidence_summary.tex}'
    assert h in main
    main=main.replace(h,'\\input{'+PREFIX+'/manuscript/full_policy_experiment.tex}\n\\input{'+PREFIX+'/manuscript/prior_summary.tex}')
    summary='\\paragraph{The earlier nonlinear comparisons.}\nThe Prior Numerical Evidence companion reproduces the previously main-text nonlinear comparisons in full. They establish their original finite-law and continuous-economy results, not the all-state certificate of the new quadratic economy. In particular, adaptive NBO costs more than fresh NBO in every changing-future cell, and cached SAA is least-cost among the fully certified methods in all eight cells. The new experiment does not erase those results or turn their current scalar targets into full-policy claims.\n\n'+h+'\n'
    save(R/'manuscript/prior_summary.tex',summary)
    abstract=r'''\begin{abstract}
This paper develops Neural Bellman Operators for policy evaluation and feasible
improvement in controlled economies. Centered continuation errors and economic
transport bounds determine when a learned future can be reused or refreshed.
A coercive Bellman-residual theorem gives an all-state policy-loss certificate,
and a trainable-factor result links a neural gradient and rank bound to that
certificate. A source-frozen capital experiment has continuous Gaussian shocks,
24 reoptimized dates, and ten or fifty vector controls. All 480 neural,
conventional-quadratic and structural services meet the full-policy tolerance;
all 608 failed intermediate checks are retained. Cold and warm starts are
compared with complete measured service costs, and method-level probabilities
refer to an explicitly enumerated initialization randomizer. Investment-response
bands concern reoptimized futures. The structural comparator remains fully
competitive: candidate accuracy is not identified with neural superiority.
The original nonlinear capital studies, recursive utility, endogenous
preferences, temporal selves and games retain their complete accounts.
Full-policy guarantees in the declared discrete-time instance are distinguished
from the separate diffusion-transfer and strategic conditions.
\end{abstract}'''
    main=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:abstract,main,flags=re.S)
    save(R/'ECTA.tex',links(main,'ECTA'))
    supp=(OLD/'supp.tex').read_text()
    supp=supp.replace('\\bibliographystyle','\\clearpage\n\\input{'+PREFIX+'/manuscript/full_policy_proofs.tex}\n\\input{'+PREFIX+'/results/generated/record.tex}\n\\bibliographystyle',1)
    save(R/'supp.tex',links(supp,'supp'))
    save(R/'applications.tex',links((OLD/'applications.tex').read_text(),'applications'))
    pre=oldmain.split('\\begin{document}')[0]
    body='These earlier nonlinear capital sections are reproduced from the reviewed manuscript without substantive deletion. Their original finite-law, specified-future, catalogue and diffusion targets remain distinct from the new full-policy experiment.\n\n'+''.join('\\input{'+p+'}\n' for p in prior)
    save(R/'evidence.tex',links(wrapper(pre,'Prior Numerical Evidence for Neural Bellman Operators',body,prefix='E'),'evidence'))
    save(R/'response.tex',links(wrapper(pre,'Response to the Referee','\\input{'+PREFIX+'/manuscript/response_body.tex}\n',bib=False),'response'))
    olddeps=set();newdeps=set()
    for n in ('ECTA','supp','applications'):olddeps|=dependencies(OLD/(n+'.tex'))
    for n in DOCS:newdeps|=dependencies(R/(n+'.tex'))
    getlabels=lambda ds:set().union(*(set(re.findall(r'\\label\{([^}]+)\}',p.read_text())) for p in ds))
    oldlabels=getlabels(olddeps);newlabels=getlabels(newdeps)
    missing=sorted(oldlabels-newlabels);assert not missing,missing
    changed=subprocess.check_output(['git','diff','--name-only','--diff-filter=MDT',BASE,'--'],cwd=ROOT,text=True).splitlines()
    assert not changed,('Inherited file changed',changed)
    baseline=subprocess.check_output(['git','ls-tree','-r',BASE],cwd=ROOT,text=True).splitlines()
    preserved=[]
    for p in sorted(olddeps):
        rel=str(p.relative_to(ROOT));original=subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT)
        assert original==p.read_bytes(),rel
        locations=[n for n in DOCS if p in dependencies(R/(n+'.tex'))]
        preserved.append({'path':rel,'sha256':hashlib.sha256(original).hexdigest(),'unchanged_in_repository':True,'current_documents':locations,'historical_only':not bool(locations)})
    audit={'baseline_commit':BASE,'unchanged_baseline_git_entries':len(baseline),'modified_or_deleted_inherited_files':changed,
           'inherited_source_components':len(olddeps),'inherited_labels':len(oldlabels),'current_labels':len(newlabels),'missing_inherited_labels':missing,'components':preserved}
    save(R/'PRESERVATION.json',json.dumps(audit,indent=2)+'\n')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    save(R/'SOURCE_COMMIT.txt',source+'\n')
    save(ROOT/'CURRENT_REVISION.md','# Neural Bellman Operators: full-policy revision\n\nRead `revisions/2026-10-05-r23/README.md`. The native article is `revisions/2026-10-05-r23/ECTA.tex`; the compiled article is `revisions/2026-10-05-r23/build/ECTA.pdf`. All inherited files and prior adverse results are retained.\n')
    readme='''# Neural Bellman Operators — R23 full-policy revision

## Reading order

The native article is `ECTA.tex` and its compiled PDF is `build/ECTA.pdf`.
`build/response.pdf` answers every B1–B9 and M1–M10 comment in the R21 report.
`build/supp.pdf` retains the technical supplement and adds the new proofs.
`build/evidence.pdf` reproduces the relocated nonlinear main-text evidence.
`build/applications.pdf` retains the complete economic applications.

The topic, original author, economic models and adverse evidence are retained.
`PRESERVATION.json` verifies inherited Git objects, source components and labels.
No R22 branch or main branch is overwritten.

## New mathematical and executed content

A coercive own-policy Bellman-residual theorem yields an all-state certificate
against all adapted finite-cost policies. Its continuous-Gaussian capital
instance has 24 dates and 10 or 50 full vector controls. A trainable-factor
proposition connects the returned-policy gradient and a verified rank bound
to policy accuracy. The implementation allowance is explicit and conditional
on its declared relative action-error contract.

All 480 frozen services meet the 1e-4 full-policy tolerance. All 1,088 attempted
candidates, including 608 unsuccessful checks, are retained. Warm and cold
neural and matched quadratic procedures receive the same population evaluation
information. Riccati is a separately timed strong comparator, not a verifier
input. Successful certificates are not presented as neural cost dominance.
The finite randomizer is exactly the sixteen registered seeds; clocks are
realized measurements, not population expected runtimes.

## Reproduction from this repository

Use Python 3.11, NumPy 2.3.5, and a native TeX installation with `econsocart`
and its dependencies. Set OMP_NUM_THREADS, OPENBLAS_NUM_THREADS and
MKL_NUM_THREADS to 1. Run from the repository root:

```sh
python -m unittest discover -s revisions/2026-10-05-r23/code -p 'test_*.py' -v
python revisions/2026-10-05-r23/code/replay_and_tables.py
python revisions/2026-10-05-r23/code/assemble_publication.py
python revisions/2026-10-05-r23/code/build_publication.py
```

The replay verifies original hashes and decisions without rerunning fits or
replacing clocks. Factor diagnostics and response bands are post-execution
analyses, not new primary fits. The source freeze is
`8b2d4175227801950e6ceaaed1f229d5378191f0`; execution source is
`0702221528a32b5b4a28f197eb9bb65f539baeeb`; original evidence is
`d6b170643b9c024a7d689bb1d68e9444214d44a0`. The reviewed manuscript is
`278916666b32e03081ffe8d4aa05d9766c259b85`, and its review is pinned at
`281e57b18a2d88de68d2219da1a7194e90570d13`.

The complete policy result is for the specified discrete-time economy. It is
not a zero-error diffusion transfer, an empirically calibrated counterfactual,
or a numerical certificate for every recursive-utility or game application.
The strongest method-level numerical objections are addressed explicitly in
the response, not hidden by changing the paper's subject.
'''
    save(R/'README.md',readme)
    print(json.dumps({k:v for k,v in audit.items() if k!='components'},indent=2))

if __name__=='__main__':assemble()
