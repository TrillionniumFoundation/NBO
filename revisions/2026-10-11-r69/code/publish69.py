"""Publish only after complete audit and clean offline archive reproduction."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
REV='revision/econometrica-nbo-r69-referee-revision-2026-10-11'
SOURCE='revision/econometrica-nbo-r69-source-2026-10-11'
READY='revision/econometrica-nbo-r69-review-ready-2026-10-11'
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=REPO).returncode:run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])

def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE69.json').read_text())
    if release['status']!='passed':raise AssertionError('Build not passed')
    tested=run(['git','rev-parse','HEAD']);archive=commit('R69: retain complete audited results and compiled original-paper revision')
    paths=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[REL]
    log=R/'audit/build-logs/clean-rebuild69.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r69-clean-') as tmp:
        root=Path(tmp);bundle=root/'source.tar'
        with bundle.open('wb') as f:subprocess.run(['git','archive',archive,*paths],cwd=REPO,stdout=f,check=True)
        subprocess.run(['tar','-xf',str(bundle),'-C',str(root)],check=True)
        copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for p in (copy/'tables').glob('*69.tex'):p.unlink()
        for name in ('RESULT_AUDIT69.json','RELEASE69.json','TESTS69.json'):(copy/'audit'/name).unlink(missing_ok=True)
        with log.open('w') as out:
            result=subprocess.run([sys.executable,str(copy/'code/build69.py')],cwd=copy,stdout=out,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError('Clean archive build failed:\n'+log.read_text()[-9000:])
        clean=json.loads((copy/'audit/RELEASE69.json').read_text())
        old={d['document']:d for d in release['documents']};new={d['document']:d for d in clean['documents']}
        matches={name:dict(pages=old[name]['pages']==new[name]['pages'],text=old[name]['text_sha256']==new[name]['text_sha256'],pdf_bytes=old[name]['sha256']==new[name]['sha256']) for name in old}
        if not all(v['pages'] and v['text'] for v in matches.values()):raise AssertionError(matches)
        if clean['tests']['total']!=release['tests']['total']:raise AssertionError('Clean test count changed')
        save(R/'audit/CLEAN_REBUILD69.json',dict(status='passed',archive_commit=archive,document_matches=matches,
            clean_release=clean,log_sha256=sha(log),network_used=False,scientific_services_rerun=False,
            removed_generated_pdfs_tables_audit_and_tests=True))
    (R/'README.md').write_text('''# Neural Bellman Operators — R69

The active referee package consists of [the article](build/ECTA.pdf),
[technical supplement](build/supp.pdf), and [point-by-point response](build/response.pdf).
The [complete development article](build/complete.pdf) retains the whole R67
article and adds the full new derivations. The original title, economic model,
constructive continuation, prior statements and adverse evidence are unchanged.

The source and result identities are in `audit/INPUT_BINDINGS69.json`,
`audit/SOURCE_FREEZE69.json` and `audit/FINAL_DELIVERY69.json`.
The audit retains every one of the 188 predeclared service receipts, including
failures. Exact achieved readout gaps, independent context validation, 64-block
reuse, Bellman-centered original-policy cost inference and two-control
comparisons have distinct records. Independent rational mid-bin path checks
are not described as complete reintegration of every large Bellman tree.

Ordinary source files are `ECTA.tex`, `supp.tex`, `complete.tex`, `response.md`,
`sections/`, and `code/`. Run `python3 code/build69.py` from this directory to
replay and rebuild with the checked dependencies. No scientific services,
training or new policy-cost samples are created by that builder. Its dependency
roots are the unchanged sibling R62–R67 directories.

The relocation map is `CONTENT_MAP69.md`. Prior broader NBO development remains
in `../2026-10-10-r67/build/complete62.pdf` and its corresponding companions.
The full previous study is included unchanged in the complete R69 article.

The normalized noninferiority margin is a prespecified decision tolerance, not
an estimated monetary calibration. Numerical precision, strict superiority,
complete timing advantage and reliable predictor fitting remain distinct.
''')
    (REPO/'README.md').write_text('''# Neural Bellman Operators

Canonical referee revision: `'''+READY+'''`.

[Main article](revisions/2026-10-11-r69/build/ECTA.pdf) ·
[Technical supplement](revisions/2026-10-11-r69/build/supp.pdf) ·
[Referee response](revisions/2026-10-11-r69/build/response.pdf) ·
[Complete development](revisions/2026-10-11-r69/build/complete.pdf)

[Revision guide](revisions/2026-10-11-r69/README.md) and
[content-preservation map](revisions/2026-10-11-r69/CONTENT_MAP69.md).

R69 develops the original paper with achieved certificate-aware readouts,
independent validation, prospective reuse and original policy-cost inference
at a verified regret scale. Its full audit, process failures and uncertainty
are retained. The source-bound release does not infer neural superiority from
safe return, a smaller certificate, or a confidence interval containing zero.
The prior review, original R67 records, incomplete R68 upload and historical
broader NBO companions remain unchanged on their existing branches.
''')
    # Store small page previews as inspection aids, not as proof of inspection.
    for name in ('ECTA','supp','response'):
        subprocess.run(['pdftoppm','-f','1','-singlefile','-r','100','-png',str(R/'build'/(name+'.pdf')),str(R/'build'/(name+'-page1'))],check=True)
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if any(p.suffix.lower() in FORBIDDEN for p in files):raise AssertionError('Standalone font file in release')
    manifest={str(p.relative_to(R)):sha(p) for p in files if p.name!='FINAL_DELIVERY69.json'}
    final=dict(status='passed',canonical_branch=READY,revision_branch=REV,source_branch=SOURCE,
        tested_publication_source_commit=tested,clean_archive_commit=archive,
        workflow_run_id=os.getenv('GITHUB_RUN_ID'),workflow_head_sha=os.getenv('GITHUB_SHA'),
        source_binding=json.loads((R/'audit/INPUT_BINDINGS69.json').read_text()),
        documents=release['documents'],tests=release['tests'],file_sha256=manifest,file_count=len(manifest),
        scientific_returns=release['scientific_returns'],scientific_failures=release['scientific_failures'],
        clean_archive_rebuild='passed',publication_seconds=time.perf_counter()-start,
        independent_check_scope='All represented new rational mid-bin trajectories and critical primitive tests; not complete independent large-tree reintegration',
        visual_inspection='Preview generation is not a claim of human or model visual inspection')
    save(R/'audit/FINAL_DELIVERY69.json',final)
    for name,digest in manifest.items():
        if sha(R/name)!=digest:raise AssertionError('File changed during final binding: '+name)
    final_commit=commit('R69: publish original-paper referee revision after clean audit and archive reproduction')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+REV,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+READY])
    for branch in (REV,SOURCE,READY):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(final_commit+'\t'):raise AssertionError('Remote ref mismatch '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=final_commit,branches=[REV,SOURCE,READY],tests=release['tests'],documents=release['documents']),indent=2))
if __name__=='__main__':main()
