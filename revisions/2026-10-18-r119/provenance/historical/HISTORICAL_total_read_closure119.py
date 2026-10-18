"""Prove the disjoint read-evidence union equals the original 359-branch scope."""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import sqlite3

HERE=Path(__file__).parent
OUT=HERE/'HISTORICAL_remote_closure119'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    return h.hexdigest()


def main():
    manifest=HERE/'HISTORICAL_stream_all_blobs.jsonl'
    expected={r['sha']:r for r in map(json.loads,manifest.open())}
    assert len(expected)==66471
    db=sqlite3.connect(HERE/'HISTORICAL_index.sqlite');db.row_factory=sqlite3.Row
    rows={};counts=collections.Counter();parses=collections.Counter()
    def put(r):
        assert r['sha'] in expected,r['sha']
        assert r['sha'] not in rows,('overlapping read partitions',r['sha'])
        assert len(r['raw_sha256'])==64
        rows[r['sha']]=r;counts[r['read_partition']]+=1
        counts['total_unique_bytes']+=r['bytes']
        parses[r['interpretation_scope']]+=1
    for q in db.execute('select s.*,o.sha256,o.size from source_blobs s join objects o on s.sha=o.sha'):
        r=dict(q)
        if r['sha'] in expected:
            put({'sha':r['sha'],'raw_sha256':r['sha256'],'bytes':r['size'],
                 'read_partition':'historical_source_index','git_blob_hash_verified':True,
                 'interpretation_scope':r['parse_kind']+':'+r['parse_status'],
                 'evidence':'HISTORICAL_source_blobs.jsonl.gz and HISTORICAL_objects.jsonl.gz'})
    for path in sorted((HERE/'HISTORICAL_local_raw_run').glob('shard-*/records.jsonl')):
        for no,line in enumerate(path.open(),1):
            r=json.loads(line);assert r['git_blob_verified'] is True
            put({'sha':r['sha'],'raw_sha256':r['sha256'],'bytes':r['bytes_read'],
                 'read_partition':'available_raw_offline_stream','git_blob_hash_verified':True,
                 'interpretation_scope':r.get('parse',{}).get('format','parse_error'),
                 'format_parse_complete':r.get('parse',{}).get('semantic_complete'),
                 'evidence_file':str(path),'evidence_line':no,
                 'evidence_line_sha256':hashlib.sha256(line.encode()).hexdigest()})
    with gzip.open(OUT/'FINAL_OBJECT_UNION119.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);assert r['complete'] and r['git_blob_verified']
            put({'sha':r['sha'],'raw_sha256':r['sha256'],'bytes':r['bytes_read'],
                 'read_partition':'initially_missing_immutable_remote_stream',
                 'git_blob_hash_verified':True,'interpretation_scope':r['parse_format'],
                 'format_parse_complete':r['semantic_complete'],
                 'evidence_file':r['record_path'],'evidence_line':r['record_line'],
                 'evidence_line_sha256':r['record_line_sha256']})
    missing=sorted(set(expected)-set(rows));unexpected=sorted(set(rows)-set(expected))
    target=OUT/'ALL_66471_HISTORICAL_BLOB_READS119.jsonl.gz'
    with gzip.open(target,'wt',encoding='utf-8') as f:
        for s in sorted(rows):
            r=rows[s]
            r.update(witness_commit=expected[s]['witness_commit'],
                     witness_path=expected[s]['witness_path'])
            f.write(json.dumps(r,sort_keys=True)+'\n')
    summary={'scope':'Complete unique-byte/Git-identity read coverage of all blobs reachable from the original 359 branch references. Syntax extraction, opaque binary custody, safe array interpretation and mathematical proof verification are distinct.',
             'historical_branches':359,'distinct_historical_heads':301,
             'expected_unique_blobs':66471,'observed_unique_blobs':len(rows),
             'disjoint_partition_counts':dict(counts),'interpretation_counts':dict(parses),
             'missing_objects':missing,'unexpected_objects':unexpected,
             'all_historical_blob_bytes_read_and_git_verified':not missing and not unexpected,
             'all_historical_theorems_independently_proved':False,
             'all_historical_experiments_rerun':False,
             'all_historical_software_parse_success':False,
             'remaining_semantic_defects':['Three preserved historical Python syntax errors.','The exact historical R118_ACTIVE_SOURCE_DELTA.tar.gz is truncated; raw bytes are intact and verified.'],
             'opaque_scope':['PyTorch/model/object-array pickle contents are not executed or unpickled.','PDF/image/binary payloads are byte/hash audited; this union is not a visual or semantic review of every such payload.','Encoded/macro-generated mathematics requires the separate recovery and human proof audit.'],
             'historical_manifest_sha256':sha(manifest),
             'script_sha256':sha(Path(__file__)),
             'portable_union':{'path':target.name,'bytes':target.stat().st_size,'sha256':sha(target)}}
    (OUT/'ALL_HISTORY_READ_CLOSURE119.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,sort_keys=True))
    return 0 if summary['all_historical_blob_bytes_read_and_git_verified'] else 2


if __name__=='__main__':raise SystemExit(main())
