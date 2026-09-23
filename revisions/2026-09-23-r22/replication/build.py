"""Materialize and compile the complete Econometrica R22 referee object."""
from pathlib import Path
from decimal import Decimal,ROUND_CEILING,ROUND_FLOOR
import hashlib,json,re,subprocess,os,zipfile
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r22';PAPER=REV/'paper'
REVIEW='fc16c4fb27b54e11c67ce1983b6830a39038f063'

def read(p):return json.loads(p.read_text())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def number(v,n=8,upper=True):
    return format(Decimal(str(v)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_CEILING if upper else ROUND_FLOOR),'f')
def escape(s):
    for a,b in [ ('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('$',r'\$'),('#',r'\#'),('_',r'\_'),('^',r'\textasciicircum{}') ]:s=s.replace(a,b)
    return s

def tables():
    d=read(REV/'results/moment_continuum.json');rows=d['rows'];neural=[r for r in rows if r['representation']=='neural' and r['optimizer']=='adam']
    state=read(REV/'results/full_state/time_envelope.json')[1]['all_start_times_regret_upper']
    constants={'NeuralRegret':number(max(r['K_regret_upper'] for r in neural),6),
       'GainMin':number(min(r['K_gain_from_initial_lower'] for r in neural),6,False),
       'RatioMax':number(max(r['true_regret_ratio_upper'] for r in neural),7),
       'ConditionalGain':number(min(r['neural_adam_minus_direct_adam_uniform_payoff_gain_lower'] for r in d['conditional_representation_comparison']),6,False),
       'GlobalBound':number(state,9),'ShiftError':f"{read(REV/'results/root_repair/summary.json')['max_delivered_intercept_difference']:.4g}",
       'RuntimeMs':number(1000*read(REV/'results/runtime_cost.json')['rows'][0]['median_seconds'],3),
       'ComplexBound':number(read(REV/'results/proof_checks.json')['complex_pair_integrand_upper'],6)}
    if 'e' in constants['ShiftError']:
        mant,ex=constants['ShiftError'].split('e');constants['ShiftError']=r'$'+mant+r'\times10^{'+str(int(ex))+r'}$'
    constants.update({'StressAccepted':str(read(REV/'results/stress/summary.json')['accepted']), 'StressRejected':str(read(REV/'results/stress/summary.json')['rejected']), 'RecoveryAccepted':str(read(REV/'results/rejection_recovery/summary.json')['accepted']), 'RecoveryRejected':str(read(REV/'results/rejection_recovery/summary.json')['rejected'])})
    write(PAPER/'result_macros.tex','\n'.join(r'\newcommand{\RXXII'+k+'}{'+v+'}' for k,v in constants.items())+'\n')
    lines=[r'\begin{table}[htbp]',r'\caption{Matched-initial-policy crossed experiment: complete four-expert systems}\label{tab:r22crossed}',r'\small\begin{tabular}{llrrrr}',r'\toprule',r'Ensemble & Configuration & Regret upper & Gain lower & Gradients & Gen. sec.\\\midrule']
    names={('neural','adam'):'Neural--Adam',('neural','lbfgsb'):'Neural--L-BFGS-B',('direct','adam'):'Direct--Adam',('direct','lbfgsb'):'Direct--L-BFGS-B'}
    for r in rows:
        lines.append(f"{r['base_seed']} & {names[r['representation'],r['optimizer']]} & {number(r['K_regret_upper'])} & {number(r['K_gain_from_initial_lower'],8,False)} & {r['gradient_evaluations']} & {r['generation_seconds']:.3f}"+r'\\')
    lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\parbox{.96\textwidth}{\footnotesize Uniform bounds concern $K$ at $t=0,k=2$. Gain is relative to the initial mixture. A negative gain lower bound makes no positive-improvement claim. Generation excludes checking; full costs are in the supplement.}',r'\end{table}']
    write(PAPER/'crossed_table.tex','\n'.join(lines)+'\n')
    lines=[r'\begin{table}[htbp]',r'\caption{Neural--Adam versus direct--Adam: uniform true-payoff comparison}\label{tab:r22conditional}',r'\begin{tabular}{rrrr}',r'\toprule',r'Ensemble & Vertex gain lower & Direct Jensen upper & Uniform gain lower\\\midrule']
    for r in d['conditional_representation_comparison']:
        lines.append(f"{r['base_seed']} & {number(r['minimum_vertex_payoff_gain_lower'],8,False)} & {number(r['direct_mixture_jensen_upper'])} & {number(r['neural_adam_minus_direct_adam_uniform_payoff_gain_lower'],8,False)}"+r'\\')
    lines += [r'\bottomrule\end{tabular}',r'\end{table}'];write(PAPER/'conditional_table.tex','\n'.join(lines)+'\n')
    lines=[r'\small\begin{longtable}{rrllrrrr}',r'\caption{All 48 final vertex proposals}\label{tab:r22ledger}\\',r'\toprule',r'Seed & $v$ & Rep. & Opt. & Grad. & Search & Delivered regret & Check sec.\\\midrule\endfirsthead',r'\toprule',r'Seed & $v$ & Rep. & Opt. & Grad. & Search & Delivered regret & Check sec.\\\midrule\endhead']
    for f in sorted((REV/'results/crossed').glob('seed*/vertex*/*/record.json')):
        r=read(f);tag='N' if r['representation']=='neural' else 'D';tag+=r'$^{\dagger}$' if not r['accepted'] else ''
        lines.append(f"{r['base_seed']} & {r['vertex']} & {tag} & {'Adam' if r['optimizer']=='adam' else 'LBFGS'} & {r['gradient_evaluations']} & {r['line_search_evaluations']} & {number(r['delivered_certificate']['regret_upper'])} & {r['final_checker_seconds']:.3f}"+r'\\')
    lines += [r'\bottomrule\end{longtable}',r'\normalsize $\dagger$: rejected proposal; the initial incumbent is delivered. Search counts are additional objective calls as defined in the text.']
    write(PAPER/'full_ledger.tex','\n'.join(lines)+'\n')
    rr=read(REV/'results/root_repair/summary.json')['rows'];lines=[r'\begin{table}[htbp]\caption{Selected-block root-safe diagnostic; not a replacement primary experiment}\begin{tabular}{lrrr}\toprule',r'Configuration & Gradients & Regret upper & Gen. sec.\\\midrule']
    for r in rr:
        cert=r['certificate'];bound=number(cert['regret_upper']) if cert['status']=='CERTIFIED' else 'Rejected'
        lines.append(f"{names[r['representation'],r['optimizer']]} & {r['gradient_evaluations']} & {bound} & {r['generation_seconds']:.3f}"+r'\\')
    lines += [r'\bottomrule\end{tabular}\end{table}'];write(PAPER/'repair_table.tex','\n'.join(lines)+'\n')
    lines=[r'\begin{table}[htbp]\caption{Conditional-price timing diagnostic}\begin{tabular}{rrrrr}\toprule',r'Experts & Max. nodes & Coeff. bytes & Median ms & 90th pct. ms\\\midrule']
    for r in read(REV/'results/runtime_cost.json')['rows']:
        lines.append(f"{r['experts']} & {r['maximum_quadrature_nodes_per_query']} & {r['compiled_coefficient_bytes']} & {1000*r['median_seconds']:.3f} & {1000*r['p90_seconds']:.3f}"+r'\\')
    lines += [r'\bottomrule\end{tabular}\end{table}'];write(PAPER/'runtime_table.tex','\n'.join(lines)+'\n')
    return constants

def materialize(constants):
    old=ROOT/'revisions/2026-09-23-r21/paper'
    # Preserve old scientific text; only current interpretive labels are corrected.
    for name in ['method','results']:
        s=(old/f'{name}.tex').read_text()
        s=re.sub('same-family representation ablation','same-policy-class end-to-end comparison',s,flags=re.I)
        s=re.sub('representation ablation','end-to-end configuration comparison',s,flags=re.I)
        s=s.replace('sufficient compensation','a sufficient re-budgeted wealth increment')
        write(PAPER/f'retained_r21_{name}.tex',s)
    main=(old/'main.tex').read_text()
    main=main.replace('revisions/2026-09-23-r21/paper/introduction','revisions/2026-09-23-r22/paper/introduction')
    main=main.replace('revisions/2026-09-23-r21/paper/method','revisions/2026-09-23-r22/paper/retained_r21_method')
    main=main.replace(r'\input{revisions/2026-09-23-r21/paper/results}',r'\input{revisions/2026-09-23-r22/paper/method}'+'\n'+r'\input{revisions/2026-09-23-r22/paper/results}'+'\n'+r'\section{Earlier regional results, retained with their original scopes}'+'\n'+'The next results are the frozen R20/R21 analyses. Their end-to-end baseline is not the new crossed representation experiment. The precise re-budgeted interpretation above governs current welfare terminology.'+'\n'+r'\input{revisions/2026-09-23-r22/paper/retained_r21_results}')
    main=main.replace('revisions/2026-09-23-r21/paper/conclusion','revisions/2026-09-23-r22/paper/conclusion')
    write(PAPER/'main.tex',main)
    tex=(ROOT/'ECTA_R21.tex').read_text().replace('R21','R22')
    tex=tex.replace(r'\usepackage{xurl}',r'\usepackage{xurl,longtable}')
    tex=tex.replace(r'\input{revisions/2026-09-23-r21/paper/main}',r'\input{revisions/2026-09-23-r22/paper/main}')
    tex=tex.replace(r'\begin{document}',r'\input{revisions/2026-09-23-r22/paper/result_macros}'+'\n'+r'\begin{document}')
    tex=tex.replace(r'\begin{appendix}',r'\begin{appendix}'+'\n'+r'\input{revisions/2026-09-23-r22/paper/proofs}')
    abstract=r'''We develop policy-value-separated Neural Bellman Operators for the original stopped consumption--portfolio economy. A crossed experiment matches delivered initial policies and separates neural versus direct parameterizations from Adam versus L-BFGS-B. At a common gradient-call cap, independently initialized neural--Adam ensembles attain uniform regional regret below \RXXIINeuralRegret{}. A verified pair-moment Jensen theorem proves initial-to-final payoff gain of at least \RXXIIGainMin{} and a uniform gain of at least \RXXIIConditionalGain{} over matched direct--Adam mixtures, without synchronized corner initialization. Direct L-BFGS-B remains the stronger overall regional configuration. Active rejection exposes deterministic rollback repetition and a financing-root defect; separately identified supervisory and root-safe repairs address them. A warm-start current-state actor/witness refinement tightens the independently checked complete-domain bound to \RXXIIGlobalBound{}, still above the unchanged $.01$ objective. Constructive residual corrections, cover complexity, and deployment accounting distinguish the general verification mechanism from the model-specific financial decoder. Earlier proofs, numerical evidence, and adverse comparisons are retained.'''
    tex=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',tex,flags=re.S)
    write(ROOT/'ECTA_R22.tex',tex)
    supp=(ROOT/'SUPP_R21.tex').read_text().replace('R21','R22').replace(r'\usepackage{xurl}',r'\usepackage{xurl,longtable}')
    supp=supp.replace(r'\begin{document}',r'\input{revisions/2026-09-23-r22/paper/result_macros}'+'\n'+r'\begin{document}')
    supp=supp.replace(r'\input{revisions/2026-09-23-r21/paper/supplement}',r'\input{revisions/2026-09-23-r22/paper/supplement}'+'\n'+r'\input{revisions/2026-09-23-r21/paper/supplement}')
    supp=supp.replace(r'\clearpage'+'\n'+r'\input{revisions/2026-09-23-r18/paper/references}',r'\clearpage'+'\n'+r'\section{Historical R21 exposition, preserved verbatim}'+'\n'+r'\input{revisions/2026-09-23-r21/paper/introduction}'+'\n'+r'\input{revisions/2026-09-23-r21/paper/conclusion}'+'\n'+r'\clearpage'+'\n'+r'\input{revisions/2026-09-23-r18/paper/references}')
    supp=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}Complete crossed-configuration ledgers, proof dependencies, root and rejection diagnostics, deployment costs, and retained historical technical material accompany the main paper. Prospective executions, post-observation repairs, analytic certification, and arithmetic diagnostics are identified separately.\end{abstract}',supp,flags=re.S)
    write(ROOT/'SUPP_R22.tex',supp)
    response=(REV/'RESPONSE.md').read_text().replace('7.2405032566',constants['GlobalBound'])
    response=response.replace('0.026111',constants['GainMin']).replace('0.003112',constants['ConditionalGain'])
    # Counts can differ across hardware-sensitive repeat executions; never hard-code them as certificates.
    stress=read(REV/'results/stress/summary.json');recovery=read(REV/'results/rejection_recovery/summary.json')
    response=response.replace('accepts three of eight blocks and rejects five',f"accepts {stress['accepted']} of eight blocks and rejects {stress['rejected']}")
    response=response.replace('accepts six blocks, rejects two',f"accepts {recovery['accepted']} blocks, rejects {recovery['rejected']}")
    write(REV/'RESPONSE_EXECUTED.md',response)
    body=[]
    for para in response.split('\n\n'):
        if para.startswith('# '):continue
        if para.startswith('## '):body.append(r'\section{'+escape(para[3:])+'}')
        else:body.append(escape(para.replace('\n',' ')))
    pre=tex.split(r'\begin{document}')[0]
    doc=pre+r'''\begin{document}
\begin{frontmatter}
\title{Response to the Final R21 Referee Report}
\runtitle{Neural Bellman Operators: Response}
\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}\address[id=add1]{\orgname{Peking University}}\end{aug}
\begin{abstract}Point-by-point response to the Econometrica-standard report dated September 23, 2026, at review commit fc16c4fb. This document accompanies the complete R22 manuscript, supplement, code, and execution record.\end{abstract}
\end{frontmatter}
'''+ '\n\n'.join(body)+r'\end{document}'+'\n'
    write(ROOT/'RESPONSE_R22.tex',doc)
    # Record, rather than erase, the previously published revision entry.
    original_index=ROOT/'REVISION_INDEX.md';archive=REV/'archive/REVISION_INDEX_R21.md'
    if not archive.exists() and original_index.exists():archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(original_index.read_bytes())
    entry=f'''# NBO -- R22 referee entry\n\nLatest addressed report: `{REVIEW}` / `reviews/2026-09-23-econometrica-r21-final/referee_report.md`.\n\n- Main: `ECTA_R22.pdf` and `ECTA_R22.tex`.\n- Supplement: `SUPP_R22.pdf` and `SUPP_R22.tex`.\n- Response: `RESPONSE_R22.pdf`, `RESPONSE_R22.tex`, and `revisions/2026-09-23-r22/RESPONSE_EXECUTED.md`.\n- Proofs and code: `revisions/2026-09-23-r22/paper/` and `replication/`.\n- Results and provenance: `revisions/2026-09-23-r22/results/` and `publication_manifest.json`.\n\nNeural--Adam regional regret upper: {constants['NeuralRegret']}; uniform initial-to-final payoff gain lower: {constants['GainMin']}; same-Adam uniform neural-minus-direct payoff gain lower: {constants['ConditionalGain']}. These are local, optimizer-conditional results. Direct L-BFGS-B remains the stronger end-to-end local configuration. The new all-start-time, complete-domain current-state bound is {constants['GlobalBound']}, not 0.01.\n\nThe original target, model, title, proofs, numerical results, and adverse baselines are retained. Historical R21 entry: `revisions/2026-09-23-r22/archive/REVISION_INDEX_R21.md`. The regression fixture records the local preflight financing failure separately from the clean reference execution.\n'''
    write(ROOT/'R22_REVIEW.md',entry);write(original_index,entry)

def compile_docs():
    logs=REV/'build_logs';logs.mkdir(exist_ok=True);results=[]
    for name in ['ECTA_R22','SUPP_R22','RESPONSE_R22']:
        for i in range(3):
            p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,capture_output=True,text=True)
            write(logs/f'{name}_pass{i+1}.log',p.stdout+p.stderr)
            if p.returncode:raise RuntimeError(f'{name} pass {i+1} failed: '+p.stdout[-3000:])
        text=(ROOT/(name+'.log')).read_text(errors='replace')
        if re.search(r'There were undefined (references|citations)|LaTeX Warning: (Reference|Citation).*undefined',text):raise RuntimeError(name+' has unresolved references')
        over=[float(x) for x in re.findall(r'Overfull \\hbox \(([0-9.]+)pt too wide\)',text)]
        info=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
        results.append({'document':name,'pages':int(re.search(r'Pages:\s+(\d+)',info).group(1)),
             'pdf_sha256':sha(ROOT/(name+'.pdf')),'source_sha256':sha(ROOT/(name+'.tex')),'max_overfull_hbox_pt':max(over,default=0)})
    write(REV/'results/build.json',json.dumps(results,indent=2)+'\n')
    if max(r['max_overfull_hbox_pt'] for r in results)>3:raise RuntimeError('Layout overfull box exceeds3pt; inspect build logs')

def manifest():
    preservation={'mode':'local archive comparison pending repository verification'}
    if (ROOT/'.git').exists():
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',REVIEW],cwd=ROOT,text=True).splitlines();changed=[]
        for p in paths:
            old=subprocess.check_output(['git','rev-parse',REVIEW+':'+p],cwd=ROOT,text=True).strip()
            new=subprocess.check_output(['git','hash-object',str(ROOT/p)],cwd=ROOT,text=True).strip() if (ROOT/p).is_file() else None
            if old!=new:changed.append(p)
        assert changed==['REVISION_INDEX.md'],changed
        assert (REV/'archive/REVISION_INDEX_R21.md').read_bytes()==subprocess.check_output(['git','show',REVIEW+':REVISION_INDEX.md'],cwd=ROOT)
        preservation={'review_commit':REVIEW,'baseline_files_checked':len(paths),'changed_original_paths':changed,'old_index_archived_byte_identically':True}
    files={str(p.relative_to(ROOT)):sha(p) for p in sorted(REV.rglob('*')) if p.is_file() and '__pycache__' not in str(p) and p.name!='publication_manifest.json'}
    files.update({n:sha(ROOT/n) for n in ['ECTA_R22.tex','ECTA_R22.pdf','SUPP_R22.tex','SUPP_R22.pdf','RESPONSE_R22.tex','RESPONSE_R22.pdf','R22_REVIEW.md','REVISION_INDEX.md']})
    data={'review_commit':REVIEW,'source_commit':os.getenv('R22_SOURCE_COMMIT','local'),
       'protocol_commits':['082a3fdcf97d426df65858702b506bcdd7384ee3','a1e73f4262a232db147b245521af6af429e8f501','98df6e83a2d0ccfae0aab65d5750344e8b629414'],
       'reference_execution':'results/crossed; fixed local financing-failure fixture retained separately',
       'preservation':preservation,'documents':read(REV/'results/build.json'),'files':files}
    write(REV/'publication_manifest.json',json.dumps(data,indent=2)+'\n')
    with zipfile.ZipFile(ROOT/'NBO_R22_review_package.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(REV.rglob('*')):
            if p.is_file() and '__pycache__' not in str(p) and p.suffix not in ['.log','.tmp']:z.write(p,str(p.relative_to(ROOT)))
        for n in ['ECTA_R22.tex','ECTA_R22.pdf','SUPP_R22.tex','SUPP_R22.pdf','RESPONSE_R22.tex','RESPONSE_R22.pdf','R22_REVIEW.md','REVISION_INDEX.md']:z.write(ROOT/n,n)
        z.writestr('REPRODUCE.txt','Checkout the exact publication commit in TrillionniumFoundation/NBO. The repository retains all inherited dependencies. Run the ordered commands in .github/workflows/r22-publication.yml. No font files are included in this package.\n')

if __name__=='__main__':
    constants=tables();materialize(constants);compile_docs();manifest()
