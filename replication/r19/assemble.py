"""Deterministic R19 publication assembly from checked scientific records.

No historical scientific input is overwritten. Main arguments and all proofs
are compiled together with the retained models, adverse cases, and compendium.
"""
from __future__ import annotations
import hashlib,json,os,re,subprocess
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REL='revisions/2026-09-20-r19';R=ROOT/REL;P=R/'paper';O=ROOT/'replication/r19/output'
OLD=ROOT/'revisions/2026-09-19-r14-referee-response/paper'
R15=ROOT/'revisions/2026-09-19-r15-referee-response/paper'
BASE='d15591aff0bed68334cbb205294edfb04297427c'
REVIEW='a17c867624e34f1264ff5cba60e51a850026803f'

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def js(name):return json.loads((O/name).read_text())
def inp(name):return '\\input{'+REL+'/paper/'+name+'}\n'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dec(q,n=6,up=False):
    q=Q(q);s=10**n;i=-((-q.numerator*s)//q.denominator) if up else (q.numerator*s)//q.denominator
    sign='-' if i<0 else '';i=abs(i)
    return sign+str(i//s)+'.'+str(i%s).zfill(n)
def interval(pair,n=6):return '$['+dec(pair[0],n)+','+dec(pair[1],n,True)+']$'
def table(name,caption,label,cols,header,rows,note):
    text='\\begin{table}[tbp]\n\\centering\\small\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'
    text+='\n'.join(' & '.join(row)+' \\\\' for row in rows)
    text+='\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip\n\\begin{minipage}{0.96\\linewidth}\\footnotesize\n'+note+'\n\\end{minipage}\n\\end{table}\n'
    write(P/name,text)

def make_tables():
    f=js('final_checks.json');e=js('enforcement.json');rows=[]
    by={x['id']:x for x in f['rational_bounds']}
    for row in e['rows']:
      b=by[row['id']];rows.append(['Adjustment' if row['adjustment'] else 'No adjustment','Positive' if row['sign']=='positive' else 'Nonpositive',interval(b['initial_fee']),interval(b['no_surrender_value'])])
    note='All intervals are outward decimal enclosures of checked rational bounds. Initial fees use profitable feasible lower witnesses and a zero-surrender optimal-action supergraph for the upper endpoint. Uniform thresholds are '+interval(by['1.positive']['uniform_fee'])+' with adjustment and '+interval(by['0.positive']['uniform_fee'])+' without adjustment; they are not substituted for initial capacity costs. The common law is 0.125, the operating benefit is 0.42425, and the compulsory term is one interval.'
    table('table_enforcement.tex','Initial implementation in the unchanged settlement economy','tab:r19-enforcement','llcc','Regime & Mandate & Initial fee & No-surrender value',rows,note)
    a=js('continuous_benchmark.json');ca=list(map(Q,a['threshold_adjustment']));fa=Q(a['fee_adjustment']);f0=Q(a['fee_no_adjustment']);eta=Q(a['eta']);c0=Q(a['threshold_no_adjustment']);p0=Q(a['surplus_no_adjustment'])
    lower0=1-eta/(f0-c0)-c0-f0*f0/50-eta
    rows=[['Initial fee threshold',interval(ca),interval([c0,c0])],['Offered fee',dec(fa,2),dec(f0,2)],['Exact purchaser payoff',interval(a['surplus_adjustment']),interval([p0,p0])],['Robust purchaser lower bound','$'+dec(Q(a['robust_adjustment_lower']))+'$','$'+dec(lower0)+'$']]
    table('table_continuous_benchmark.tex','A continuous-diffusion procurement certificate','tab:r19-continuous','lcc','Quantity & Adjustment & No adjustment',rows,'The robust rows use a single global loss tolerance $\\eta=10^{-6}$ and a transfer that guarantees weak participation. The adjusted lower payoff exceeds the no-adjustment exact upper payoff by more than $'+dec(Q(a['robust_decision_margin_lower']))+'$. All displayed intervals are outward rational enclosures. This is the stated Brownian quadratic economy, not the CRRA settlement constructor.')
    pp=js('proposals.json');rows=[];summary=[]
    groups=[('nearest',None,'Nearest anchor'),('polynomial',None,'Polynomial'),('bank',None,'Evaluated bank')]+[('neural',s,'Neural '+str(s)) for s in pp['seeds']]+[('exact',None,'Exact DP')]
    for adj in (True,False):
      for method,seed,label in groups:
        rr=[r for r in pp['rows'] if r['adjustment']==adj and r['method']==method and r['seed']==seed]
        if len(rr)!=3:raise ValueError('missing complete three-law comparator '+str((adj,method,seed)))
        offline=rr[0]['teacher_seconds']+rr[0]['training_seconds'];online=sum(r['online_with_reference_seconds'] for r in rr);gap=max(g for r in rr for g in r['gaps'].values())
        rows.append(['Yes' if adj else 'No',label,f'{offline:.3f}',f'{online:.3f}',f'{gap:.3g}'])
        summary.append(dict(adjustment=adj,method=method,seed=seed,offline_seconds=offline,three_query_seconds=online,worst_gap=gap,parameter_bytes=rr[0]['parameter_bytes']))
    table('table_repeated_proposals.tex','Repeated proposals and complete policy controls','tab:r19-proposals','llrrr','Adjustment & Method & Offline (s) & Workload (s) & Largest gap',rows,'Offline cost includes the method\'s teachers and fitting. Workload is the sum over the three test laws of proposal, feasible-policy evaluation, and exact upper-reference time. Largest gap includes both initial mandates and every test law, with the arithmetic allowance. Independent checking is timed separately in the validation receipts. All methods share the same canonical transition arrays; this is not a state-dimension experiment.')
    write(O/'table_summary.json',json.dumps(dict(enforcement=e['rows'],continuous=a,proposal_groups=summary),indent=2,sort_keys=True)+'\n')

def labels(s):return set(re.findall(r'\\label\{([^}]+)\}',s))
def external_refs(s,local):
    def f(m):
      name=m.group(2)
      return '\\'+m.group(1)+'{'+(name if name in local or name.startswith('paper-') else 'paper-'+name)+'}'
    return re.sub(r'\\(ref|eqref|pageref)\{([^}]+)\}',f,s)

def split_proofs(name):
    source=(P/name).read_text();proofs=[];pattern=r'\\begin\{proof\}(.*?)\\end\{proof\}'
    for match in re.finditer(pattern,source,re.S):
      before=source[:match.start()];found=re.findall(r'\\begin\{(theorem|proposition|lemma|corollary)\}.*?\\label\{([^}]+)\}',before,re.S)
      if not found:raise ValueError('proof without theorem label '+name)
      kind,label=found[-1];proofs.append('\\subsection{Proof of '+kind.title()+'~\\ref{'+label+'}}\n'+match.group(0)+'\n')
    normalized=re.sub(pattern,lambda m:'\\noindent The proof is in the supplementary appendix.\n',source,flags=re.S)
    new='main_'+name;write(P/new,normalized)
    return inp(new.removesuffix('.tex')),proofs

def assemble_text():
    original=(OLD/'main.tex').read_text();heads=list(re.finditer(r'^\\section\{([^}]+)\}',original,re.M))
    blocks=[(m.group(1),original[m.start():heads[i+1].start() if i+1<len(heads) else len(original)]) for i,m in enumerate(heads)]
    if blocks[0][0]!='Introduction' or blocks[-1][0]!='Conclusion':raise ValueError('unexpected historical manuscript structure')
    introduction=(P/'introduction.tex').read_text()
    related=re.search(r'\\paragraph\*\{Related literature\.\}.*?(?=\\paragraph\*\{Organization\.\})',blocks[0][1],re.S)
    if related:introduction+='\n'+related.group(0)
    newmain=[introduction];proofs=[];newparts={}
    for name in ('information_theorem.tex','enforcement_theorem.tex','interval_response.tex','continuous_benchmark.tex'):
      inc,pr=split_proofs(name);newparts[name]=inc;proofs.extend(pr)
    evidence=(P/'new_evidence.tex').read_text();cut='\\subsection{Evidence identities and continuous instruments}'
    evidence_main,evidence_audit=evidence.split(cut,1)
    write(P/'main_new_evidence.tex',evidence_main)
    for title,text in blocks[1:-1]:
      if title=='Response Sets and Procurement':newmain.append(newparts['information_theorem.tex'])
      if title=='Contract Choice in the Settlement Economy':
        for name in ('enforcement_theorem.tex','interval_response.tex','continuous_benchmark.tex'):newmain.append(newparts[name])
      if title=='Neural Bellman Operators and the Computational Comparison':
        text=text.replace('\\subsection{Arithmetic and an open financial mandate}',inp('repeated_proposals')+'\n\\subsection{Arithmetic and an open financial mandate}')
      newmain.append(text)
      if title=='Contract Choice in the Settlement Economy':newmain.append(inp('main_new_evidence'))
    newmain.append((P/'conclusion.tex').read_text());main='\n'.join(newmain)
    write(P/'main.tex',main)
    info=(R15/'information.tex').read_text()
    info=info.replace('with a compact action representation and randomization','with a finite polyhedral action representation and randomization')
    info=info.replace('every $\\lambda\\geq R_w/\\delta$','every positive $\\lambda\\geq R_w/\\delta$')
    info=info.replace('maximize the dynamic reward $B+bA-(1-\\rho_F)aH$','with zero quality premium, maximize the dynamic reward $B+(d+b)A-(1-\\rho_F)aH$')
    old='The deposited continuum certificate takes the smaller of the independently checked value-message bound and the whole-interval graph bound, and records which one determines each cell.'
    new='The retained executed continuum certificate uses its stated value-message algorithm. The whole-interval graph is a separately proved refinement; no empirical cell is retrospectively assigned to an algorithm that was not executed.'
    if old not in info:raise ValueError('unrecognized R15 empirical claim')
    info=info.replace(old,new)
    bridge=(R15/'operator_bridge.tex').read_text();start=bridge.index('\\subsection{Repeated proposals and end-to-end costs}');end=bridge.index('\\subsection{Decision-directed rather than independent error charges}')
    removed=bridge[start:end];bridge=bridge[:start]+bridge[end:]
    bridge+='\nThe main paper\'s Proposition~\\ref{prop:r19-continuous} supplies an explicit continuous candidate and decision budget in a distinct Brownian economy. It does not change the scope of the CRRA constructor statement above.\n'
    technical=(P/'technical_appendix.tex').read_text()
    prooftext='\\section{Proofs of the New Main Results}\n'+'\n'.join(proofs)
    local=labels(info+bridge+technical+prooftext)
    write(P/'proofs_new.tex',external_refs(prooftext,local))
    write(P/'interface_information.tex',external_refs('\\section{Known Dynamics and Directed Messages}\n'+info,local))
    write(P/'interface_operator.tex',external_refs('\\section{Operator Error and Continuous Verification}\n'+bridge,local))
    write(P/'technical_current.tex',external_refs(technical,local))
    write(P/'audit_notes.tex',external_refs('\\section{Evidence Identity and Historical Preservation}\n'+evidence_audit,local))
    # All R14 proofs remain verbatim, with their already-prefixed paper references.
    supp=inp('proofs_new')+'\n\\section{Retained Response and Procurement Proofs}\n'+'\\input{'+str((OLD/'proofs').relative_to(ROOT))+'}\n'+inp('interface_information')+inp('interface_operator')+inp('technical_current')+inp('audit_notes')
    write(P/'supplement.tex',supp)
    write(R/'historical/R15_unexecuted_experiment_description.tex',removed)
    write(R/'historical/R14_main_source.tex',original)
    for name in ('README.md','REVISION_INDEX.md'):
      write(R/'historical'/name,subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True))
    inventory=[]
    for path in sorted(list(OLD.glob('*.tex'))+list(R15.glob('*.tex'))):inventory.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path)))
    write(R/'preserved_sources.json',json.dumps(inventory,indent=2)+'\n')
    write(R/'PRESERVATION.md','# Preservation map\n\nEvery original R14 and R15 source remains unchanged at its original path. `preserved_sources.json` records their SHA-256 values. The current main retains the entire R14 economic environment, response/procurement theory, continuous-instrument construction, settlement results, adverse mechanism map, operator comparison, arithmetic account, and model-transfer analysis. The introduction and conclusion are rewritten; the complete older main source and published compendium remain available.\n\nNew main proofs are moved without abridgment into the current supplement. Useful R15 information and operator statements are normalized and proved there. The fee-free reward is corrected to include the operating-benefit term in the graph accounting formula; positive multipliers and the finite polyhedral representation are stated explicitly. The undeployed R15 four-family experiment is preserved as a historical design, not misreported as observed output. The executed R19 three-seed study and all unfavorable results replace that unsupported empirical description in the current argument. No old theorem or numerical table is silently assigned to a different model.\n')

def wrappers():
    abstract='''We study the information and enforcement needed to procure a dynamic service when the agent may adjust operating choices and surrender. An institutional information theorem constructs dynamically implementable economies with identical values on an entire family of queries but opposite procurement rankings. It gives the minimax decision loss and the exact noise threshold at which a purchaser-directed joint query resolves it. Initial-state enforcement is distinguished from uniform state-wide implementation, with sufficient conditions connecting their orderings and a sharp global near-optimal-response frontier. Whole-interval action-loss certificates retain this global behavioral budget. An explicit controlled Brownian economy supplies analytic Bellman candidates, verified stopping obstacles, and a participation-adjusted procurement comparison. In the original stochastic settlement economy, independently bracketed initial fees and retained continuous-instrument certificates quantify the enforcement comparison without identifying array accuracy with diffusion approximation. Repeated neural proposals are evaluated against teacher-bank and exact-policy controls, with unfavorable outcomes and complete cost accounts retained.'''
    main=(ROOT/'ECTA_R14.tex').read_text().replace('Revision R14','Revision R19').replace('September 19, 2026','September 20, 2026')
    main=main.replace('\\input{revisions/2026-09-19-r14-referee-response/paper/main}',inp('main').strip())
    main=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',main,flags=re.S)
    main=main.replace('\\begin{document}','\\setlength{\\emergencystretch}{2em}\n\\begin{document}')
    write(ROOT/'ECTA_R19.tex',main);write(R/'ECTA_R19.tex',main)
    supp=(ROOT/'SUPP_R14.tex').read_text().replace('Revision R14','Revision R19').replace('September 19, 2026','September 20, 2026')
    supp=supp.replace('revisions/2026-09-19-r14-referee-response/ECTA_R14',REL+'/ECTA_R19').replace('[ECTA_R14.pdf]','[ECTA_R19.pdf]')
    supp=supp.replace('\\setcounter{section}{15}','\\setcounter{section}{0}').replace('\\input{revisions/2026-09-19-r14-referee-response/paper/proofs}',inp('supplement').strip())
    supp=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\nThis supplement contains complete proofs of the institutional information theorem, initial implementation conditions, global response-loss frontier, whole-interval certificate, and continuous Brownian application. It retains the response-set and procurement proofs and supplies the occupancy, directed-message, operator-residual, and continuous-verification interfaces. Arithmetic, first-date attainment, structural reachability, inference provenance, and preservation are documented separately from their economic implications.\n\\end{abstract}',supp,flags=re.S)
    supp=supp.replace('\\begin{document}','\\setlength{\\emergencystretch}{2em}\n\\begin{document}')
    write(ROOT/'SUPP_R19.tex',supp);write(R/'SUPP_R19.tex',supp)
    front=r'''\documentclass[ecta]{econsocart}
\usepackage{xr-hyper}
\input{revisions/2026-09-17-r9-participation-permissions/paper/preamble}
\externaldocument[paper-]{revisions/2026-09-20-r19/ECTA_R19}[ECTA_R19.pdf]
\setlength{\emergencystretch}{2em}
\makeatletter
\def\copyright@text{Revision R19 --- September 20, 2026}
\def\@runjournal{Revision R19 Response}
\def\form@runauthors{\def\@runjournal{Revision R19 Response}}
\makeatother
\begin{document}
\begin{frontmatter}
\title{Response to the Referee:\\Neural Bellman Operators}
\runtitle{Response to the Referee}
\begin{aug}
\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}
\address[id=add1]{\orgname{Peking University}}
\end{aug}
\end{frontmatter}
'''
    response=front+inp('response')+'\\end{document}\n'
    write(ROOT/'RESPONSE_R19.tex',response);write(R/'RESPONSE_R19.tex',response)
    comp=(ROOT/'COMPENDIUM_R14.tex').read_text();prefix=comp[:comp.index('\\section*{Reading the current revision')]
    prefix=prefix.replace('Revision R14','Revision R19').replace('current main manuscript','R19 main manuscript')
    prefix=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\nThis volume contains the current R19 main paper and proof supplement, followed by the complete unchanged R14 research compendium. The latter preserves the earlier operator theory, recursive utility, equilibrium derivations, full papers, supplements, and adverse numerical cases. Historical pages retain their original assumptions and target identities. Their preservation is not a claim that every historical statement applies to the current numerical target.\n\\end{abstract}',prefix,flags=re.S)
    prefix=prefix.replace('\\begin{document}','\\makeatletter\n\\def\\copyright@text{Revision R19 --- September 20, 2026}\n\\def\\form@runauthors{\\def\\@runjournal{R19 Research Compendium}}\n\\makeatother\n\\begin{document}')
    comp=prefix+'\\section*{Current paper and complete preserved research record}\nRead the current main paper and supplement first. The remaining pages preserve the entire prior research record, without reassigning its conclusions to a new model.\n'
    for path in (REL+'/ECTA_R19.pdf',REL+'/SUPP_R19.pdf','revisions/2026-09-19-r14-referee-response/COMPENDIUM_R14.pdf'):
      comp+='\\includepdf[pages=-]{'+path+'}\n'
    comp+='\\end{document}\n';write(ROOT/'COMPENDIUM_R19.tex',comp);write(R/'COMPENDIUM_R19.tex',comp)

def metadata():
    text='''# Neural Bellman Operators — R19

The current author manuscript is **R19, September 20, 2026**. The reviewed base is `d15591aff0bed68334cbb205294edfb04297427c`; the R18 report is at review commit `a17c867624e34f1264ff5cba60e51a850026803f`. The author development branch is `revision/econometrica-r19-development-2026-09-20`; the checked rereview snapshot is `revision/econometrica-r19-referee-release-2026-09-20`.

## Read the current revision

- [Main manuscript](revisions/2026-09-20-r19/ECTA_R19.pdf), with root source `ECTA_R19.tex`.
- [Complete proof supplement](revisions/2026-09-20-r19/SUPP_R19.pdf), with root source `SUPP_R19.tex`.
- [Point-by-point response](revisions/2026-09-20-r19/RESPONSE_R19.pdf), with root source `RESPONSE_R19.tex`.
- [Complete preserved research compendium](revisions/2026-09-20-r19/COMPENDIUM_R19.pdf).

The new results concern institution-dependent query information, initial implementation and global response loss, whole-fee-cell certificates, and an explicitly verified Brownian procurement benchmark. The unchanged CRRA settlement target has freshly bracketed initial enforcement fees and a repeated three-seed study including evaluated-bank and exact-DP policy controls. Earlier adverse cases and the complete research record remain preserved.

## Reproduce from this checkout

Use Python 3.11, NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0, and PyMuPDF 1.26.6, with one BLAS/OpenMP thread. TeX requires the deposited `econsocart` class, latexmk, and standard AMS/Palatino packages.

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python replication/r19/prepare_release.py
python replication/r19/replicate.py
python -O replication/r19/verify.py
python -O replication/r19/final_checks.py
python -O replication/r14/verify.py --receipt replication/r19/output/inherited_validation.json
python replication/r19/assemble.py
python replication/r19/publish.py
```

The producer is not the verifier. The independent R19 checker reconstructs Bellman and selected-policy calculations without importing the producer's engine. The second check reproduces inference and establishes first-date attainment. The R14 checker revalidates the retained full fee cover and rational economic bounds read-only. Tables are generated from the checked records. `build_report.json` and `release_manifest.json` identify the actual compiled files and evidence hashes.

## Evidence boundaries

The Brownian example is a genuine continuous diffusion with analytic residual and stopping-obstacle verification. It does **not** certify inclusion of the CRRA settlement diffusion in the numerical target's decision margins. The repeated study is on one two-state-variable target and does **not** establish a high-dimensional end-to-end neural advantage. These two extensions are not marked closed. Numerical parameters remain normalized, not empirically estimated. No acceptance decision is inferred from a successful software check.

## Prior research

Earlier versions are historical, not current submission entry points. [Preservation map](revisions/2026-09-20-r19/PRESERVATION.md) records the retained source and publication files. The full prior README and revision index are archived unchanged in the R19 historical directory.
'''
    write(ROOT/'README.md',text)
    write(R/'README.md',text.replace('(revisions/2026-09-20-r19/','('))
    write(ROOT/'REVISION_INDEX.md','# Authoritative revision index\n\nCurrent author paper: **R19**, `revisions/2026-09-20-r19/`. Entry points: `ECTA_R19.tex`, `SUPP_R19.tex`, `RESPONSE_R19.tex`, `COMPENDIUM_R19.tex`. Compiled outputs have matching PDF names in that directory. See its `release_manifest.json`, `build_report.json`, and the independent receipts under `replication/r19/output/`.\n\nR18 reviewed author identity: `'+BASE+'`. R18 report identity: `'+REVIEW+'`. The new author changes are isolated on R19 revision branches; the main and report branches are not modified.\n\nHistorical R14 full publication: `revisions/2026-09-19-r14-referee-response/`. Historical R15 mathematical fragments: `revisions/2026-09-19-r15-referee-response/paper/`. The old index is preserved at `revisions/2026-09-20-r19/historical/REVISION_INDEX.md`; its claims of then-current status apply only to that historical snapshot.\n')
    status=dict(reviewed_author=BASE,report_commit=REVIEW,new_science=['institution-dependent minimal information and minimax regret','initial enforcement conditions and sharp global eta frontier','whole-cell occupancy-weighted loss certificate','analytic continuous Brownian verification and procurement margin','regenerated settlement initial thresholds','three-seed evaluated-bank and exact-policy study'],not_established=['decision-separating constructor inclusion for the original CRRA diffusion','high-dimensional end-to-end neural computational advantage'],preservation='Original R14 and R15 sources remain unchanged; all older compiled compendium pages retained.')
    write(R/'response_status.json',json.dumps(status,indent=2)+'\n')

def main():
    for name,key in (('validation.json','passed'),('final_checks.json','passed'),('inherited_validation.json','all_passed')):
      if not js(name).get(key):raise ValueError('publication requires successful '+name)
    make_tables();assemble_text();wrappers();metadata()
    print('Complete R19 manuscript, supplement, response, compendium sources and generated tables assembled.',flush=True)
if __name__=='__main__':main()
