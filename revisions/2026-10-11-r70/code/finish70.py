"""Final ordinary-source integration of pinned intervening R69 mathematics."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
def write(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
def main():
    marker=R/'audit/INTERVENING_SOURCE70.json'
    if marker.exists():return
    src=R/'inputs/training69.tex';raw=src.read_text()
    blocks=list(re.finditer(r'\\begin\{proposition\}.*?\\end\{proposition\}',raw,re.S))
    proofs=re.findall(r'\\begin\{proof\}.*?\\end\{proof\}',raw,re.S)
    if len(blocks)!=2 or len(proofs)!=2:raise AssertionError('Intervening R69 propositions changed')
    header=r'''\section{Matched readouts and complete recovery}\label{sec:training69}
For $x\in[0,1]^d$, the two fixed feature maps used in the comparison are
\[
 \phi^{\rm R}_{jh}(x)=\frac1d(1-|4x_h-j|)_+,
 \qquad
 \phi^{\rm B}_{jh}(x)=\frac1d{4\choose j}x_h^j(1-x_h)^{4-j},
 \quad 0\le j\le4,
\]
with $1\le h\le d$. Both are nonnegative partitions of unity with $5d$ box readout coefficients. The first is an additive hat basis with an exact ReLU realization; the second is a degree-four Bernstein basis. Both purchase the same verified boundary contexts and approximate action labels, and optimize the same certificate loss. The label-loss control changes the objective, not its hat features. The achieved rational optimization certificate is evaluated after quantization.

\subsection{Complete recovery under a validation law}
The validation design draws each coordinate as $U/2^{16}$, with $U$ uniform on $\{0,\ldots,2^{16}-1\}$. These states are representable by the twenty-four-bit policy acquisition contract, but are not uniform over that finer grid. The following result applies to the declared independent context law and recovery. It does not assert that on-policy recursive states have that law.
'''
    text=header+blocks[0][0]+ '\n'+r'\noindent\emph{Proof.} See Supplement, Section~\ref{supp:retained69-proof1}.'+'\n\n'+r'''The executed validation uses the root-query specialization and records descendant queries separately. It does not fit a runtime model and declare it a valid worst-case endpoint cost. The predictable-deployment result in Section~\ref{sec:deployment70} adds an explicit context-transfer premise and a complete operation account.

\subsection{An additional vector witness}
In the two-control economy a trained, projected and downward-rounded proposal can supply a new evaluated upper witness. Its insertion leaves the triangular lower cover unchanged. The original corner endpoints remain in that cover.
'''+blocks[1][0]+'\n'+r'\noindent\emph{Proof.} See Supplement, Section~\ref{supp:retained69-proof2}.'+'\n'+r'The vector benchmark changes the trained proposal or the choice of a triangle to refine, not the authority of the global lower cover. Its training objective remains action-label loss.'+'\n'
    write(R/'sections/training69-retained70.tex',text)
    prooftext=(R/'sections/proofs70.tex').read_text()+'\n'+r'\section{Retained intervening training results}\label{supp:retained69}'+'\n'
    for j,(block,proof) in enumerate(zip(blocks,proofs),1):
        label=re.findall(r'\\label\{([^}]+)\}',block[0])[0]
        prooftext+=r'\subsection{Proof of Proposition~\ref{'+label+'}}'+r'\label{supp:retained69-proof'+str(j)+'}\n'+proof+'\n'
    write(R/'sections/proofs70.tex',prooftext)
    mainfile=R/'ECTA.tex';text=mainfile.read_text();text=text.replace(r'\input{sections/vector67}',r'\input{sections/vector67}'+'\n'+r'\input{sections/training69-retained70}',1)
    write(mainfile,text)
    for name in ('ECTA','supp'):
        p=R/(name+'.tex');text=p.read_text().replace(r'\externaldocument{',r'\externaldocument[][nocite]{')
        text=re.sub(r'\\ead\[label=[^\]]+\]',lambda m:r'\ead[label=e70'+name+']',text)
        write(p,text)
    # Do not import the article's bibliography or author labels into the response.
    p=R/'code/build70.py';text=p.read_text();anchor="    head=re.sub(r'(\\\\begin\\{abstract\\}).*?(\\\\end\\{abstract\\})'"
    lines=text.splitlines(True);output=[];done=False
    for line in lines:
        if line.startswith('    head=re.sub('):
            output.append("    head=re.sub(r'^\\\\externaldocument[^\\n]*\\n?', '', head, flags=re.M).replace('label=e70supp','label=e70response')\n");done=True
        output.append(line)
    if not done:raise AssertionError('Response assembly anchor')
    write(p,''.join(output))
    for name in ('sections/study70.tex','sections/supp70.tex','response.md'):
        p=R/name;text=p.read_text()
        text=text.replace('new predictor-independent uniform context stream','new predictor-independent context stream drawn uniformly from the sixteen-bit dyadic state grid')
        text=text.replace('These 6,144 context--date observations','These 6,144 method--context--date evaluations')
        text=text.replace('The contexts are predictor-independent and disjoint from fitting.','The contexts are predictor-independent and disjoint from fitting. Each coordinate is drawn uniformly as U/2^16, with integer U from zero to 2^16-1; this finite law differs from both the full twenty-four-bit acquisition grid and the continuous law used for policy-cost inference.')
        write(p,text)
    p=R/'sections/supp70.tex';text=p.read_text()
    note=r'''\paragraph{Exact context law and counting.}
Training and validation coordinates are uniform on the sixteen-bit dyadic grid, not on the continuous state cube or the full twenty-four-bit acquisition grid. Matching methods share these validation draws. The 6,144 method--context--date evaluations are not pooled as 6,144 independent states: every stated validation bound uses its own 256-row record. The separate cost-inference experiment retains the original continuous initial and innovation laws.
'''
    text=text.replace(r'\input{tables/validation70}',note+'\n'+r'\input{tables/validation70}',1);write(p,text)
    # Publish the method-specific screen comparison directly from audited data.
    p=R/'code/tables70.py';text=p.read_text();anchor="    print(json.dumps(dict(tables=8,"
    addition='''    small={kind:sorted((x for x in d['validation'] if x['d']==2 and x['T']==2 and x['kind']==kind),key=lambda x:x['seed']) for kind in ('hat-relu','bernstein4')}
    counts=lambda kind:' and '.join(str(x['screen_returns']) for x in small[kind])
    maxgap=max(F(x['dual_gap_exact']) for x in unique.values())
    if maxgap>F(1,10**7):raise AssertionError('Displayed readout gap bound')
    paragraph='At a fixed purchased-information and coefficient budget, the hat--ReLU readouts close '+counts('hat-relu')+' of 256 small-task validation contexts for the two seeds, compared with '+counts('bernstein4')+' for Bernstein. The achieved exact box dual gaps are at most $10^{-7}$ across the certificate-aware catalogue. This is a method-specific improvement in the declared context screen, not a uniform complete-runtime advantage. All methods and both tasks remain in the supplementary validation table.\\n'
    put('tables/screen-findings70.tex',paragraph)
'''
    if anchor not in text:raise AssertionError('Derived table anchor')
    text=text.replace(anchor,addition+anchor,1);write(p,text)
    p=R/'sections/study70.tex';text=p.read_text().replace(r'\input{tables/cold70}',r'\input{tables/cold70}'+'\n'+r'\input{tables/screen-findings70}',1);write(p,text)
    p=R/'README.md';text=p.read_text().replace('The builder does not fit new scientific policies or add inference rows.','The builder adds no experimental policies or inference rows. Small fitting and simulation calls inside regression tests remain test fixtures, not additions to the scientific catalogue.')
    text+='\nThe intervening R69 training propositions are retained from source commit e709dcce64100b58d2af1a7057eba1f8359a1408. Their exact statements and proofs are preserved; the incomplete R69 publication is not described as a completed predecessor release. For original cross-document links in older PDFs, use the original immutable predecessor directory.\n';write(p,text)
    record=dict(status='passed',intervening_source_commit='e709dcce64100b58d2af1a7057eba1f8359a1408',source_sha256=hashlib.sha256(raw.encode()).hexdigest(),retained_proposition_labels=[re.findall(r'\\label\{([^}]+)\}',b[0])[0] for b in blocks],statement_sha256=[hashlib.sha256(b[0].encode()).hexdigest() for b in blocks],proof_sha256=[hashlib.sha256(p.encode()).hexdigest() for p in proofs],validation_law='Each coordinate uniform on the 16-bit dyadic grid; independent of fitting; shared across matching methods. Cost inference retains the original continuous law.',publication_changes=['Retain both intervening R69 propositions and their proofs','Explicit finite validation law and nonpooled evaluation counts','Independent external labels without imported bibliography','Derived method-specific screen comparison'],scientific_records_modified=False)
    write(marker,json.dumps(record,sort_keys=True,indent=2)+'\n')
    p=R/'CONTENT_MAP70.md';write(p,p.read_text()+'\nThe intervening R69 complete-work and optional-vector-witness propositions are retained verbatim in sections/training69-retained70.tex; their proofs are in sections/proofs70.tex. The full pinned source is inputs/training69.tex.\n')
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
