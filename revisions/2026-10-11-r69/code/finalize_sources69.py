"""Finalize ordinary publication sources without changing frozen science."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]
SCIENCE='c8c420763a36e8da41a34b0187d7160f1c323952'
REVIEW='4b27b56f4514f6c1d77b69fe707f7202f8b06b19'
PAPER='eacd3e217ae1e2e9ea6e154b48da7d103159d051'

def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def edit(file,old,new):
    text=file.read_text()
    if old not in text:
        if new in text:return
        raise AssertionError('Publication anchor missing: '+str(file))
    if text.count(old)!=1:raise AssertionError('Repeated publication anchor')
    file.write_text(text.replace(old,new,1))
def main():
    edit(R/'sections/operational67.tex',
         'The service comparison below retains the preregistered L-BFGS and conventional fits, rather than relabeling those models as minimizers of '+r'\eqref{eq:readout-loss67}'+'.',
         'The preceding R67 comparison, reproduced in the complete development companion, retains its original L-BFGS and conventional fits. Section~'+r'\ref{sec:training69}'+ ' now adds separately executed fixed-feature readouts under '+r'\eqref{eq:readout-loss67}'+', without relabeling the earlier models.')
    edit(R/'sections/vector67.tex',
         'The two-control execution is a verified extension of the NBO query backend, not evidence for a trained two-output selector.',
         'The preceding two-control execution is a verified extension of the NBO query backend, not evidence for a trained two-output selector. The new comparison in Section~'+r'\ref{sec:study69}'+ ' separately evaluates trained two-output proposals under this unchanged certificate.')
    edit(R/'sections/centered69.tex',
         r'If $L_Q,L_V$ are state Lipschitz bounds and $\rho$ bounds $\|x-\bar x\|$, then',
         r'If $L_Q,L_V$ are state Lipschitz bounds in the $\ell_1$ norm and $\rho$ bounds $\|x-\bar x\|_1$, then')
    build=R/'code/build69.py';text=build.read_text()
    text=text.replace("for x in contrasts:extra+=f\"| d={x['d']}, T={x['T']} | {x['contrast']} | [{x['interval'][0]:.8f}, {x['interval'][1]:.8f}] |\\n\"",
        "from tables69 import interval as displayed_interval\n    for x in contrasts:extra+=f\"| d={x['d']}, T={x['T']} | {x['contrast']} | {displayed_interval(x['interval'])} |\\n\"")
    if 'from tables69 import interval as displayed_interval' not in text:raise AssertionError('Outward response interval display missing')
    build.write_text(text)
    frozen=json.loads((R/'audit/SOURCE_FREEZE69.json').read_text())
    checked={}
    for name,digest in frozen['source_sha256'].items():
        path=str((R/name).relative_to(REPO));raw=git('show',SCIENCE+':'+path)
        if sha(raw)!=digest or sha((R/name).read_bytes())!=digest:raise AssertionError('Prepared scientific-source identity: '+name)
        checked[name]=digest
    prior='revisions/2026-10-10-r67'
    old_tree=git('rev-parse',PAPER+':'+prior).decode().strip()
    current_tree=git('rev-parse','HEAD:'+prior).decode().strip()
    if old_tree!=current_tree:raise AssertionError('Original R67 subtree changed')
    report=git('show',REVIEW+':reviews/2026-10-11-econometrica-numerical-methods-r67/referee_report.md')
    (R/'inputs').mkdir(exist_ok=True);(R/'inputs/referee-r67.md').write_bytes(report)
    record=dict(review_commit=REVIEW,reviewed_manuscript_commit=PAPER,report_sha256=sha(report),
        prepared_and_tested_scientific_commit=SCIENCE,
        recorded_freeze_source_commit=frozen['source_commit'],
        recorded_freeze_field_meaning='Workflow trigger commit; preparation generated ordinary vector source and applied the declared outward-support fix before testing and creating the freeze. The prepared commit, not the trigger, contains all frozen blobs.',
        scientific_blob_hashes_verified_at_prepared_commit=checked,
        executed_evidence_commit=git('rev-parse','refs/remotes/origin/r69-executed').decode().strip(),
        prior_r67_subtree_sha=old_tree,prior_r67_subtree_unchanged=True,
        frozen_manifest_sha256=sha((R/'audit/SOURCE_FREEZE69.json').read_bytes()))
    (R/'audit/INPUT_BINDINGS69.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    (R/'inputs/LITERATURE69.md').write_text('''# Verified additional primary reference

Nan Jiang and Lihong Li (2016), Doubly Robust Off-policy Value Evaluation for
Reinforcement Learning. Proceedings of the 33rd International Conference on
Machine Learning, Proceedings of Machine Learning Research 48, 652–661.
Primary publisher record: https://proceedings.mlr.press/v48/jiang16.html

The R69 text distinguishes its paid original-optimum interval calculation
from off-policy importance weighting and does not claim priority for sequential
value-based variance reduction. The inherited bibliography is preserved.

Econometric Society author-information page:
https://www.econometricsociety.org/publications/econometrica/information-authors
The article uses the retained econsocart source, author–year citations, complete
proofs and a separate technical supplement. The inherited 45/25-page publication
targets are checked by the builder; successful typesetting is not editorial
acceptance or a complete visual inspection.
''')
    print(json.dumps(dict(status='publication_sources_bound',scientific_commit=SCIENCE,review=REVIEW,prior_tree=old_tree),indent=2))
if __name__=='__main__':main()
