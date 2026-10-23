"""Integrate R96 once; retain every R95 scientific section and failed receipt."""
from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'audit/reproduction96';out.mkdir(parents=True,exist_ok=True)
    if (out/'INTEGRATION96.json').exists():raise RuntimeError('Integration is single-use')
    old=ROOT/'preserved/R95-source';old.mkdir(parents=True,exist_ok=True)
    for n in ('ECTA.tex','supp.tex','appendix.tex','preamble.tex','response.tex','README.md','references92-canonical.bib','RELEASE95.json','SOURCE95.json'):
        if (ROOT/n).exists():shutil.copy2(ROOT/n,old/n)
    before={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'sections').glob('*.tex') if not p.name.endswith('96.tex')}
    main=(ROOT/'ECTA.tex').read_text()
    pre=main.split('\\begin{abstract}')[0]
    abstract=r'''\begin{abstract}
This paper develops Neural Bellman Operators for constructing feasible dynamic policies and bounding their loss against the original economic optimum. Own-future neural construction retains feasible action witnesses and explicit acquisition errors. Under recursive risk, reference-centered qualification gives state-dependent complete-policy comparisons. We derive an executable convex-order AVaR enclosure with second-order innovation resolution, and connect a complete admission-and-fallback policy to simultaneous economic resolving power. A new remotely frozen investment comparison matches design rank, labels and executable payload across ReLU, quadratic and adaptive spline continuations, while charging conventional fallback. The prespecified margin is one percent of the maximal first-date investment charge, with a simultaneous half-width budget below half that margin. The estimand uses a declared dyadic initial-state distribution and the original continuous innovation law. A separate acquisition-and-reuse region identifies which policy, work and price bounds justify deployment. Broader NBO applications and earlier adverse evidence retain their original hypotheses and records.
\end{abstract}
\begin{keyword}
\kwd{Dynamic programming}\kwd{Neural approximation}\kwd{Recursive risk}
\kwd{Policy qualification}\kwd{Computational economics}
\end{keyword}
\end{frontmatter}
'''
    keep=('core49','accuracy62-print','recursive86','risk91','centeredrisk92','continuous95','precision96','study96','complexity86')
    main=pre+abstract+'\\input{sections/introduction96}\n'+''.join('\\input{sections/'+s+'}\n' for s in keep)+'\\input{sections/conclusion96}\n\\bibliographystyle{ecta-fullname}\n\\bibliography{references92-canonical}\n\\end{document}\n'
    (ROOT/'ECTA.tex').write_text(main)
    appendix=(ROOT/'appendix.tex').read_text();moves=('population86','coupled89','prospective86','study95')
    anchor='\\input{sections/frozen72}'
    if anchor not in appendix:raise AssertionError('Inherited appendix entry point changed')
    appendix=appendix.replace(anchor,''.join('\\input{sections/'+s+'}\n' for s in moves)+anchor,1)
    appendix=appendix.replace('\\bibliographystyle{ecta-fullname}','\\input{sections/evidence96}\n\\bibliographystyle{ecta-fullname}')
    (ROOT/'appendix.tex').write_text(appendix)
    supp=(ROOT/'supp.tex').read_text().replace('\\bibliographystyle{ecta-fullname}','\\input{sections/proofs96}\n\\bibliographystyle{ecta-fullname}')
    (ROOT/'supp.tex').write_text(supp)
    bib=(ROOT/'references92-canonical.bib').read_text()
    bib=bib.replace('and Yang, Wenhao','and Yang, Shangzhe').replace('and Zhang, Yiran','and Zhang, Tiangang').replace('Feature-Based Risk-Averse Learning','Reinforcement Learning with Markov Risk Measures and Multipattern Risk Approximation')
    for key,entry in [('hoeffding1963',r'''@article{hoeffding1963,
 author={Hoeffding, Wassily}, title={Probability Inequalities for Sums of Bounded Random Variables},
 journal={Journal of the American Statistical Association}, year={1963}, volume={58}, number={301}, pages={13--30}, doi={10.1080/01621459.1963.10500830}}
'''),('alomari2016hermite',r'''@misc{alomari2016hermite,
 author={Alomari, Mohammad W.}, title={A Generalization of {Hermite--Hadamard}'s Inequality},
 year={2016}, howpublished={arXiv:1603.08045}}
''')]:
        if '{'+key+',' not in bib:bib+='\n'+entry
    (ROOT/'references92-canonical.bib').write_text(bib)
    # The failed R95 ledger remains immutable outside the current copy.
    ledger=ROOT/'audit/PREPARATION72.json';data=json.loads(ledger.read_text())
    shutil.copy2(ledger,old/'PREPARATION72-failed-in-R95.json')
    rec=data['unchanged_active_sections'].pop('sections/core49.tex')
    original=ROOT/'preserved/R95-source/core49-before-amendment.tex'
    if sha(original)!=rec['sha256']:raise AssertionError('Historical core identity does not match failed ledger')
    amended=dict(rec,original_sha256=rec['sha256'],sha256=sha(ROOT/'sections/core49.tex'),original_path=str(original.relative_to(ROOT)),reason='Intentional R95 clarification: earlier expected-cost evidence is distinct from the new explicitly specified nested-risk experiment. Scientific results retained.')
    data['amended_active_sections']={'sections/core49.tex':amended}
    data['statement_preservation']='Every prior active section has exactly one current assignment. Unchanged sections retain their historical hash; explicitly amended sections retain both original and current hashes and reasons.'
    ledger.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    test=ROOT/'code/tests_publication72.py';shutil.copy2(test,old/'tests_publication72.py')
    source=test.read_text();start=source.index('    def test_every_prior_active_section_has_one_assignment(self):');end=source.index('    def test_new_theorem_proofs_and_reference_keys(self):',start)
    replacement='''    def test_every_prior_active_section_has_one_assignment(self):
        import hashlib
        a=json.loads((R/'audit/PREPARATION72.json').read_text())
        unchanged=a['unchanged_active_sections'];amended=a.get('amended_active_sections',{})
        self.assertFalse(set(unchanged)&set(amended))
        original=json.loads((R/'preserved/R95-source/PREPARATION72-failed-in-R95.json').read_text())
        self.assertEqual(set(unchanged)|set(amended),set(original['unchanged_active_sections']))
        for path,record in dict(unchanged,**amended).items():
            count=sum((R/(doc+'.tex')).read_text().count('\\\\input{'+path[:-4]+'}') for doc in ('ECTA','supp','appendix'))
            self.assertEqual(count,1)
            self.assertEqual(hashlib.sha256((R/path).read_bytes()).hexdigest(),record['sha256'])
            if path in amended:
                self.assertTrue(record['reason'])
                self.assertEqual(record['original_sha256'],original['unchanged_active_sections'][path]['sha256'])
                self.assertEqual(hashlib.sha256((R/record['original_path']).read_bytes()).hexdigest(),record['original_sha256'])
'''
    test.write_text(source[:start]+replacement+source[end:])
    current='\n'.join((ROOT/(doc+'.tex')).read_text() for doc in ('ECTA','supp','appendix'))
    previous='\n'.join((old/(doc+'.tex')).read_text() for doc in ('ECTA','supp','appendix'))
    prior_inputs=re.findall(r'\\input\{(sections/[^}]+)\}',previous)
    checks={name:current.count('\\input{'+name+'}')==1 for name in prior_inputs}
    if not all(checks.values()):raise AssertionError('An inherited scientific section lost its assignment')
    if any(sha(ROOT/p)!=v for p,v in before.items()):raise AssertionError('An inherited scientific section changed')
    if (ROOT/'build').exists():shutil.move(str(ROOT/'build'),str(old/'compiled-R95-history'))
    # Current source status only; old releases are historical, never R96 approval.
    record=dict(review_commit='2fcf0bbd5926ee927c14a5f6d122fb50bb420988',reviewed_commit='85263fd95ccbb60f0cf1875c0f29f1b7c2558a34',inherited_section_hashes=before,assignments=checks,relocated_intact=list(moves),all_scientific_sections_unchanged=True,amended_preservation_record=amended)
    (out/'INTEGRATION96.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    (ROOT/'README.md').write_text('''# Neural Bellman Operators — R96

The current revision addresses the R95 report at `2fcf0bbd5926ee927c14a5f6d122fb50bb420988` and descends from its reviewed R95 manuscript. The original NBO title, author, economic primitives and scientific sections remain. The paper adds convex-order risk precision, complete-service admission and prespecified resolving power, a rank/label/payload-matched confirmation, and an acquisition-and-reuse region.

Read `ECTA.tex`, `supp.tex`, `appendix.tex` and `response.md`. The full protocol is `PROTOCOL96.md`; constant-to-code assignments are in `CONSTANTS96.json`. New tables embed the actual confirmation source commit and freeze hash. All prior scientific section files are retained unchanged and assigned exactly once; `audit/reproduction96/INTEGRATION96.json` records that check. The failed R95 preservation declaration is retained under `preserved/R95-source/` and repaired by explicitly distinguishing amended from unchanged source.

The workflow commits ordinary sources and then actual fitted models and calibration before opening a new confirmation stream. The scientific sources cannot change after that freeze. Four current PDFs, when built, are in `build/`. `RELEASE96.json` records actual gates; an old release or a submitted job is not R96 approval. The primary experiment remains scalar-control and two-date. No full largest-vector execution, field-calibrated monetary welfare claim or universal neural superiority is asserted.

From this directory: `python code/run_tests95.py --output-dir audit/reproduction96/tests`, `python code/build95.py --audit-dir audit/reproduction96/build`. Frozen confirmation can be reproduced under a new tag with `python code/experiment96.py evaluate --tag replay`; the same stream adds no independent observations. Run from a full repository checkout because historical suites require original repository fixtures outside this directory.
''')
    print(json.dumps({'inherited_sections':len(before),'assigned':len(checks),'relocated':moves,'status':'integrated'},indent=2))
if __name__=='__main__':main()
