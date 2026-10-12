"""Clean full-archive reproduction, immutable evidence and remote R77 staging.

A separate hash-bound visual review is required before final publication.
"""
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,time
import build72 as b
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
HISTORY=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72,73)]
SOURCE='revision/econometrica-nbo-r77-source-2026-10-11';WORK='revision/econometrica-nbo-r77-referee-revision-2026-10-11';READY='revision/econometrica-nbo-r77-review-ready-2026-10-11'

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])

def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE77.json').read_text())
    if release['status']!='passed' or not release['full_retained_replay']:raise AssertionError('Full release build required')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    changed=run(['git','diff','--name-only','HEAD','--',*HISTORY])
    if changed:raise AssertionError('Historical tracked paths changed: '+changed)
    archive_commit=commit('R77: retain complete audited original-paper sources and compiled reading documents')
    paths=HISTORY+[REL]
    with tempfile.TemporaryDirectory(prefix='nbo-r77-archive-') as tmp:
        root=Path(tmp);archive=root/'source.tar'
        with archive.open('wb') as out:subprocess.run(['git','archive',archive_commit,*paths],cwd=REPO,stdout=out,check=True)
        archive_sha=b.sha(archive);archive_bytes=archive.stat().st_size
        subprocess.run(['tar','-xf',str(archive),'-C',str(root)],check=True);archive.unlink()
        copied=root/REL;shutil.rmtree(copied/'build');(copied/'build').mkdir()
        for pattern in ('*72.tex','*73.tex','*77.tex'):
            for path in (copied/'tables').glob(pattern):path.unlink()
        dependency=root/'revisions/2026-10-10-r62/inputs/revisions/2026-10-08-r49/code/service49.py'
        if not dependency.exists():raise AssertionError('Transitive numerical input omitted')
        log=R/'audit/build-logs/clean-rebuild77.log'
        with log.open('w') as out:
            result=subprocess.run([sys.executable,str(copied/'code/build77.py'),'--full'],cwd=copied,stdout=out,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError('Clean archive rebuild failed:\n'+log.read_text()[-18000:])
        rebuilt=json.loads((copied/'audit/RELEASE77.json').read_text())
        if not rebuilt['full_retained_replay'] or rebuilt['total_tests']!=release['total_tests']:raise AssertionError('Clean test set incomplete')
        matches={}
        for first,second in zip(release['documents'],rebuilt['documents']):
            if first['document']!=second['document']:raise AssertionError('Rebuild document order')
            result=dict(pages_equal=first['pages']==second['pages'],text_equal=first['text_sha256']==second['text_sha256'],pdf_bytes_equal=first['sha256']==second['sha256'])
            if not result['pages_equal'] or not result['text_equal']:raise AssertionError(('Rebuild mismatch',first['document'],result))
            matches[first['document']]=result
        b.save(R/'audit/CLEAN_REBUILD77.json',dict(status='passed',archive_commit=archive_commit,archive_sha256=archive_sha,archive_bytes=archive_bytes,
            archived_paths=paths,full_transitive_sources_and_test_data=True,generated_pdfs_and_current_tables_removed=True,
            full_retained_replay=True,total_tests=rebuilt['total_tests'],document_matches=matches,
            new_simulation_rows=0,scientific_service_clocks_replaced=False,network_used_by_builder=False,
            independent_replay=rebuilt['independent_replay'],clean_release=rebuilt,log_sha256=b.sha(log)))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**R77 — original-paper referee revision.**

[Main article](revisions/2026-10-11-r77/build/ECTA.pdf) · [Technical Supplement](revisions/2026-10-11-r77/build/supp.pdf) · [Numerical and Development Appendix](revisions/2026-10-11-r77/build/appendix.pdf) · [Referee response](revisions/2026-10-11-r77/build/response.pdf)

[Revision guide](revisions/2026-10-11-r77/README.md) · [Content preservation](revisions/2026-10-11-r77/CONTENT_MAP77.md) · [Release audit](revisions/2026-10-11-r77/audit/RELEASE77.json)

The same NBO title, author, investment primitives and original Bellman optimum
are retained. R77 qualifies the original-law costs of the actual four attained
continuation constructions. Exact conditional integration, independently
implemented full-bin arithmetic, explicit precision components and priced
controller selection link construction to an economic decision. The fixed new
catalogue and every prior adverse comparison remain separately identified.

All preceding active sections are compiled byte-identically once. Full inherited
and new tests, complete dual-arithmetic cost replay and clean archive reproduction
have passed. Review-ready publication additionally requires the hash-bound PDF
visual record and `revisions/2026-10-11-r77/audit/FINAL_DELIVERY77.json`.
Old revision and review branches are unchanged.

Offline full build: `python3 revisions/2026-10-11-r77/code/build77.py --full`.
''')
    b.save(R/'audit/INHERITED_IMMUTABILITY77.json',dict(status='passed',base_commit='2d7d9c4e62abc2230087f3a092a5c493b8ca6cb0',modified_historical_tracked_paths=[]))
    excluded={'DELIVERY_FILES77.json','STAGED_DELIVERY77.json','FINAL_DELIVERY77.json','VISUAL77.json'}
    files={str(p.relative_to(R)):b.sha(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded}
    b.save(R/'audit/DELIVERY_FILES77.json',files)
    record=dict(status='checks_passed_visual_pending',canonical_branch=READY,source_branch=SOURCE,revision_branch=WORK,
        tested_source_commit=release['tested_source_commit'],archive_commit=archive_commit,total_tests=release['total_tests'],documents=release['documents'],
        new_independent_policy_cost_rows=release['new_independent_policy_cost_rows'],full_bin_trajectories_per_implementation=release['independent_replay']['full_bin_trajectories_per_implementation'],
        files=len(files),delivery_files_sha256=b.sha(R/'audit/DELIVERY_FILES77.json'),workflow_run_id=os.environ.get('GITHUB_RUN_ID'),stage_seconds=time.perf_counter()-start)
    b.save(R/'audit/STAGED_DELIVERY77.json',record)
    sha=commit('R77: stage clean-archive verified manuscript, full evidence and complete policy-cost qualification')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+WORK,'HEAD:refs/heads/'+SOURCE])
    for branch in (WORK,SOURCE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(sha+'\t'):raise AssertionError('Remote staging mismatch')
    print(json.dumps(dict(status='remote_staging_verified',commit=sha,tests=release['total_tests'],documents=release['documents'],visual_pending=True),indent=2))
if __name__=='__main__':main()
