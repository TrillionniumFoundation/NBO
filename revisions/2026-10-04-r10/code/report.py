"""Audit raw records, generate every new table, and integrate preserved roots."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,time
from pathlib import Path
from decimal import Decimal, ROUND_CEILING
import numpy as np
import torch
from tube_certificate import P,I,exp_i,spectral_bound,enclosure
from paired import stats
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];O=R/'results';M=R/'manuscript'
BASE='f8215d6df9026afa108a03c2823cbd6e054a9de8'
PREFIX='revisions/2026-10-04-r10'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def read(name):return json.loads((O/name).read_text())

def upper_decimal(value,places=5):
    """Print an upper endpoint without rounding the displayed bound down."""
    x=Decimal.from_float(float(value))
    return format(x.quantize(Decimal(1).scaleb(-places),rounding=ROUND_CEILING),f'.{places}f')

def paired_average(d,other,differences):
    return {**stats(np.mean(differences,axis=0)), 'dimension':d, 'comparator':other,
      'interpretation':'mean payoff of three fixed fitted actors minus three matched comparators, paired by path; not a seed-population interval'}

def prepare():
    a=R/'archive';a.mkdir(exist_ok=True)
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    hashes={}
    for name in names:
        p=ROOT/name;expected=subprocess.check_output(['git','rev-parse',f'{BASE}:{name}'],cwd=ROOT,text=True).strip()
        b=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        if actual!=expected:raise AssertionError(f'base file changed: {name}')
        hashes[name]=hashlib.sha256(b).hexdigest()
    put(a/'R9_FILES_SHA256.json',hashes)
    for source,target in [('ECTA.tex','ECTA.r9.tex'),('supp.tex','supp.r9.tex')]:
        (a/target).write_bytes((ROOT/source).read_bytes())
    put(O/'PRESERVATION_INPUT.json',dict(base=BASE,files=len(hashes)))

def audit():
    c=read('CONTINUOUS_CERTIFICATES.json');matrices=np.load(O/'MATRICES.npz');replays=[]
    assert len(c['records'])==54
    for d in [10,20,50]:
        B=matrices[f'B_{d}'];start=time.perf_counter();sp=spectral_bound(B)
        selected=enclosure(B,.1,0.,16384,sp)
        replays.append(dict(dimension=d,full_certificate_seconds=time.perf_counter()-start,
                            regret_upper=selected['regret_upper'],spectral=sp))
        for row in [r for r in c['records'] if r['dimension']==d]:
            check=enclosure(B,row['epsilon'],row['initial_std_upper'],row['panels'],sp)
            assert check['matrix_sha256']==row['matrix_sha256']
            assert abs(check['regret_upper']-row['regret_upper'])<1e-13
    fits=[];aggregates=[];raw_checks=0
    for d in [10,20,50]:
        sim=read(f'PAIRED_d{d}.json');path=O/f'PAIRED_d{d}.npz';assert digest(path)==sim['raw_sha256']
        z=np.load(path)
        for row in sim['records']:
            q=stats(z[f"{row['id']}_{row['steps']}"]);assert abs(q['mean']-row['mean'])<1e-13
            assert np.max(np.abs(np.array(q['ci95'])-row['ci95']))<1e-13;raw_checks+=1
        for method in ['actor','direct_tube','direct_full']:
          for seed in [11,29,47]:
            ident=f'{method}_d{d}_s{seed}';r=read(f'{ident}.json');w=O/f'{ident}.pt'
            assert digest(w)==r['weights_sha256']==sim['policy_source_sha256'][ident]
            state=torch.load(w,map_location='cpu',weights_only=True)
            assert np.array_equal(state['B'].numpy(),matrices[f'B_{d}'])
            assert state['epsilon']==.1
            assert all(torch.isfinite(t).all() for group in ['critic','actor'] for t in state[group].values())
            assert r['seed']==seed and r['dimension']==d and r['method']==method
            fits.append(r)
        for other in ['anchor','direct_tube','direct_full']:
            differences=[]
            for seed in [11,29,47]:
                key=other if other=='anchor' else f'{other}_d{d}_s{seed}'
                differences.append(z[f'actor_d{d}_s{seed}_160']-z[f'{key}_160'])
            aggregates.append(paired_average(d,other,differences))
    put(O/'CERTIFICATE_REPLAY.json',replays);put(O/'PAIRED_AGGREGATES.json',aggregates)
    put(O/'ALL_FITS.json',fits)
    put(O/'AUDIT.json',dict(certificate_records_replayed=54,raw_payoff_rows_recomputed=raw_checks,
        fitted_policies=len(fits),training_failures=[r['id'] for r in fits if r['failure']],
        incomplete_budgets=[r['id'] for r in fits if r['steps']!=r['requested_steps']],
        tube_target=.1,tube_bounds_below_target=all(r['regret_upper']<=.1 for r in c['records']),
        no_sampled_diagnostics_used_in_certificate=True,scope='arithmetic and provenance checks, not a guarantee of actor superiority'))

def table(name,caption,label,cols,header,rows,note,long=False):
    if long:
        text='\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'+header+'\\\\\n\\midrule\\endhead\n'
        text+='\n'.join(rows)+'\n\\bottomrule\n\\end{longtable}\n\\noindent{\\footnotesize '+note+'}\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+'\\\\\n\\midrule\n'
        text+='\n'.join(rows)+'\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip\\begin{minipage}{.97\\linewidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
    (M/name).write_text(text)

def tables():
    c=read('CONTINUOUS_CERTIFICATES.json')['records'];fits=read('ALL_FITS.json');replays=read('CERTIFICATE_REPLAY.json')
    annuity=(1-exp_i(-I(P['discount'])*I(P['T'])))/I(P['discount'])
    selected=[r for r in c if r['epsilon']==.1 and r['panels']==16384];rows=[]
    for r in selected:
        welfare=float(((exp_i(I(r['regret_upper'])/annuity)-1)*100).hi)
        rows.append(f"{r['dimension']} & {r['initial_std_upper']:.2f} & {upper_decimal(r['anchor_regret'][1],5)} & {upper_decimal(r['regret_upper'],5)} & {upper_decimal(welfare,2)}\\\\")
    table('table_bounds.tex','Continuous-economy bounds for every deployed tube policy','tab:r10bounds','rrrrr',r'$d$ & $s_0$ & Anchor bound & Tube bound & Flow supplement (\%)',rows,
      r'$\epsilon=.1$; 16,384 outward quadrature panels. Initial mean is unrestricted. The optimum allows all adapted controls in $[.02,2]^d$. Supplement is externally financed and uses an outward logarithmic-utility conversion. Printed upper endpoints are rounded upward. Bounds are conditional on the documented arithmetic contract.')
    names={'anchor':'Schedule','actor':'NBO actor','direct_tube':'Direct tube','direct_full':'Direct full'};rows=[]
    for d in [10,20,50]:
        cert=next(r['full_certificate_seconds'] for r in replays if r['dimension']==d)
        sim=read(f'PAIRED_d{d}.json')
        for method in ['anchor','actor','direct_tube','direct_full']:
            group=[r for r in fits if r['dimension']==d and r['method']==method]
            train=0 if method=='anchor' else np.mean([r['training_seconds'] for r in group])
            online=np.mean([r['seconds'] for r in sim['online'] if r['method']==method])*1000
            total=f'{train+cert:.3f}' if method!='direct_full' else '--'
            rows.append(f'{d} & {names[method]} & {train:.3f} & {total} & {online:.3f}\\\\')
    table('table_cost.tex','Measured cost of the trained and deployed policies','tab:r10cost','rlrrr',r'$d$ & Method & Training (s) & Training + bound (s) & Deployment (ms)',rows,
      r'Training is the mean of three separate seed runs; deployment evaluates 256 states and includes the inward schedule guard where applicable. Matrix verification plus scalar quadrature is charged in full to each certified method; no shared-cost amortization is used. The schedule needs no training and has the tighter guarantee. Direct-full training time is recorded, but no tube certificate is assigned to it. Detailed per-run memory and failures appear in the supplement.')
    rows=[]
    for r in read('PAIRED_AGGREGATES.json'):
        rows.append(f"{r['dimension']} & {names[r['comparator']]} & {r['mean']:.6f} & {r['ci95'][0]:.6f} & {r['ci95'][1]:.6f}\\\\")
    table('table_paired.tex','Paired actor-minus-comparator payoff differences','tab:r10paired','rlrrr',r'$d$ & Comparator & Mean difference & Lower 95\% & Upper 95\%',rows,
      r'512 common paths, 160 Euler steps. Each row averages the pathwise payoff differences of the three fixed seed fits before computing a Monte Carlo interval. These are not intervals over a population of training seeds and do not include Euler bias. No simulation result is substituted into the continuous-time proof.')
    rows=[]
    for r in fits:
        rows.append(f"{r['dimension']} & {names[r['method']]} & {r['seed']} & {r['training_seconds']:.2f} & {r['diagnostics']['residual_rms']:.4f} & {r['diagnostics']['sample_full_action_gap_max']:.4f} & {r['peak_process_rss_kib']/1024:.1f} & {int(r['failure'] is not None)}\\\\")
    table('table_all_fits.tex','All fitted policies, without seed exclusion','tab:r10allfits','rlrrrrrr',r'$d$ & Method & Seed & Seconds & RMS & Gap & MiB & Fail',rows,
      r'RMS and gap are diagnostics on 128 held-out states, not uniform certificates. Peak RSS is the separate process high-water mark, including the interpreter and libraries. Every requested fit is retained. All raw optimizer histories, negative trace-product batches, saved weights, sample counts, and bisection counts are committed.',True)
    rows=[]
    for r in c:
        rows.append(f"{r['dimension']} & {r['initial_std_upper']:.2f} & {r['epsilon']:.2f} & {r['panels']} & {upper_decimal(r['anchor_regret'][1],6)} & {upper_decimal(r['regret_upper'],6)}\\\\")
    table('table_all_bounds.tex','Complete radius, dispersion, and quadrature account','tab:r10allbounds','rrrrrr',r'$d$ & $s_0$ & $\epsilon$ & Panels & Anchor upper & Policy upper',rows,
      r'Quadrature endpoints are outward, not an error tolerance passed to an ordinary numerical integrator. Zero radius denotes the exact feasible schedule. Printed upper endpoints are rounded upward. The same matrix majorant is used for each dimension.',True)
    files={str(p.relative_to(ROOT)):digest(p) for p in O.glob('*.json')}
    files.update({str(p.relative_to(ROOT)):digest(p) for p in O.glob('*.npz')})
    put(R/'TABLE_MANIFEST.json',dict(inputs=files,outputs={str(p.relative_to(ROOT)):digest(p) for p in M.glob('table_*.tex')}))

def integrate():
    main=(R/'archive/ECTA.r9.tex').read_text();supp=(R/'archive/supp.r9.tex').read_text()
    oldlabels=set(re.findall(r'\\label\{([^}]+)\}',main));oldsections=re.findall(r'\\(?:sub)*section\*?\{([^}]+)\}',main)
    abstract='''We develop Neural Bellman Operators for economic control with recursive utility, endogenous preferences, and strategic interaction. Evaluation, feasible improvement, and verification are separate maps. A guarded critic and signed interval action cover connect neural proposals to nodal economic error accounts. We additionally derive a continuous-time performance bound for a dense nonlinear capital economy. Consumption curvature and synchronous state comparison control arbitrary adapted deviations; a schedule-centred neural actor inherits a computable regret bound over the original, unrestricted comparison class. Interval spectral verification and scalar quadrature avoid state-space covering. Generic actors and direct HJB comparators are trained in dimensions ten, twenty, and fifty, with all seeds, deployment costs, and paired payoffs reported. The feasible schedule remains an explicit, cheaper comparator with a tighter structural bound. Preference refinement, financed welfare comparisons, and finite-game deviations retain their separate scopes. The results distinguish guaranteed policy performance from optimizer convergence and measured actor gains.'''
    main=re.sub(r'(?<=\\begin\{abstract\})[\s\S]*?(?=\\end\{abstract\})','\n'+abstract+'\n',main,count=1)
    marker='\\section{Conclusion}\\label{sec:conclusion}'
    assert main.count(marker)==1
    main=main.replace(marker,f'\\input{{{PREFIX}/manuscript/continuous.tex}}\n\\input{{{PREFIX}/manuscript/study.tex}}\n'+marker)
    marker='\\section{Replication and Scope of Numerical Evidence}\\label{app:replication}'
    assert main.count(marker)==1
    main=main.replace(marker,f'\\input{{{PREFIX}/manuscript/proofs.tex}}\n'+marker)
    old='These bounds are materially wider than a tight neural-policy certificate. Paired simulations remain discretized policy comparisons.'
    new='Those historical absolute brackets are distinct from the new continuous-time neural-policy bound in Theorem~\\ref{thm:r10tube}. The latter uses the original capital economy and full adapted comparison class, with a schedule-centred actor architecture. Paired simulations remain discretized policy comparisons.'
    assert old in main;main=main.replace(old,new)
    paragraph='\\paragraph{Current revision.}'
    main=main.replace(paragraph,'\\paragraph{R9 revision record.}',1)
    insertion=f'''\n\\paragraph{{R10 revision record.}} The current source descends from the complete R9 evidence commit. Section~\\ref{{sec:r10continuous}} and its proof give the continuous-capital guarantee; Section~\\ref{{sec:r10study}} reports the complete training and deployment comparison. Exact previous roots, all new source and results, the response to the 3 October 2026 R8 advisory report, and the current execution identities are stored under \\texttt{{{PREFIX}}}. Earlier numerical accounts and unsuccessful experiments remain unchanged.\n'''
    main=main.replace('\\bibliographystyle{ecta-fullname}',insertion+'\\bibliographystyle{ecta-fullname}')
    intro='Section~\\ref{sec:model} specifies the economy.'
    add='The continuous-capital result closes a different part of the error account: curvature and a verified coupling norm bound the gain from arbitrary adapted deviations, while a schedule-centred actor supplies a uniformly constrained neural policy. The resulting bound concerns the original diffusion rather than a nodal surrogate. Its stronger structural benchmark is reported alongside every fitted policy.\n\n'
    assert intro in main;main=main.replace(intro,add+intro,1)
    supp=supp.replace('\\end{document}',f'\\input{{{PREFIX}/manuscript/supplement.tex}}\n\\end{{document}}')
    assert oldlabels<=set(re.findall(r'\\label\{([^}]+)\}',main))
    assert oldsections==re.findall(r'\\(?:sub)*section\*?\{([^}]+)\}',main)
    (ROOT/'ECTA.tex').write_text(main);(ROOT/'supp.tex').write_text(supp)
    put(O/'INTEGRATION.json',dict(base=BASE,all_original_root_labels_retained=True,all_original_root_section_headings_retained=True,
          original_root_label_count=len(oldlabels),new_material='additive inputs; abstract and present-tense synthesis updated; exact R9 roots archived'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','audit','tables','integrate']);a=p.parse_args();globals()[a.stage]()
