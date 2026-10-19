#!/usr/bin/env python3
"""Refresh current author-response source routes without running any science.

Usage:
  python provenance/author_response120/refresh_current_bindings120.py \
    --output provenance/AUTHOR_RESPONSE_BINDING_CURRENT120.json

Run after the current prose/source edits are stable. Each output receipt is
created exclusively; use a new dated output path for subsequent checks. The
immutable R119 routes and original report text are verified, never rewritten.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, re

def sha(data):
    return hashlib.sha256(data).hexdigest()

def readj(path):
    return json.loads(path.read_text())

def binding(path, root):
    data = path.read_bytes()
    return {'path':str(path.relative_to(root)), 'bytes':len(data), 'sha256':sha(data),
            'git_blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    revision = args.revision.resolve()
    output = args.output if args.output.is_absolute() else revision/args.output
    if output.exists():
        raise FileExistsError('Preserve the earlier receipt; choose a new output path: '+str(output))
    old = revision.parent/'2026-10-18-r119'
    repo = revision.parent.parent
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    requirements_path = revision/'provenance/R97_REQUIREMENTS120.json'
    requirements = readj(requirements_path)
    assert len(requirements['items']) == 30
    before_requirements = sha(requirements_path.read_bytes())
    files = {}
    originals = {}
    for row in requirements['items']:
        assert row['closed'] is False
        assert sha(row['exact_text'].encode()) == row['comment_sha256']
        original_path = old/'provenance'/row['source_path']
        if original_path not in originals:
            originals[original_path] = original_path.read_text()
        assert row['exact_text'] in originals[original_path]
        for entry in row['r120_current_source_routes']:
            path = (revision/entry['path']).resolve()
            path.relative_to(revision)
            current = binding(path, revision)
            text = path.read_text() if entry.get('labels') else ''
            for label in entry.get('labels', []):
                assert '\\label{'+label+'}' in text, (path,label)
            entry.update({k:current[k] for k in ['bytes','sha256']})
            files[current['path']] = current
        row['r120_source_route_observed_utc'] = now
    requirements['source_binding_refreshed_utc'] = now
    requirements_path.write_text(json.dumps(requirements,indent=2,ensure_ascii=False)+'\n')

    history_path = revision/'provenance/HISTORICAL_ROUTE_BINDINGS120.json'
    history_bytes = history_path.read_bytes()
    history = json.loads(history_bytes)
    assert len(history['rows']) == 1049
    checked_maps = {}
    for row in history['rows']:
        assert row['r120_new_closure_asserted'] is False
        path = repo/row['r119_map']
        if path not in checked_maps:
            data=path.read_bytes();checked_maps[path]=(sha(data),json.loads(data))
        digest,data=checked_maps[path]
        assert digest == row['r119_map_sha256']
        original=data[row['r119_array']][row['r119_row_index']]
        assert original['key']==row['key']
        assert sha(original['exact_text'].encode())==row['original_comment_hash']
    assert history_path.read_bytes() == history_bytes

    identity_path = revision/'SOURCE_IDENTITY120.json'
    identity = readj(identity_path)
    for entry in identity.get('r120_written_mathematical_sources', []):
        path = (revision/entry['path']).resolve()
        path.relative_to(revision)
        entry['sha256']=sha(path.read_bytes())
        entry['labels']=re.findall(r'\\label\{([^}]+)\}',path.read_text())
    identity['r120_mathematical_source_observed_utc']=now
    identity_path.write_text(json.dumps(identity,indent=2,ensure_ascii=False)+'\n')
    for rel in ['new120/response120_body.tex','CONTENT_RETENTION_MAP120.md','REVISION_BOUNDARY120.md',
                'SOURCE_IDENTITY120.json','provenance/R97_REQUIREMENTS120.json',
                'provenance/HISTORICAL_ROUTE_BINDINGS120.json','provenance/SOURCE_ONLY_REVIEW120.json']:
        current=binding(revision/rel,revision);files[rel]=current
    body=(revision/'new120/response120_body.tex').read_text()
    labels=re.findall(r'\\label\{response120:([^}]+)\}',body)
    assert len(labels)==30 and set(labels)=={row['comment_id'] for row in requirements['items']}
    pending=sorted(set(re.findall(r'R120_PENDING_[A-Z_]+',body.replace('\\_','_'))))
    receipt={
        'schema':'NBO_R120_CURRENT_AUTHOR_RESPONSE_BINDING_V1','observed_utc':now,
        'scope':'Source/route/text binding only. No scientific code, statistical analysis, build, workflow or Git ref is executed or changed.',
        'status':'passed','current_R97_items':30,'inherited_item_parent_routes':1049,
        'inherited_distinct_report_documents':len({row['report_id'] for row in history['rows']}),
        'inherited_map_bytes_unchanged':True,'requirements_before_sha256':before_requirements,
        'pending_markers':pending,'current_files':sorted(files.values(),key=lambda x:x['path']),
        'refresher_sha256':sha(Path(__file__).read_bytes()),
        'note':'Earlier checks remain dated snapshots. Do not interpret route inclusion as blanket scientific closure or a pending marker as an executed result.',
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':'passed','receipt':str(output),'sha256':sha(output.read_bytes()),
                      'current_files':len(files),'pending_markers':pending},indent=2))

if __name__=='__main__':
    main()
