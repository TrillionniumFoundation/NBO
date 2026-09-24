"""Check deterministic scientific identity, then index the published papers."""
from pathlib import Path
import hashlib,json,os,subprocess,re,gzip
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
PARENT='88015b77a0c26e7b883156410b684b229fd7e86f'
BRANCH='revision/econometrica-r34-verified-policy-frontier-2026-09-24'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact_identity():
    expected=json.loads((R/'EXPECTED_EXACT.json').read_text())
    checked={}
    for rel,target in expected['canonical_certificate_sha256'].items():
        data=gzip.decompress((R/rel).read_bytes());actual=hashlib.sha256(data).hexdigest()
        assert actual==target,('scientific certificate changed',rel,actual,target)
        checked[rel]=actual
    for rel,target in expected['frozen_input_sha256'].items():
        assert sha(ROOT/rel)==target,('frozen input changed',rel)
    assert len(checked)==294
    result={'passed':True,'exact_certificates_matching_local_reference':len(checked),
            'input_files_checked':len(expected['frozen_input_sha256']),
            'reference':'Locally constructed and independently checked before remote reproduction; timings and PDF metadata are not part of scientific equality.'}
    (R/'results/EXACT_REPRODUCTION_CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True))
    return result

def main():
    identity=exact_identity()
    summary=json.loads((R/'results/summary.json').read_text());restart=json.loads((R/'results/restart_summary.json').read_text())
    audit=json.loads((R/'results/restart_independent_audit.json').read_text())
    preserve=json.loads((R/'PRESERVATION_MAP.json').read_text());boundary=json.loads((R/'results/boundary_recheck.json').read_text())
    assert summary['passed']==42 and audit['passed'] and audit['total_certificates']==294 and restart['strictly_tightened']==22
    assert preserve['main_lossless_after_recorded_path_updates'] and boundary['certified']
    artifacts=[]
    for stem in ('ECTA','SUPP','RESPONSE','COMPUTATION','HISTORY'):
        p=ROOT/f'{stem}_R34.pdf';info=subprocess.check_output(['pdfinfo',str(p)],text=True)
        pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
        artifacts.append({'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'pages':pages,'source':f'{stem}_R34.tex'})
    assert artifacts[0]['pages']<=45,'main article exceeds the editorial page target'
    source_files=[p for p in R.rglob('*') if p.is_file() and p.suffix in ('.py','.tex','.md','.sh') and 'build' not in p.parts]
    sources={str(p.relative_to(ROOT)):sha(p) for p in source_files}
    m={'revision':'R34','parent_commit':PARENT,'source_referee_commit':'e9bc144fbb6843d6a3436825a28584efb64fb8f1',
       'protocol_commit':'70526abec87eeadd52dd7b30eaf75a78ba70e79c',
       'build_source_commit':os.environ.get('GITHUB_SHA','local-prepublication-check'),
       'branch':BRANCH,'workflow_run':os.environ.get('GITHUB_RUN_ID'),
       'publication_artifacts':artifacts,'source_sha256':sources,'support_summary':summary,'restart_summary':restart,
       'exact_reproduction':identity,'boundary_rational_recheck':boundary['certified'],
       'journal_style_sha256':{name:sha(ROOT/name) for name in ('econsocart.cls','econsocart.cfg')},
       'preservation':'Full previous main and supplement retained; five previous PDFs included unchanged in HISTORY_R34; staged R33 transfer archive unchanged.',
       'remaining_scopes':'30 positive global cost gaps remain. No newly proved neural-specific speed advantage, high-dimensional scaling, measured deployment amortization, or full stopped-feedback certificate.'}
    (R/'PUBLICATION_MANIFEST.json').write_text(json.dumps(m,indent=2,sort_keys=True))
    lines=['# R34 referee reading entry','',
      '**Certified Bellman Operators with Neural Proposals: All-Restart Bounds for Costly Policy Revision**','',
      'Based on the complete latest available R30 report, the executed R32 record, and the staged R33 source archive. This branch contains a fresh exact execution and a new theorem and experiment exploiting simultaneous operating feasibility at every restart.',
      '', '## Documents','']
    for a in artifacts:lines.append(f'- [{a["path"]}]({a["path"]}) — {a["pages"]} pages; [LaTeX source]({a["source"]}).')
    lines+=['','## New theorem and complete audit',
      'The new restart-propagated certificate constructs a global cost lower bound from two-sided operating witnesses and unrestricted support values. It retains every action, covers randomized Markov rules, states the precise feasible-history extension, and is checked using whole-cell inequalities and exact proof selectors without invoking the envelope optimizer.',
      '', '**294 independently checked certificate objects:** 168 support solves, 42 freshly reconstructed class controls, 42 primal-dual summaries, and 42 new propagated bounds. All 42 deployments satisfy their unchanged operating tolerance and preserve installed returns. All 18 installed-neural cases reduce cost relative to the class minimum. The new propagation tightens 22 global intervals and leaves 20 unchanged, with no extra unrestricted support solve. Twelve spline cases have exact zero cost and global gap; none of the 30 previously positive gaps is claimed closed.',
      '', 'The largest absolute tightening is for horizon 12, epsilon .01, installed seed 31003: the integrated lower bound rises by approximately .261684 while the upper deployment is unchanged. All 42 rows, including zero improvements, and all 28 malformed-certificate tests are retained. Finite-tree tests include randomized mixtures. Remote publication must reproduce all 294 canonical certificate hashes from the locally audited reference.',
      '', 'The original stopped-control all-domain .01 objective and full scalar-boundary proof remain intact. Rational boundary inequalities are rerun; endpoint quadrature is inherited, not relabeled. Neural-specific speedup and the all-domain stopped-feedback target are not claimed as newly solved.',
      '', '## Reading and replication',
      'Main theorem: Section 6 (restart propagation); results: the section titled "Computed effect of the restart restriction". The supplement includes the precise feasibility class, checker contract, complete 42-case table, and all prior technical details. The response covers F1–F12 and T1–T10 individually.',
      '', '[Protocol](revisions/2026-09-24-r34/PROTOCOL.md) · [Implementation and provenance](revisions/2026-09-24-r34/IMPLEMENTATION_NOTES.md) · [Publication manifest](revisions/2026-09-24-r34/PUBLICATION_MANIFEST.json) · [Exact reproduction check](revisions/2026-09-24-r34/results/EXACT_REPRODUCTION_CHECK.json) · [Restart results](revisions/2026-09-24-r34/results/restart_summary.json) · [Final independent audit](revisions/2026-09-24-r34/results/restart_independent_audit.json) · [Preservation map](revisions/2026-09-24-r34/PRESERVATION_MAP.json)',
      '', 'Reproduce with `python revisions/2026-09-24-r34/run_study.py`, `python revisions/2026-09-24-r34/run_closure.py`, then the report/build commands in COMPUTATION_R34. All computation uses the Python standard library on fixed installed proposals. Full stage timings, repeated audit costs, and raw exact outputs are recorded.',
      '',f'Frozen parent: `{PARENT}`. Build-source commit: `{m["build_source_commit"]}`. Workflow run: `{m["workflow_run"]}`. The publication commit is the commit containing this index; it is not embedded in a file hashed into itself. Main, review, and previous revision branches are not modified.']
    (ROOT/'R34_REVIEW.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'documents':artifacts,'exact_reproduction':identity},indent=2))
if __name__=='__main__':main()
