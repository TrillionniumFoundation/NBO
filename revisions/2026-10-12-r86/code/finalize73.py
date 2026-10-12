"""Publish review-ready only after the staged files and actual visual report agree."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def main():
    stage=json.loads((R/'audit/STAGED_DELIVERY73.json').read_text());visual=json.loads((R/'audit/VISUAL73.json').read_text())
    if stage['status']!='checks_passed_visual_pending' or visual['status']!='passed':raise AssertionError('Required release gate absent')
    if sha(R/'audit/DELIVERY_FILES73.json')!=stage['delivery_files_sha256']:raise AssertionError('Delivery manifest changed')
    files=json.loads((R/'audit/DELIVERY_FILES73.json').read_text())
    for name,h in files.items():
        if sha(R/name)!=h:raise AssertionError('A staged file changed after validation: '+name)
    if not visual.get('actual_render_inspection'):raise AssertionError('Actual render inspection required')
    for d in stage['documents']:
        v=visual['documents'].get(d['document'])
        if not v or v['sha256']!=d['sha256'] or v['pages']!=d['pages']:raise AssertionError('Visual report refers to another PDF')
    clean=json.loads((R/'audit/CLEAN_REBUILD73.json').read_text())
    if clean['status']!='passed' or not clean['full_retained_replay']:raise AssertionError('Full clean rebuild absent')
    final={**stage,'status':'passed','final_source_parent':run(['git','rev-parse','HEAD']),
           'visual_report_sha256':sha(R/'audit/VISUAL73.json'),'clean_rebuild_sha256':sha(R/'audit/CLEAN_REBUILD73.json'),
           'publication_scope':'Original-paper R73, full inherited and new tests, exact new action-value and optimization audit, byte-preserved prior sections, full self-contained archive rebuild and actual current-PDF visual review'}
    (R/'audit/FINAL_DELIVERY73.json').write_text(json.dumps(final,indent=2,sort_keys=True)+'\n')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    run(['git','add','-f',str((R/'audit/FINAL_DELIVERY73.json').relative_to(REPO))]);run(['git','commit','-m','R73: publish visually checked original-paper revision with complete reproducibility evidence'])
    commit=run(['git','rev-parse','HEAD']);branches=[stage[k] for k in ('revision_branch','source_branch','canonical_branch')]
    run(['git','push','--atomic','origin',*['HEAD:refs/heads/'+branch for branch in branches]])
    for branch in branches:
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(commit+'\t'):raise AssertionError('Remote branch mismatch')
    print(json.dumps(dict(status='remote_publication_verified',commit=commit,branches=branches,tests=stage['total_tests'],documents=stage['documents']),indent=2))
if __name__=='__main__':main()
