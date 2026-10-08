"""Bind and publish a clean, fully materialized R48 candidate. No science reruns."""
from __future__ import annotations
import hashlib,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE='3e142dda054f6fd3b9559c0cf2faa658933a2169'
TARGET='revision/econometrica-nbo-r48-review-ready-2026-10-08'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def verify():
    m=json.loads((R/'publication/PAPER_SOURCE_SHA256.json').read_text())
    for group in ('inputs','assembled_sources'):
        for name,digest in m[group].items():assert H(R/name)==digest,name
    files=json.loads((R/'audit/FILES_SHA256.json').read_text())
    for name,digest in files.items():assert H(R/name)==digest,name
    sci=json.loads((R/'audit/EXECUTION_COMPLETE.json').read_text())
    for group in ('source_hashes','result_hashes'):
        for name,digest in sci[group].items():assert H(R/name)==digest,name
    release=json.loads((R/'audit/RELEASE_AUDIT.json').read_text())
    assert release['total_tests']==96 and all(t['passed'] for t in release['tests'].values())
    for doc in release['compilation']:
        assert all(doc[k]==0 for k in ('undefined_references','duplicate_labels','missing_characters','overfull_boxes'))
        assert H(R/'build'/(doc['document']+'.pdf'))==doc['pdf_sha256']
    return release,len(files)
def main():
    release,file_count=verify()
    source=git('rev-parse','HEAD')
    check=subprocess.run(['git','ls-remote','--exit-code','--heads','origin',TARGET],cwd=ROOT,stdout=subprocess.PIPE,text=True)
    assert check.returncode==2,'Target exists, or remote query failed; no overwrite permitted'
    assert H(R/'audit/REVIEWED_R47_REPORT.md')==H(ROOT/'reviews/2026-10-08-econometrica-numerical-methods-r47/referee_report.md')
    (ROOT/'ECTA.tex').write_text('\\input{revisions/2026-10-08-r48/ECTA.tex}\n')
    (ROOT/'supp.tex').write_text('\\input{revisions/2026-10-08-r48/supp.tex}\n')
    (ROOT/'README.md').write_text('''# Neural Bellman Operators

## Authoritative referee revision: R48

The complete revision is on `revision/econometrica-nbo-r48-review-ready-2026-10-08`. This is a revision of the original paper by Qian QI, not a replacement subject.

[Main article](revisions/2026-10-08-r48/build/ECTA.pdf) | [Technical supplement](revisions/2026-10-08-r48/build/supp.pdf) | [Point-by-point response](revisions/2026-10-08-r48/build/response.pdf).

[Ordinary source and reproduction instructions](revisions/2026-10-08-r48/README.md) | [Release audit](revisions/2026-10-08-r48/audit/RELEASE_AUDIT.json) | [Clean rebuild](revisions/2026-10-08-r48/audit/CLEAN_REBUILD.json) | [Final delivery](revisions/2026-10-08-r48/audit/FINAL_DELIVERY.json).

The exact compiler preserves the same witness policy, including ties. A complete prospective study supplies 44 construction services, 204 rungs, 48 direct constrained-policy contrasts, a priced observation account and full first-crossing work curves. At tolerance 1, witness certifies 12/12 main services and each FVI comparator certifies 6/12. Actual direct costs identify six witness-higher contrasts and no witness-lower contrast; all 48 intervals exclude recouping the predeclared replacement fee in either direction. The error-driven coordinate comparator returns uniform grids on the completed catalogue; it is not presented as an effective nonuniform-adaptation success.

Every R47 main/supplement label and the original theory/application companions remain available. Prior revision and review paths are unchanged, and their adverse observations and publication failures are not rewritten. No universal neural superiority or journal acceptance is asserted.
''')
    git('switch','-c',TARGET)
    git('add','-f','revisions/2026-10-08-r48');git('add','ECTA.tex','supp.tex','README.md')
    assert not git('diff','--cached','--name-only','--diff-filter=D'),'No deletion permitted'
    git('commit','-m','R48: integrated Econometrica manuscript, compiler proofs, decision study and response')
    candidate=git('rev-parse','HEAD')
    subprocess.run([os.environ.get('PYTHON','python'),str(R/'code/clean48.py')],cwd=ROOT,check=True)
    clean=json.loads((R/'audit/CLEAN_REBUILD.json').read_text());assert clean['successful'] and clean['candidate_commit']==candidate
    release,file_count=verify()
    # Fetch exactly the known review commit to compare unchanged historical paths.
    subprocess.run(['git','fetch','--no-tags','--filter=blob:none','--depth=1','origin',BASE],cwd=ROOT,check=True)
    changed=git('diff','--name-only',BASE,'HEAD').splitlines()
    allowed=lambda n:n.startswith('revisions/2026-10-08-r48/') or n.startswith('.github/workflows/nbo-r48-') or n in ('ECTA.tex','supp.tex','README.md')
    assert all(allowed(n) for n in changed),[n for n in changed if not allowed(n)]
    assert not git('diff','--name-only','--diff-filter=D',BASE,'HEAD')
    save(R/'audit/FINAL_DELIVERY.json',{'revision':'R48','review_commit':BASE,'reviewed_source_commit':'27f3c36984f00ff060d0586712a01b87355914ba','protocol_commit':'ce166e6feb49796bbc60670bcc36201eec07837b','scientific_source_commit':'53e4eff391bd4b6e035981c7fbb96df1aeff0e54','scientific_evidence_commit':'1aba28ca9aada2d28aa3ce2118c9bfbf769234c5','study_run':37712096165,'study_artifact':11523019602,'study_artifact_sha256':'9ac1f57b4e4b899594029e775c1f1c9e921ad943490e85481badedcd5d722bbc','publication_input_commit':source,'candidate_commit':candidate,'publication_run':os.environ.get('GITHUB_RUN_ID'),'target_branch':TARGET,'manifest_files_verified':file_count,'tests':96,'clean_rebuild':clean,'compiled_documents':release['compilation'],'changed_paths_from_review':changed,'historical_paths_unchanged':True,'deleted_paths':[],'scientific_execution_repeated':False,'prior_failed_R47_publication_relabelled':False,'journal_or_peer_approval':False,'note':'The final Git commit contains this delivery record. It does not self-embed its own commit hash.'})
    git('add','-f','revisions/2026-10-08-r48/audit/CLEAN_REBUILD.json','revisions/2026-10-08-r48/audit/FINAL_DELIVERY.json','revisions/2026-10-08-r48/audit/clean-rebuild.log')
    git('commit','-m','R48: bind successful offline clean rebuild and complete immutable delivery')
    final=git('rev-parse','HEAD')
    assert not git('status','--porcelain','--','revisions/2026-10-08-r48'),'Uncommitted revision files'
    subprocess.run(['git','push','origin','HEAD:refs/heads/'+TARGET],cwd=ROOT,check=True)
    remote=git('ls-remote','--heads','origin',TARGET).split()[0];assert remote==final
    print(json.dumps({'target_branch':TARGET,'commit':final,'candidate':candidate,'tests':96,'clean_rebuild':True},indent=2))
if __name__=='__main__':main()
