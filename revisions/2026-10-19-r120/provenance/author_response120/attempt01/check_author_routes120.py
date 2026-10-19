#!/usr/bin/env python3
"""Read-only author-route verification; never imports or runs scientific code."""
from pathlib import Path
from collections import Counter
import datetime, hashlib, json, re

BASE = Path('/workspace/scratch/913249553838')
REPO = BASE / 'NBO'
OLD = REPO / 'revisions/2026-10-18-r119'
NEW = REPO / 'revisions/2026-10-19-r120'
AUDIT = BASE / 'audit120/review_lineage'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def readj(path):
    return json.loads(path.read_text())

def exclusive(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(content, bytes):
        content = (json.dumps(content, indent=2, ensure_ascii=False) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(content)

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
constraint_rows = []
for path in sorted((AUDIT / 'constraints').glob('*API.json')):
    env = readj(path)
    result = env['result']
    assert not result.get('isError'), path
    source = result['structuredContent']
    data = source['content'].encode()
    assert blob(data) == source['sha'], (path, 'Git blob identity')
    native_source = NEW / 'provenance/independent_constraints120' / Path(env['path']).name
    native_api = NEW / 'provenance/independent_constraints120' / path.name
    exclusive(native_source, data)
    exclusive(native_api, path.read_bytes())
    constraint_rows.append({
        'original_commit': env['ref'], 'original_repository_path': env['path'],
        'requested_utc': env['requested_utc'], 'observed_utc': env['observed_utc'],
        'git_blob_sha1': source['sha'], 'bytes': len(data), 'sha256': sha(data),
        'native_source': str(native_source.relative_to(NEW)),
        'api_envelope': str(native_api.relative_to(NEW)),
        'api_envelope_sha256': sha(native_api.read_bytes()),
        'source_byte_identity_verified': True,
    })
assert len(constraint_rows) == 7
exclusive(NEW / 'provenance/independent_constraints120/CONSTRAINT_SOURCE_BINDINGS120.json', {
    'schema': 'NBO_R120_INDEPENDENT_EPISODE_SOURCE_CONSTRAINTS_V1',
    'checked_utc': now, 'rows': constraint_rows,
    'scope': 'Exact read-back of historical source documents. No actor, sample, protocol or historical file changed; no inference about a currently running process is made.',
})

routes_path = NEW / 'provenance/HISTORICAL_ROUTE_BINDINGS120.json'
routes = readj(routes_path)
assert len(routes['rows']) == 1049
assert Counter(row['category'] for row in routes['rows']) == {
    'major': 620, 'additional': 394, 'overlapping_parent': 35,
}
assert len({(row['category'], row['key']) for row in routes['rows']}) == 1049
assert len({row['report_id'] for row in routes['rows']}) == 35
maps = {}
sources = {}
reports = {}
for row in routes['rows']:
    map_path = REPO / row['r119_map']
    if map_path not in maps:
        data = map_path.read_bytes()
        maps[map_path] = (sha(data), json.loads(data))
    digest, original_map = maps[map_path]
    assert digest == row['r119_map_sha256']
    original = original_map[row['r119_array']][row['r119_row_index']]
    assert original['key'] == row['key']
    assert original['review_commit'] == row['review_commit']
    assert original['report_git_blob_sha1'] == row['report_git_blob_sha1']
    assert sha(original['exact_text'].encode()) == row['original_comment_hash']
    old_treatment = original.get('current_author_treatment', original.get('author_response'))
    old_remaining = original.get('remaining_scientific_requirement', original.get('remaining_requirement'))
    assert old_treatment == row['r119_author_treatment']
    assert old_remaining == row['r119_remaining_requirement']
    assert row['r120_new_closure_asserted'] is False
    report_path = OLD / 'provenance' / original['source_path']
    if report_path not in reports:
        data = report_path.read_bytes()
        reports[report_path] = (blob(data), data.decode())
    report_blob, report_text = reports[report_path]
    assert report_blob == original['report_git_blob_sha1']
    assert original['exact_text'] in report_text, (row['key'], 'exact original text')
    assert original['current_source_bindings'] == row['r119_current_source_bindings']
    for binding in row['r119_current_source_bindings']:
        p = OLD / binding['path']
        if p not in sources:
            data = p.read_bytes()
            sources[p] = {'bytes': len(data), 'sha256': sha(data), 'git_blob_sha1': blob(data)}
        for field in ['bytes', 'sha256', 'git_blob_sha1']:
            assert sources[p][field] == binding[field], (p, field)

requirements_path = NEW / 'provenance/R97_REQUIREMENTS120.json'
requirements = readj(requirements_path)
assert len(requirements['items']) == 30
assert {row['comment_id'] for row in requirements['items']} == (
    {f'B{i}' for i in range(1, 11)} | {f'M{i}' for i in range(1, 11)} | {f'minor-{i}' for i in range(1, 11)}
)
body_path = NEW / 'new120/response120_body.tex'
body = body_path.read_text()
assert body.count('\\subsection{') == 30
assert body.count('\\paragraph{Original advisory request.}') == 30
assert body.count('\\paragraph{Completed inherited response.}') == 30
assert body.count('\\paragraph{Concrete R120 author action.}') == 30
assert body.count('\\paragraph{Scientific boundary.}') == 30
for row in requirements['items']:
    assert row['closed'] is False
    assert sha(row['exact_text'].encode()) == row['comment_sha256']
    report_path = OLD / 'provenance' / row['source_path']
    assert row['exact_text'] in reports[report_path][1]
    assert '\\label{response120:' + row['comment_id'] + '}' in body
    assert row['planned_r120_author_action'] and row['continuing_scientific_boundary']
    assert 'pending' in row['r120_empirical_status']
pending = sorted(set(re.findall(r'R120(?:\\_PENDING)(?:\\_[A-Z]+)+', body)))
assert len(pending) == 5

bound = []
for p in [routes_path, requirements_path, body_path, NEW / 'SOURCE_IDENTITY120.json',
          NEW / 'CONTENT_RETENTION_MAP120.md', NEW / 'REVISION_BOUNDARY120.md',
          NEW / 'provenance/LINEAGE_REFRESH120.json', NEW / 'provenance/R119_RETENTION_BINDINGS120.json',
          NEW / 'provenance/independent_constraints120/CONSTRAINT_SOURCE_BINDINGS120.json']:
    data = p.read_bytes()
    bound.append({'path': str(p.relative_to(NEW)), 'bytes': len(data), 'sha256': sha(data), 'git_blob_sha1': blob(data)})

receipt = {
    'schema': 'NBO_R120_AUTHOR_RESPONSE_READ_ONLY_CHECK_V1', 'checked_utc': now,
    'status': 'passed', 'scientific_execution': False, 'build_execution': False,
    'historical_or_R119_mutation': False,
    'route_count': len(routes['rows']), 'route_categories': dict(Counter(r['category'] for r in routes['rows'])),
    'distinct_report_documents': len(reports), 'exact_original_text_routes_checked': len(routes['rows']),
    'retained_R119_source_files_checked': len(sources),
    'controlling_advisory_items': len(requirements['items']),
    'explicit_pending_fields': pending,
    'constraint_sources_git_byte_verified': len(constraint_rows),
    'current_preparation_bindings': bound,
    'checker_sha256': sha(Path(__file__).read_bytes()),
    'scope': 'Checks source identity, complete inherited routes, exact original request text and honest pending R120 status. It does not establish new theorem validity, scientific outcomes or publication success. Later editorial changes need a new dated binding check; earlier receipts remain historical snapshots.',
}
exclusive(NEW / 'provenance/AUTHOR_RESPONSE_READ_ONLY_CHECK120.json', receipt)
exclusive(AUDIT / 'AUTHOR_RESPONSE_READ_ONLY_CHECK120.json', receipt)
print(json.dumps({k: receipt[k] for k in ['status', 'route_count', 'distinct_report_documents', 'retained_R119_source_files_checked', 'controlling_advisory_items', 'constraint_sources_git_byte_verified']}, indent=2))
