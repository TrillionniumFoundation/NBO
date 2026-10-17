"""Integrate ordinary R81 sources; preserve every original wrapper and section."""
from pathlib import Path
import json,re
from prepare81 import sha,save
R=Path(__file__).resolve().parents[1]
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement. Attained continuations retain action witnesses and an original-optimum error account. We derive representation-calibrated residual qualification and exact action-switch certificates that transfer policy-cost conclusions to classes of optimization outputs. A prospective nonlinear-investment study compares nine complete controllers under the original continuous law. Calibrated qualification improves both ReLU and Bernstein constructions, while reversing their earlier matched cost ordering. Independently implemented whole-bin evaluation identifies the gains and conditional purchase regions. Three fixed-label optimization problems have complete action-stable minimizer classes, which inherit their attained-policy intervals without further sampling. Recursive query, vector-control, predictable evaluation and deployment-allocation results retain their assumptions and evidence. The numerical comparison identifies the effect of specified constructions and qualification rules, not universal neural dominance.'''
INTRO=r'''A continuation approximation matters because it produces an economic decision. Prediction error, original-optimum policy loss and the resources required to verify that loss are different objects. This paper connects them through a constructive Neural Bellman Operator (NBO), its attained own-future continuation and the complete feasible controller that is implemented under the original economic law.

The operator first fits each date against its own attained future and retains feasible action witnesses. Its affine--ReLU realization and primitive error budget do not require an unrestricted nonconvex optimizer to succeed. A complementary recursive implementation queries the original Bellman problem at the states needed by action search. Primitive curvature, verified endpoint bounds and protected conventional refinement determine its validity; a trained proposal changes only optional query locations. This distinction separates the constructive neural continuation from the performance of a neural warm start.

A qualified shallow continuation can be evaluated without the original-value descendant tree. Its residual oscillation and implemented greedy gaps control original-optimum policy loss, while exact conditional feature integration supplies the evaluation primitives. Fixed-label qualification readouts have finite optimization certificates. Purchased Bellman information can also be reused subject to verified state displacement, capacity repair, retention and precision contracts. These constructions are retained together with their actual work accounts; the absence of a tensor state table does not erase horizon dependence.

We address two additional questions about the attained continuation. First, does a qualification bound charge a common represented function consistently across bases? Coefficientwise bounds can differ even on identical affine functions. We construct derivative-control qualification that is exact on the affine intersection of the ReLU and Bernstein classes and retains the original residual and policy-loss account. The construction is convex and admits exact primal--dual checks. It does not assert that the nonlinear function classes or their numerical conditioning are identical.

Second, can the economic conclusion survive changes in the numerical optimizer's output? For each robust alternative action, a rational dual certificate bounds the qualification objective required to change the implemented choice. A strict lower barrier certifies the action throughout an entire objective sublevel. With a fixed terminal actor in the two-date construction, this yields a complete-policy and original-law cost statement. Partially certified covers instead give an explicit cost enlargement through their initial-law probability. This is an optimization-to-policy transfer, not a fitting-seed success probability.

The prospective factorial experiment fixes both bases, both qualification rules and both observation resolutions before evaluating nine complete controllers. Both own-future fits are constructed under the declared rule. Two independent whole-bin implementations and exact rational checks qualify the continuous-law cost observations. The calibration improves the attained ReLU and Bernstein policies, but their matched ranking reverses. The earlier ReLU advantage under coefficientwise qualification and the new Bernstein advantage under calibrated qualification are both retained. The comparison identifies an operational qualification mechanism rather than attributing a ranking to a representation name.

The attained-cost event also supports conditional economic choices. Joint marginal and paired intervals have sharp difference-constraint and deployment-allocation interpretations. Where action stability holds throughout a readout class, the same cost intervals and conditional charge regions apply to that class without a new union bound over optimizers. Monetary decisions still require a loss scale, deployment count and resource charges; the experiment does not invent those inputs or count simulation rows as economic deployments.

\paragraph{Relation to existing methods.}
Lipschitz extensions and distance transforms underlie the constructive envelope \citep{mcshane1934,felzenszwalb2012}. Approximate and safe policy iteration have established error analyses \citep{munos2003,pirotta2013,scherrer2015}, as does convex dynamic-programming approximation \citep{yang2020convex}. Learned warm starts and optimization-based control supply related numerical methods \citep{sakaue2023warm,sambharya2023,agrawal2020control}. We retain these connections without claiming that a common verifier establishes the incremental value of its neural proposal.

Value-function control variates and telescoping identities are established evaluation tools \citep{munos2006variance,jiang2016}. Time-uniform concentration and off-policy confidence sequences have their own theory \citep{howard2020time,karampatziakis2021}. Our original-law costs include the numerical qualification required to use such bounds for an implemented controller. Minimax-regret decisions have an established economic role \citep{manski2004}; shortest-path difference constraints are classical \citep{floyd1962}. The new transfer identifies when the paid attained-policy evidence remains valid for an entire qualification sublevel, using exact robust-action switch barriers rather than an unobserved distance to the optimizer.

\paragraph{Reading path.}
The article develops the original operator, attained-continuation qualification, optimization-stable policies, predictable evaluation and actual economic costs. The Technical Supplement retains the core proofs. The Numerical and Development Appendix compiles the recursive query, pre-query readout, vector-control and historical evidence sections without alteration, together with all new dual proofs and factorial records. Historical companion editions retain diffusions, recursive and endogenous preferences, temporal selves and games under their own hypotheses. Their preservation is not a claim that the present expected-cost identities apply without modification to those different objectives.
'''
CONCLUSION=r'''Neural Bellman Operators connect attained continuation construction to feasible policy decisions under the original law. The original witness and residual-qualification results provide the policy-loss account. Affine-calibrated derivative bounds make a representation-dependent qualification charge explicit, and rational action-switch barriers extend attained-policy conclusions to stated optimization sublevels.

The prospective factorial comparison identifies policy-cost gains from calibrated qualification in both bases. It also reverses the earlier matched basis ranking, demonstrating why equal feature counts alone do not identify a representation effect. Complete action-stable classes inherit their attained-cost intervals without additional sampling; unresolved cells retain their explicit enlargement. These constructive and economic conclusions do not require a universal neural ordering, a hidden-layer success assumption, or an unmeasured long-horizon speed claim.

The conditional purchase and deployment results use the qualified costs and declared resource charges as separate inputs. Original construction, failed reuse, adverse query timings, vector descendant growth and broader applications remain available with their own assumptions and records. A numerical decision is useful only through the complete chain from an attained approximation to a qualified and economically interpretable policy.
'''

def main():
    done=R/'audit/INTEGRATION81.json'
    if done.exists():print('R81 sources already integrated; not overwriting author edits.');return
    preparation=json.loads((R/'audit/PREPARATION81.json').read_text())
    mainfile=R/'ECTA.tex';text=mainfile.read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
    left=text.index(r'\section{Introduction}');right=text.index(r'\input{sections/core49}')
    text=text[:left]+r'\section{Introduction}\label{sec:introduction65}'+'\n'+INTRO+'\n'+text[right:]
    moved=('sections/query63','sections/operational67','sections/vector67')
    for path in moved:
        needle=r'\input{'+path+'}'
        if text.count(needle)!=1:raise AssertionError('Expected old main section '+path)
        text=text.replace(needle+'\n','',1)
    text=text.replace(r'\input{sections/qualification73}',r'\input{sections/qualification73}'+'\n'+r'\input{sections/calibration81}',1)
    text=text.replace(r'\input{sections/cost77}',r'\noindent The following attained-cost experiment retains the legacy coefficientwise qualification rule. Section~\ref{sec:study81} subsequently tests calibrated qualification on a separately frozen factorial catalogue.'+'\n'+r'\input{sections/cost77}'+'\n'+r'\input{sections/study81}',1)
    left=text.index(r'\section{Conclusion}');right=text.index(r'\bibliographystyle',left)
    text=text[:left]+r'\section{Conclusion}\label{sec:conclusion65}'+'\n'+CONCLUSION+'\n'+text[right:]
    mainfile.write_text(text)
    p=R/'appendix.tex';text=p.read_text();needle=r'\bibliographystyle'
    offset=text.index(needle)
    additions='\n'+r'\section*{Retained recursive and vector constructions}'+'\n'+'\n'.join(r'\input{'+s+'}' for s in moved)+'\n'+r'\input{sections/proof81}'+'\n'
    p.write_text(text[:offset]+additions+text[offset:])
    (R/'response.md').write_text((R/'response81.md').read_text())
    mapping={}
    for path,item in preparation['active_sections'].items():
        occurrences=[]
        for document in ('ECTA','supp','appendix'):
            count=(R/(document+'.tex')).read_text().count(r'\input{'+path[:-4]+'}')
            occurrences.extend([document]*count)
        if len(occurrences)!=1 or sha(R/path)!=item['sha256']:raise AssertionError('Preservation failed '+path)
        mapping[path]=dict(before=item['document'],after=occurrences[0],sha256=item['sha256'])
    save(done,dict(status='integrated',active_sections=mapping,new_sections=['sections/calibration81.tex','sections/study81.tex','sections/proof81.tex'],new_statistical_observations=0))
    lines=['# R81 content and provenance map','', 'Every inherited active section is compiled once with unchanged bytes. The original R80 snapshot wrappers and inherited R79-era PDFs remain in `preserved/R80-snapshot/`. R80 scientific records remain source-bound; R81 adds proofs, independent replay and manuscript integration, not additional independent cost observations.','', '| Section | Previous location | R81 location |','|---|---|---|']
    for name,item in mapping.items():lines.append(f"| `{name}` | {item['before']} | {item['after']} |")
    lines+=['','New main sections: `calibration81.tex`, `study81.tex`. New complete dual/coupling proofs and all 94 estimands: `proof81.tex`. Earlier wrapper labels are retained. The original title and author remain unchanged.']
    (R/'CONTENT_MAP81.md').write_text('\n'.join(lines)+'\n')
    (R/'README.md').write_text('''# Neural Bellman Operators — R81

Ordinary sources: `ECTA.tex`, `supp.tex`, `appendix.tex`, `response.md`.
The corresponding current PDFs are under `build/` only after successful build.

R81 integrates the separately frozen R80 factorial experiment into the original
NBO paper. It adds affine-calibrated qualification, exact action-switch duals,
optimizer-class policy-cost transfer and a complete conditional charge account.
Both calibrated own-controller gains and the reversed matched basis ranking are
reported. Every inherited active section and scientific record is preserved.

The controlling advisory report is R67 (11 October 2026), review commit
`4b27b56f4514f6c1d77b69fe707f7202f8b06b19`. The executed R80 baseline is
`ec8d40a058bfc03a88a62a223559698c5e849b22`.

Full offline build, from a checkout containing the pinned dependency revisions:

    python3 revisions/2026-10-12-r81/code/build81.py

`audit/RELEASE81.json` records current-source tests, complete bin replay, exact
switch verification and typography checks. `audit/CLEAN_REBUILD81.json` records
a separate clean-archive build. `audit/FINAL_DELIVERY81.json` binds the delivered
sources and PDFs only after both pass. Visual inspection, if performed, is a
separate hash-bound record; it is not implied by compilation or text extraction.

`CONTENT_MAP81.md` gives every inherited section's reading location. Old files
in `preserved/` and old-numbered audit files retain their historical provenance.
No new R81 independent policy-cost observations or scientific retiming is claimed.
''')
    print(json.dumps(dict(status='integrated',preserved_sections=len(mapping),abstract_words=len(ABSTRACT.split()),moved_sections=moved)))
if __name__=='__main__':main()
