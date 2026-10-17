"""One-time integration preserving every R91 active section and original wrapper."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    marker=R/'audit/INTEGRATION92.json'
    if marker.exists():
        print('R92 ordinary author sources already integrated; no overwrite.');return
    backup=R/'preserved/R91-entry-points';backup.mkdir(parents=True,exist_ok=True)
    old_inputs={}
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.tex','preamble.tex'):
        p=R/name;q=backup/name
        if q.exists() and q.read_bytes()!=p.read_bytes():raise AssertionError('Conflicting original wrapper '+name)
        shutil.copy2(p,q)
        old_inputs[name]=re.findall(r'\\input\{(sections/[^}]+)\}',p.read_text())
    if (R/'build').exists():
        dest=R/'preserved/R91-compiled-history'
        if dest.exists():raise AssertionError('Preserved build already exists')
        shutil.move(str(R/'build'),str(dest))
    main=(R/'ECTA.tex').read_text()
    if r'\title{Neural Bellman Operators}' not in main:raise AssertionError('Original topic changed')
    abstract='This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement under the original economic law. Attained continuations retain feasible action witnesses and an original-optimum error account. Shared-parameter qualification extends from acquired actions to complete policies and endogenous occupations. Joint state-context construction supplies a common neural circuit under explicit primitive and acquisition conditions. Signed transition qualification treats recursive preferences without changing their objective. Reference-centered risk kernels now yield state-dependent original-optimum certificates, exact penalized risk occupations and strict support-based kernel exclusions. Stored continuations and coupled precision allocation provide a separate horizon-resource account. Prospective selection and uniform price-fee regions connect qualification to economic decisions. Independent investment evaluation identifies improvements and noninferiority while retaining unresolved comparisons. A frozen shared-proposal study finds no incremental ReLU query-work advantage. Exact nonlinear diagnostics distinguish certificate sharpening from empirical superiority. Diffusions, endogenous preferences, temporal selves and games retain their original hypotheses and comparison principles.'
    main=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',main,count=1,flags=re.S)
    needle=r'\input{sections/risk91}'
    if main.count(needle)!=1:raise AssertionError('Signed theorem insertion point')
    main=main.replace(needle,needle+'\n'+r'\input{sections/centeredrisk92}')
    paragraph=r'''\paragraph{State-dependent qualification under nonlinear preferences.}
The signed scalar account can charge states that cannot jointly determine the recursive loss. We center the original risk dual at the actual stored continuation, retaining its nonnegative dual slack as a penalty. State-dependent subsolutions and supersolutions then compare the complete policy with the original Bellman optimum. An exact finite risk-occupation identity and strict support certificates retain changing risk kernels without replacing them by physical probabilities or a frozen reference tilt. This connects the continuation's geometry to qualification work while preserving all original preference and feasible-action obligations.

'''
    main=main.replace(r'\paragraph{Reading path.}',paragraph+r'\paragraph{Reading path.}')
    closing='\nThe centered-risk extension retains where an error occurs and which risk kernels can make it consequential. Its exact finite occupation representation and safe kernel exclusions sharpen the same original-optimum account. Full construction and arithmetic costs remain separate from the size of a verified certificate; the unchanged empirical comparisons are not converted into neural-superiority claims by this analytical improvement.\n\n'
    main=main.replace(r'\bibliographystyle{ecta-fullname}',closing+r'\bibliographystyle{ecta-fullname}')
    (R/'ECTA.tex').write_text(main)
    for name,section in (('supp.tex','proofs92'),('appendix.tex','evidence92')):
        p=R/name;text=p.read_text();needle=r'\bibliographystyle{ecta-fullname}'
        if text.count(needle)!=1:raise AssertionError('Bibliography insertion point '+name)
        text=text.replace(needle,r'\input{sections/'+section+'}\n'+needle)
        p.write_text(text)
    canonical=(R/'references91-canonical.bib').read_text();extra=(R/'references92.bib').read_text()
    if 'ruszczynski2010risk' in canonical:
        if '10.1007/s10107-010-0393-3' not in canonical:raise AssertionError('Conflicting risk citation')
    else:canonical+='\n'+extra
    (R/'references92-canonical.bib').write_text(canonical)
    for name in ('ECTA.tex','supp.tex','appendix.tex'):
        p=R/name;p.write_text(p.read_text().replace('references91-canonical','references92-canonical').replace('label=e91','label=e92'))
    # Independent completeness check uses greedy cap fillings in all coordinate
    # orders, different from production's free-coordinate vertex enumeration.
    p=R/'code/independent92.py';text=p.read_text()
    text=text.replace('from itertools import product','from itertools import product,permutations')
    needle="                need(F(k['reference'])==rho,'Original risk reference')"
    insertion="""
                complete=set()
                for order in permutations(range(S)):
                    qq=[F(0)]*S;remaining=F(1)
                    for z in order:
                        qq[z]=min(remaining,p[z]/(1-alpha));remaining-=qq[z]
                    need(remaining==0,'Independent risk-envelope filling')
                    complete.add(tuple(qq))
                need(complete=={tuple(map(F,qq)) for qq in k['q']},'Complete independent risk envelope')
"""
    if text.count(needle)!=1:raise AssertionError('Independent completeness insertion point')
    text=text.replace(needle,needle+insertion);p.write_text(text)
    retained={}
    for name,inputs in old_inputs.items():
        current=re.findall(r'\\input\{(sections/[^}]+)\}',(R/name).read_text())
        missing=[x for x in inputs if x not in current]
        if missing:raise AssertionError(('Dropped active sections',name,missing))
        retained[name]={'inherited':len(inputs),'current':len(current),'missing':missing}
    marker.parent.mkdir(parents=True,exist_ok=True)
    marker.write_text(json.dumps({'status':'integrated','baseline':'368a9e754f5de04eb1957e152f22d6ef2c34f2fe','review':'b030d87d7e96440eb25a3178c94ee6a87940cdb0','active_sections':retained,'ordinary_inputs':{p.name:sha(p) for p in backup.glob('*')},'old_pdfs':'preserved/R91-compiled-history; not R92 outputs'},indent=2)+'\n')
    print(json.dumps(retained,indent=2),flush=True)
if __name__=='__main__':main()
