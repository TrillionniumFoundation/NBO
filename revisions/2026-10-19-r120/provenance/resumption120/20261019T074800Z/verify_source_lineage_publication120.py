#!/usr/bin/env python3
"""Read-only source/report/remote-tree verification; no scientific imports or runs.

The output is exclusive and binds the dated raw connector envelopes beside it.
Do not use this check as an experimental result or a final publication claim.
"""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
REV = HERE.parents[2]
OLD = REV.parent / '2026-10-18-r119'
F = '369d02724cf12ae0e54390b4e7b5f894f703892e'
PARENT = '82618f037540233dda7d1ba8bfd3ddfdc88afbf9'
BRANCH = 'refs/heads/revision/econometrica-nbo-r120-certified-policy-improvement-2026-10-19'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def readj(path):
    return json.loads(path.read_bytes())

def binding(path):
    data = path.read_bytes()
    return {'path':str(path.relative_to(REV)), 'bytes':len(data),
            'sha256':sha(data), 'git_blob_sha1':blob(data)}

def main():
    output = HERE/'LINEAGE_SOURCE_PUBLICATION_VERIFIED120.json'
    assert not output.exists(), 'Keep prior observations; use a new dated audit directory.'
    earlier = readj(REV/'provenance/REMOTE_HEADS120.json')
    latest = readj(HERE/'REMOTE_HEADS_API120.json')
    previous = {x['ref']:x['object']['sha'] for x in earlier['parsed']}
    current = {x['ref']:x['object']['sha'] for x in latest['parsed']}
    changed = {key:[value,current.get(key)] for key,value in previous.items()
               if current.get(key) != value}
    added = {key:value for key,value in current.items() if key not in previous}
    assert len(previous)==360 and len(current)==361
    assert changed=={} and added=={BRANCH:F}
    assert sum(x.startswith('refs/heads/review/') for x in current)==36

    commit = readj(HERE/'SOURCE_F_COMMIT_API120.json')['parsed']
    root = readj(HERE/'SOURCE_F_ROOT_TREE_API120.json')['parsed']
    revisions = readj(HERE/'SOURCE_F_REVISIONS_TREE_API120.json')['parsed']
    tree = readj(HERE/'SOURCE_F_REVISION_TREE_API120.json')['parsed']
    assert commit['sha']==F and [x['sha'] for x in commit['parents']]==[PARENT]
    assert commit['tree']['sha']==root['sha']=='16c38ff041a7fa3c8972109e361494d4e5855c16'
    assert not root['truncated'] and not revisions['truncated'] and not tree['truncated']
    assert next(x for x in root['tree'] if x['path']=='revisions')['sha']==revisions['sha']
    assert next(x for x in revisions['tree'] if x['path']=='2026-10-19-r120')['sha']==tree['sha']
    entries = {x['path']:x for x in tree['tree']}
    remote_freeze = readj(HERE/'SOURCE_F_FREEZE_API120.json')['raw_tool_response']['structuredContent']
    manifest_bytes = remote_freeze['content'].encode('utf-8')
    assert manifest_bytes==(REV/'SOURCE_FREEZE120.json').read_bytes()
    assert blob(manifest_bytes)==remote_freeze['sha']==entries['SOURCE_FREEZE120.json']['sha']
    manifest = json.loads(manifest_bytes)
    assert manifest['total_files']==len(manifest['files'])==157
    assert manifest['total_bytes']==sum(x['bytes'] for x in manifest['files'])==1206453
    assert set(manifest['scientific_files'])=={x['path'] for x in manifest['files']}
    checked=[]
    for item in manifest['files']:
        data=(REV/item['path']).read_bytes()
        assert len(data)==item['bytes']==entries[item['path']]['size']
        assert sha(data)==item['sha256']==manifest['scientific_files'][item['path']]
        assert blob(data)==item['git_blob']==entries[item['path']]['sha']
        checked.append(dict(item,remote_tree_git_blob=entries[item['path']]['sha']))

    registry=readj(REV/'provenance/LINEAGE_REFRESH120.json')
    assert len(registry['reports'])==35
    report_checks=[]
    for report in registry['reports']:
        assert current['refs/heads/'+report['review_branch']]==report['review_commit']
        path=OLD/'provenance/reviews'/report['report_id']/'referee_report.md'
        data=path.read_bytes()
        assert len(data)==report['bytes'] and sha(data)==report['sha256']
        assert blob(data)==report['git_blob_sha1']
        report_checks.append({'report_id':report['report_id'], 'review_commit':report['review_commit'],
                              'bytes':len(data), 'sha256':sha(data), 'git_blob_sha1':blob(data)})
    control=readj(HERE/'CONTROL_R97_FILE_API120.json')['raw_tool_response']['structuredContent']
    control_bytes=control['content'].encode('utf-8')
    assert blob(control_bytes)==control['sha']=='33ba8b144e2f7816b19b036404341402d23a582f'
    assert sha(control_bytes)=='479b28c8800084846336cac078877a01dbbd2bae546d179633a2734401da19b9'
    assert control_bytes==(OLD/'provenance/reviews/2026-10-14-econometrica-numerical-methods-r97/referee_report.md').read_bytes()

    publication=readj(REV/'provenance/SOURCE_PUBLICATION120.json')
    assert publication['source_commit']==F and publication['tree_sha']==root['sha']
    assert publication['parent_sha']==PARENT and publication['remote_update_success'] is True
    prose_paths=['new120/response120_body.tex','SOURCE_IDENTITY120.json',
                 'provenance/R97_REQUIREMENTS120.json','CONTENT_RETENTION_MAP120.md','REVISION_BOUNDARY120.md']
    assert not set(prose_paths).intersection(manifest['scientific_files'])
    receipt={
        'schema':'NBO_R120_RESUMPTION_LINEAGE_SOURCE_PUBLICATION_V1',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'Read-only comparison of remote refs, existing report bytes, source-freeze manifest and remote Git trees; no scientific, statistical, timing, build or workflow execution.',
        'status':'passed',
        'remote_observed_utc':latest['observed_utc'],
        'prior_snapshot':binding(REV/'provenance/REMOTE_HEADS120.json'),
        'prior_snapshot_observed_utc':earlier['observed_utc'],
        'prior_heads':360,'current_heads':361,'changed_or_missing_prior_heads':changed,
        'added_heads':added,'all_prior360_unchanged':True,'original359_preservation_inherited':True,
        'review_ref_count':36,'persisted_distinct_report_documents':35,
        'new_controlling_report_found':False,'new_completed_author_source_found':False,
        'complete_author_baseline':{'revision':'R119','source_commit':'6250abfd317f3b2a56cb1303eb5ce78249bf4042','publication_head':PARENT},
        'controlling_advisory':{'commit':'9723c6cd2cc8b3e071422f3e522d4a843946db63','blob':control['sha'],
                               'sha256':sha(control_bytes),'bytes':len(control_bytes),
                               'assessed_manuscript':'f802fe64d91d9f5c1c8f86123b0fbe114e622279',
                               'scope':'Owner-commissioned AI-assisted advisory on R97, not an Econometric Society decision or a review of R119/R120.'},
        'source_F':{'commit':F,'tree':root['sha'],'revision_subtree':tree['sha'],'parent':PARENT,
                    'git_commit_recorded_date':commit['committer']['date'],
                    'local_manifest_prepared_utc':manifest['prepared_utc'],
                    'root_publication_receipt_observed_utc':publication['observed_utc'],
                    'independent_remote_ref_observed_utc':latest['observed_utc'],
                    'manifest':binding(REV/'SOURCE_FREEZE120.json'),
                    'scientific_inputs_verified':157,'scientific_input_bytes_verified':1206453,
                    'scope':'Prospective scientific-source barrier only. It is not a completed R120 manuscript, executed campaign, actor/sample publication or final source/PDF/CI claim.',
                    'timing_qualification':'The 02:49 preparation time is not remote publication. Git date, root publication observation and this independent remote observation are retained separately.'},
        'frozen_files':checked,'report_checks':report_checks,
        'prose_metadata_paths_outside_scientific_freeze':prose_paths,
        'publication_receipt_binding':binding(REV/'provenance/SOURCE_PUBLICATION120.json'),
        'prior_lineage_binding':binding(REV/'provenance/LINEAGE_REFRESH120.json'),
        'api_envelopes':[binding(p) for p in sorted(HERE.glob('*API120.json'))],
        'checker_binding':binding(Path(__file__)),
        'unchanged_scientific_priorities':['Original-objective action improvement with paid comparison and exact regret/action bounds.',
            'All eight conventional/neural representations and all four services retain the frozen equal-access comparison.',
            'Actual new F/M/D barriers, independent new states and all negative/adverse observations remain necessary.',
            'Ordinary value-label fitting does not complete action-aware acquisition or prove neural-specific adoption.'],
        'independent_episode_boundaries':'R98, R115 and R119 A/B/C/D retain their own actors, samples, rules and evidence. This metadata update supplies no result for any of them.',
        'no_scientific_execution_by_this_audit':True,
    }
    with output.open('x') as stream:
        json.dump(receipt,stream,indent=2,ensure_ascii=False);stream.write('\n')
    print(json.dumps({'status':'passed','receipt':str(output),'sha256':sha(output.read_bytes()),
                      'heads':361,'frozen_files':157,'reports':35},indent=2))

if __name__=='__main__':
    main()
