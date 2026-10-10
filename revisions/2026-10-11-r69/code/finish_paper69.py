"""Publication-only corrections after the first complete record audit.

No frozen scientific source or observation changes. Relocated proofs and
tables remain in the supplement and the complete development article.
"""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1]

def change(path,old,new):
    text=path.read_text()
    if old not in text:
        if new in text:return
        raise AssertionError('Missing publication anchor: '+str(path))
    if text.count(old)!=1:raise AssertionError('Repeated anchor')
    path.write_text(text.replace(old,new,1))

def main():
    marker=R/'audit/PUBLICATION_CORRECTIONS69.json'
    if marker.exists():print('Publication corrections already retained.');return
    for name in ('ECTA','supp','complete'):
        p=R/(name+'.tex');text=p.read_text()
        text=text.replace(r'\externaldocument{',r'\externaldocument[][nocite]{')
        p.write_text(text)
    full=R/'sections/study69.tex';text=full.read_text()
    addition=r'''\paragraph{What changed in the measured service.}
In the two-state validation task, the certificate-trained ReLU readouts close 48 and 50 of 256 contexts for the two seeds, compared with 25 and 21 for the coefficient-matched Bernstein readouts. The achieved readout dual gaps are at most $9.9\times10^{-8}$ across the new fitted catalogue. This improvement in one validation metric does not establish a complete-runtime gain. Median ReLU cold-start work is 0.465 seconds against 0.365 for adaptive search in the two-state task, and 1.618 against 0.666 in the eight-state task.

In two-state reuse, ReLU has four final-process wins in eight comparisons and three early persistent crossings; Bernstein has four and four, respectively. None of the three learned reuse methods wins a final eight-state process. These finite timing outcomes retain all repetitions, including baseline variability. In the four-date vector diagnostic, the transferred ReLU proposal uses 872,033 deployed action queries against 592,658 for adaptive refinement, with complete times of 62.014 and 41.366 seconds. The evidence supports achieved certificate-aware fitting and a better context screen in the first task, not a universal neural work advantage.

The new centered intervals are approximately 165--306 times narrower than the ordinary cash-cost intervals on the same path rows. Their extra original-Bellman evaluation is included in the inference service. They resolve the prespecified noninferiority scale, while all still contain zero; strict policy-cost superiority is not identified.
'''
    text=text.replace(r'\input{tables/findings69}',r'\input{tables/findings69}'+'\n'+addition,1)
    full.write_text(text)
    active=text.replace(r'\input{tables/cold69}',r'The full cold-start comparison is in Supplement, Table~\ref{tab:cold69}.')
    active=active.replace(r'\input{tables/vector69}',r'The complete vector work and memory comparison is in Supplement, Table~\ref{tab:vector69}.')
    (R/'sections/study69-print.tex').write_text(active)
    change(R/'ECTA.tex',r'\input{sections/study69}',r'\input{sections/study69-print}')
    centered=(R/'sections/centered69.tex').read_text();proofs=[]
    def retain_proof(match):
        number=len(proofs)+1;label='supp:centered-proof69-'+str(number)
        proofs.append(r'\subsection{Proof '+str(number)+r' for the centered comparison}\label{'+label+'}\n'+match[0])
        return r'\noindent The proof is given in Supplement, Section~\ref{'+label+'}.'
    centered_print=re.sub(r'\\begin\{proof\}.*?\\end\{proof\}',retain_proof,centered,flags=re.S)
    if len(proofs)!=2:raise AssertionError('Expected both centered theorem and precision proofs')
    (R/'sections/centered69-print.tex').write_text(centered_print)
    change(R/'ECTA.tex',r'\input{sections/centered69}',r'\input{sections/centered69-print}')
    supplement=R/'sections/supp69.tex'
    supplement.write_text(supplement.read_text()+'\n'+r'\section{Proofs for the Bellman-centered comparison}\label{supp:centered-proofs69}'+'\n'+'\n\n'.join(proofs)+'\n'+r'\section{Complete cold-start and vector work tables}\label{supp:all-work69}'+'\n'+r'\input{tables/cold69}'+'\n'+r'\input{tables/vector69}'+'\n')
    build=R/'code/build69.py';text=build.read_text()
    old="head=head.replace(r'\\externaldocument{build/ECTA}[ECTA.pdf]','')"
    new="head=head.replace(r'\\externaldocument[][nocite]{build/ECTA}[ECTA.pdf]','').replace(r'\\externaldocument{build/ECTA}[ECTA.pdf]','')"
    if old not in text:raise AssertionError('Response external reference anchor')
    text=text.replace(old,new,1)
    old="        run([sys.executable,'code/audit69.py'],'complete-record-audit69')"
    new=old+"\n        run([sys.executable,'code/independent_inference69.py'],'independent-inference69')\n        independent=json.loads((R/'audit/INDEPENDENT_INFERENCE69.json').read_text())\n        receipt=json.loads((R/'audit/INDEPENDENT_INFERENCE_RECEIPT69.json').read_text())\n        if independent['checked_contrasts']!=12 or independent['status']!='passed' or sha(R/'audit/INDEPENDENT_INFERENCE69.json')!=receipt['reproduced_report_sha256']:\n            raise AssertionError('Independent inference replay differs from retained local receipt')"
    if old not in text:raise AssertionError('Full audit anchor')
    build.write_text(text.replace(old,new,1))
    mapping=R/'CONTENT_MAP69.md';mapping.write_text(mapping.read_text()+'\nThe complete R69 cold-start and vector tables and both Bellman-centered proofs are in `sections/supp69.tex`; the active article references them and retains its theorem statements and quantitative interpretation. All remain inline in the complete development article. Cross-document links import labels without importing bibliography entries. No statement, proof, table, or observation is deleted by this correction.\n')
    audit=json.loads((R/'results69/inference-d2-T2-paired-s6901-r0/summary.json').read_text())
    if len(audit['centered'])!=6:raise AssertionError('Unexpected inference catalogue')
    marker.write_text(json.dumps(dict(status='publication_sources_corrected',initial_run=38078116461,
        initial_publication_issue='Shared Hoeffding citation imported from the supplement into the complete edition; active manuscript 46 pages before relocation',
        corrections=['Use xr-hyper nocite option for external labels','Retain complete work tables and centered proofs in the supplement and complete article','Add actual matched-screen, complete-work and inference-precision interpretation','Run the independent exact-sum/80-digit interval replay in ordinary and clean builds'],
        scientific_sources_modified=False,scientific_records_modified=False,prior_source_preservation_gate_retained=True),sort_keys=True,indent=2)+'\n')
    print('Publication-only corrections applied; frozen science unchanged.')
if __name__=='__main__':main()
