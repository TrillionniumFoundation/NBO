"""Apply the R14 patch to the exact remote review base, never synthetic history.

Requires normal Git authentication configured outside this program. It neither
accepts nor writes access tokens. Existing revision branch names cause failure.
With --publish, both NEW branches are pushed atomically and verified afterward.
"""
from __future__ import annotations
import argparse,json,subprocess,sys,time
from pathlib import Path
REPO='https://github.com/TrillionniumFoundation/NBO.git'
BASE='857bfeab28ca1b7a7f732edf180126f3ded6b451'
REVIEW='review/econometrica-r13-numerical-methods-2026-09-22-442ef9b'
BRANCH='revision/econometrica-r14-independent-state-audit-2026-09-22'
COPY='revision/econometrica-r14-referee-copy-2026-09-22'

def git(args,cwd=None):
    p=subprocess.run(['git',*args],cwd=cwd,text=True,capture_output=True)
    if p.returncode:raise RuntimeError('git '+ ' '.join(args)+'\n'+p.stdout+p.stderr)
    return p.stdout.strip()

def main(patch:Path,workdir:Path,publish:bool):
    patch=patch.resolve();workdir=workdir.resolve()
    if not patch.is_file():raise FileNotFoundError(patch)
    if workdir.exists():raise FileExistsError('Use a new work directory; existing directories are never overwritten.')
    workdir.mkdir(parents=True);repo=workdir/'NBO';receipt={'state':'not_published','repository':REPO,'required_review_base':BASE,'requested_branches':[BRANCH,COPY]}
    try:
        git(['clone','--no-checkout',REPO,str(repo)])
        if git(['rev-parse',f'origin/{REVIEW}'],repo)!=BASE:raise RuntimeError('Review branch changed; inspect the newer review before publication.')
        for branch in [BRANCH,COPY]:
            if git(['ls-remote','--heads','origin',f'refs/heads/{branch}'],repo):raise RuntimeError('Refusing to overwrite existing branch '+branch)
        # Authorship comes from the user's normal configured Git identity.
        git(['config','user.name'],repo);git(['config','user.email'],repo)
        git(['checkout','-b',BRANCH,BASE],repo)
        git(['apply','--check',str(patch)],repo);git(['apply','--index',str(patch)],repo)
        paths=git(['diff','--cached','--name-only'],repo).splitlines()
        roots={'ECTA_R14.tex','ECTA_R14.pdf','SUPP_R14.tex','SUPP_R14.pdf','R14_REVIEW.md','REVISION_INDEX.md'}
        if any(x not in roots and not x.startswith('revisions/2026-09-22-r14/') for x in paths):raise RuntimeError('Patch modifies a path outside the R14 allowlist.')
        git(['commit','-m','revision(r14): execute neural domain audit, independent certificates and state-price proof'],repo)
        science=git(['rev-parse','HEAD'],repo)
        directory=repo/'revisions/2026-09-22-r14'
        manifest=json.loads((directory/'canonical_manifest.json').read_text())
        original_receipt=json.loads((directory/'publication_receipt.json').read_text())
        (directory/'local_delivery_receipt.json').write_text(json.dumps(original_receipt,indent=2)+'\n')
        manifest['remote_publication']={'state':'prepared_not_yet_pushed','source_commit':science,'result_commit':science,'build_commit':science,'response_commit':science,'review_base':BASE}
        (directory/'canonical_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        prepared={'state':'prepared_not_yet_pushed','source_commit':science,'result_commit':science,'build_commit':science,'response_commit':science,'review_base':BASE,'local_delivery_identity_preserved':'local_delivery_receipt.json','branches':[BRANCH,COPY]}
        (directory/'publication_receipt.json').write_text(json.dumps(prepared,indent=2)+'\n')
        git(['add','revisions/2026-09-22-r14/canonical_manifest.json','revisions/2026-09-22-r14/publication_receipt.json','revisions/2026-09-22-r14/local_delivery_receipt.json'],repo)
        git(['commit','-m','meta(r14): pin remote-based source, result, build and response identities'],repo)
        final=git(['rev-parse','HEAD'],repo);git(['branch',COPY,final],repo)
        receipt.update(prepared);receipt['review_commit']=final
        if publish:
            git(['push','--atomic','origin',f'{BRANCH}:refs/heads/{BRANCH}',f'{COPY}:refs/heads/{COPY}'],repo)
            for branch in [BRANCH,COPY]:
                observed=git(['ls-remote','--heads','origin',f'refs/heads/{branch}'],repo).split()[0]
                if observed!=final:raise RuntimeError('Remote verification mismatch for '+branch)
            receipt['state']='published_and_remote_heads_verified'
        else:receipt['state']='prepared_locally_no_push_requested'
    except Exception as e:
        receipt['error']=str(e);raise
    finally:
        (workdir/'publication_attempt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--patch',type=Path,required=True);p.add_argument('--workdir',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args();main(a.patch,a.workdir,a.publish)
