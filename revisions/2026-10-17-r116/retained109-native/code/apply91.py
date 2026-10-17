"""One-time R91 editorial integration; publication reads ordinary resulting TeX.

Run on the copied R90 directory. Previously integrated author sources are not
regenerated or overwritten. Every inherited section remains an active input.
"""
from pathlib import Path
import hashlib, json, re, shutil
R=Path(__file__).resolve().parents[1]
BASE='9e06160b5464c41a5b84eaab9c3c4d171fc22832'
EXPECTED={'ECTA.tex':'9cb1c93a61b9c52bb62f4d783a197df6c8a462df',
          'supp.tex':'9f0214ac441a0650ef0d69968da508aaa8d4c26d',
          'appendix.tex':'9a795e2ae1b92db4370bc29e64d30464dab80fb9'}
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement under the original economic law. Attained continuations retain action witnesses and an original-optimum error account. Shared-parameter qualification transfers to complete multi-date policies through endogenous occupations and contingent patterns. A joint state-context construction supplies one neural circuit with uniform guarantees under explicit primitive and acquisition conditions. Signed transition qualification extends the original-optimum account to recursive preferences, including tail-risk and entropic evaluations, while retaining the direction and date of approximation error. Stored continuations and coupled residual--transition precision allocation provide a separate horizon-resource account. Prospective selection and uniform price-fee regions connect qualification with economic decisions. Independent investment evaluation identifies policy-cost improvements and noninferiority while retaining unresolved comparisons. A frozen shared-proposal study finds no incremental ReLU query-work advantage. Diffusions, endogenous preferences, temporal selves and games retain their original hypotheses and comparison principles.'''
PARAGRAPH=r'''\paragraph{Signed qualification under the original preference primitive.}
A common continuation allows policy loss to be charged to the difference between a selected-action upper discrepancy and an all-action lower discrepancy. Section~\ref{sec:risk91} proves this signed account for complete policies under monotone cash-invariant recursive evaluations. It supplies explicit Wasserstein allowances for average value at risk and entropic evaluation rather than transferring the expectation coefficient without proof. Global constant bias cancels, whereas state-dependent bias can affect future choices and must remain charged. Sharp examples distinguish these cases and prevent a static tail-risk objective from being silently replaced by a nested one. Local risk sensitivity enters the dated precision budget without an unjustified product of later tail multipliers; the actual continuation moduli and their construction costs remain explicit.

'''
CONCLUSION=r'''
Signed qualification further separates a harmless global offset from a state-dependent approximation that changes complete-policy incentives. The recursive order proof retains the original preference primitive, and the explicit tail-risk and entropic moduli price transition information at the stated economic accuracy. Its sharpness examples and exhaustive finite-policy diagnostics support verification without being counted as new economic observations. This extends the original NBO argument while leaving empirical algorithm comparisons, application-specific prices and the largest vector reimplementation as distinct evidence requirements.

'''

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def blob(p):
    b=Path(p).read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def save(p,x):
    p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def bibliography():
    chosen={};order=[];duplicates=[];sources={}
    for name in ('references.bib','references78.bib','references84.bib','references90.bib','references91.bib'):
        text=(R/name).read_text();sources[name]=sha(R/name)
        starts=list(re.finditer(r'(?m)^\s*@\w+\s*\{\s*([^,\s]+)',text))
        for i,m in enumerate(starts):
            key=m[1];entry=text[m.start():starts[i+1].start() if i+1<len(starts) else len(text)].strip()
            if key in chosen:
                old,origin=chosen[key]
                doi=lambda s:re.search(r'\bdoi\s*=\s*\{([^}]+)\}',s,re.I)
                x,y=doi(old),doi(entry)
                if old!=entry and not (x and y and x[1].lower()==y[1].lower()):
                    raise AssertionError('Ambiguous duplicate bibliography key '+key)
                duplicates.append({'key':key,'kept_source':origin,'also_in':name,'kept':old,'duplicate':entry})
            else:chosen[key]=(entry,name);order.append(key)
    (R/'references91-canonical.bib').write_text('\n\n'.join(chosen[k][0] for k in order)+'\n')
    save('audit/BIBLIOGRAPHY91.json',{'status':'passed','entries':len(order),'source_hashes':sources,
         'canonical_sha256':sha(R/'references91-canonical.bib'),'duplicates':duplicates,
         'scope':'All original .bib files retained unchanged. Only the active citation-key catalogue is canonicalized; duplicates must be identical or share the same DOI.'})

def main():
    if r'\input{sections/risk91}' in (R/'ECTA.tex').read_text():
        if not (R/'audit/INTEGRATION91.json').exists():raise AssertionError('Unrecorded partial integration')
        print('Existing ordinary R91 author sources retained; no reauthoring performed.');return
    archive=R/'preserved/R90-entry';archive.mkdir(parents=True,exist_ok=True)
    records={}
    for name,expected in EXPECTED.items():
        p=R/name
        if blob(p)!=expected:raise AssertionError('Unexpected R90 entry point '+name)
        shutil.copy2(p,archive/name);old=p.read_text();new=old.replace('label=e90','label=e91')
        if name=='ECTA.tex':
            new=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+ABSTRACT+'\n\\end{abstract}',new,flags=re.S)
            anchor=r'\paragraph{Reading path.}'
            if new.count(anchor)!=1:raise AssertionError('Introduction anchor')
            new=new.replace(anchor,PARAGRAPH+anchor)
            new=new.replace(r'\input{sections/transport90}',r'\input{sections/transport90}'+'\n'+r'\input{sections/risk91}')
            new=new.replace(r'\bibliographystyle{ecta-fullname}',CONCLUSION+r'\bibliographystyle{ecta-fullname}')
        elif name=='supp.tex':
            new=new.replace(r'\input{sections/proofs90}',r'\input{sections/proofs90}'+'\n'+r'\input{sections/proofs91}')
            new=new.replace(r'\end{abstract}','The signed recursive qualification theorem, sharpness examples and risk-specific transport proofs are included in full.\n'+r'\end{abstract}')
        else:
            new=new.replace(r'\input{sections/evidence90}',r'\input{sections/evidence90}'+'\n'+r'\input{sections/evidence91}')
        new=re.sub(r'\\bibliography\{[^}]+\}',lambda m:r'\bibliography{references91-canonical}',new)
        before=re.findall(r'\\input\{(sections/[^}]+)\}',old);after=re.findall(r'\\input\{(sections/[^}]+)\}',new)
        if any(after.count(x)<before.count(x) for x in before):raise AssertionError('Inherited active section removed')
        p.write_text(new);records[name]={'baseline_git_blob':expected,'sha256':sha(p),'inherited_inputs':before,'current_inputs':after}
    pre=R/'preamble.tex';shutil.copy2(pre,archive/'preamble.tex')
    with pre.open('a') as stream:
        stream.write('\n% Stable current-document identity for clean typesetting reproduction.\n\\ifdefined\\pdfinfoomitdate\\pdfinfoomitdate=1\\fi\n\\ifdefined\\pdfsuppressptexinfo\\pdfsuppressptexinfo=15\\fi\n\\ifdefined\\pdftrailerid\\pdftrailerid{}\\fi\n')
    if (R/'build').is_dir() and not (archive/'inherited-build').exists():shutil.copytree(R/'build',archive/'inherited-build')
    bibliography()
    save('audit/INTEGRATION91.json',{'status':'passed','baseline_commit':BASE,'entries':records,'all_inherited_active_inputs_retained':True,'new_topic':False,'scope_narrowed':False})
    print('R91 ordinary main article, full supplement, appendix and canonical bibliography integrated.')
if __name__=='__main__':main()
