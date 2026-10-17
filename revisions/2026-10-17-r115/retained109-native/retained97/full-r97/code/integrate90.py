"""Integrate R89 and R90 into ordinary TeX; retain the inherited wrappers verbatim."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]

def sha(data):return hashlib.sha256(data).hexdigest()
def write(path,text):
    p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def replace_once(text,old,new):
    if text.count(old)!=1:raise AssertionError(('Expected unique editorial anchor',old,text.count(old)))
    return text.replace(old,new,1)
def inputs(text):return re.findall(r'\\input\{(sections/[^}]+)\}',text)
def main():
    olddir=R/'preserved/R89-entry-points';olddir.mkdir(parents=True,exist_ok=True)
    records={};old={}
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','README.md','sections/evidence86.tex'):
        p=R/name;q=olddir/name;q.parent.mkdir(parents=True,exist_ok=True)
        if not q.exists():q.write_bytes(p.read_bytes())
        old[name]=q.read_text();records[name]=sha(q.read_bytes())
    article=old['ECTA.tex']
    additions=[('sections/recursive86',['sections/pattern89']),('sections/population86',['sections/transport90']),('sections/complexity86',['sections/coupled89']),('sections/prospective86',['sections/sharedstudy89'])]
    for anchor,new in additions:
        token='\\input{'+anchor+'}'
        article=replace_once(article,token,token+'\n'+'\n'.join('\\input{'+x+'}' for x in new))
    intro=r'''\paragraph{Complete policies, singular transitions and paid precision.}
The common-coefficient restriction is imposed on an entire contingent pattern before its occupation flow is relaxed. This strengthens pairwise compatibility and supplies an exact finite-state limit with a separate continuous-law enclosure error. When transition-probability widths do not shrink, a complementary transport certificate tests the numerical kernel against the stored continuation itself. Its residual-span account bounds complete-policy loss relative to the original Bellman optimum even for singular transition approximations, without imposing continuity on the greedy actor. Residual accuracy and transition precision then enter the same explicit economic error budget, while the coupled resource program retains the cost of evaluating the stored successor.

The frozen shared-proposal experiment tests incremental query work on unseen states and an unseen dimension. It retains its conventional and polynomial comparators and its calibration-selected service. The ReLU proposal does not reduce query work on this catalogue. This direct test is distinct from the joint-domain construction theorem and from the independently evaluated complete-policy cost comparison. The article keeps all three objects separate rather than treating a valid certificate as proof of a computational or economic advantage.

'''
    article=replace_once(article,r'\paragraph{Reading path.}',intro+r'\paragraph{Reading path.}')
    conclusion=r'''
\paragraph{The original law remains the benchmark.}
Pattern-consistent occupations and transport-qualified residuals provide complementary complete-policy guarantees. The former retains shared decisions across the contingent plan; the latter prices the action-value effect of numerical transition approximation, including singular laws. Both extend the original NBO construction and preserve its original-optimum interpretation. Their proofs identify every required regularity, qualification and arithmetic condition. The prospective evidence and coupled accuracy account connect those conditions to measured or explicitly priced resources without replacing unmeasured costs by assumed savings.

'''
    article=replace_once(article,r'\bibliographystyle{ecta-fullname}',conclusion+r'\bibliographystyle{ecta-fullname}')
    article=replace_once(article,r'\bibliography{references,references78,references84}',r'\bibliography{references,references78,references84,references90}')
    # Preserve the original abstract and add only the missing complete-policy scope.
    abstract_add=' The complete-pattern extension retains shared choices before relaxing occupations. A transport-qualified residual-span bound treats singular transition approximations under the original Bellman optimum and enters a coupled residual--transition accuracy budget. A frozen shared-proposal study retains its negative query-work result.'
    article=replace_once(article,r'\end{abstract}',abstract_add+'\n'+r'\end{abstract}')
    article=article.replace('label=e86ECTA','label=e90ECTA')
    write('ECTA.tex',article)
    supplement=old['supp.tex']
    supplement=replace_once(supplement,r'\input{sections/proofs86}',r'\input{sections/proofs86}'+'\n'+r'\input{sections/proofs89}'+'\n'+r'\input{sections/proofs90}')
    supplement=replace_once(supplement,r'\bibliography{references}',r'\bibliography{references,references90}')
    supplement=replace_once(supplement,r'\end{abstract}',' It additionally supplies the full pattern-disaggregation, coupled-successor-cost and original-law transport-qualification proofs, including the stationary discounted extension.\n'+r'\end{abstract}')
    write('supp.tex',supplement.replace('label=e86supp','label=e90supp'))
    appendix=old['appendix.tex']
    appendix=replace_once(appendix,r'\input{sections/evidence86}',r'\input{sections/evidence86}'+'\n'+r'\input{sections/evidence90}')
    appendix=replace_once(appendix,r'\bibliography{references,references78}',r'\bibliography{references,references78,references84,references90}')
    write('appendix.tex',appendix.replace('label=e86appendix','label=e90appendix'))
    evidence=old['sections/evidence86.tex']
    evidence=replace_once(evidence,r'\IfFileExists{tables/all-prospective86.tex}{\input{tables/all-prospective86}}{\par The complete generated table is a required output of the reproduction command; this source state has not yet generated it.}',r'\input{tables/all-prospective86}')
    evidence=replace_once(evidence,r'\IfFileExists{tables/prices86.tex}{\input{tables/prices86}}{\par The breakpoint table is generated from the exact evaluation intervals and is required by the reproduction command.}',r'\input{tables/prices86}')
    write('sections/evidence86.tex',evidence)
    checks={}
    for name in ('ECTA.tex','supp.tex','appendix.tex'):
        previous=inputs(old[name]);current=inputs((R/name).read_text())
        if any(current.count(x)!=1 for x in previous):raise AssertionError(('Lost or repeated inherited active section',name))
        if len(current)!=len(set(current)):raise AssertionError(('Repeated current section',name))
        checks[name]={'previous':previous,'current':current,'all_previous_retained_once':True,'sha256':sha((R/name).read_bytes())}
    allcurrent=[s for v in checks.values() for s in v['current']]
    if len(allcurrent)!=len(set(allcurrent)):raise AssertionError('A substantive section occurs in two current documents')
    if (R/'response90.md').exists():write('response.md',(R/'response90.md').read_text())
    write('audit/INTEGRATION90.json',json.dumps({'status':'passed','preserved_wrapper_sha256':records,'documents':checks,'scope':'Source integration, not numerical execution or PDF approval.'},indent=2,sort_keys=True)+'\n')
    write('CONTENT_MAP90.md','# R90 active content map\n\nThe original title, author, economic primitives and every preceding active substantive section are retained. R89 entry points are preserved verbatim under `preserved/R89-entry-points`.\n\n'+ '\n'.join('## '+name+'\n\n'+'\n'.join('- `'+x+'.tex`' for x in v['current'])+'\n' for name,v in checks.items())+'\nNew main results: complete-pattern occupation (`pattern89`), coupled successor cost (`coupled89`), transport-qualified original-optimum policy accuracy (`transport90`). Full proofs: `proofs89`, `proofs90`. All held-out timing repetitions and exact transport fixtures: `evidence90`. Mandatory economic tables replace two explicitly preserved placeholder branches; no numerical row is deleted.\n')
    print(json.dumps({'status':'passed','active_sections':len(allcurrent),'new_main_sections':4,'new_proof_sections':2}))
if __name__=='__main__':main()
