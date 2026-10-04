"""Lossless, bounded Git transport for every frozen continuation-menu trial.

Scientific fitting and confirmation finish before this module runs. Each trial
adds its complete original payload to a single new staging ref with a compare-
and-swap update. A private index preserves the previous tree without checking
out, reading, or downloading earlier raw blobs. Only bounded analysis subsets
are downloaded by the collector. Their receipts bind every omitted local raw
file to its Git blob in the complete remote tree. Final evidence has that
cumulative staging commit as parent; its numerical source remains S.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import time

R16 = 'revisions/2026-10-04-r16'
TRIAL_PREFIX = R16+'/results/continuation_menu/trials'
STAGING_BRANCH = 'revision/econometrica-nbo-r16-menu-transport-2026-10-04'
SOURCE_BRANCH = 'revision/econometrica-nbo-r16-menu-source-2026-10-04'
EVIDENCE_BRANCH = 'revision/econometrica-nbo-r16-menu-evidence-2026-10-04'
PART_BYTES = 23*1024*1024
MAX_ANALYSIS_PARTS = 2
MAX_NEW_BYTES = 512*1024*1024
NETWORK_TIMEOUT_SECONDS = 600
PUBLISH_TIMEOUT_SECONDS = 1800


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def facts(data):
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())


def safe(root, name):
    p = PurePosixPath(str(name))
    require(not p.is_absolute() and '..' not in p.parts and str(p) not in ('', '.'), 'unsafe relative path')
    require(not any(c in str(p) for c in '\0\n\r\t'), 'control character in path')
    result = Path(root).joinpath(*p.parts)
    require(result.resolve().is_relative_to(Path(root).resolve()), 'path escapes its root')
    return result


def inventory(root):
    root = Path(root)
    result = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'symbolic link in evidence')
        if path.is_file():
            name = path.relative_to(root).as_posix(); safe(root, name)
            result[name] = facts(path.read_bytes())
    return result


def _env(extra=None):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_NO_LAZY_FETCH='1',
               GIT_AUTHOR_NAME='github-actions[bot]', GIT_COMMITTER_NAME='github-actions[bot]',
               GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',
               GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
    token = env.get('GITHUB_TOKEN')
    if token:
        # The credential remains in this subprocess environment, scoped to the
        # explicitly configured GitHub server; it is never put in an argument,
        # a remote URL, a receipt, or the on-disk Git configuration.
        host = env.get('GITHUB_SERVER_URL', 'https://github.com').rstrip('/')
        number = int(env.get('GIT_CONFIG_COUNT', '0'))
        env['GIT_CONFIG_COUNT'] = str(number+1)
        env[f'GIT_CONFIG_KEY_{number}'] = 'http.'+host+'/.extraheader'
        env[f'GIT_CONFIG_VALUE_{number}'] = 'AUTHORIZATION: basic '+base64.b64encode(('x-access-token:'+token).encode()).decode()
    if extra:
        env.update(extra)
    return env


def git(repo, *args, data=None, check=True, extra=None, deadline=None):
    timeout = NETWORK_TIMEOUT_SECONDS if any(a in {'fetch','push','ls-remote'} for a in args) else 120
    if deadline is not None:
        remaining = deadline-time.perf_counter()
        if remaining <= 0:
            raise TimeoutError('fixed lossless transport time budget exhausted; original samples are retained')
        timeout = min(timeout, remaining)
    try:
        result = subprocess.run(['git', '-C', str(repo), *map(str, args)], input=data,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=_env(extra), timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError('bounded Git transport command timed out; no scientific execution may be repeated') from exc
    if check and result.returncode:
        raise RuntimeError('git '+str(args[0])+' failed: '+result.stderr.decode(errors='replace')[-3000:])
    return result.stdout if check else result


def oid(value):
    require(bool(re.fullmatch('[0-9a-f]{40}', value or '')), 'complete Git SHA-1 required')
    return value


def tree(repo, commit, deadline=None):
    """Tree metadata only: -l would request sizes and could fetch old blobs."""
    result = {}
    for entry in git(repo, 'ls-tree', '-rz', '--full-tree', oid(commit), deadline=deadline).split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t', 1); mode, kind, sha = meta.decode().split()
        require(kind == 'blob', 'non-blob object in evidence tree')
        result[name.decode()] = dict(mode=mode, git_blob=sha)
    return result


def remote_head(repo, branch=STAGING_BRANCH, remote='origin'):
    rows = git(repo, 'ls-remote', '--heads', remote, 'refs/heads/'+branch).decode().splitlines()
    require(len(rows) <= 1, 'ambiguous remote ref')
    return oid(rows[0].split()[0]) if rows else None


def initialize(repo, source, remote='origin'):
    oid(source)
    require(os.environ.get('GITHUB_RUN_ATTEMPT', '1') == '1', 'second workflow execution is prohibited')
    require(remote_head(repo, STAGING_BRANCH, remote) is None, 'transport ref already exists; never reuse an earlier run')
    require(remote_head(repo, EVIDENCE_BRANCH, remote) is None, 'complete evidence ref already exists')
    require(remote_head(repo, SOURCE_BRANCH, remote) == source, 'the immutable numerical source ref differs')
    git(repo, 'push', '--porcelain', '--force-with-lease=refs/heads/'+STAGING_BRANCH+':',
        remote, source+':refs/heads/'+STAGING_BRANCH)
    return dict(complete=True, numerical_source_commit=source, initial_staging_commit=source,
                staging_branch=STAGING_BRANCH, creation_only=True)


def prepare_repo(repo, url):
    repo = Path(repo)
    require(not repo.exists() or not any(repo.iterdir()), 'transport object repository must be new')
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '--bare', '--quiet', str(repo)], check=True, env=_env())
    git(repo, 'remote', 'add', 'origin', url)
    git(repo, 'config', 'remote.origin.promisor', 'true')
    git(repo, 'config', 'remote.origin.partialclonefilter', 'blob:none')
    git(repo, 'config', 'extensions.partialClone', 'origin')
    git(repo, 'config', 'gc.auto', '0')


def fetch_staging(repo, source, remote='origin', deadline=None):
    oid(source)
    git(repo, '-c', 'protocol.version=2', 'fetch', '--quiet', '--no-tags', '--filter=blob:none',
        '--depth=130', remote, 'refs/heads/'+STAGING_BRANCH, deadline=deadline)
    head = oid(git(repo, 'rev-parse', 'FETCH_HEAD', deadline=deadline).decode().strip())
    git(repo, 'merge-base', '--is-ancestor', source, head, deadline=deadline)
    return head


def analysis_names(raw_files):
    result = []
    for name in sorted(raw_files):
        p = PurePosixPath(name)
        wanted = name == 'TRIAL.json' or name.startswith('confirmation/')
        if len(p.parts) == 3 and p.parts[0] == 'fits':
            wanted = p.name in {'FIT_WORK.json', 'CANDIDATE_FIT.json', 'SCALAR_CANDIDATE.json', 'scalar_candidate_grid.npz'}
            wanted = wanted or bool(re.fullmatch(r'(stage[123]\.json|actions_stage[123]\.npz)', p.name))
        if wanted:
            result.append(name)
    return result


def make_receipt(trial_dir, manifest):
    trial_dir = Path(trial_dir); trial = read(trial_dir/'TRIAL.json')
    expected = {t['trial_id']:t for t in manifest['matrix']['include']}
    ident = trial['trial']['trial_id']
    require(ident in expected and trial['trial'] == expected[ident], 'undeclared complete trial identity')
    for key in ['numerical_source_commit', 'assessment_fingerprint', 'protocol_sha256']:
        require(trial[key] == manifest[key], 'trial/source binding differs: '+key)
    raw = inventory(trial_dir)
    require({n:v['sha256'] for n,v in raw.items() if n != 'TRIAL.json'} == trial['files'], 'original trial inventory changed')
    require(sum(v['bytes'] for v in raw.values()) < MAX_NEW_BYTES, 'trial exceeds the fixed per-push object budget')
    require(all(v['bytes'] <= PART_BYTES for v in raw.values()), 'one raw file exceeds the existing bounded transport contract')
    return dict(schema='nbo-r16-menu-transport-receipt-v1', trial_id=ident,
        numerical_source_commit=manifest['numerical_source_commit'], assessment_fingerprint=manifest['assessment_fingerprint'],
        protocol_sha256=manifest['protocol_sha256'], github_run_id=manifest.get('github_run_id'),
        payload_tree_prefix=TRIAL_PREFIX+'/'+ident, attempt_complete=bool(trial['complete']),
        raw_files=raw, analysis_files={n:raw[n] for n in analysis_names(raw)},
        omitted_local_raw_policy='All original files remain in the remote Git tree and original bounded artifacts; the collector downloads only this exact analysis subset',
        raw_bytes=sum(v['bytes'] for v in raw.values()), new_blob_limit_bytes=MAX_NEW_BYTES)


def _write_blobs(repo, payload, deadline=None):
    answer = {}
    for name, data in sorted(payload.items()):
        safe(Path('/transport-root'), name)
        answer[name] = git(repo, 'hash-object', '-w', '--stdin', data=data, deadline=deadline).decode().strip()
        require(answer[name] == facts(data)['git_blob'], 'Git object hash differs from its bound payload')
    return answer


def append_commit(repo, parent, blobs, message, deadline=None):
    """No worktree and no old blob reads, including on a competing CAS retry."""
    before = tree(repo, parent, deadline=deadline)
    require(not (set(blobs) & set(before)), 'append would replace an existing path')
    with tempfile.TemporaryDirectory(prefix='nbo-menu-private-index-') as temp:
        extra = {'GIT_INDEX_FILE':str(Path(temp)/'index')}
        git(repo, 'read-tree', parent, extra=extra, deadline=deadline)
        records = b''.join(b'100644 '+oid(sha).encode()+b'\t'+name.encode()+b'\0' for name,sha in sorted(blobs.items()))
        git(repo, 'update-index', '-z', '--index-info', data=records, extra=extra, deadline=deadline)
        # Existing source/staging blobs are deliberately absent locally. Their
        # exact OIDs were read from the parent tree and are checked again below;
        # write-tree must not fetch them merely to check local object presence.
        newtree = git(repo, 'write-tree', '--missing-ok', extra=extra, deadline=deadline).decode().strip()
    commit = git(repo, 'commit-tree', newtree, '-p', parent, data=(message+'\n').encode(), deadline=deadline).decode().strip()
    after = tree(repo, commit, deadline=deadline)
    require(all(after.get(n) == value for n,value in before.items()), 'existing remote evidence changed')
    require(set(after)-set(before) == set(blobs), 'unexpected new path in transport commit')
    require(all(after[n] == dict(mode='100644', git_blob=sha) for n,sha in blobs.items()), 'new Git tree differs from payload')
    return oid(commit)


def publish_trial(repo, trial_dir, manifest, remote='origin', max_attempts=256, before_push=None):
    """CAS retries reuse the identical sealed trial; they never refit or redraw."""
    started = time.perf_counter(); deadline = started+PUBLISH_TIMEOUT_SECONDS
    receipt = make_receipt(trial_dir, manifest); prefix = receipt['payload_tree_prefix']
    payload = {}
    for name, expected in receipt['raw_files'].items():
        data = safe(trial_dir, name).read_bytes(); require(facts(data) == expected, 'trial changed during transfer')
        payload[prefix+'/'+name] = data
    receipt_data = json_bytes(receipt)
    payload[prefix+'/TRANSPORT_RECEIPT.json'] = receipt_data
    blobs = _write_blobs(repo, payload, deadline=deadline)
    # Release full payload memory before fetching any concurrently added trees.
    del payload
    for attempt in range(int(max_attempts)):
        parent = fetch_staging(repo, manifest['numerical_source_commit'], remote, deadline=deadline)
        before = tree(repo, parent, deadline=deadline); present = {n for n in before if n.startswith(prefix+'/')}
        if present:
            require(present == set(blobs) and all(before[n]['mode'] == '100644' and before[n]['git_blob'] == blobs[n] for n in blobs),
                    'this trial already has a different remote payload; no replacement is allowed')
            return receipt, dict(complete=True, trial_id=receipt['trial_id'], staging_commit=parent,
                numerical_source_commit=manifest['numerical_source_commit'], assessment_fingerprint=manifest['assessment_fingerprint'],
                receipt_git_blob=facts(receipt_data)['git_blob'], receipt_sha256=facts(receipt_data)['sha256'],
                identical_payload_already_present=True, cas_attempts=attempt,
                elapsed_transport_seconds=time.perf_counter()-started, fixed_transport_timeout_seconds=PUBLISH_TIMEOUT_SECONDS,
                work_scope='post-scientific lossless transport, excluded from numerical fitting and verification clocks')
        commit = append_commit(repo, parent, blobs, 'transport(r16): append complete frozen menu trial '+receipt['trial_id'], deadline=deadline)
        if before_push is not None:
            before_push(attempt, parent, commit)
        push = git(repo, 'push', '--porcelain', '--force-with-lease=refs/heads/'+STAGING_BRANCH+':'+parent,
                   remote, commit+':refs/heads/'+STAGING_BRANCH, check=False, deadline=deadline)
        if push.returncode == 0:
            return receipt, dict(complete=True, trial_id=receipt['trial_id'], staging_commit=commit,
                numerical_source_commit=manifest['numerical_source_commit'], assessment_fingerprint=manifest['assessment_fingerprint'],
                receipt_git_blob=facts(receipt_data)['git_blob'], receipt_sha256=facts(receipt_data)['sha256'],
                identical_payload_already_present=False, cas_attempts=attempt+1,
                elapsed_transport_seconds=time.perf_counter()-started, fixed_transport_timeout_seconds=PUBLISH_TIMEOUT_SECONDS,
                work_scope='post-scientific lossless transport, excluded from numerical fitting and verification clocks')
        # A race and a lost success acknowledgment are both resolved by a new
        # metadata-only fetch. The exact original payload is never replaced.
        remaining = deadline-time.perf_counter()
        if remaining <= 0:raise TimeoutError('fixed CAS time budget exhausted; original samples retained')
        time.sleep(min(10., .15*(attempt+1), remaining))
    raise RuntimeError('bounded CAS retry budget exhausted; original parts and trial remain unchanged')


def make_analysis(trial_dir, receipt, publication, out):
    out = Path(out); require(not out.exists(), 'analysis folder already exists'); out.mkdir(parents=True)
    for name, expected in receipt['analysis_files'].items():
        data = safe(trial_dir, name).read_bytes(); require(facts(data) == expected, 'analysis input changed')
        target = safe(out, name); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
    write(out/'TRANSPORT_RECEIPT.json', receipt)
    write(out/'TRANSPORT_PUBLICATION.json', publication)
    files = inventory(out)
    write(out/'ANALYSIS_MANIFEST.json', dict(schema='nbo-r16-menu-analysis-v1', trial_id=receipt['trial_id'],
        numerical_source_commit=receipt['numerical_source_commit'], assessment_fingerprint=receipt['assessment_fingerprint'],
        files=files, complete_original_trial_bytes=receipt['raw_bytes'],
        remote_training_raw_preserved=True, all_three_confirmation_stages_retained=True))
    return out


def partition_analysis(folder, out):
    folder, out = Path(folder), Path(out)
    require(not out.exists(), 'analysis parts already exist')
    files = inventory(folder); manifest = read(folder/'ANALYSIS_MANIFEST.json')
    bins, sizes = [], []
    for name, data in sorted(files.items()):
        require(data['bytes'] <= PART_BYTES, 'analysis file exceeds one bounded artifact')
        i = next((j for j,size in enumerate(sizes) if size+data['bytes'] <= PART_BYTES), len(bins))
        if i == len(bins): bins.append({}); sizes.append(0)
        bins[i][name] = data; sizes[i] += data['bytes']
    require(len(bins) <= MAX_ANALYSIS_PARTS, 'analysis subset exceeds the two-part frozen budget; nothing omitted')
    whole = hashlib.sha256(canonical(files)).hexdigest()
    for i, rows in enumerate(bins):
        dest = out/f'analysis{i:02d}'; dest.mkdir(parents=True)
        for name in rows:
            target = safe(dest/'payload', name); target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe(folder,name), target)
        write(dest/'ANALYSIS_PART.json', dict(schema='nbo-r16-menu-analysis-part-v1', trial_id=manifest['trial_id'],
            numerical_source_commit=manifest['numerical_source_commit'], assessment_fingerprint=manifest['assessment_fingerprint'],
            index=i, parts=len(bins), files=rows, complete_analysis_inventory_sha256=whole))
        require(sum(v['bytes'] for v in inventory(dest).values()) < 24*1024*1024, 'analysis artifact exceeds 24 MiB including metadata')
    return dict(parts=len(bins), bytes=sum(sizes), complete_original_trial_bytes=manifest['complete_original_trial_bytes'])


def verify_analysis_trial(folder, manifest):
    folder = Path(folder); analysis = read(folder/'ANALYSIS_MANIFEST.json')
    receipt = read(folder/'TRANSPORT_RECEIPT.json'); publication = read(folder/'TRANSPORT_PUBLICATION.json')
    expected = {t['trial_id']:t for t in manifest['matrix']['include']}
    require(receipt['trial_id'] in expected, 'undeclared analysis trial')
    require(analysis['schema'] == 'nbo-r16-menu-analysis-v1' and receipt['schema'] == 'nbo-r16-menu-transport-receipt-v1', 'unknown analysis or transport schema')
    for key in ['numerical_source_commit','assessment_fingerprint','protocol_sha256']:
        require(receipt[key] == manifest[key], 'analysis numerical source differs: '+key)
    require(receipt['github_run_id'] == manifest.get('github_run_id'), 'different frozen workflow run')
    require(analysis['trial_id'] == receipt['trial_id'] and analysis['numerical_source_commit'] == receipt['numerical_source_commit'] and analysis['assessment_fingerprint'] == receipt['assessment_fingerprint'], 'analysis identity differs')
    local = inventory(folder)
    require(all(local.get(n) == v for n,v in analysis['files'].items()), 'analysis inventory changed')
    extras = set(local)-set(analysis['files'])-{'ANALYSIS_MANIFEST.json'}
    require(extras <= set(receipt['raw_files']) and all(local[n] == receipt['raw_files'][n] for n in extras),
            'unknown or changed raw file in a complete future checkout')
    require(set(analysis['files']) == set(receipt['analysis_files'])|{'TRANSPORT_RECEIPT.json','TRANSPORT_PUBLICATION.json'}, 'unlisted or omitted analysis file')
    require(receipt['analysis_files'] == {n:receipt['raw_files'][n] for n in analysis_names(receipt['raw_files'])}, 'analysis selection differs from frozen rule')
    for name, value in receipt['analysis_files'].items():
        require(facts(safe(folder,name).read_bytes()) == value, 'analysis file differs from original raw')
    rf = facts((folder/'TRANSPORT_RECEIPT.json').read_bytes())
    require(publication['complete'] and publication['trial_id'] == receipt['trial_id'] and publication['receipt_sha256'] == rf['sha256'] and publication['receipt_git_blob'] == rf['git_blob'], 'remote publication acknowledgment differs')
    trial = read(folder/'TRIAL.json')
    require(trial['trial'] == expected[receipt['trial_id']], 'trial metadata differs')
    require({n:v['sha256'] for n,v in receipt['raw_files'].items() if n != 'TRIAL.json'} == trial['files'], 'remote raw receipt omits original evidence')
    return receipt


def restore_analysis_parts(input_dir, out, manifest):
    out = Path(out); require(not out.exists(), 'analysis restoration destination exists'); out.mkdir(parents=True)
    expected = {t['trial_id'] for t in manifest['matrix']['include']}; found = {}
    for path in Path(input_dir).rglob('ANALYSIS_PART.json'):
        row = read(path); ident = row['trial_id']; key = (ident,row['index'])
        require(ident in expected and key not in found, 'undeclared or duplicate analysis part')
        require(row['numerical_source_commit'] == manifest['numerical_source_commit'] and row['assessment_fingerprint'] == manifest['assessment_fingerprint'], 'analysis part source differs')
        found[key] = (path,row)
    require({key[0] for key in found} == expected, 'missing complete trial analysis')
    receipts = {}
    for ident in sorted(expected):
        rows = sorted((v for k,v in found.items() if k[0] == ident), key=lambda x:x[1]['index'])
        count = rows[0][1]['parts']; whole = rows[0][1]['complete_analysis_inventory_sha256']
        require(1 <= count <= MAX_ANALYSIS_PARTS and [r['index'] for _,r in rows] == list(range(count)), 'missing analysis part index')
        collected = {}
        for path,row in rows:
            require(row['schema'] == 'nbo-r16-menu-analysis-part-v1' and row['parts'] == count and row['complete_analysis_inventory_sha256'] == whole, 'inconsistent analysis part family')
            require(inventory(path.parent/'payload') == row['files'], 'changed or unlisted analysis part bytes')
            for name,value in row['files'].items():
                require(name not in collected, 'duplicate reconstructed analysis file'); collected[name] = value
                target = safe(out/ident, name); target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(safe(path.parent/'payload',name), target)
        require(hashlib.sha256(canonical(collected)).hexdigest() == whole, 'complete analysis inventory differs')
        receipts[ident] = verify_analysis_trial(out/ident, manifest)
    return receipts


def assert_transport_tree(repo, tip, receipts, manifest):
    expected = {t['trial_id'] for t in manifest['matrix']['include']}
    require(set(receipts) == expected, 'full fixed trial transport population required')
    source = manifest['numerical_source_commit']; git(repo,'merge-base','--is-ancestor',source,tip)
    base, actual = tree(repo,source), tree(repo,tip)
    require(all(actual.get(n) == v for n,v in base.items()), 'historical or frozen source tree changed')
    additions = {}
    for ident, receipt in receipts.items():
        require(receipt['trial_id'] == ident and receipt['payload_tree_prefix'] == TRIAL_PREFIX+'/'+ident, 'transport receipt path differs')
        for key in ['numerical_source_commit','assessment_fingerprint','protocol_sha256']:
            require(receipt[key] == manifest[key], 'transport receipt source differs')
        for name,value in receipt['raw_files'].items():
            safe(Path('/transport-root'), name)
            additions[receipt['payload_tree_prefix']+'/'+name] = dict(mode='100644',git_blob=oid(value['git_blob']))
        additions[receipt['payload_tree_prefix']+'/TRANSPORT_RECEIPT.json'] = dict(mode='100644',git_blob=facts(json_bytes(receipt))['git_blob'])
    require(not (set(base)&set(additions)), 'transport path existed in the immutable source')
    require(set(actual) == set(base)|set(additions), 'staging has an omitted or unregistered path')
    require(all(actual.get(n) == v for n,v in additions.items()), 'full remote raw Git tree differs from complete receipts')
    return dict(complete=True,numerical_source_commit=source,staging_commit=tip,trial_count=len(receipts),
        full_raw_files=sum(len(r['raw_files']) for r in receipts.values()),
        full_raw_bytes=sum(r['raw_bytes'] for r in receipts.values()),
        verification='Git tree blob IDs and modes checked against exact per-file SHA256/byte-count/Git-blob receipts; receipt blobs themselves checked. Git blob identity incorporates its byte length. No omitted training blob downloaded.',
        source_tree_preserved=True)


def finalize(repo, manifest_path, results_root, summary_root, remote='origin'):
    manifest = read(manifest_path); source = manifest['numerical_source_commit']
    require(os.environ.get('GITHUB_RUN_ATTEMPT','1') == '1','second workflow execution is prohibited')
    require(remote_head(repo,SOURCE_BRANCH,remote) == source,'immutable source ref differs')
    require(remote_head(repo,EVIDENCE_BRANCH,remote) is None,'complete evidence ref already exists')
    results_root, summary_root = Path(results_root).resolve(), Path(summary_root).resolve()
    repo = Path(repo).resolve()
    audit = read(results_root/'FINAL_AUDIT.json')
    require(audit['complete'] and audit['numerical_source_commit'] == source,'complete scientific audit required')
    receipts = {t['trial_id']:verify_analysis_trial(results_root/'trials'/t['trial_id'],manifest) for t in manifest['matrix']['include']}
    parent = fetch_staging(repo,source,remote); proof = assert_transport_tree(repo,parent,receipts,manifest)
    before = tree(repo,parent); payload = {}
    for folder in [results_root,summary_root]:
        for path in sorted(folder.rglob('*')):
            require(not path.is_symlink(),'symlink in final evidence')
            if not path.is_file(): continue
            name = path.relative_to(repo).as_posix()
            require(name.startswith(R16+'/results/continuation_menu/') or name.startswith(R16+'/results/continuation_menu_summary/'),'unexpected final evidence path')
            data = path.read_bytes(); value = facts(data)
            if name in before:
                require(before[name] == dict(mode='100644',git_blob=value['git_blob']),'finalization would change sealed raw data')
            else: payload[name] = data
    require(payload and sum(len(v) for v in payload.values()) < MAX_NEW_BYTES,'final metadata push exceeds its fixed bound')
    commit = append_commit(repo,parent,_write_blobs(repo,payload),'revision(r16): complete all frozen menu evidence, reports and audits')
    # No worker may append an extra trial between audit and final publication.
    require(remote_head(repo,STAGING_BRANCH,remote) == parent,'staging changed after complete audit')
    git(repo,'push','--atomic','--porcelain','--force-with-lease=refs/heads/'+EVIDENCE_BRANCH+':',remote,commit+':refs/heads/'+EVIDENCE_BRANCH)
    return dict(complete=True,numerical_source_commit=source,staging_parent=parent,evidence_commit=commit,
                evidence_branch=EVIDENCE_BRANCH,new_payload_bytes=sum(len(v) for v in payload.values()),full_tree_proof=proof)


def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('initialize');p.add_argument('--repo',type=Path,required=True);p.add_argument('--source',required=True)
    p=sub.add_parser('publish');
    for name in ['repo','trial-dir','manifest','analysis','analysis-parts']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--url',required=True)
    p=sub.add_parser('finalize')
    for name in ['repo','manifest-path','results-root','summary-root']:p.add_argument('--'+name,type=Path,required=True)
    args=vars(parser.parse_args());command=args.pop('command')
    if command == 'publish':
        manifest=read(args.pop('manifest'));parts=args.pop('analysis_parts');analysis=args.pop('analysis')
        prepare_repo(args['repo'],args.pop('url'))
        receipt,publication=publish_trial(args['repo'],args['trial_dir'],manifest)
        make_analysis(args['trial_dir'],receipt,publication,analysis)
        result=dict(publication=publication,analysis=partition_analysis(analysis,parts))
    else:result=globals()[command](**args)
    print(json.dumps(result,sort_keys=True,indent=2,allow_nan=False))


if __name__ == '__main__':main()
